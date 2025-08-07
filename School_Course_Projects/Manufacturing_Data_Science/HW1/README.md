# HW1 - House Price Prediction with Taipei Metro Data

## Overview
This project focuses on predicting house prices in Taipei using machine learning models with metro station proximity as a key feature. The analysis includes exploratory data analysis (EDA), data preprocessing, feature engineering, and model comparison.

## Dataset Description
- **Training Data**: `X_train.csv`, `y_train.csv` - Features and target values for model training
- **Test Data**: `X_test.csv`, `y_test.csv` - Features and target values for model evaluation  
- **Metro Data**: `taipei_metros.csv` - Information about Taipei metro stations including coordinates, station names, and line information
- **Additional Test Results**: `y_test_without_tuned.csv` - Test predictions from untuned models

## Project Structure
```
HW1/
├── B10704026_劉子揚.ipynb          # Main analysis notebook
├── test.ipynb                      # Decision tree testing notebook
├── Feature_Importance_XGBoost.png  # XGBoost feature importance visualization
├── taipei_metros.csv               # Taipei metro station data
├── X_train.csv                     # Training features
├── X_test.csv                      # Test features  
├── y_train.csv                     # Training targets (house prices)
├── y_test.csv                      # Test targets (house prices)
├── y_test_without_tuned.csv        # Untuned model predictions
└── catboost_info/                  # CatBoost model training logs
```

## Analysis Workflow

### 1. Exploratory Data Analysis (EDA)
- Data exploration and descriptive statistics
- Analysis of high-price and low-price property characteristics
- Data quality assessment and missing value identification

### 2. Data Preprocessing
- Data cleaning and handling of missing values
- Feature engineering and transformation
- Feature selection using mutual information regression

### 3. Model Development
The project implements and compares multiple machine learning models:

#### Models Used:
- **XGBoost Regressor** - Gradient boosting algorithm optimized for performance
- **CatBoost Regressor** - Gradient boosting with categorical feature handling
- **Random Forest** - Ensemble learning method
- **Other regression models** for comparison

#### Model Evaluation:
- Mean Absolute Error (MAE) as the primary evaluation metric
- Cross-validation for robust performance assessment
- Feature importance analysis

### 4. Results
Based on the analysis:
- **CatBoost**: MAE of 22,764.28
- Comprehensive model comparison across different algorithms
- Feature importance visualization showing key predictors

## Key Features
- **Metro Proximity**: Distance and accessibility to Taipei metro stations
- **Property Characteristics**: Size, age, location, and other housing features
- **Geographic Features**: Coordinates and regional information

## Technical Implementation
- **Language**: Python
- **Key Libraries**: 
  - `pandas`, `numpy` for data manipulation
  - `matplotlib`, `seaborn` for visualization
  - `scikit-learn` for machine learning utilities
  - `xgboost` for XGBoost implementation
  - `catboost` for CatBoost implementation
- **Feature Selection**: Mutual information regression for optimal feature subset
- **Model Training**: Cross-validation and hyperparameter optimization

## Files Description
- **`B10704026_劉子揚.ipynb`**: Main notebook containing the complete analysis pipeline
- **`test.ipynb`**: Supplementary notebook for decision tree exploration
- **`Feature_Importance_XGBoost.png`**: Visualization of feature importance from XGBoost model
- **`catboost_info/`**: Directory containing CatBoost training logs and metrics

## Usage
1. Ensure all required libraries are installed
2. Load the data files in the same directory as the notebooks
3. Run `B10704026_劉子揚.ipynb` for the complete analysis
4. Use `test.ipynb` for additional decision tree experiments

## Results Summary
The project successfully demonstrates the application of multiple machine learning algorithms for house price prediction, with CatBoost showing competitive performance. The analysis provides insights into the most important features affecting house prices in the Taipei area, with metro accessibility being a significant factor.

## Author
Name: 劉子揚 (Liu, Tzu-Yang)
