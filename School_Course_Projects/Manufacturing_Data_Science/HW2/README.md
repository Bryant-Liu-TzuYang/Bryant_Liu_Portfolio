# HW2 - Multimodal Data Mining with Image and Text Features

## Overview
This project focuses on predicting numerical labels using multimodal machine learning techniques that combine image features extracted from deep learning models with text features processed through TF-IDF vectorization. The analysis integrates computer vision and natural language processing approaches for enhanced predictive performance.

## Dataset Description
- **Training Data**: `train_data.json` - JSON file containing feature data including text, categories, and image paths
- **Test Data**: `test_data.json` - JSON file containing test features for prediction
- **Training Labels**: `train_label.csv` - CSV file containing target labels for supervised learning
- **Image Data**: Referenced through `img_filepath` column, processed using deep learning feature extraction

## Project Structure
```
HW2/
├── hw2.ipynb                    # Main analysis notebook with complete pipeline
├── feature_engineering.ipynb   # Dedicated notebook for feature extraction and engineering
├── run_model.ipynb             # Model training and evaluation notebook
└── README.md                   # This documentation file
```

## Analysis Workflow

### 1. Data Loading and Preprocessing
- Loading JSON and CSV data files
- Merging training data with labels based on `Pid` (Post ID)
- Converting timestamp data (`Postdate`) to datetime format
- Exploratory data analysis to understand feature distributions

### 2. Feature Engineering

#### Image Feature Extraction
- **Deep Learning Model**: ResNet-101 pretrained model for feature extraction
- **Image Processing**: 
  - Resize images to 300x300 pixels
  - Normalize pixel values
  - Extract 2048-dimensional feature vectors from the penultimate layer
- **GPU Acceleration**: Supports CUDA, MPS (Apple Silicon), and CPU backends
- **Error Handling**: Robust processing with fallback for corrupted images

#### Text Feature Processing
- **TF-IDF Vectorization**: Applied to combined text from `Title` and `Alltags` fields
- **Feature Dimensionality**: 100 most important TF-IDF features
- **Text Preprocessing**: String concatenation and cleaning

#### Categorical Feature Encoding
- **One-Hot Encoding**: Applied to categorical variables like `Category`, `Concept`, and `Subcategory`
- **Feature Consistency**: Analysis of category distributions between training and test sets

### 3. Model Development

#### XGBoost Implementation
- **Algorithm**: Gradient boosting with absolute error objective
- **Key Parameters**:
  - Max depth: 10
  - Learning rate: 0.01
  - Column sampling: 0.8
  - Early stopping: 100 rounds
- **Training Strategy**: 10,000 boosting rounds with validation monitoring

#### Model Evaluation
- **Primary Metric**: Mean Absolute Error (MAE)
- **Secondary Metrics**: Root Mean Squared Error (RMSE) and R² score
- **Validation Strategy**: Train-test split with 90-10 ratio

### 4. Results
Based on the analysis:
- **Final MAE**: ~1.606 (validation set)
- **Final RMSE**: ~2.124 (validation set) 
- **Training Performance**: Demonstrated convergence with early stopping
- **Feature Importance**: Combination of image features, text features, and categorical encodings

## Key Features

### Multimodal Integration
- **Image Features**: 2048-dimensional ResNet-101 extracted features
- **Text Features**: TF-IDF vectorized title and tag information
- **Categorical Features**: One-hot encoded category, concept, and subcategory data
- **Temporal Features**: Postdate information for time-based patterns

### Technical Implementation
- **Language**: Python
- **Deep Learning**: PyTorch with torchvision for image processing
- **Machine Learning Libraries**:
  - `xgboost` for gradient boosting
  - `scikit-learn` for feature processing and evaluation
  - `pandas`, `numpy` for data manipulation
- **Text Processing**: TF-IDF vectorization with sklearn
- **Image Processing**: ResNet-101 feature extraction with normalization
- **GPU Support**: CUDA and Apple Silicon MPS acceleration

## Files Description
- **`hw2.ipynb`**: Complete end-to-end analysis pipeline including data loading, feature engineering, model training, and evaluation
- **`feature_engineering.ipynb`**: Focused notebook for feature extraction from images and text, including TF-IDF and ResNet processing
- **`run_model.ipynb`**: Model training notebook with XGBoost implementation and hyperparameter optimization

## Usage
1. Ensure all required libraries are installed:
   ```bash
   pip install torch torchvision pandas numpy scikit-learn xgboost tqdm pillow
   ```
2. Set up the data path to point to your dataset directory
3. Run `feature_engineering.ipynb` first to extract and prepare features
4. Use `hw2.ipynb` for the complete analysis pipeline
5. Execute `run_model.ipynb` for focused model training and evaluation

## Technical Highlights
- **Multimodal Learning**: Successfully combines visual and textual information
- **Deep Feature Extraction**: Leverages pretrained ResNet-101 for robust image representations
- **Scalable Processing**: GPU acceleration for efficient image feature extraction
- **Robust Preprocessing**: Handles missing data and corrupted images gracefully
- **Feature Integration**: Concatenates diverse feature types for comprehensive representation

## Results Summary
The project demonstrates effective multimodal machine learning by combining deep learning-based image features with traditional NLP text features. The XGBoost model achieves competitive performance with MAE of approximately 1.606, showcasing the value of integrating multiple data modalities for improved predictive accuracy.

## Author
Name: 劉子揚 (Liu, Tzu-Yang)
