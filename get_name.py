import re
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

SCROLL_PAUSE_TIME = 2

driver = uc.Chrome(service=Service(ChromeDriverManager().install()), 
                          options=chrome_options,
                          headless=False)

driver.get('https://www.wanted.co.kr/jobsfeed')

def get_job_info(keyword):
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/aside/ul/li[1]/button').click()
    driver.implicitly_wait(2)

    driver.find_element(By.XPATH, '//*[@id="nav_searchbar"]/div/div[2]/div/form/input').send_keys(keyword)
    driver.find_element(By.XPATH, '//*[@id="nav_searchbar"]/div/div[2]/div/form/input').send_keys(Keys.ENTER)
    driver.implicitly_wait(1)
    
    driver.find_element(By.XPATH, '//*[@id="search_tab_position"]').click()
    driver.implicitly_wait(1)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if last_height == new_height:
            break
        last_height = new_height
    
    job_corp_names = driver.find_elements(By.CLASS_NAME, 'JobCard_companyName__vZMqJ')
    job_locations = driver.find_elements(By.CLASS_NAME, 'JobCard_location__2EOr5')
    job_position_names = driver.find_elements(By.CLASS_NAME, 'JobCard_title__ddkwM')
    job_div = driver.find_element(By.XPATH, '//*[@id="search_tabpanel_position"]/div/div[4]')
    job_links = job_div.find_elements(By.TAG_NAME, 'a')
    
    job_info_df = pd.DataFrame(list(zip(map(lambda x: x.text, job_corp_names), 
                                   map(lambda x: x.text, job_locations), 
                                   map(lambda x: x.text, job_position_names),
                                    map(lambda x: x.get_attribute('href'), job_links))),
                               columns=['name', 'location', 'position', 'link'])

    selected_job_info_df = job_info_df[(job_info_df.location.apply(lambda x: True if re.search(r'서울|경기', x) is not None else False))
                & (job_info_df.position.apply(lambda x: True if re.search(r'data|데이터', x.lower()) is not None else False))
                & (job_info_df.position.apply(lambda x: True if re.search(r'analyst|scientist|과학|분석|애널리스트|사이언티스트', x.lower()) is not None else False))]
    
    return selected_job_info_df
    