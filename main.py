from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import time
import re
import os
from datetime import datetime

def amazon_reviews(asin):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("disable-gpu")
    
    # chromedriver.exe 설치된 경로
    driver = wd.Chrome(executable_path = 'chromedriver.exe', options = options)

    url = f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1'
    driver.get(url)
    driver.implicitly_wait(10)
    res = driver.page_source
    obj = bs(res, 'html.parser')

    # 총 리뷰 수
    rev = obj.select('#filter-info-section > div > span')[0].get_text().strip()
    rev = int(rev.split(' ')[4].replace(',', ''))
    print("total contents: " + str(rev))

    stars = []
    contents = []

    while len(stars) < rev:
        time.sleep(3)
        source = driver.page_source
        bs_obj = bs(source, "html.parser")

        # 리뷰 평점
        for u in bs_obj.findAll('i', {'data-hook' : 'review-star-rating'}):
            star = u.get_text().strip()
            star = star.split(' ')[-1]
            star = int(star.replace('.', ''))/10
            stars.append(star)

        # 리뷰 내용
        for a in bs_obj.findAll('span', {'data-hook' : 'review-body'}):
            content = a.get_text().strip()
            contents.append(content)

        print("to do: " + str(rev - len(stars)))

        if rev - len(stars) < 10:
            break
        
        # 다음 페이지
        driver.find_element(By.XPATH, '//div[@id="cm_cr-pagination_bar"]/ul/li[2]/a').click()
        # 크롤링 - 다음 페이지 제어를 위해 임시 데이터('//*[@id="a-autoid-3"]/span/i') 로딩 기다림
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="a-autoid-3"]/span/i')))

    driver.close()
    driver.quit()
    df = pd.DataFrame({'rating' : stars, "contents" : contents})
    
    return df

# example: apple airpods max - sky blue
code = 'B08PZJN7BD'
data = amazon_reviews(code)
data.to_csv(code + '.csv', index = False)