import logging
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from .same_prouct_or_not import same_product_or_not

MAX_TIMEOUT_SECONDS = 120


def accept_alert(driver: webdriver.Chrome):
    """Accept an alert dialog in the browser."""
    driver.refresh()
    wait = WebDriverWait(driver, timeout=10)
    alert = wait.until(lambda d: d.switch_to.alert)
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
    

def sendkeywords_and_search(aitem_name, driver):
    """
    Send keywords to the search bar and perform the search action.

    Args:
        aitem_name: The name of the item to search for
        driver: WebDriver instance for web scraping
    """
    item_search_input = driver.find_element(By.NAME, "search-input")
    search_button = driver.find_element(By.CSS_SELECTOR, "button[type='button'][class*='rounded-bl-[0px]']")
    item_search_input.send_keys(aitem_name)
    search_button.send_keys(Keys.ENTER)


def search(aitem_name, driver, client):
    """
    Search for the item on Momo homepage and return the corresponding information.

    Search for "one" item only. The iteration is done in the main function.

    Args:
        aitem_name: The name of the item to search for
        driver: WebDriver instance for web scraping
        client: OpenAI client for product comparison

    Returns:
        Tuple of (momo_product_name, momo_product_link, momo_product_price) or error messages
    """

    try:
        driver.get("https://www.momoshop.com.tw/main/Main.jsp")
    except Exception as e:
        mes = f"getlink|Error opening Momo website: {e}"
        logging.error(mes)
        return f"{mes}", f"{mes}", 0

    try:
        sendkeywords_and_search(aitem_name, driver)
    except Exception as e:
        if "element click intercepted" in str(e).lower():
            handle_unexpected_alert(driver)
            sendkeywords_and_search(aitem_name, driver)
        else:
            mes = f"search_momo | Failed to send keywords and search: {e}"
            logging.error(mes)
            return f"{mes}", f"{mes}", 0


    # get product name using explicit wait
    # todo: Currently using CLASS_NAME, may need optimization
    try:
        wait = WebDriverWait(driver, timeout=MAX_TIMEOUT_SECONDS)
        product_Name_List = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "prdName"))
        )
    except Exception as e:
        if "invalid session id" in str(e).lower():
            mes = f"session error: {e}"
        else:
            mes = f"no search result: {e}"
        logging.warning(mes)
        return "no search result", "no search result", 0

    # get product links
    elems = driver.find_elements(
        By.CSS_SELECTOR, "a[href][class='goods-img-url'][title]"
    )
    links = [elem.get_attribute("href") for elem in elems]

    # if no links found, try to get links from another class
    if len(links) == 0:
        elems = driver.find_elements(
            By.CSS_SELECTOR, "a[class='goodsUrl'][href]"
        )
        links = [elem.get_attribute("href") for elem in elems]

    # get product prices
    prices = driver.find_elements(By.CLASS_NAME, "price")

    # Ensure we have matching counts for safe iteration
    min_count = min(len(product_Name_List), len(links), len(prices))
    if min_count == 0:
        return "no search result", "no search result", 0
    
    # Create a DataFrame with product information
    products_data = []
    for i in range(min_count):
        product_name = product_Name_List[i].text
        
        # Skip if we don't have a corresponding link
        if i >= len(links):
            continue
            
        product_link = links[i]
        
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
        momo_Product_Name = row['name']
        product_link = row['link']
        price = row['price']
        
        # If client is available, use AI comparison
        if client is not None:
            is_the_same_product = same_product_or_not(
                prd1=aitem_name, prd2=momo_Product_Name, client=client
            )
            
            # If this is the same product, return it immediately (it has the lowest price)
            if is_the_same_product == 1:
                return momo_Product_Name, product_link, price
    
    # If no matching product found
    return "no corresponding item", "no corresponding item", 0



### ------------------------------------ ###

### ------- Testing the function ------- ###

### ------------------------------------ ###

"""
cd /Users/bryant_lue/Documents/GitHub/Shopee_Crawler_Website/website
python3 -m src.search_momo 
"""

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
            driver = webdriver.Chrome(options=options)

        # Windows and Linux → autoinstaller (automatically downloads correct version)
        elif system in ["Windows", "Linux"]:
            if system == "Linux":
                options.binary_location = "/usr/bin/google-chrome"
            driver_path = chromedriver_autoinstaller.install()
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(options=options, service=service)

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
    print(f"Momo result: Name={name}, Link={link}, Price={price}")
    driver.quit()
