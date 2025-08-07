from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from notion_client import Client
import re
from .models import NotionDatabase, User, db
from .logging_config import get_logger
from .middleware import log_api_call, log_function_call

database_bp = Blueprint('database', __name__)
logger = get_logger(__name__)

@log_function_call("Database ID extraction")
def extract_database_id_from_url(url):
    """Extract database ID from Notion URL"""
    logger.debug(f"Extracting database ID from URL: {url}")
    
    # Pattern for Notion database URLs
    pattern = r'https://www\.notion\.so/[^/]+/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        database_id = match.group(1)
        logger.debug(f"Extracted database ID: {database_id}")
        return database_id
    
    logger.warning(f"Could not extract database ID from URL: {url}")
    return None

@log_function_call("Notion database validation")
def validate_notion_database(api_key, database_id):
    """Validate Notion database access"""
    try:
        logger.info(f"Validating Notion database access for database {database_id}")
        
        notion = Client(auth=api_key)
        database = notion.databases.retrieve(database_id)
        
        title = database.get('title', [{}])[0].get('plain_text', 'Untitled Database')
        logger.info(f"Successfully validated database: {title}")
        
        return True, title
    except Exception as e:
        logger.error(f"Failed to validate Notion database {database_id}: {str(e)}")
        return False, str(e)

@database_bp.route('/', methods=['POST'])
@jwt_required()
@log_api_call("Add Notion database")
def add_database():
    """Add a new Notion database"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not data.get('database_url'):
            return jsonify({'error': 'Database URL is required'}), 400
        
        # Extract database ID from URL
        database_id = extract_database_id_from_url(data['database_url'])
        if not database_id:
            return jsonify({'error': 'Invalid Notion database URL'}), 400
        
        # Check if database already exists for this user
        existing_db = NotionDatabase.query.filter_by(
            user_id=current_user_id, 
            database_id=database_id
        ).first()
        
        if existing_db:
            return jsonify({'error': 'This database is already connected'}), 409
        
        # Validate database access (optional - requires Notion API key)
        # This would require the user to provide their Notion API key
        database_name = data.get('database_name', 'Untitled Database')
        
        # Create database record
        notion_db = NotionDatabase(
            user_id=current_user_id,
            database_id=database_id,
            database_name=database_name,
            database_url=data['database_url']
        )
        
        db.session.add(notion_db)
        db.session.commit()
        
        return jsonify({
            'message': 'Database added successfully',
            'database': notion_db.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add database', 'details': str(e)}), 500

@database_bp.route('/', methods=['GET'])
@jwt_required()
def get_databases():
    """Get user's Notion databases"""
    try:
        current_user_id = int(get_jwt_identity())
        databases = NotionDatabase.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'databases': [db.to_dict() for db in databases]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get databases', 'details': str(e)}), 500

@database_bp.route('/<int:database_id>', methods=['GET'])
@jwt_required()
def get_database(database_id):
    """Get specific database details"""
    try:
        current_user_id = int(get_jwt_identity())
        database = NotionDatabase.query.filter_by(
            id=database_id, 
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found'}), 404
        
        return jsonify({
            'database': database.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get database', 'details': str(e)}), 500

@database_bp.route('/<int:database_id>', methods=['PUT'])
@jwt_required()
def update_database(database_id):
    """Update database details"""
    try:
        current_user_id = int(get_jwt_identity())
        database = NotionDatabase.query.filter_by(
            id=database_id, 
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('database_name'):
            database.database_name = data['database_name']
        
        if data.get('is_active') is not None:
            database.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Database updated successfully',
            'database': database.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update database', 'details': str(e)}), 500

@database_bp.route('/<int:database_id>', methods=['DELETE'])
@jwt_required()
def delete_database(database_id):
    """Delete a database"""
    try:
        current_user_id = int(get_jwt_identity())
        database = NotionDatabase.query.filter_by(
            id=database_id, 
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found'}), 404
        
        db.session.delete(database)
        db.session.commit()
        
        return jsonify({
            'message': 'Database deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete database', 'details': str(e)}), 500

@database_bp.route('/<int:database_id>/test', methods=['POST'])
@jwt_required()
def test_database_connection(database_id):
    """Test database connection and get sample data"""
    try:
        current_user_id = int(get_jwt_identity())
        database = NotionDatabase.query.filter_by(
            id=database_id, 
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found'}), 404
        
        data = request.get_json()
        api_key = data.get('notion_api_key')
        
        if not api_key:
            return jsonify({'error': 'Notion API key is required'}), 400
        
        # Test connection and get sample data
        is_valid, result = validate_notion_database(api_key, database.database_id)
        
        if not is_valid:
            return jsonify({'error': 'Failed to connect to database', 'details': result}), 400
        
        # Get sample data (first few items)
        try:
            notion = Client(auth=api_key)
            response = notion.databases.query(
                database_id=database.database_id,
                page_size=5
            )
            
            sample_items = []
            for item in response.get('results', []):
                # Extract properties (this is a simplified version)
                properties = item.get('properties', {})
                item_data = {}
                for prop_name, prop_value in properties.items():
                    if prop_value.get('type') == 'title':
                        title = prop_value.get('title', [])
                        item_data[prop_name] = title[0].get('plain_text', '') if title else ''
                    elif prop_value.get('type') == 'rich_text':
                        rich_text = prop_value.get('rich_text', [])
                        item_data[prop_name] = rich_text[0].get('plain_text', '') if rich_text else ''
                
                sample_items.append(item_data)
            
            return jsonify({
                'message': 'Connection successful',
                'database_name': result,
                'sample_items': sample_items,
                'total_items': len(response.get('results', []))
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to fetch sample data', 'details': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': 'Failed to test connection', 'details': str(e)}), 500 