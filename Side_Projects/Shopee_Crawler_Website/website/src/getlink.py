"""
Module for crawling Momo shopping website to find corresponding product links.

This module provides functionality to search for products on Momo website
based on item names from uploaded files, using Selenium WebDriver and OpenAI API.
"""

import os
import re
import pandas as pd
import time
import logging
import chromedriver_autoinstaller
from concurrent.futures import ProcessPoolExecutor, as_completed
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoAlertPresentException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from .same_prouct_or_not import same_product_or_not
from .search_coupang import search as coupang_search
from .search_momo import search as momo_search
from ..db import get_db

# Constants
OPEN_API_KEY = os.environ.get('OPEN_API_KEY', None)
MAX_TIMEOUT_SECONDS = 120
MAX_WORKERS = os.cpu_count() - 2  # Adjust based on your CPU cores


def init_log_info(logger: logging.Logger, total_crawl_num, filename: str):
    """Initialize logging information for the crawling process."""
    logger.warning(
        f"{filename}｜Expected Total Crawl Num = {total_crawl_num}"
    )


def setup_logging(time_stamp) -> logging.Logger:
    """
    Set up logging configuration and return a logger instance.
    """
    import pytz
    from datetime import datetime
    
    # 設定 UTC+8 時區
    taipei_tz = pytz.timezone('Asia/Taipei')
    
    # 自定義 Formatter 類別，使用 GMT+8 時區
    class GMT8Formatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=taipei_tz)
            if datefmt:
                s = dt.strftime(datefmt)
            else:
                s = dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]  # 保留毫秒但只取前3位
            return s
    
    # 設定基本配置
    logging.basicConfig(
        filename=f"logs/getlink_{time_stamp}.log",
        encoding="utf-8",
        level=logging.WARNING,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 獲取 logger 並設定自定義 formatter
    logger = logging.getLogger(__name__)
    
    # 為所有 handlers 設定 GMT+8 formatter
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'baseFilename') and 'getlink' in handler.baseFilename:
            handler.setFormatter(GMT8Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
    
    return logger


def performance_logging(
    logger: logging.Logger, start_time: time, filename: str
) -> None:
    """Log performance information for the crawling process."""
    # Use GMT+8 timezone for consistent time display
    import pytz
    taipei_tz = pytz.timezone('Asia/Taipei')
    elapsed_seconds = time.time() - start_time
    time_dis = time.strftime(
        "%H:%M:%S", time.gmtime(elapsed_seconds)
    )
    logger.warning(f"{filename}｜total spend {time_dis}")


def initialize_webdriver() -> webdriver.Chrome:
    """
    Initialize and return a Chrome WebDriver with specified options.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    import platform
    import os

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-client-side-phishing-detection")
    options.page_load_strategy = "eager"

    system = platform.system()
    arch = platform.machine()

    # Ensure Selenium Manager is used (do not fall back to any PATH chromedriver)
    try:
        os.environ.pop("webdriver.chrome.driver", None)
        orig_path = os.environ.get("PATH", "")
        safe_path_parts = [p for p in orig_path.split(os.pathsep) if "chromedriver" not in p and "chromedriver_autoinstaller" not in p]
        os.environ["PATH"] = os.pathsep.join(safe_path_parts)
    except Exception:
        pass

    # Mac M1 → Chromium + chromedriver_py
    if system == "Darwin" and arch == "arm64":
        from chromedriver_py import binary_path

        svc = webdriver.ChromeService(executable_path=binary_path)
        driver = webdriver.Chrome(options=options, service=svc)

    # Windows → autoinstaller (use returned path explicitly to avoid PATH conflicts)
    elif system == "Windows":
        driver_path = chromedriver_autoinstaller.install()
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(options=options, service=service)

    # Linux (e.g., WSL) → Already downloaded chromedriver in Dockerfile
    elif system == "Linux":
        driver_path = "/usr/local/bin/chromedriver"
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(options=options, service=service)
        # If running in a minimal container, you may also need:
        # options.binary_location = "/usr/bin/google-chrome"

    else:
        raise EnvironmentError(f"Unsupported platform: {system}-{arch}")

    driver.set_page_load_timeout(MAX_TIMEOUT_SECONDS)
    return driver


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


def handle_server_timeout(
    df: pd.DataFrame, i: int, driver, aitem_name: str, client, platform: str = "momo", count=0
) -> None:
    """
    Handle server timeout by retrying the search operation.

    Args:
        df: DataFrame to update with results
        i: Row index
        driver: WebDriver instance
        aitem_name: Item name to search for
        client: OpenAI client
        platform: Platform to search on ('momo' or 'coupang')
        count: Current retry count
    """
    count += 1
    try:
        if platform == 'momo':
            prd_name, link, price = momo_search(aitem_name, driver, client)
            df.loc[i, "Momo Item Name"] = prd_name
            df.loc[i, "Momo Link"] = link
            df.loc[i, "Momo Price"] = price
        elif platform == 'coupang':
            prd_name, link, price = coupang_search(aitem_name, driver, client)
            df.loc[i, "Coupang Item Name"] = prd_name
            df.loc[i, "Coupang Link"] = link
            df.loc[i, "Coupang Price"] = price
        else:
            logging.error(f"Unsupported platform: {platform}")
            return
    except Exception as e:
        mes = f"getlink|servertimeout on {platform}: {e}"
        logging.error(mes)
        logging.error("handling server_timeout again")
        driver.quit()
        time.sleep(3)
        driver = initialize_webdriver()
        if count > 3:
            mes = (
                f"getlink|server timeout for {platform} for more than 3 times, "
                "let's give up this item and move on"
            )
            logging.error(mes)
            return
        else:
            handle_server_timeout(df, i, driver, aitem_name, client, platform, count)
    return


def process_row(
    index,
    item_name,
    pattern,
    platforms,
    max_retry=3,
):
    """
    Process a single row by cleaning the item name and searching for it.

    Args:
        index: Row index
        item_name: Original item name
        pattern: Regex pattern for cleaning
        platforms: Comma-separated string of platforms to search
        max_retry: Maximum retry attempts

    Returns:
        Tuple of (index, results) where results is dict of {platform: (name, link, price)}
    """
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=OPEN_API_KEY)
    except Exception as e:
        mes = f"getlink|Error initializing OpenAI client: {e}"
        logging.error(mes)
        return index, {platform: (mes, mes, 0) for platform in platforms.split(',')}

    # clean the item name
    try:
        aitem_name = re.sub(pattern, "", item_name)
        aitem_name = re.sub(r"[【】\s+]", " ", aitem_name).strip()
        from website.src.clean_prd_name import clean_prd_name

        aitem_name = clean_prd_name(aitem_name, client)
    except Exception as e:
        mes = f"failed to clean item name {e}"
        return index, {platform: (mes, mes, 0) for platform in platforms.split(',')}

    results = {}
    selected_platforms = [p.strip() for p in platforms.split(',')]
    
    # Search for the item on each platform
    for platform in selected_platforms:
        for attempt in range(max_retry):
            driver = None
            try:
                driver = initialize_webdriver()
                if platform == 'momo':
                    prd_name, link, price = momo_search(aitem_name, driver, client)
                elif platform == 'coupang':
                    prd_name, link, price = coupang_search(aitem_name, driver, client)
                else:
                    prd_name, link, price = f"Unknown platform: {platform}", "", 0
                
                results[platform] = (prd_name, link, price)
                if driver:
                    driver.quit()
                break  # Success, break retry loop
            except Exception as e:
                logging.error(f"[Row {index}] Error on {platform}: {e}")
                try:
                    if driver:
                        driver.quit()
                except Exception as quit_error:
                    logging.error(f"[Row {index}] Error quitting driver: {quit_error}")
                time.sleep(2)  # Wait before retrying
                
                if attempt == max_retry - 1:  # Last attempt failed
                    results[platform] = (f"Error after {max_retry} attempts", "", 0)

    return index, results


def main(uploadFilename, time_stamp, platforms) -> None:
    """
    Main function to process uploaded file and crawl product information.

    Args:
        uploadFilename: Name of the uploaded file
        time_stamp: Timestamp for file identification
        platforms: Comma-separated string of platforms to search (e.g., "momo,coupang")
    """
    logger = setup_logging(time_stamp)
    UPLOAD_FILE_PATH = f"data/uploads/{time_stamp}_{uploadFilename}"
    OUTPUT_FILE_PATH = f"data/outputs/links_{time_stamp}_{uploadFilename}"
    start_time = time.time()

    # init and database
    db = get_db()

    # read the uploaded file
    fileType = uploadFilename.split(".")[-1].lower()
    try:
        # read excel file
        if fileType == "xlsx":
            df = pd.read_excel(UPLOAD_FILE_PATH)
        # read csv file
        elif fileType == "csv":
            df = pd.read_csv(UPLOAD_FILE_PATH, encoding="utf-8")
        else:
            db.execute(
                "UPDATE files SET status = ?, progress = ? WHERE stamp = ?",
                ("err[unsupport file type]", "err", time_stamp),
            )
            db.commit()
    except Exception as e:
        mes = f"getlink|Error reading the uploaded file: {e}"
        logging.error(mes)
        raise Exception(mes)

    # try to get item names and total_crawl_num
    try:
        item_names = df.iloc[:, 0]
        total_crawl_num = len(item_names)
    except Exception as e:
        mes = f"getlink|Error getting item names from the uploaded file: {e}"
        logging.error(mes)
        raise Exception(mes)

    # remove unwanted text from item names
    text_to_removed = [
        "現貨",
        "廠商直送",
        "蝦皮直送",
        "大型配送",
        "含運無安裝",
        "含基本安裝",
        "舊機回收",
        "送原廠禮",
        "免運費",
        "官方旗艦店",
        "第一視角飛行體驗",
        "陳列機限地區",
        "含基本安裝",
        "基本安裝",
        "七天鑑賞期",
        "買一送一",
        "保固延長",
        "支援線上客服",
        "限量供應",
        "含安裝服務",
        "30天退貨保障",
        "VIP專屬服務",
        "提供租賃方案",
        "低碳配送",
        "保護包裝",
        "同日到貨",
        "環保包裝",
        "品牌直營",
        "免服務費",
        "多件折扣",
        "到府維修",
        "分期零利率",
        "專屬會員折扣",
        "全新機保證",
        "虛擬實境體驗",
        "新機上市",
        "預購優惠",
        "免運",
    ]
    pattern = "|".join(map(re.escape, text_to_removed))

    # init logger info
    init_log_info(logger, total_crawl_num, uploadFilename)
    
    # Parse platforms string
    selected_platforms = [p.strip() for p in platforms.split(',')]
    logger.warning(f"Selected platforms: {selected_platforms}")

    # start crawling with ProcessPoolExecutor
    completed = 0
    with ProcessPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:  # Adjust this to match your CPU core count
        futures = [
            executor.submit(process_row, i, item_names[i], pattern, platforms)
            for i in range(total_crawl_num)
        ]
        for f in as_completed(futures):
            index, results_dict = f.result()
            
            # Handle results for each platform
            for platform in selected_platforms:
                if platform in results_dict:
                    name, link, price = results_dict[platform]
                    if name and link and name != "" and link != "":
                        df.loc[index, f"{platform.title()} Item Name"] = name
                        df.loc[index, f"{platform.title()} Link"] = link
                        df.loc[index, f"{platform.title()} Price"] = price

            completed += 1
            percentage = "%.1f" % ((completed / total_crawl_num) * 100)
            db.execute(
                "UPDATE files SET percentage = ?, progress = ? WHERE stamp = ?",
                (
                    percentage,
                    f"{percentage}% ({completed}/{total_crawl_num})",
                    time_stamp,
                ),
            )
            db.commit()

            # update and output progress at the first item or every 10 items
            if (completed == 1) or (completed % 10 == 0):
                # update time spent in database
                elapsed_seconds = int(time.time() - start_time)
                hours, remainder = divmod(elapsed_seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if hours > 0:
                    time_spent_str = f"{hours}hr {minutes}min"
                else:
                    time_spent_str = f"{minutes}min"

                db.execute(
                    "UPDATE files SET timeSpent = ? WHERE stamp = ?",
                    (time_spent_str, time_stamp),
                )

                if fileType == "xlsx":
                    df.to_excel(OUTPUT_FILE_PATH, index=False)
                elif fileType == "csv":
                    df.to_csv(OUTPUT_FILE_PATH, index=False, encoding="utf-8")

    # Ensure all items are processed before final export
    # Check if any platform columns have null values
    selected_platforms = [p.strip() for p in platforms.split(',')]
    count = 0
    all_completed = False
    
    while not all_completed and count < 30:
        all_completed = True
        for platform in selected_platforms:
            platform_name_col = f"{platform.title()} Item Name"
            if platform_name_col in df.columns and df[platform_name_col].isnull().sum() != 0:
                all_completed = False
                break
        
        if not all_completed:
            count += 1
            time.sleep(1)
        else:
            break
    
    if count >= 30:
        logger.error("Some items failed to complete processing")

    # export file
    if fileType == "xlsx":
        df.to_excel(OUTPUT_FILE_PATH, index=False)
    elif fileType == "csv":
        df.to_csv(OUTPUT_FILE_PATH, index=False, encoding="utf-8")
    logger.warning(
        f"{uploadFilename}｜Crawling completed, total time: "
        f"{time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}"
    )

    # evaluate the results
    from .evaluation import evaluate_crawl_results
    try:
        evaluate_crawl_results(OUTPUT_FILE_PATH, fileType, total_crawl_num)
    except Exception as e:
        logger.error(f"Error evaluating crawl results: {e}")
        raise Exception(f"getlink|Error evaluating crawl results: {e}")

    return

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
    name, link, price = momo_search(item_name, driver, client)
    print(f"Momo: {name}, {link}, {price}")
    name, link, price = coupang_search(item_name, driver, client)
    print(f"Coupang: {name}, {link}, {price}")
    driver.quit()
