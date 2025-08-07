# Shopee Crawler Website

A comprehensive web application for crawling and analyzing e-commerce data from Shopee and other platforms, featuring AI-powered analysis and Notion integration.

## 🌟 Features

- **Web Scraping**: Automated data collection from e-commerce platforms
- **Data Analysis**: AI-powered product analysis and insights
- **Notion Integration**: Seamless data management and storage
- **Web Interface**: User-friendly dashboard for data visualization
- **Docker Support**: Containerized deployment for easy setup
- **Background Processing**: Efficient handling of large-scale crawling tasks

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite
- **AI/ML**: OpenAI API for product analysis
- **Deployment**: Docker, Docker Compose
- **Data Processing**: Pandas, NumPy
- **Web Scraping**: Custom crawling modules
- **APIs**: Notion API, OpenAI API
- **Monitoring**: Sentry for error tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bryant-Liu-TzuYang/Bryant_Liu_Portfolio.git
   cd Bryant_Liu_Portfolio/Side_Projects/Shopee_Crawler_Website
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with the following variables:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   NOTION_INTEGRATION_TOKEN=your_notion_token
   NOTION_PAGE_ID=your_notion_page_id
   SENTRY_DSN=your_sentry_dsn
   SECRET_KEY=your_secret_key
   FLASK_DEBUG=False
   ```

4. **Run with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

   Or run directly:
   ```bash
   python wsgi.py
   ```

## 📁 Project Structure

```
Shopee_Crawler_Website/
├── website/                 # Main Flask application
│   ├── static/             # CSS, JS, images
│   ├── templates/          # HTML templates
│   ├── src/               # Core application modules
│   └── config.py          # Configuration settings
├── service/               # Background services
├── data/                  # Data storage
├── nginx/                 # Nginx configuration
├── docker-compose.yml     # Docker setup
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI-powered analysis
- `NOTION_INTEGRATION_TOKEN`: Notion integration token for data management
- `NOTION_PAGE_ID`: Target Notion page ID for data storage
- `SENTRY_DSN`: Sentry DSN for error monitoring
- `SECRET_KEY`: Flask application secret key
- `FLASK_DEBUG`: Debug mode (set to `False` in production)

### Docker Configuration
The application includes Docker support with:
- Multi-stage build for optimized images
- Gunicorn WSGI server for production
- Nginx reverse proxy configuration
- Volume mounting for persistent data

## 🎯 Key Capabilities

1. **E-commerce Data Extraction**: Automated crawling of product information, prices, and reviews
2. **AI-Powered Analysis**: Intelligent product categorization and market insights
3. **Real-time Monitoring**: Live dashboard for tracking crawling progress
4. **Data Export**: Multiple export formats (CSV, Excel, JSON)
5. **Notion Integration**: Automated data synchronization with Notion databases
6. **Scalable Architecture**: Designed to handle large-scale data processing

## 🔍 Use Cases

- Market research and competitive analysis
- Price monitoring and trend analysis
- Product catalog management
- E-commerce business intelligence
- Academic research on online marketplaces

## 🛡️ Security & Best Practices

- Environment-based configuration management
- Secure API key handling
- Input validation and sanitization
- Error monitoring with Sentry
- Docker containerization for isolation

---

*This project demonstrates full-stack development skills, web scraping expertise, AI integration, and modern deployment practices. It showcases the ability to build scalable, production-ready applications for real-world business needs.*

**🔗 Technologies Showcased**: Python, Flask, Docker, AI/ML, Web Scraping, API Integration, Database Management, Frontend Development

