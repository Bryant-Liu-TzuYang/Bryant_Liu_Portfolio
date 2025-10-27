## !! THIS IS AI-GENERATED AND IS STILL BEING REVIEWED!!

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
