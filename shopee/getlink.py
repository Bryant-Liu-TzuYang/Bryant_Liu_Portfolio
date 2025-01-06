# Latest Update: 2024/10/22

from selenium import webdriver
import re
import pandas as pd
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, 
    UnexpectedAlertPresentException, 
    NoAlertPresentException, 
    NoSuchElementException, 
    InvalidArgumentException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from same_prouct_or_not import same_product_or_not
from pathlib import PurePath
from openai import OpenAI


MAX_TIMEOUT_SECONDS = 10

def initialize_webdriver() -> webdriver.Chrome:
    """
    Initialize and return a Chrome WebDriver with specified options.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.page_load_strategy = 'eager'
    options.chrome_executable_path = "/Users/bryant_lue/Documents/GitHub/Shopee_Link_Crawler/chromedriver"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
    return driver


def search(aitem_name, driver, client):
    driver.get("https://www.momoshop.com.tw/main/Main.jsp")
    
    item_search_input = driver.find_element(By.ID, "keyword")
    search_button = driver.find_element(By.CLASS_NAME, "inputbtn")
    item_search_input.send_keys(aitem_name)
    search_button.send_keys(Keys.ENTER)


    product_Name_List = driver.find_elements(By.CLASS_NAME, "prdName")
    elems = driver.find_elements(By.CSS_SELECTOR, "a[href][class='goods-img-url'][title]")
    links = [elem.get_attribute('href') for elem in elems]
    
    if (len(links) == 0):
        elems = driver.find_elements(By.CSS_SELECTOR, "a[class='goodsUrl'][href]")
        links = [elem.get_attribute('href') for elem in elems]

    prices = driver.find_elements(By.CLASS_NAME, "price")

    lowest_price_temp = 100000000000000
    momo_price_temp = ""
    lowest_price_index = 100000000000000

    #iterate through items on a momo page search result
    if (len(product_Name_List) == 0):
        return "no search result", "no search result"
    
    for i in range(len(product_Name_List)):
        product_Name = product_Name_List[i].text
        price = prices[i]
        
        try:
            momo_price_temp = int(re.sub("[$,]+","",price.text))
        except:
            continue
        
        is_the_same_product = same_product_or_not(aitem_name, product_Name, client=client)
        if (is_the_same_product == 0):
            continue
        
        # price_gap = (ashopee_price - momo_price_temp) / momo_price_temp

        if (momo_price_temp < lowest_price_temp):
            lowest_price_temp = momo_price_temp
            lowest_price_index = int(i)

    if lowest_price_index == 100000000000000:
        return "no corresponded item", "no corresponded item"
    else:
        correct_link = links[lowest_price_index]
        correct_name = product_Name_List[lowest_price_index].text
        return correct_name, correct_link



def accept_alert(driver: webdriver.Chrome):
    driver.refresh()
    wait = WebDriverWait(driver, timeout=10)
    alert = wait.until(lambda d : d.switch_to.alert)
    alert.accept()
    return


def handle_unexpected_alert(driver: webdriver.Chrome) -> None:
    """
    Handle an unexpected alert by refreshing the page and accepting the alert.
    """
    try:
        accept_alert(driver)
    except NoAlertPresentException:
        return


def handle_server_timeout(df: pd.DataFrame, i, driver, aitem_name, client):
    try:
        df.loc[i, "Momo link"], df.loc[i, "Momo price"] = search(aitem_name, driver, client)
    except UnexpectedAlertPresentException:
        driver.close()
        time.sleep(10)
        driver = initialize_webdriver()
        handle_server_timeout(df, i, driver, aitem_name, client)


### <initialization>
def main() -> None:
    driver = initialize_webdriver()

    RAWDATA_PATH = PurePath("/Users/bryant_lue/Documents/GitHub/Shopee_Link_Crawler/data/11_11 Spike_20241029.csv")
    OUTPUT_FILE_PATH = PurePath("output/11_11 Spike_20241029.csv")
    df = pd.read_csv(RAWDATA_PATH)

    start_time = time.time()
    
    item_names = df.iloc[:,0]
    total_crawl_num = len(item_names)

    client = OpenAI(
        api_key="SECRET"
    )

    text_to_removed = [
    "現貨", "廠商直送", "蝦皮直送", "大型配送", "含運無安裝", 
    "含基本安裝","舊機回收", "送原廠禮", "免運費", "官方旗艦店", "公司貨",
    
    "第一視角飛行體驗", "陳列機限地區", "含基本安裝", "基本安裝", "七天鑑賞期", "買一送一", 
    "保固延長", "支援線上客服", "限量供應", "含安裝服務", "30天退貨保障", 
    "VIP專屬服務",
    
    "提供租賃方案", "低碳配送", "保護包裝", "同日到貨", "環保包裝", 
    "品牌直營", "免服務費", "多件折扣", "到府維修", "分期零利率",
    
    "專屬會員折扣", "全新機保證", "虛擬實境體驗", "新機上市", "預購優惠","免運"
    ]

    pattern = '|'.join(map(re.escape, text_to_removed))


    for i in range(total_crawl_num):
        try:
            # clean aitem_name
            aitem_name = re.sub(pattern, "", item_names[i])
            aitem_name = re.sub(r'[【】\s+]', ' ', aitem_name).strip()
        except:
            continue

        try: 
            df.loc[i, 'Momo item name'], df.loc[i, 'Momo link'] = search(aitem_name, driver, client)
        except TimeoutException:
            print("TimeoutException")
            try:
                driver.close()
            except UnexpectedAlertPresentException:
                print("handling UnexpectedAlertPresentException")
                handle_unexpected_alert(driver)
            
            driver = initialize_webdriver()
            print("server_timeout_SOP_start")
            handle_server_timeout(df, i, driver, aitem_name, client)
        
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
        print(f"Total time spent: {elapsed_time}")
        
        df.to_csv(OUTPUT_FILE_PATH)

    driver.quit()


main()
