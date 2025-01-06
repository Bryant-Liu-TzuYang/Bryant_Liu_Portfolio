# Latest Update 2024/8/16

from selenium import webdriver
import re
import pandas as pd
import logging
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, 
    UnexpectedAlertPresentException, 
    NoAlertPresentException, 
    NoSuchElementException, 
    InvalidArgumentException,
    InvalidSessionIdException
)
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.alert import Alert
# from selenium.webdriver.support import expected_conditions as EC


def initialize_webdriver() -> webdriver.Chrome:
    """
    Initialize and return a Chrome WebDriver with specified options.
    """
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f'--user-agent={USER_AGENT}')
    options.page_load_strategy = 'eager'
    options.chrome_executable_path = "/Users/bryant_lue/Documents/GitHub/Shopee_Link_Crawler/chromedriver"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
    return driver


def init_log_info(logger: logging.Logger, total_crawl_num):
    logger.info(f"Expected Total Crawl Num = {total_crawl_num}")
    logger.info(f"MAX_TIMEOUT_SECONDS = {MAX_TIMEOUT_SECONDS}")
    logger.info("-"*50)
    logger.info("-"*50)
    logger.info("-"*50)


def setup_logging() -> logging.Logger:
    """
    Set up logging configuration and return a logger instance.
    """
    now = datetime.now()
    date_time = now.strftime("%Y%m%d_%H:%M:%S")
    logging.basicConfig(
    filename=f'log/main_{date_time}.log',
    encoding='utf-8',
    level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    return logger


def find_seoprice(driver: webdriver.Chrome, logger: logging.Logger):
    lowest_price_temp = 100000000000000
    price_temp = ""

    tags = driver.find_elements(By.CLASS_NAME, "seoPrice")
    
    for tag in tags:
        logger.info(tag.text)
        price_temp = int(tag.text.replace(",", ""))
        if price_temp < lowest_price_temp:
            lowest_price_temp = price_temp

    logger.info(f"lowest_price_temp = {lowest_price_temp}")
    return lowest_price_temp


def find_special(driver: webdriver.Chrome, logger: logging.Logger):
    lowest_price_temp = 100000000000000
    price_temp = ""

    tags = driver.find_elements(By.CLASS_NAME, "special")
    
    for tag in tags:
        logger.info(tag.text)
        text_temp = tag.text.replace(",", "")
        price_temp = int(re.search(r'\d+', text_temp).group())

        if price_temp < lowest_price_temp:
            lowest_price_temp = price_temp

    logger.info(f"lowest_price_temp = {lowest_price_temp}")
    return lowest_price_temp


def fetch_momo_price(driver: webdriver.Chrome, logger: logging.Logger, alink: str):
    """
    Fetch the price from a Momo product page. Returns the lowest price found as a string.
    If no price is found or an error occurs, returns an empty string.
    """
    global valid_num
    global invalid_link_num
    
    # make sure page is loaded
    try:
        driver.get(alink)
    except InvalidArgumentException:
        logger.info("InvalidArgumentException")
        invalid_link_num += 1
        return "Invalid Link" # leave
    except:
        logger.info("InvalidSessionIdException")
        driver.quit()
        time.sleep(10)
        driver = initialize_webdriver()
        fetch_momo_price(driver=driver, logger=logger, alink=alink)
    
    # find seoPrice
    try:
        lowest_price_temp = find_seoprice(driver, logger)
    except UnexpectedAlertPresentException:
        logger.info("UnexpectedAlertPresentException")
        try:
            accept_alert(driver, logger)
            lowest_price_temp = find_seoprice(driver, logger)
        except NoAlertPresentException:
            logger.info("NoAlertPresent")
            return "NoAlertPresent"
    except NoSuchElementException:
        logger.info("NoSuchElementException")
        return "NoSuchElementException" # leave
    

    # find special
    if (lowest_price_temp == 100000000000000):
        logger.info("now try to find special")
        try:
            lowest_price_temp = find_special(driver, logger)
        except UnexpectedAlertPresentException:
            logger.info("UnexpectedAlertPresentException")
            try:
                accept_alert(driver, logger)
                lowest_price_temp = find_special(driver, logger)
            except NoAlertPresentException:
                logger.info("NoAlertPresent")
                return "NoAlertPresent"
        except NoSuchElementException:
            logger.info("NoSuchElementException")
            return "NoSuchElementException" # leave


    if (lowest_price_temp == 100000000000000):
        lowest_price_temp = ""
        logger.info("sold_out")
        return "sold_out"  # leave
    else:
        logger.info("normal process")
        valid_num += 1
        return lowest_price_temp  # leave


def accept_alert(driver: webdriver.Chrome, logger: logging.Logger):
    driver.refresh()
    wait = WebDriverWait(driver, timeout=10)
    alert = wait.until(lambda d : d.switch_to.alert)
    logger.info(f"Alert text: {alert.text}")
    alert.accept()
    logger.info("accept a alert")
    return


def handle_unexpected_alert(driver: webdriver.Chrome, logger: logging.Logger) -> None:
    """
    Handle an unexpected alert by refreshing the page and accepting the alert.
    Logs the alert text if found.
    """
    try:
        accept_alert(driver, logger)
    except NoAlertPresentException:
        logger.info("No alert present")


def handle_server_timeout(df_data: pd.DataFrame, logger: logging.Logger, i, alink:str, driver):
    logger.info("server_timeout_SOP_start")
    try:
        df_data.loc[i, "Momo Price"] = fetch_momo_price(driver, logger, alink)
    except:
        logger.info("Cannot connect to server")
        driver.close()
        time.sleep(10)
        driver = initialize_webdriver()
        handle_server_timeout(df_data, logger, i, alink, driver)


def performance_logging(logger: logging.Logger, start_time: time):
    global crawled_num
    global valid_num
    global invalid_link_num
    
    logger.info(f"crawled_num = {crawled_num}")
    logger.info(f"valid_num = {valid_num}")
    
    try:
        logger.info(f"valid_percentage = {(valid_num/crawled_num):.2%}")
    except ZeroDivisionError:
        logger.info(f"valid_percentage = {0:.2%}")
    
    logger.info(f"invalid_link_num = {invalid_link_num}")
    time_dis = time.strftime("%H:%M:%S",time.gmtime(time.time()-start_time))
    logger.info(f"total spend {time_dis}")
    logger.info("")
    logger.info("-"*50)
    logger.info("-"*50)
    logger.info("")


def main() -> None:
    """
    Main function to initialize the logger and webdriver, crawl prices from Momo links,
    and save the results to a CSV file. Logs the execution details.
    """
    global valid_num
    global invalid_link_num
    global crawled_num

    logger = setup_logging()
    driver = initialize_webdriver()

    OUTPUT_FILE_PATH = "output/11_11 Spike_20241029 copy.csv"
    RAWDATA_PATH = "/Users/bryant_lue/Documents/GitHub/Shopee_Link_Crawler/data/11_11 Spike_20241029 copy.csv"
    df_data = pd.read_csv(RAWDATA_PATH)

    start_time = time.time()

    row = df_data.iloc[:, 1]
    total_crawl_num = len(row)
    

    init_log_info(logger, total_crawl_num)

    for i in range(total_crawl_num):
        alink = row[i]
        logger.info(f"now moving on to item {i}")
        logger.info(f"visiting {alink}")

        
        if pd.notna(alink):
            crawled_num += 1
            try:
                df_data.loc[i, "Momo Price"] = fetch_momo_price(driver, logger, alink)
            except TimeoutException:
                logger.info("TimeoutException")
                try:
                    driver.close()
                except UnexpectedAlertPresentException:
                    handle_unexpected_alert(driver, logger)
                
                driver = initialize_webdriver()
                handle_server_timeout(df_data, logger, i, alink, driver)

        df_data.to_csv(OUTPUT_FILE_PATH)

        performance_logging(logger, start_time)

    driver.quit()

MAX_TIMEOUT_SECONDS = 10
valid_num = 0
invalid_link_num = 0
crawled_num = 0

main()
