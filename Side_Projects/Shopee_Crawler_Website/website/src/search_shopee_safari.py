"""
Search for a product on Shopee and return its details using Safari WebDriver.
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
from selenium.webdriver.safari.service import Service as SafariService
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
            time.sleep(5)
        except:
            logging.error("Could not find login button")
            return False
            
        if login_button.is_displayed() and login_button.is_enabled():
            logging.info("Clicking login button...")
            print("Clicking login button...")
            
            try:
                # Try multiple methods to click the login button
                print("Method 1: Standard click")
                login_button.click()
                time.sleep(2)
                
                # Check if anything happened
                new_url = driver.current_url
                if new_url == driver.current_url:
                    print("Method 2: JavaScript click")
                    driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(2)
                
                # Try form submission as alternative
                if "login" in driver.current_url.lower():
                    print("Method 3: Form submission via Enter key")
                    try:
                        # Find password field and press Enter
                        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
                        password_input.send_keys("\n")
                        time.sleep(2)
                    except:
                        pass
                
                print("Clicked login button")
                
            except Exception as e:
                print(f"Error clicking login button: {e}")
                return False
            
            # Monitor page changes after clicking
            print("Monitoring page changes after login click...")
            for i in range(15):  # Check for 15 seconds
                time.sleep(1)
                current_url = driver.current_url
                
                # Only print URL changes to reduce noise
                if i == 0 or i % 5 == 0:
                    print(f"Second {i+1}: URL = {current_url}")
                
                # Check if we've been redirected away from login
                if "login" not in current_url.lower():
                    print("✅ Redirected away from login page!")
                    break
                    
                # Check for CAPTCHA or verification requirements
                try:
                    # Check for CAPTCHA
                    captcha_elements = driver.find_elements(By.CSS_SELECTOR, 
                        ".shopee-captcha, [class*='captcha'], iframe[src*='captcha'], [id*='captcha']")
                    if captcha_elements and any(elem.is_displayed() for elem in captcha_elements):
                        print("🤖 CAPTCHA detected! Please solve it manually...")
                        input("Press Enter after solving CAPTCHA...")
                        continue
                    
                    # Check for SMS verification
                    sms_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "[placeholder*='驗證碼'], [class*='sms'], [class*='verification'], input[maxlength='6']")
                    if sms_elements and any(elem.is_displayed() for elem in sms_elements):
                        print("📱 SMS verification detected! Please enter code manually...")
                        input("Press Enter after entering SMS code...")
                        continue
                    
                except Exception as e:
                    # Ignore monitoring errors to avoid spam
                    if i % 10 == 0:  # Only log every 10 seconds
                        print(f"Monitoring error: {e}")
                        
        else:
            logging.error("Login button is not clickable")
            print(f"Login button displayed: {login_button.is_displayed()}")
            print(f"Login button enabled: {login_button.is_enabled()}")
            return False

        # Wait for login to complete - check if we're redirected or login form disappears
        logging.info("Waiting for login to complete...")
        time.sleep(3)  # Initial wait for any immediate changes
        
        # Final comprehensive check for login success
        current_url = driver.current_url
        print(f"Final URL check: {current_url}")
        
        # Check if login was successful by multiple methods
        login_success = False
        
        # Method 1: Check if we're no longer on login page by URL
        if "login" not in current_url.lower():
            print("Method 1: No longer on login page (URL check)")
            login_success = True
        
        # Method 2: Look for search bar (main indicator)
        if not login_success:
            try:
                search_elements = driver.find_elements(By.CSS_SELECTOR, 
                    "input[class='shopee-searchbar-input__input'], input[placeholder*='搜尋'], .shopee-searchbar input")
                if search_elements and any(elem.is_displayed() for elem in search_elements):
                    print("Method 2: Search bar found - login successful!")
                    login_success = True
            except:
                pass
        
        # Method 3: Check if password field is gone
        if not login_success:
            try:
                password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
                visible_password_fields = [field for field in password_fields if field.is_displayed()]
                if not visible_password_fields:
                    print("Method 3: Password field gone - login likely successful!")
                    login_success = True
                else:
                    print(f"Still found {len(visible_password_fields)} visible password fields")
            except:
                pass
        
        if login_success:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed - trying manual intervention...")
            # Give user a chance to manually complete login
            try:
                manual_input = input("Login seems to have failed. Complete it manually and type 'done' when finished (or 'skip' to continue): ").strip().lower()
                if manual_input == 'done':
                    print("Manual login completed, continuing...")
                    return True
                elif manual_input == 'skip':
                    print("Skipping login verification...")
                    return True
            except:
                pass
            
            logging.error("Login failed - still on login page")
            # Take a screenshot for debugging
            try:
                screenshot_path = f"login_failure_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except:
                pass
            return False
                
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
            print("⚠️ Login failed, but attempting to continue...")
            # Try to navigate away from login page anyway
            try:
                driver.get("https://shopee.tw/")
                time.sleep(5)
                print("Navigated back to homepage after login failure")
            except:
                pass
        else:
            print("✅ Login successful, navigating to homepage...")
            # After successful login, navigate back to homepage to ensure we're in the right place
            try:
                driver.get("https://shopee.tw/")
                time.sleep(5)
            except:
                pass
    
    # Check current URL and page state
    current_url = driver.current_url
    print(f"Current URL before search: {current_url}")
    
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
    # Try multiple selectors for search input
    search_input_selectors = [
        "input[class='shopee-searchbar-input__input']",
        "input[placeholder*='搜尋']",
        "input[data-testid='search-input']",
        ".shopee-searchbar-input input",
        "input[name='keyword']"
    ]
    
    item_search_input = None
    for selector in search_input_selectors:
        try:
            item_search_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"Found search input with selector: {selector}")
            break
        except:
            continue
    
    if not item_search_input:
        mes = "getlink|Could not find search input field"
        logging.error(mes)
        print("❌ Could not find search input - trying manual intervention...")
        try:
            manual_input = input("Could not find search input. Please navigate to search manually and type 'done' when ready: ").strip().lower()
            if manual_input == 'done':
                # Try again after manual intervention
                for selector in search_input_selectors:
                    try:
                        item_search_input = driver.find_element(By.CSS_SELECTOR, selector)
                        if item_search_input.is_displayed():
                            print(f"Found search input after manual intervention: {selector}")
                            break
                    except:
                        continue
        except:
            pass
            
        if not item_search_input:
            return f"{mes}", f"{mes}", 0
    
    # Try multiple selectors for search button
    search_button_selectors = [
        "button[class='btn btn-solid-primary btn--s btn--inline shopee-searchbar__search-button']",
        "button[data-testid='search-button']",
        ".shopee-searchbar__search-button",
        "button.shopee-searchbar__search-button",
        "button[type='submit']"
    ]
    
    search_button = None
    for selector in search_button_selectors:
        try:
            search_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"Found search button with selector: {selector}")
            break
        except:
            continue
    
    if not search_button:
        print("⚠️ Could not find search button - will try Enter key instead")

    try:
        # Send search query and click search button
        print(f"Searching for: {aitem_name}")
        item_search_input.clear()
        item_search_input.send_keys(aitem_name)
        time.sleep(1)  # Small delay before clicking search
        
        if search_button:
            search_button.click()
            print("Search button clicked successfully")
        else:
            # Try pressing Enter as fallback
            item_search_input.send_keys("\n")
            print("Pressed Enter to search (no button found)")
        
        # Wait for search results page to load
        time.sleep(5)
        current_url = driver.current_url
        print(f"Current URL after search: {current_url}")
        
    except Exception as e:
        mes = f"getlink|Error performing search: {e}"
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
    def initialize_webdriver() -> webdriver.Safari:
        """
        Initialize and return a Safari WebDriver with specified options.
        
        Note: Safari WebDriver requires the following setup:
        1. Enable "Develop" menu in Safari Preferences
        2. Enable "Allow Remote Automation" in Safari's Develop menu
        3. Run: sudo safaridriver --enable in terminal (one-time setup)
        """
        from selenium import webdriver
        from selenium.webdriver.safari.service import Service as SafariService
        import platform

        # Check if we're on macOS (Safari is only available on macOS)
        system = platform.system()
        if system != "Darwin":
            raise EnvironmentError(f"Safari WebDriver is only available on macOS. Current system: {system}")

        try:
            # Create Safari service
            service = SafariService()
            
            # Create Safari driver with service
            driver = webdriver.Safari(service=service)
            
            # Set page load timeout
            driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
            
            # Set implicit wait
            driver.implicitly_wait(10)
            
            print("Safari WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            print(f"Failed to initialize Safari WebDriver: {e}")
            print("\nTroubleshooting steps:")
            print("1. Enable 'Develop' menu in Safari Preferences > Advanced")
            print("2. Enable 'Allow Remote Automation' in Safari's Develop menu")
            print("3. Run 'sudo safaridriver --enable' in terminal (one-time setup)")
            print("4. Make sure Safari is closed before running this script")
            raise

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
