import logging
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .same_prouct_or_not import same_product_or_not

MAX_TIMEOUT_SECONDS = 120

def search(aitem_name, driver, client):
    """
    Search for the item on coupang homepage and return the corresponding information.

    Search for "one" item only. The iteration is done in the main function.

    Args:
        aitem_name: The name of the item to search for
        driver: WebDriver instance for web scraping
        client: OpenAI client for product comparison

    Returns:
        Tuple of (coupang_product_name, coupang_product_link, coupang_product_price) or error messages
    """

    try:
        driver.get("https://www.tw.coupang.com/")
    except Exception as e:
        mes = f"getlink|Error opening coupang website: {e}"
        logging.error(mes)
        return f"{mes}", f"{mes}", 0

    # sending keywords to search bar and then click search button
    try:
        # Wait for the search input to be clickable
        wait = WebDriverWait(driver, timeout=MAX_TIMEOUT_SECONDS)
        
        # Try multiple selectors for the search input, prioritizing the working one
        search_input_selectors = [
            "input[name='q']:not(.ad-keyword)",  # Try the one without ad-keyword class first
            "input[name='q']",  # Fallback to any input with name='q'
            "input[type='text'][title='酷澎商品搜尋']",
            "input.headerSearchKeyword",
            "input[placeholder*='搜尋']"
        ]
        
        item_search_input = None
        for selector in search_input_selectors:
            try:
                # First check if element exists and is displayed
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Try to wait for it to be clickable
                        item_search_input = wait.until(
                            lambda d: element if element.is_displayed() and element.is_enabled() else None
                        )
                        break
                if item_search_input:
                    break
            except:
                continue
        
        if item_search_input is None:
            raise Exception("Could not find interactable search input element")
        
        # Scroll to the element to ensure it's in view
        driver.execute_script("arguments[0].scrollIntoView(true);", item_search_input)
        time.sleep(1)
        
        # Clear any existing text and send the search term
        item_search_input.clear()
        item_search_input.send_keys(aitem_name)
        
        # Try multiple selectors for the search button
        search_button_selectors = [
            "button[type='submit'][title='搜尋']",
            "button[title='搜尋']",
            "button.headerSearchBtn",
            "form button[type='submit']"
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        search_button = button
                        break
                if search_button:
                    break
            except:
                continue
        
        if search_button is None:
            item_search_input.send_keys(Keys.ENTER)
        else:
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(0.5)
            search_button.click()
        
    except Exception as e:
        mes = f"getlink|Error interacting with search elements: {e}"
        logging.error(mes)
        return f"{mes}", f"{mes}", 0

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
        return "no search result", "no search result", 0

    # get product links - only from product units
    product_units = driver.find_elements(By.CSS_SELECTOR, "li.ProductUnit_productUnit__Qd6sv")
    links = []
    for unit in product_units:
        try:
            link_elem = unit.find_element(By.CSS_SELECTOR, "a[href][target='_blank']")
            links.append(link_elem.get_attribute("href"))
        except:
            # If no link found in this unit, append None to maintain index alignment
            links.append(None)

    # get product prices
    prices = driver.find_elements(By.CSS_SELECTOR, "strong[class='Price_priceValue__A4KOr']")

    # Ensure we have matching counts for safe iteration
    min_count = min(len(prdnames), len(links), len(prices))
    if min_count == 0:
        return "no search result", "no search result", 0

    # Create a DataFrame with product information
    products_data = []
    for i in range(min_count):
        product_name = prdnames[i].text
        product_link = links[i]
        
        # Skip if link is None (no valid link found for this product)
        if product_link is None:
            continue
            
        try:
            # Clean and convert price to integer
            price_text = prices[i].text
            price_value = int(re.sub("[$,]+", "", price_text))
        except (ValueError, AttributeError):
            # Skip products with invalid prices
            continue
            
        products_data.append({
            'name': product_name,
            'link': product_link,
            'price': price_value,
            'original_index': i
        })
    
    # Convert to DataFrame and check if we have any valid products
    if not products_data:
        return "no search result", "no search result", 0
        
    df = pd.DataFrame(products_data)
    
    # Sort by price in ascending order (lowest price first)
    df_sorted = df.sort_values('price', ascending=True).reset_index(drop=True)
    
    # Iterate through sorted products and find the first matching one
    for _, row in df_sorted.iterrows():
        coupang_Product_Name = row['name']
        product_link = row['link']
        price = row['price']
        
        # If client is available, use AI comparison
        if client is not None:
            is_the_same_product = same_product_or_not(
                prd1=aitem_name, prd2=coupang_Product_Name, client=client
            )
            
            # If this is the same product, return it immediately (it has the lowest price)
            if is_the_same_product == 1:
                return coupang_Product_Name, product_link, price
    
    # If no matching product found
    return "no corresponding item", "no corresponding item", 0



if __name__ == "__main__":
    def initialize_webdriver() -> webdriver.Chrome:
        """
        Initialize and return a Chrome WebDriver with specified options.
        """
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller
        import platform

        options = Options()
        # options.add_argument("--headless=new")
        # options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        # options.add_argument("--disable-application-cache")
        # options.add_argument("--disable-translate")
        # options.add_argument("--disable-background-networking")
        options.add_argument("--disable-client-side-phishing-detection")
        options.page_load_strategy = "eager"

        system = platform.system()
        arch = platform.machine()

        # Mac M1 → Chromium + chromedriver_py
        if system == "Darwin" and arch == "arm64":
            from chromedriver_py import binary_path

            svc = webdriver.ChromeService(executable_path=binary_path)
            driver = webdriver.Chrome(options=options, service=svc)

        # Windows and Linux → autoinstaller (automatically downloads correct version)
        elif system in ["Windows", "Linux"]:
            if system == "Linux":
                options.binary_location = "/usr/bin/google-chrome"
            
            chromedriver_autoinstaller.install()
            driver = webdriver.Chrome(options=options)

        else:
            raise EnvironmentError(f"Unsupported platform: {system}-{arch}")

        driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
        return driver
    driver = initialize_webdriver()
    client = None  # Replace with actual OpenAI client initialization if needed
    item_name = "Apple iPhone 16 256GB 6.1吋"
    from openai import OpenAI
    OPEN_API_KEY = (
        "sk-proj-jb1EUVA0fiEayF_84ImFYstsuxtMC1qGFSdo4AHOfUkmtAiCJiCyuNmCnn63c3kRjD"
        "rylt2UOzT3BlbkFJhE1_44XPbFqBra_STstH2RzA1qjBkYDLeD3xemUSvUQtfCO3UtADpS"
        "KRZgdZxUju3ddSJOlTEA"
    )
    client = OpenAI(api_key=OPEN_API_KEY)
    name, link, price = search(item_name, driver, client)
    print(f"Coupang result: Name={name}, Link={link}, Price={price}")
    driver.quit()
