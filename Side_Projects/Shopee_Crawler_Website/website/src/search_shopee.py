"""
Search for a product on Shopee and return its details.
"""


import logging
import re
import pandas as pd
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from .same_prouct_or_not import same_product_or_not

MAX_TIMEOUT_SECONDS = 120

# Configuration for login credentials
# For security, you should set these as environment variables
SHOPEE_USERNAME = os.getenv('SHOPEE_USERNAME', 'b10704026@g.ntu.edu.tw')
SHOPEE_PASSWORD = os.getenv('SHOPEE_PASSWORD', 'Bry31533561')

def human_like_type(element, text, min_delay=0.05, max_delay=0.2):
    """
    Type text character by character with random delays to simulate human typing.
    
    Args:
        element: WebElement to type into
        text: Text to type
        min_delay: Minimum delay between characters (seconds)
        max_delay: Maximum delay between characters (seconds)
    """
    element.clear()
    time.sleep(random.uniform(0.2, 0.5))  # Initial delay after clearing
    
    for char in text:
        element.send_keys(char)
        # Random delay between characters
        time.sleep(random.uniform(min_delay, max_delay))
    
    # Small delay after typing is complete
    time.sleep(random.uniform(0.3, 0.8))

def login_to_shopee(driver, username=None, password=None):
    """
    Login to Shopee with provided credentials.
    
    Args:
        driver: WebDriver instance
        username: Shopee username/email (optional, will use env var if not provided)
        password: Shopee password (optional, will use env var if not provided)
        
    Returns:
        bool: True if login successful, False otherwise
    """
    if not username:
        username = SHOPEE_USERNAME
    if not password:
        password = SHOPEE_PASSWORD

    logging.info(f"Logging in with username: {username}")

    if not username or not password:
        logging.error("Username or password not provided")
        return False
    
    try:
        logging.info("Attempting to login to Shopee...")
        
        # Wait for login elements
        wait = WebDriverWait(driver, timeout=30)
        
        # Find username/email input field
        try:
            username_input = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[class='X0Jdtz'][name='loginKey']")))
            username_input = username_input[0] if isinstance(username_input, list) else username_input
            print(f"username_input: {username_input}")
        except:
            logging.error("Could not find username input field")
            return False
            
        # Find password input field
        try:
            password_input = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[class='X0Jdtz'][placeholder='密碼'][name='password']"))
            )
            password_input = password_input[0] if isinstance(password_input, list) else password_input
            print(f"password_input: {password_input}")
        except:
            logging.error("Could not find password input field")
            return False

        # Clear and enter credentials with human-like delays
        logging.info("Entering username...")
        human_like_type(username_input, username, min_delay=0.1, max_delay=0.3)
        
        # Additional delay between username and password
        time.sleep(random.uniform(1.0, 2.0))
        
        logging.info("Entering password...")
        human_like_type(password_input, password, min_delay=0.08, max_delay=0.25)
        
        # Delay before clicking login button
        time.sleep(random.uniform(0.5, 1.5))
        
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[class='b5aVaf PVSuiZ Gqupku qz7ctP qxS7lQ Q4KP5g']")
            print(f"login_button: {login_button}")
        except:
            logging.error("Could not find login button")
            return False
            
        if login_button.is_displayed() and login_button.is_enabled():
            logging.info("Clicking login button...")
            # Small delay before clicking
            time.sleep(random.uniform(0.3, 0.8))
            login_button.click()
        else:
            logging.error("Login button is not clickable")
            return False

        # Wait for login to complete - check if we're redirected or login form disappears
        logging.info("Waiting for login to complete...")
        time.sleep(random.uniform(3.0, 5.0))  # Random delay for login processing
        
        # Check if login was successful by looking for elements that appear after login
        try:
            # Wait for the search bar to appear (indicates successful login)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[class='shopee-searchbar-input__input']"))
            )
            logging.info("Login successful!")
            return True
        except:
            # Check if we're still on login page
            login_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            if login_elements:
                logging.error("Login failed - still on login page")
                return False
            else:
                # Assume login was successful if password field is gone
                logging.info("Login appears to be successful!")
                return True
                
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return False

