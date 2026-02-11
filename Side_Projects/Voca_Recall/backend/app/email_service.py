from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, EmailService, NotionDatabase, db
from .logging_config import get_logger
from .middleware import log_api_call
from datetime import datetime
import pytz
from .email import reload_email_schedules
from .redis_utils import add_to_schedule, remove_from_schedule

email_service_bp = Blueprint('email_service', __name__)
logger = get_logger(__name__)


@email_service_bp.route('', methods=['GET'])
@jwt_required()
@log_api_call("Get all email services")
def get_email_services():
    """Get all email services for the current user"""
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Fetching email services for user {current_user_id}")
        
        services = EmailService.query.filter_by(user_id=current_user_id).all()
        
        # Enrich with database info
        service_list = []
        for service in services:
            service_dict = service.to_dict()
            database = NotionDatabase.query.get(service.database_id)
            if database:
                service_dict['database_name'] = database.database_name
                service_dict['database_url'] = database.database_url
            service_list.append(service_dict)
        
        return jsonify({
            'services': service_list,
            'total': len(service_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get email services for user {current_user_id}: {str(e)}")
        return jsonify({'error': 'Failed to get email services', 'details': str(e)}), 500


@email_service_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
@log_api_call("Get email service by ID")
def get_email_service(service_id):
    """Get a specific email service"""
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Fetching email service {service_id} for user {current_user_id}")
        
        service = EmailService.query.filter_by(id=service_id, user_id=current_user_id).first()
        
        if not service:
            return jsonify({'error': 'Email service not found'}), 404
        
        service_dict = service.to_dict()
        database = NotionDatabase.query.get(service.database_id)
        if database:
            service_dict['database_name'] = database.database_name
            service_dict['database_url'] = database.database_url
        
        return jsonify(service_dict), 200
        
    except Exception as e:
        logger.error(f"Failed to get email service {service_id}: {str(e)}")
        return jsonify({'error': 'Failed to get email service', 'details': str(e)}), 500


@email_service_bp.route('', methods=['POST'])
@jwt_required()
@log_api_call("Create email service")
def create_email_service():
    """Create a new email service"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not data.get('database_id'):
            return jsonify({'error': 'database_id is required'}), 400
        
        if not data.get('service_name'):
            return jsonify({'error': 'service_name is required'}), 400
        
        # Verify database belongs to user
        database = NotionDatabase.query.filter_by(
            id=data['database_id'],
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found or not authorized'}), 404
        
        # Parse send_time if provided
        send_time = None
        if data.get('send_time'):
            try:
                send_time = datetime.strptime(data['send_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid time format. Expected HH:MM'}), 400
        
        # Parse date range if provided
        date_range_start = None
        date_range_end = None
        if data.get('date_range_start'):
            try:
                date_range_start = datetime.strptime(data['date_range_start'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format for date_range_start. Expected YYYY-MM-DD'}), 400
        
        if data.get('date_range_end'):
            try:
                date_range_end = datetime.strptime(data['date_range_end'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format for date_range_end. Expected YYYY-MM-DD'}), 400
        
        # Validate vocabulary_count
        vocabulary_count = data.get('vocabulary_count', 10)
        if not isinstance(vocabulary_count, int) or vocabulary_count < 1 or vocabulary_count > 50:
            return jsonify({'error': 'vocabulary_count must be between 1 and 50'}), 400
        
        # Validate selection_method
        selection_method = data.get('selection_method', 'random')
        if selection_method not in ['random', 'latest', 'date_range']:
            return jsonify({'error': 'selection_method must be one of: random, latest, date_range'}), 400
        
        # Create email service
        service = EmailService(
            user_id=current_user_id,
            database_id=data['database_id'],
            service_name=data['service_name'],
            description=data.get('description'),
            send_time=send_time,
            timezone=data.get('timezone', 'UTC'),
            frequency=data.get('frequency', 'daily'),
            vocabulary_count=vocabulary_count,
            selection_method=selection_method,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            is_active=data.get('is_active', True),
            column_selection=data.get('column_selection', [])
        )
        
        # Calculate initial run time
        service.next_run_at = service.calculate_next_run(datetime.utcnow())
        service.status = 'PENDING'
        
        db.session.add(service)
        db.session.commit()
        
        # Add to Redis Schedule
        if service.is_active and service.next_run_at:
            try:
                # Ensure UTC timestamp
                timestamp = service.next_run_at.replace(tzinfo=pytz.UTC).timestamp()
                add_to_schedule(service.id, timestamp)
            except Exception as e:
                logger.error(f"Failed to add service {service.id} to Redis schedule: {e}")

        return jsonify({
            'message': 'Email service created successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create email service: {str(e)}")
        return jsonify({'error': 'Failed to create email service', 'details': str(e)}), 500


@email_service_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@log_api_call("Update email service")
def update_email_service(service_id):
    """Update an existing email service"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        service = EmailService.query.filter_by(id=service_id, user_id=current_user_id).first()
        
        if not service:
            return jsonify({'error': 'Email service not found'}), 404
        
        # Update fields
        if 'service_name' in data:
            service.service_name = data['service_name']
        
        if 'description' in data:
            service.description = data['description']
        
        if 'send_time' in data:
            try:
                service.send_time = datetime.strptime(data['send_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid time format. Expected HH:MM'}), 400
        
        if 'timezone' in data:
            service.timezone = data['timezone']
        
        if 'frequency' in data:
            service.frequency = data['frequency']
        
        if 'vocabulary_count' in data:
            vocab_count = int(data['vocabulary_count'])
            if vocab_count < 1 or vocab_count > 50:
                return jsonify({'error': 'vocabulary_count must be between 1 and 50'}), 400
            service.vocabulary_count = vocab_count
        
        if 'selection_method' in data:
            if data['selection_method'] not in ['random', 'latest', 'date_range']:
                return jsonify({'error': 'selection_method must be one of: random, latest, date_range'}), 400
            service.selection_method = data['selection_method']
        
        if 'date_range_start' in data:
            if data['date_range_start']:
                try:
                    service.date_range_start = datetime.strptime(data['date_range_start'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format for date_range_start. Expected YYYY-MM-DD'}), 400
            else:
                service.date_range_start = None
        
        if 'date_range_end' in data:
            if data['date_range_end']:
                try:
                    service.date_range_end = datetime.strptime(data['date_range_end'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format for date_range_end. Expected YYYY-MM-DD'}), 400
            else:
                service.date_range_end = None
        
        if 'is_active' in data:
            service.is_active = bool(data['is_active'])
            
        # Recalculate next_run_at if scheduling parameters changed
        if any(key in data for key in ['send_time', 'timezone', 'frequency', 'is_active']):
            # If reactivating, or changing schedule, update next_run_at
            # We calculate from NOW, because if service was inactive or time changed, we want the *next* logical run.
            service.next_run_at = service.calculate_next_run(datetime.utcnow())
            service.status = 'PENDING'
        
        # Update column selection if provided
        if 'column_selection' in data:
            try:
                service.column_selection = data['column_selection']
            except ValueError:
                return jsonify({'error': 'Invalid column selection format'}), 400
        
        db.session.commit()
        
        # Update Redis Schedule
        try:
            if service.is_active and service.next_run_at:
                timestamp = service.next_run_at.replace(tzinfo=pytz.UTC).timestamp()
                add_to_schedule(service_id, timestamp)
            else:
                remove_from_schedule(service_id)
        except Exception as e:
            logger.error(f"Failed to update Redis schedule for service {service_id}: {e}")
        
        logger.info(f"Updated email service {service_id} for user {current_user_id}")
        
        return jsonify({
            'message': 'Email service updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update email service {service_id}: {str(e)}")
        return jsonify({'error': 'Failed to update email service', 'details': str(e)}), 500


@email_service_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
@log_api_call("Delete email service")
def delete_email_service(service_id):
    """Delete an email service"""
    try:
        current_user_id = int(get_jwt_identity())
        
        service = EmailService.query.filter_by(id=service_id, user_id=current_user_id).first()
        
        if not service:
            return jsonify({'error': 'Email service not found'}), 404
        
        db.session.delete(service)
        db.session.commit()
        
        # Remove from Redis Schedule
        try:
            remove_from_schedule(service_id)
        except Exception as e:
            logger.error(f"Failed to remove service {service_id} from Redis schedule: {e}")
        
        logger.info(f"Deleted email service {service_id} for user {current_user_id}")
        
        return jsonify({'message': 'Email service deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete email service {service_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete email service', 'details': str(e)}), 500


@email_service_bp.route('/database/<int:database_id>', methods=['GET'])
@jwt_required()
@log_api_call("Get email services for database")
def get_services_by_database(database_id):
    """Get all email services for a specific database"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Verify database belongs to user
        database = NotionDatabase.query.filter_by(
            id=database_id,
            user_id=current_user_id
        ).first()
        
        if not database:
            return jsonify({'error': 'Database not found or not authorized'}), 404
        
        services = EmailService.query.filter_by(
            database_id=database_id,
            user_id=current_user_id
        ).all()
        
        return jsonify({
            'services': [service.to_dict() for service in services],
            'database_name': database.database_name,
            'total': len(services)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get services for database {database_id}: {str(e)}")
        return jsonify({'error': 'Failed to get email services', 'details': str(e)}), 500
