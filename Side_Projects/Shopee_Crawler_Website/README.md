# Shopee Link Crawler Website

A powerful web-based tool for crawling and extracting product links from Momo / Coupang. This application allows users to upload CSV/Excel files containing product information and automatically crawls Momo / Coupang to find relevant product links.

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

## File Structure

```
├── website/                    # Main application package
│   ├── src/                   # Core crawling logic
│   │   ├── getlink.py         # Main crawler implementation
│   │   └── same_product_or_not.py  # AI product matching
│   ├── static/                # Frontend assets
│   ├── templates/             # HTML templates (including trending_coupang.html)
│   │   └── eval.html           # Evaluation dashboard page
│   ├── config.py              # Configuration settings
│   ├── db.py                  # Database operations
│   └── notion_service.py      # Notion integration
├── data/                      # Data storage directory
│   ├── uploads/               # User uploaded files
│   ├── outputs/               # Generated result files
│   ├── ranking/               # Trending product data
│   ├── test_data/             # Test datasets
│   └── eval.csv               # Evaluation results
├── logs/                      # Application logs
├── dev/                       # Development tools and notebooks
├── nginx/                     # Nginx configuration
├── docker-compose.yml         # Docker services configuration
├── Dockerfile                 # Container build instructions
├── requirements.txt           # Python dependencies
└── wsgi.py                   # WSGI entry point
```

## Configuration

### Environment Variables

Create a configuration file based on `website/config.template.py`:

```python
# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key"

# Database Configuration
DATABASE_PATH = "instance/shoppee.sqlite"

# Crawler Settings
MAX_WORKERS = 6  # Adjust based on your CPU cores
MAX_TIMEOUT_SECONDS = 120
```

### Docker Configuration

The application uses Docker Compose with the following services:

- **web**: Flask application with Gunicorn
- **nginx**: Reverse proxy server

Modify `docker-compose.yml` to customize ports and volumes as needed.

## API Integration

### OpenAI Integration
The application uses OpenAI's GPT model for intelligent product matching. Configure your API key in the settings to enable this feature.

### Notion Integration
Built-in Notion service allows for documentation and update management. Configure your Notion API credentials to use this feature.

## Monitoring and Logging

- **Application Logs**: Stored in `logs/` directory with daily rotation
- **Access Logs**: Nginx and Gunicorn access logs
- **Error Tracking**: Sentry integration for production error monitoring
- **Progress Tracking**: Real-time updates stored in SQLite database

## Development

### Local Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up pre-commit hooks** (optional)
   ```bash
   pre-commit install
   ```

3. **Run in development mode**
   ```bash
   export FLASK_ENV=development
   python wsgi.py
   ```

### Adding New Features

1. **Backend Logic**: Add new functionality in `website/src/`
2. **Database Changes**: Update schema in `website/schema.sql`
3. **Frontend**: Modify templates in `website/templates/`
4. **Styling**: Update CSS in `website/static/style.css`

## Deployment

### Production Deployment

1. **Update configuration**
   - Set production API keys
   - Configure Sentry DSN for error tracking
   - Update security settings

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Set up reverse proxy** (if not using included Nginx)
   - Configure SSL certificates
   - Set up domain routing

### Cloud Deployment

The application is designed to work with cloud platforms:

- **Azure**: Containerized deployment support
- **AWS**: ECS or EC2 deployment
- **Google Cloud**: Cloud Run or Compute Engine

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   - Ensure Chrome browser is installed
   - Verify ChromeDriver compatibility
   - Check Docker Chrome installation

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check API quota and billing
   - Monitor rate limits

3. **File Upload Issues**
   - Check file permissions on upload directory
   - Verify file format compatibility
   - Monitor disk space

### Debug Mode

Enable debug logging by setting log level to DEBUG in the configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Author

**Bryant Liu**

For questions, issues, or feature requests, please contact the development team.

## Changelog

See Notion Page [Shoppee](https://www.notion.so/Shoppee-4454baa0c2964320ba4177f288cc7113?source=copy_link) for version history and updates.

---

*This application is designed for educational and research purposes. Please ensure compliance with Shopee's terms of service and robots.txt when using this crawler.*
