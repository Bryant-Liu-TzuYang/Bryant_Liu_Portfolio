"""
Module for evaluating the results of web scraping operations.

This module provides functionality to analyze and evaluate the success rate
of web scraping results from Momo and Coupang website crawling operations.
"""

import os
import pandas as pd

# Constants
MOMO_URL_PREFIX = "https://www.momoshop.com.tw/goods/"
COUPANG_URL_PREFIX = "https://www.tw.coupang.com/products/"
ERROR_PREFIX = "getlink|"
NO_SEARCH_RESULT = "no search result"
NO_CORRESPONDING_ITEM = "no corresponding item"
EVAL_FILE_PATH = "data/eval.csv"


def evaluate_platform(dataframe, platform_name, url_prefix, total_crawl_num):
    """
    Evaluate the performance for a specific platform (Momo or Coupang).
    
    Args:
        dataframe (pd.DataFrame): The data to evaluate
        platform_name (str): Name of the platform ('Momo' or 'Coupang')
        url_prefix (str): URL prefix to identify valid links
        total_crawl_num (int): Total number of crawl attempts
        
    Returns:
        dict: Dictionary containing evaluation metrics for the platform
    """
    # Handle different possible column name formats
    item_name_variations = [
        f"{platform_name} item name",      # "Momo item name"
        f"{platform_name} Item Name",      # "Coupang Item Name"
        f"{platform_name}_item_name",      # Alternative format
        f"{platform_name}_Item_Name"       # Alternative format
    ]
    
    link_variations = [
        f"{platform_name} link",           # "Momo link"
        f"{platform_name} Link",           # "Coupang Link"
        f"{platform_name}_link",           # Alternative format
        f"{platform_name}_Link"            # Alternative format
    ]
    
    # Find the actual column names
    item_name_col = None
    link_col = None
    
    for variation in item_name_variations:
        if variation in dataframe.columns:
            item_name_col = variation
            break
    
    for variation in link_variations:
        if variation in dataframe.columns:
            link_col = variation
            break
    
    # Check if the platform columns exist in the dataframe
    if item_name_col is None or link_col is None:
        return {
            f"{platform_name} Valid Items Rate (%)": "N/A",
            f"{platform_name} No Search Result Rate (%)": "N/A", 
            f"{platform_name} No Corresponding Item Rate (%)": "N/A",
            f"{platform_name} Error Rate (%)": "N/A",
            f"{platform_name} NA Rate (%)": "N/A",
            f"{platform_name} Valid Items": "N/A",
            f"{platform_name} No Search Result": "N/A",
            f"{platform_name} No Corresponding Item": "N/A",
            f"{platform_name} Error Count": "N/A",
            f"{platform_name} NA Count": "N/A",
        }
    
    # Count different types of results
    no_search_result_count = (
        dataframe[item_name_col].value_counts().get(NO_SEARCH_RESULT, 0)
    )
    no_corresponding_item_count = (
        dataframe[item_name_col].value_counts().get(NO_CORRESPONDING_ITEM, 0)
    )
    valid_items_count = (
        dataframe[link_col]
        .str.startswith(url_prefix, na=False)
        .sum()
    )
    error_count = (
        dataframe[item_name_col].str.startswith(ERROR_PREFIX, na=False).sum()
    )
    na_count = dataframe[item_name_col].isna().sum()
    
    # Calculate rates
    no_search_result_rate = (
        no_search_result_count / total_crawl_num * 100 if total_crawl_num > 0 else 0
    )
    no_corresponding_item_rate = (
        no_corresponding_item_count / total_crawl_num * 100 if total_crawl_num > 0 else 0
    )
    valid_items_rate = (
        valid_items_count / total_crawl_num * 100 if total_crawl_num > 0 else 0
    )
    error_rate = (
        error_count / total_crawl_num * 100 if total_crawl_num > 0 else 0
    )
    na_rate = (
        na_count / total_crawl_num * 100 if total_crawl_num > 0 else 0
    )
    
    return {
        f"{platform_name} Valid Items Rate (%)": f"{valid_items_rate:.2f}%",
        f"{platform_name} No Search Result Rate (%)": f"{no_search_result_rate:.2f}%",
        f"{platform_name} No Corresponding Item Rate (%)": f"{no_corresponding_item_rate:.2f}%",
        f"{platform_name} Error Rate (%)": f"{error_rate:.2f}%",
        f"{platform_name} NA Rate (%)": f"{na_rate:.2f}%",
        f"{platform_name} Valid Items": valid_items_count,
        f"{platform_name} No Search Result": no_search_result_count,
        f"{platform_name} No Corresponding Item": no_corresponding_item_count,
        f"{platform_name} Error Count": error_count,
        f"{platform_name} NA Count": na_count,
    }


def evaluate_crawl_results(filepath, file_type, total_crawl_num=0):
    """
    Evaluate the results of a web crawling operation for both Momo and Coupang platforms.

    Args:
        filepath (str): Path to the file containing crawl results
        file_type (str): Type of file ('xlsx' or 'csv')
        total_crawl_num (int): Total number of crawl attempts (optional)

    Returns:
        None: Results are saved to evaluation CSV file

    Raises:
        ValueError: If file_type is not supported
        FileNotFoundError: If filepath does not exist
    """
    # Validate file type
    if file_type not in ["xlsx", "csv"]:
        raise ValueError(f"Unsupported file type: {file_type}")

    # Read file
    try:
        if file_type == "xlsx":
            # Try different methods to read the Excel file
            try:
                dataframe = pd.read_excel(filepath, engine='openpyxl')
            except Exception:
                try:
                    dataframe = pd.read_excel(filepath, engine='xlrd')
                except Exception:
                    # If it fails, try reading as CSV (some .xlsx files are actually CSV)
                    dataframe = pd.read_csv(filepath, encoding="utf-8")
        elif file_type == "csv":
            dataframe = pd.read_csv(filepath, encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {filepath}") from exc
    
    file_stamp = os.path.basename(filepath).split('.')[0]  # Extract file name without extension
    print(f"Evaluating crawl results for file: {file_stamp}")
    
    # If total_crawl_num is not provided, use the length of the DataFrame
    total_crawl_num = len(dataframe) if total_crawl_num == 0 else total_crawl_num

    # Evaluate Momo performance
    momo_results = evaluate_platform(dataframe, "Momo", MOMO_URL_PREFIX, total_crawl_num)
    
    # Evaluate Coupang performance
    coupang_results = evaluate_platform(dataframe, "Coupang", COUPANG_URL_PREFIX, total_crawl_num)

    # Combine results for the evaluation DataFrame
    evaluation_data = {
        "File_Stamp": file_stamp,
        "Total Crawl Number": total_crawl_num,
    }
    
    # Add Momo results
    evaluation_data.update(momo_results)
    
    # Add Coupang results  
    evaluation_data.update(coupang_results)

    # Export the evaluation results to a new DataFrame
    evaluation_dataframe = pd.DataFrame([evaluation_data])

    # Save the evaluation results to existing csv file, create new one if not exists
    # Ensure the directory exists
    os.makedirs("data", exist_ok=True)
    if (os.path.exists(EVAL_FILE_PATH)):
        evaluation_dataframe.to_csv(EVAL_FILE_PATH, mode="a", header=False, index=False)
    else:
        evaluation_dataframe.to_csv(EVAL_FILE_PATH, mode="w", header=True, index=False)
