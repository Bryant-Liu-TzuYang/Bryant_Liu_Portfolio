from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
import json
from .logging_config import get_logger, setup_frontend_logging
from .middleware import log_api_call

frontend_logs_bp = Blueprint('frontend_logs', __name__)
logger = get_logger(__name__)

# Setup dedicated frontend logger
frontend_logger = setup_frontend_logging()

@frontend_logs_bp.route('/logs', methods=['POST'])
@log_api_call("Receive frontend logs")
def receive_frontend_logs():
    """Receive logs from frontend and store them in backend logs"""
    try:
        # Try to get user identity if token is provided, but don't require it
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass  # Anonymous logging is OK
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No log data provided'}), 400
        
        # Validate required fields
        required_fields = ['level', 'message', 'timestamp', 'context']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract log data
        level = data.get('level', 'info').upper()
        message = data.get('message', '')
        timestamp = data.get('timestamp', '')
        context = data.get('context', 'Frontend')
        log_data = data.get('data', {})
        user_agent = request.headers.get('User-Agent', 'Unknown')
        client_ip = request.remote_addr
        
        # Format the frontend log message with more detailed context
        user_info = f"User: {user_id}" if user_id else "User: Anonymous"
        client_info = f"IP: {client_ip}"
        user_agent_info = f"UA: {user_agent[:100]}..." if len(user_agent) > 100 else f"UA: {user_agent}"
        
        # Create structured log message
        log_parts = [
            f"[{context}]",
            message,
            f"- {user_info}",
            f"- {client_info}",
            f"- {user_agent_info}"
        ]
        
        # Add additional data if present
        if log_data:
            log_parts.append(f"- Data: {json.dumps(log_data, separators=(',', ':'))}")
        
        formatted_message = " ".join(log_parts)
        
        # Log to dedicated frontend logger based on level
        if level == 'DEBUG':
            frontend_logger.debug(formatted_message)
        elif level == 'INFO':
            frontend_logger.info(formatted_message)
        elif level == 'WARN' or level == 'WARNING':
            frontend_logger.warning(formatted_message)
        elif level == 'ERROR':
            frontend_logger.error(formatted_message)
        elif level == 'CRITICAL':
            frontend_logger.critical(formatted_message)
        else:
            frontend_logger.info(formatted_message)  # Default to info for unknown levels
        
        # Also log to main backend logger for request tracking
        logger.info(f"Frontend log received: {level} - {context} - {message[:50]}{'...' if len(message) > 50 else ''}")
        
        return jsonify({'status': 'success', 'message': 'Log received'}), 200
        
    except Exception as e:
        logger.error(f"Failed to process frontend log: {str(e)}")
        return jsonify({'error': 'Failed to process log', 'details': str(e)}), 500

@frontend_logs_bp.route('/logs/test', methods=['POST'])
def test_frontend_logging():
    """Test endpoint for frontend logging (no auth required)"""
    try:
        frontend_logger.info("[TestEndpoint] Frontend logging test successful - connection verified")
        logger.info("Frontend logging test endpoint accessed successfully")
        return jsonify({'status': 'success', 'message': 'Test log received and written to frontend log file'}), 200
    except Exception as e:
        logger.error(f"Frontend logging test failed: {str(e)}")
        return jsonify({'error': 'Test failed', 'details': str(e)}), 500

@frontend_logs_bp.route('/logs/info', methods=['GET'])
@log_api_call("Get frontend logging info")
def get_frontend_logging_info():
    """Get information about frontend log files"""
    try:
        import os
        from datetime import datetime
        
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        today = datetime.now().strftime('%Y-%m-%d')
        
        frontend_log_file = f'notion-email-frontend-{today}.log'
        frontend_error_file = f'notion-email-frontend-error-{today}.log'
        backend_log_file = f'notion-email-backend-{today}.log'
        
        info = {
            'frontend_log_file': frontend_log_file,
            'frontend_error_file': frontend_error_file,
            'backend_log_file': backend_log_file,
            'log_directory': 'backend/logs/',
            'files_exist': {
                'frontend_log': os.path.exists(os.path.join(log_dir, frontend_log_file)),
                'frontend_error': os.path.exists(os.path.join(log_dir, frontend_error_file)),
                'backend_log': os.path.exists(os.path.join(log_dir, backend_log_file))
            }
        }
        
        return jsonify(info), 200
        
    except Exception as e:
        logger.error(f"Failed to get frontend logging info: {str(e)}")
        return jsonify({'error': 'Failed to get logging info', 'details': str(e)}), 500