def search(aitem_name, driver, client, username=None, password=None):
    """
    Search for the item on Shopee homepage and return the corresponding information.

    Search for "one" item only. The iteration is done in the main function.

    Args:
        aitem_name: The name of the item to search for
        driver: WebDriver instance for web scraping
        client: OpenAI client for product comparison
        username: Shopee username (optional)
        password: Shopee password (optional)

    Returns:
        Tuple of (shopee_product_name, shopee_product_link, shopee_product_price) or error messages
    """

    # Initialize WebDriverWait at the beginning of the function
    wait = WebDriverWait(driver, timeout=MAX_TIMEOUT_SECONDS)

    try:
        driver.get("https://shopee.tw/")
        time.sleep(3)  # Wait for the page to load
        print("Opened Shopee homepage successfully")
    except Exception as e:
        mes = f"getlink|Error opening Shopee website: {e}"
        logging.error(mes)
        return f"{mes}", f"{mes}", 0
    
    # Check if we need to login
    login_required = False
    try:
        # Check if login form is present
        print("Checking if login is required...")
        driver.find_element(By.CSS_SELECTOR, "input[class='X0Jdtz'][name='loginKey']")
        login_required = True
        logging.info("Login required detected")
    except:
        logging.info("No login required")
    
    if login_required:
        login_success = login_to_shopee(driver, username, password)
        if not login_success:
            return "Login failed", "Login failed", 0
    
    time.sleep(15)  # Wait for any potential redirects after login
    
    # Handle popup if it exists (after login)
    try:
        popup_close_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.shopee-popup__close-btn"))
        )
        popup_close_btn.click()
        logging.info("Popup closed successfully")
        # Wait a bit after closing popup
        time.sleep(2)
    except Exception as ex:
        # No popup appeared or popup already closed, continue
        logging.info(f"No popup detected or popup already closed: {ex}")

    # Wait for search elements to be available and interact with them
    try:
        # Wait for search input to be clickable
        item_search_input = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[class='shopee-searchbar-input__input']"))
        )
        
        # Wait for search button to be clickable
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='btn btn-solid-primary btn--s btn--inline shopee-searchbar__search-button']"))
        )
        
        # Send search query and click search button
        item_search_input.send_keys(aitem_name)
        search_button.click()
        
    except Exception as e:
        mes = f"getlink|Error finding search elements: {e}"
        logging.error(mes)
        return f"{mes}", f"{mes}", 0

    # get product name using explicit wait
    try:
        product_Name_List = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.line-clamp-2.break-words.min-w-0.min-h-[2.5rem].text-sm"))
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
        By.CSS_SELECTOR, "a[href][class='contents']"
    )
    links = [elem.get_attribute("href") for elem in elems]

    # get product prices
    prices = driver.find_elements(By.CSS_SELECTOR, "span[class='font-medium text-base/5 truncate']")

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

    print(f"df: {df}")
    
    # # Sort by price in ascending order (lowest price first)
    # df_sorted = df.sort_values('price', ascending=True).reset_index(drop=True)
    
    # # Iterate through sorted products and find the first matching one
    # for _, row in df_sorted.iterrows():
    #     momo_Product_Name = row['name']
    #     product_link = row['link']
    #     price = row['price']
        
    #     # If client is available, use AI comparison
    #     if client is not None:
    #         is_the_same_product = same_product_or_not(
    #             prd1=aitem_name, prd2=momo_Product_Name, client=client
    #         )
            
    #         # If this is the same product, return it immediately (it has the lowest price)
    #         if is_the_same_product == 1:
    #             return momo_Product_Name, product_link, price
    
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
        # Keep the browser open and visible for testing
        # options.add_argument("--headless=new")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--incognito")
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('blink-settings=imagesEnabled=false') 
        # options.add_argument("--disable-extensions")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument("--disable-notifications")
        # options.add_argument("--disable-application-cache")
        # options.add_argument("--disable-translate")
        # options.add_argument("--disable-background-networking")
        # options.add_argument("--disable-client-side-phishing-detection")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
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
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    driver = initialize_webdriver()
    client = None  # Replace with actual OpenAI client initialization if needed
    item_name = "Apple iPhone 16 256GB 6.1吋"
    
    # Try to get credentials from config file or environment variables
    username = None
    password = None
    
    try:
        # Fallback to environment variables
        username = os.getenv('SHOPEE_USERNAME')
        password = os.getenv('SHOPEE_PASSWORD')
    except:
        logging.warning("No credentials found. Please:")
        logging.warning("Set SHOPEE_USERNAME and SHOPEE_PASSWORD environment variables")
    
    # from openai import OpenAI
    # OPEN_API_KEY = (
    #     "sk-proj-jb1EUVA0fiEayF_84ImFYstsuxtMC1qGFSdo4AHOfUkmtAiCJiCyuNmCnn63c3kRjD"
    #     "rylt2UOzT3BlbkFJhE1_44XPbFqBra_STstH2RzA1qjBkYDLeD3xemUSvUQtfCO3UtADpS"
    #     "KRZgdZxUju3ddSJOlTEA"
    # )
    # client = OpenAI(api_key=OPEN_API_KEY)
    
    try:
        print(f"Starting search for: {item_name}")
        result = search(item_name, driver, client, username, password)
        print(f"Search result: {result}")
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing driver: {e}")
