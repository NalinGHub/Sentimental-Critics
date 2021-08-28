PLACES_CSV = 'place.csv'
REVIEWS_CSV = 'reviews.csv'
MAX_REVIEWS = 500
HEADLESS = True

# -*- coding: utf-8 -*-
"""
@author: Nalin Mehra
"""

import pandas as pd
import time
import selenium
import csv
import re
from selenium.webdriver.support.ui import WebDriverWait
#from selenium import WebdriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

def parse(review):
    item = {}
    try:
        review_text = (review.find('span', class_='section-review-text').text).replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    except Exception as e:
        review_text = None
    rating = float(review.find('span', class_='section-review-stars')['aria-label'].split(' ')[1])
    item['text'] = review_text
    item['rating'] = rating
    return item

def main():
    options = webdriver.chrome.options.Options()
    options.add_argument("--lang=en")
    options.headless = HEADLESS
    driver = webdriver.Chrome(chrome_options=options)
    file1 = open('reviews.csv', mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(file1)
    writer.writerow(['text', 'stars'])
#    url = 'https://www.google.com/maps/place/El+Indio+Mexican+Restaurant+13th+St/@29.655103,-82.3411537,17z/data=!4m7!3m6!1s0x88e8a386a5316e81:0xf88fba24cc6e73db!8m2!3d29.655103!4d-82.338965!9m1!1b1'
#    url = 'https://www.google.com/maps/place/Prum%27s+Kitchen/@29.6522797,-82.3283774,16z/data=!4m8!1m2!2m1!1srestaurants+near+Gainesville,+FL!3m4!1s0x88e8a34a15ae81ed:0xc62685e7d18d79d!8m2!3d29.6517013!4d-82.3251762?hl=en'
#    url = 'https://www.google.com/maps/place/Vegan+Gator+Food+Truck/@29.6522797,-82.3283774,16z/data=!4m8!1m2!2m1!1srestaurants+near+Gainesville,+FL!3m4!1s0x88e8a387666f9813:0x7731a5a1c839359f!8m2!3d29.6594099!4d-82.3269004?hl=en'
    placesCSV = pd.read_csv(PLACES_CSV)
    mapUrls = [mapUrl for mapUrl in placesCSV['placeUrl']]
    for url in mapUrls:
        num_reviews = 0
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        try:
            reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@jsaction='pane.rating.moreReviews']")))
        except TimeoutException as e:
            print("Place url " + url + "is not correctly formatted. Throwing " + e)
        reviews_string = str(reviews_button.get_attribute('aria-label'))
        num_reviews = int(re.search(r'\d+', reviews_string.replace(',',''))[0])
        #print(num_reviews)
        if(num_reviews > MAX_REVIEWS):
            num_reviews = MAX_REVIEWS
        reviews_button.click()
        #open dropdown menu
        clicked = False
        tries = 0
        time.sleep(1)
        while not clicked and tries < 10:
            try:
                sort = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
                sort.click()
    
                clicked = True
                time.sleep(3)
            except Exception as e:
                tries += 1
                print('failed try')
            # failed to open the dropdown...
            if tries == 10:
                return -1
        time.sleep(3)
        
        
        
        recent_rating_bt = driver.find_elements_by_xpath('//li[@role=\'menuitemradio\']')[1]
        recent_rating_bt.click()
        time.sleep(3)
        
        a = 0
        
        while a < num_reviews:
            time.sleep(3)
#            scrollable_div = driver.find_element_by_css_selector('div.section-layout.section-scrollbox.scrollable-y.scrollable-show')
            scrollable_div = driver.find_element_by_css_selector('div.section-layout.section-scrollbox.mapsConsumerUiCommonScrollable__scrollable-y.mapsConsumerUiCommonScrollable__scrollable-show')
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            #click more on review if applicable
            links = driver.find_elements_by_xpath('//button[@class=\'section-expand-review blue-link\']')
            for l in links:
                l.click()
            time.sleep(2)
            #now parse the reviews
            response = BeautifulSoup(driver.page_source, 'html.parser')
            rlist = response.find_all('div', class_='section-review-content')
            parsed_reviews = []
            for index, review in enumerate(rlist):
                if index >= a:
                    parsed = parse(review)
                    if parsed['text']:
                        parsed_reviews.append(parsed)
                    a+=1
            for r in parsed_reviews:
                row_data = list(r.values())
                print(row_data)
                writer.writerow(row_data)
    
    file1.close()

if __name__ == '__main__':
    main()