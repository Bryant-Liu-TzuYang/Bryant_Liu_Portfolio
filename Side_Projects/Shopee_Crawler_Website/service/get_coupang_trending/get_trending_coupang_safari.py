"""
This module will output the trending items from Coupang into a CSV file.
Safari version - uses local Safari browser instead of Chrome.
"""

import logging
import re
import pytz
import os
import time
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.safari.service import Service as SafariService

MAX_TIMEOUT_SECONDS = 60
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds between retries

# 設定 UTC+8 時區
taipei_tz = pytz.timezone('Asia/Taipei')

def get_trending(driver) -> str:
    """
    Search for the item on coupang homepage and return the corresponding link.

    Search for "one" item only. The iteration is done in the main function.

    Args:
        aitem_name: The name of the item to search for
        driver: WebDriver instance for web scraping
        client: OpenAI client for product comparison

    Returns:
        Tuple of (coupang_product_name, coupang_product_link) or error messages
    """

    coupang_web_links = {
        # "phone": f"https://www.tw.coupang.com/categories/手機-572306?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        # "computer": f"https://www.tw.coupang.com/categories/電腦-572307?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        # "home_electronic": f"https://www.tw.coupang.com/categories/家電數位-549477?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",

        "phone_only": f"https://www.tw.coupang.com/categories/手機-550279?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        "phone_accessories": f"https://www.tw.coupang.com/categories/手機配件-549919?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        "computer_laptop": f"https://www.tw.coupang.com/categories/電腦%2F平板-572309?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        "computer_accessories": f"https://www.tw.coupang.com/categories/電腦%2F平板周邊-550056?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        "game": f"https://www.tw.coupang.com/categories/遊戲-550183?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
        "home_electronic": f"https://www.tw.coupang.com/categories/家電數位-549477?listSize=120&filterType=&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=saleCountDesc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=",
    }

    # Get timestamp for the crawl
    time_stamp = datetime.now(taipei_tz).strftime('%Y-%m-%d')

    for category, web_link in coupang_web_links.items():
        # Check if file already exists
        output_file = f"../../data/ranking/coupang_trending_{category}_{time_stamp}.csv"
        if os.path.exists(output_file):
            logging.warning(f"File {output_file} already exists. Skipping {category} category.")
            continue

        logging.warning(f"Starting to crawl {category} category...")
        
        # Retry logic for each category
        for attempt in range(MAX_RETRIES):
            try:
                success = crawl_category(driver, category, web_link, time_stamp)
                if success:
                    logging.warning(f"Successfully crawled {category} category on attempt {attempt + 1}")
                    break
                else:
                    logging.warning(f"Failed to crawl {category} category on attempt {attempt + 1}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
            except Exception as e:
                mes = f"Attempt {attempt + 1} failed for {category}: {e}"
                logging.error(mes)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logging.warning(f"All {MAX_RETRIES} attempts failed for {category} category")


def crawl_category(driver, category, web_link, time_stamp) -> bool:
    """
    Crawl a specific category and return True if successful, False otherwise.
    """
    try:
        driver.get(web_link)
    except Exception as e:
        mes = f"getlink|Error opening coupang website: {e}"
        logging.error(mes)
        return False
        

    # get product name using explicit wait
    try:
        wait = WebDriverWait(driver, timeout=MAX_TIMEOUT_SECONDS)
        prdnames = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='ProductUnit_productName__gre7e']"))
        )
    except Exception as e:
        if "invalid session id" in str(e).lower():
            mes = f"session error: {e}"
        else:
            mes = f"no search result: {e}"
        logging.warning(mes)
        logging.warning(f"{mes}")
        return False

    # get product links - only from product units
    try:
        product_units = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.ProductUnit_productUnit__Qd6sv"))
            )
        links = []
        for unit in product_units:
            try:
                link_elem = unit.find_element(By.CSS_SELECTOR, "a[href]")
                links.append(link_elem.get_attribute("href"))
            except:
                # If no link found in this unit, append None to maintain index alignment
                links.append(None)
    except Exception as e:
        mes = f"getlink|Error getting product links: {e}"
        logging.error(mes)
        return False

    # get product prices
    try:
        prices = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "strong[class='Price_priceValue__A4KOr']"))
        )
    except Exception as e:
        mes = f"getlink|Error getting product prices: {e}"
        logging.error(mes)
        return False

    # Ensure we have matching counts for safe iteration
    min_count = min(len(prdnames), len(links), len(prices))
    if min_count == 0:
        return False
    
    # Create a DataFrame with product information
    products_data = []
    for i in range(min_count):
        product_name = prdnames[i].text
        product_link = links[i]
            
        try:
            # Clean and convert price to integer
            price_text = prices[i].text
            price_value = int(re.sub("[$,]+", "", price_text))
        except (ValueError, AttributeError):
            price_value = 0  # Set default value if price parsing fails
            
        products_data.append({
            'ranking': i+1,
            'name': product_name,
            'price': price_value,
            'link': product_link,
        })
 
    try:
        df = pd.DataFrame(products_data)
        output_file = f"../../data/ranking/coupang_trending_{category}_{time_stamp}.csv"
        # Ensure the directory exists
        os.makedirs("../../data/ranking", exist_ok=True)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        logging.warning(f"Successfully saved {category} data to {output_file}")
        return True
    except Exception as e:
        mes = f"Error saving CSV file for {category}: {e}"
        logging.error(mes)
        return False



if __name__ == "__main__":
    def initialize_webdriver() -> webdriver.Safari:
        """
        Initialize and return a Safari WebDriver with specified options.
        
        Note: Safari WebDriver requires the following setup:
        1. Enable "Allow Remote Automation" in Safari's Develop menu
        2. Safari > Preferences > Advanced > Show Develop menu in menu bar
        3. Develop > Allow Remote Automation
        """
        from selenium import webdriver
        from selenium.webdriver.safari.options import Options
        
        # Safari options (more limited compared to Chrome)
        options = Options()
        
        # Note: Safari doesn't support headless mode natively
        # Safari also has limited option support compared to Chrome
        
        try:
            # Create Safari service
            service = SafariService()
            
            # Initialize Safari driver
            driver = webdriver.Safari(service=service, options=options)
            
            # Set page load timeout
            driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
            
            logging.warning("Safari WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            logging.error(f"Failed to initialize Safari WebDriver: {e}")
            logging.error("Make sure to enable 'Allow Remote Automation' in Safari's Develop menu")
            logging.error("Safari > Preferences > Advanced > Show Develop menu in menu bar")
            logging.error("Develop > Allow Remote Automation")
            raise

    try:
        driver = initialize_webdriver()
        get_trending(driver)
    except Exception as e:
        logging.error(f"Script execution failed: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
