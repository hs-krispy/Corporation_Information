import pandas as pd
import re
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from get_certification_code import ocr

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = uc.Chrome(service=Service(ChromeDriverManager().install()), 
                          options=chrome_options,
                          headless=True)
time.sleep(1)

selected_info = ['매출액', '매출원가', '매출총이익', '판매비와 관리비', '영업손익', '영업외비용', '당기순손익']

# 스타트업 재무제표
driver.get("https://www.smes.go.kr/venturein/home/viewHome")

def search_target_corp(corparation_name):
    driver.find_element(By.ID, 'totalSearch').click()
    time.sleep(1)

    driver.find_element(By.ID, 'totalSearch').send_keys(corparation_name)
    driver.find_element(By.ID, 'totalSearch').send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, '//*[@id="real_contents"]/div[2]/ul/li[3]/a').click()
    time.sleep(0.5)
    
def scarp_info(corparation_name):
    try:
        search_target_corp(corparation_name)
        driver.find_element(By.XPATH, '//*[@id="real_contents"]/div[2]/div[2]/table/tbody/tr/td[1]/a').send_keys(Keys.ENTER)
    except:
        print('no search result')
        return
    
    time.sleep(1)
    file_path = './target_img.png'
    while True:
        img_element = driver.find_element(By.ID, 'captchaImg')
        img_png = img_element.screenshot_as_png
        with open(file_path, "wb") as file:  
            file.write(img_png) 
            
        certification_number = ocr(file_path)

        driver.find_element(By.XPATH, '//*[@id="answer"]').send_keys(certification_number)
        driver.find_element(By.XPATH, '//*[@id="answer"]').send_keys(Keys.ENTER)
        time.sleep(1)
        try:
            driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/ul/li[2]/a').click()
            time.sleep(1)
            break
        except:
            print('wrong certification number')
            pass
    
    driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/div[1]/div[2]/ul/li[2]/a').click()
    time.sleep(1)
    print(corparation_name)
    try:
        column_names = driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/div[1]/div[2]/div/div[2]/div[2]/table/thead/tr').text
        information = driver.find_element(By.XPATH, '//*[@id="real_contents"]/div/div[1]/div[2]/div/div[2]/div[2]/table/tbody').text
    except:
        print('no finance information')
        return 
    return [column_names, information]

def parse_info(text):
    exclude_numbering = ' '.join(text.split(' ')[1:])
    
    check_bracket = re.search(r'\(.*\)', exclude_numbering) 
    check_cost = re.search(r'\d', exclude_numbering)
    
    return [exclude_numbering[:check_bracket.span()[0]].strip()] + exclude_numbering[check_bracket.span()[1]:].strip().split(' ') if check_bracket is not None \
        else [exclude_numbering[:check_cost.span()[0]].strip()] + exclude_numbering[check_cost.span()[0]:].strip().split(' ')

def get_info(column_names, info_text, corp_name):
    parsed_info = list(map(lambda x: parse_info(x), info_text.split('\n')))
    result_df = pd.DataFrame(parsed_info, columns=column_names)
    result_df = result_df[result_df[column_names[0]].isin(selected_info)]
    result_df.loc[:, result_df.columns[1:]] = result_df[result_df.columns[1:]].applymap(lambda x: int(x.replace(',', '')))
    result_df['name'] = corp_name
    
    return result_df[['name'] + column_names]

