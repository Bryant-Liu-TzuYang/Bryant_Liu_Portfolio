import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any


class CustomFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to console output
        if hasattr(record, 'color') and record.color:
            level_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['RESET']
            record.levelname = f"{level_color}{record.levelname}{reset_color}"
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            record.msg = f"[{record.request_id}] {record.msg}"
        
        return super().format(record)


def setup_logging(app_name: str = 'notion-email-backend', log_level: str = None) -> None:
    """
    Setup application logging configuration
    
    Args:
        app_name: Application name for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Use environment variable if log_level not provided
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log file names with current date
    today = datetime.now().strftime('%Y-%m-%d')
    app_log_file = os.path.join(log_dir, f'{app_name}-{today}.log')
    error_log_file = os.path.join(log_dir, f'{app_name}-error-{today}.log')
    
    # Logging configuration
    config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '[%(asctime)s] %(levelname)s: %(message)s',
                'datefmt': '%H:%M:%S'
            },
            'console': {
                '()': CustomFormatter,
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                'datefmt': '%H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': app_log_file,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': error_log_file,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': log_level,
                'handlers': ['console', 'file', 'error_file']
            },
            'werkzeug': {  # Flask's built-in server
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'sqlalchemy.engine': {  # SQLAlchemy queries
                'level': 'WARNING',
                'handlers': ['file'],
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(config)


def setup_frontend_logging(app_name: str = 'notion-email-frontend', log_level: str = None) -> logging.Logger:
    """
    Setup separate logging configuration for frontend logs
    
    Args:
        app_name: Application name for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger instance for frontend logs
    """
    
    # Use environment variable if log_level not provided
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log file names with current date
    today = datetime.now().strftime('%Y-%m-%d')
    frontend_log_file = os.path.join(log_dir, f'{app_name}-{today}.log')
    frontend_error_log_file = os.path.join(log_dir, f'{app_name}-error-{today}.log')
    
    # Create a dedicated frontend logger
    frontend_logger = logging.getLogger('frontend_logger')
    frontend_logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicates
    frontend_logger.handlers.clear()
    
    # File handler for all frontend logs
    frontend_file_handler = logging.handlers.RotatingFileHandler(
        frontend_log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    frontend_file_handler.setLevel(logging.INFO)
    frontend_file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    frontend_file_handler.setFormatter(frontend_file_formatter)
    
    # Error file handler for frontend errors only
    frontend_error_handler = logging.handlers.RotatingFileHandler(
        frontend_error_log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    frontend_error_handler.setLevel(logging.ERROR)
    frontend_error_handler.setFormatter(frontend_file_formatter)
    
    # Console handler for development
    frontend_console_handler = logging.StreamHandler()
    frontend_console_handler.setLevel(logging.DEBUG)
    frontend_console_formatter = CustomFormatter()
    frontend_console_formatter._fmt = '[%(asctime)s] %(levelname)s in %(module)s: [FRONTEND] %(message)s'
    frontend_console_formatter.datefmt = '%H:%M:%S'
    frontend_console_handler.setFormatter(frontend_console_formatter)
    
    # Add handlers to frontend logger
    frontend_logger.addHandler(frontend_file_handler)
    frontend_logger.addHandler(frontend_error_handler)
    frontend_logger.addHandler(frontend_console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    frontend_logger.propagate = False
    
    return frontend_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Add color attribute for console output
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream.name == '<stdout>':
            def colored_log(self, level, message, *args, **kwargs):
                if self.isEnabledFor(level):
                    record = self.makeRecord(self.name, level, '', 0, message, args, **kwargs)
                    record.color = True
                    self.handle(record)
            
            # Bind colored logging methods
            logger.colored_debug = lambda msg, *args, **kwargs: colored_log(logger, logging.DEBUG, msg, *args, **kwargs)
            logger.colored_info = lambda msg, *args, **kwargs: colored_log(logger, logging.INFO, msg, *args, **kwargs)
            logger.colored_warning = lambda msg, *args, **kwargs: colored_log(logger, logging.WARNING, msg, *args, **kwargs)
            logger.colored_error = lambda msg, *args, **kwargs: colored_log(logger, logging.ERROR, msg, *args, **kwargs)
            logger.colored_critical = lambda msg, *args, **kwargs: colored_log(logger, logging.CRITICAL, msg, *args, **kwargs)
            break
    
    return logger


def log_request_info(logger: logging.Logger, request, user_id: str = None) -> str:
    """
    Log request information and return a request ID
    
    Args:
        logger: Logger instance
        request: Flask request object
        user_id: Optional user ID
    
    Returns:
        Request ID for tracking
    """
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(
        f"[{request_id}] {request.method} {request.path} - "
        f"IP: {request.remote_addr} - "
        f"User: {user_id or 'Anonymous'} - "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
    )
    
    return request_id


def log_response_info(logger: logging.Logger, request_id: str, status_code: int, response_time: float = None) -> None:
    """
    Log response information
    
    Args:
        logger: Logger instance
        request_id: Request ID for tracking
        status_code: HTTP status code
        response_time: Response time in milliseconds
    """
    message = f"[{request_id}] Response: {status_code}"
    if response_time:
        message += f" - Time: {response_time:.2f}ms"
    
    if status_code >= 400:
        logger.warning(message)
    else:
        logger.info(message)
