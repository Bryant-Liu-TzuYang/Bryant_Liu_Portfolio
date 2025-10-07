# Shopee Link Crawler Website

A powerful web-based tool for crawling and extracting product links from Momo / Coupang. This application allows users to upload CSV/Excel files containing product information and automatically crawls Momo / Coupang to find relevant product links.

## Table of Contents

- [Shopee Link Crawler Website](#shopee-link-crawler-website)
  - [Table of Contents](#table-of-contents)
  - [Quick Start](#quick-start)
    - [Using Docker (Recommended)](#using-docker-recommended)
    - [Manual Installation](#manual-installation)
  - [Recent Updates](#recent-updates)
    - [Trending Products Dashboard (Latest)](#trending-products-dashboard-latest)
    - [File Structure Migration](#file-structure-migration)
  - [Usage](#usage)
    - [Platform Selection Guide](#platform-selection-guide)
  - [License](#license)
  - [Author](#author)
  - [Changelog](#changelog)

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Shopee_Crawler_Website
   ```

2. **Configure OpenAI API Key**
   - Open `website/src/getlink.py`
   - Replace the OpenAI API key with your own key

3. **Start the application**
   ```bash
   docker compose build --no-cache
   docker-compose up -d
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost`

### Manual Installation

1. **Prerequisites**
   - Python 3.10+
   - Google Chrome browser
   - ChromeDriver

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

4. **Run the application**
   ```bash
   python wsgi.py
   ```




## Recent Updates

### Trending Products Dashboard (Latest)
- **New Feature**: Added comprehensive trending products analysis page for Coupang data
- **Interactive Interface**: Category selection, date filtering, and real-time data loading
- **Download Functionality**: Single category CSV and bulk ZIP download options
- **File Timestamps**: Display when trending data files were created
- **Navigation Integration**: Added to main navigation menu across all pages

### File Structure Migration
- **Data Organization**: All data files have been reorganized under the `data/` directory for better structure
- **Path Updates**: Upload files are now stored in `data/uploads/`, results in `data/outputs/`, trending data in `data/ranking/`, etc.
- **Backward Compatibility**: Existing functionality remains unchanged, only internal path references have been updated

## Usage

1. **Prepare your data file**
   - Create a CSV or Excel file with product information
   - Include columns for product names, descriptions, or other identifying information

2. **Select platforms**
   - Choose which e-commerce platforms to search:
     - **Momo**: Taiwan's largest e-commerce platform
     - **Coupang**: Leading Korean e-commerce platform
   - You can select one or both platforms for comprehensive coverage

3. **Upload and process**
   - Navigate to the web interface
   - Select your desired platforms using the checkboxes
   - Click "Upload" and select your file
   - The system will automatically start crawling the selected platforms for matching products

4. **Monitor progress**
   - Watch real-time progress updates on the dashboard
   - View detailed logs and status information
   - See which platforms are being processed

5. **Download results**
   - Once processing is complete, download the results file
   - Results include original data plus discovered links from all selected platforms
   - For multiple platforms, results will include separate columns for each platform's data

### Platform Selection Guide

- **Coupang Only**: Korean market focus, good for cross-border research (default selection)
- **Momo Only**: Fast processing, comprehensive Taiwan market coverage
- **Both Platforms**: Complete market analysis, longer processing time but maximum coverage

The output file will contain columns like:
- `Momo Item Name` and `Momo Link` (if Momo is selected)
- `Coupang Item Name` and `Coupang Link` (if Coupang is selected)


## License

This project is proprietary software. All rights reserved.

## Author

**Bryant Liu**

For questions, issues, or feature requests, please contact the development team.

## Changelog

See Notion Page [Shoppee](https://www.notion.so/Shoppee-4454baa0c2964320ba4177f288cc7113?source=copy_link) for version history and updates.
