"""
2026/1/21. Bryant: Wrappers for logging and authentication
"""


from flask import request, g, jsonify
from functools import wraps
import time
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from .logging_config import get_logger, log_request_info, log_response_info
from .models import User

logger = get_logger(__name__)


def log_requests(app):
    """
    Add request logging middleware to the Flask app
    """
    
    @app.before_request
    def before_request():
        """Log request information and start timer"""
        g.start_time = time.time()
        
        # Get user ID if available (from JWT token)
        user_id = None
        try:
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            if request.headers.get('Authorization'):
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
        except Exception:
            pass  # JWT not available or invalid
        
        # Log request and store request ID
        g.request_id = log_request_info(logger, request, user_id)
    
    @app.after_request
    def after_request(response):
        """Log response information"""
        if hasattr(g, 'start_time') and hasattr(g, 'request_id'):
            response_time = (time.time() - g.start_time) * 1000
            log_response_info(logger, g.request_id, response.status_code, response_time)
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Log unhandled exceptions"""
        request_id = getattr(g, 'request_id', 'unknown')
        logger.error(
            f"[{request_id}] Unhandled exception: {str(error)}",
            exc_info=True
        )
        
        # Let Flask handle the error normally
        raise error


def log_function_call(func_name: str = None):
    """
    Decorator to log function calls with arguments and execution time
    
    Args:
        func_name: Optional custom function name for logging
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            function_name = func_name or f"{func.__module__}.{func.__name__}"
            func_logger = get_logger(func.__module__)
            
            # Log function start
            func_logger.debug(f"Calling {function_name}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                func_logger.debug(f"Completed {function_name} in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                func_logger.error(
                    f"Error in {function_name} after {execution_time:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_database_operations(func):
    """
    Decorator specifically for database operations logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db_logger = get_logger('database')
        function_name = f"{func.__module__}.{func.__name__}"
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            db_logger.info(f"DB operation {function_name} completed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            db_logger.error(
                f"DB operation {function_name} failed after {execution_time:.2f}ms: {str(e)}",
                exc_info=True
            )
            raise
    
    return wrapper


def log_api_call(operation: str = None):
    """
    Decorator for API endpoint logging
    
    Args:
        operation: Description of the API operation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_logger = get_logger('api')
            request_id = getattr(g, 'request_id', 'unknown')
            op_name = operation or f"{func.__module__}.{func.__name__}"
            
            api_logger.info(f"[{request_id}] Starting API operation: {op_name}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                api_logger.info(f"[{request_id}] API operation {op_name} completed in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                api_logger.error(
                    f"[{request_id}] API operation {op_name} failed after {execution_time:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def developer_required():
    """
    Decorator to require developer or admin role for accessing an endpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.get(user_id)
            if not user or user.role not in ['developer', 'admin']:
                logger.warning(f"Unauthorized access attempt to developer endpoint by user {user_id}")
                return jsonify({'error': 'Developer or admin access required'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required():
    """
    Decorator to require admin role for accessing an endpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.get(user_id)
            if not user or user.role != 'admin':
                logger.warning(f"Unauthorized access attempt to admin endpoint by user {user_id}")
                return jsonify({'error': 'Admin access required'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
