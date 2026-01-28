from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from notion_client import Client
from .models import NotionToken, NotionDatabase, db
from .logging_config import get_logger
from .middleware import log_api_call

tokens_bp = Blueprint('tokens', __name__)
logger = get_logger(__name__)

@tokens_bp.route('/', methods=['GET'])
@tokens_bp.route('', methods=['GET'])
@jwt_required()
@log_api_call("Get all tokens")
def get_tokens():
    """Get all Notion API tokens for the current user"""
    try:
        current_user_id = int(get_jwt_identity())
        
        tokens = NotionToken.query.filter_by(user_id=current_user_id).order_by(NotionToken.created_at.desc()).all()
        
        return jsonify({
            'tokens': [token.to_dict() for token in tokens]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to fetch tokens: {str(e)}")
        return jsonify({'error': 'Failed to fetch tokens'}), 500

@tokens_bp.route('/<int:token_id>', methods=['GET'])
@jwt_required()
@log_api_call("Get token by ID")
def get_token(token_id):
    """Get a specific token by ID"""
    try:
        current_user_id = int(get_jwt_identity())
        
        token = NotionToken.query.filter_by(
            id=token_id,
            user_id=current_user_id
        ).first()
        
        if not token:
            return jsonify({'error': 'Token not found'}), 404
        
        return jsonify(token.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Failed to fetch token {token_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch token'}), 500

@tokens_bp.route('/', methods=['POST'])
@tokens_bp.route('', methods=['POST'])
@jwt_required()
@log_api_call("Create new token")
def create_token():
    """Create a new Notion API token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        token_value = data.get('token')
        token_name = data.get('token_name', '').strip()
        
        if not token_value:
            return jsonify({'error': 'Token is required'}), 400
        
        # Validate token by trying to authenticate with Notion API
        try:
            notion = Client(auth=token_value)
            # Try to list databases to verify the token works
            notion.search(filter={"property": "object", "value": "database"}, page_size=1)
            logger.info("Token validated successfully with Notion API")
        except Exception as e:
            logger.error(f"Invalid Notion token: {str(e)}")
            return jsonify({'error': 'Invalid Notion API token. Please check and try again.'}), 400
        
        # Create new token
        new_token = NotionToken(
            user_id=current_user_id,
            token=token_value,
            token_name=token_name if token_name else None
        )
        
        db.session.add(new_token)
        db.session.commit()
        
        logger.info(f"Created new token with ID {new_token.id} for user {current_user_id}")
        
        return jsonify({
            'message': 'Token created successfully',
            'token': new_token.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create token: {str(e)}")
        return jsonify({'error': 'Failed to create token'}), 500

@tokens_bp.route('/<int:token_id>', methods=['PUT'])
@jwt_required()
@log_api_call("Update token")
def update_token(token_id):
    """Update a Notion API token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        token = NotionToken.query.filter_by(
            id=token_id,
            user_id=current_user_id
        ).first()
        
        if not token:
            return jsonify({'error': 'Token not found'}), 404
        
        # Update token name
        if 'token_name' in data:
            token.token_name = data['token_name'].strip() if data['token_name'] else None
        
        # Update token value (and validate it)
        if 'token' in data:
            new_token_value = data['token']
            if not new_token_value:
                return jsonify({'error': 'Token value cannot be empty'}), 400
            
            # Validate new token
            try:
                notion = Client(auth=new_token_value)
                notion.search(filter={"property": "object", "value": "database"}, page_size=1)
                logger.info("New token value validated successfully")
                token.token = new_token_value
            except Exception as e:
                logger.error(f"Invalid Notion token: {str(e)}")
                return jsonify({'error': 'Invalid Notion API token. Please check and try again.'}), 400
        
        # Update active status
        if 'is_active' in data:
            token.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        logger.info(f"Updated token {token_id} for user {current_user_id}")
        
        return jsonify({
            'message': 'Token updated successfully',
            'token': token.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update token {token_id}: {str(e)}")
        return jsonify({'error': 'Failed to update token'}), 500

@tokens_bp.route('/<int:token_id>', methods=['DELETE'])
@jwt_required()
@log_api_call("Delete token")
def delete_token(token_id):
    """Delete a Notion API token"""
    try:
        current_user_id = int(get_jwt_identity())
        
        token = NotionToken.query.filter_by(
            id=token_id,
            user_id=current_user_id
        ).first()
        
        if not token:
            return jsonify({'error': 'Token not found'}), 404
        
        # Check if token is being used by any databases
        databases_using_token = NotionDatabase.query.filter_by(token_id=token_id).all()
        
        if databases_using_token:
            database_names = [db.database_name for db in databases_using_token]
            return jsonify({
                'error': 'Cannot delete token that is being used by databases',
                'databases': database_names
            }), 400
        
        db.session.delete(token)
        db.session.commit()
        
        logger.info(f"Deleted token {token_id} for user {current_user_id}")
        
        return jsonify({'message': 'Token deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete token {token_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete token'}), 500
