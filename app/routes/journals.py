from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from app.models.journal import Journal, JournalScore
from app.services.text_analyzer import TextAnalyzer
from app import db
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

journals_bp = Blueprint('journals', __name__, url_prefix='')

class JournalSchema(Schema):
    text = fields.String(required=True)

def get_user_id_from_token():
    """Extract and validate user ID from JWT token."""
    try:
        return int(get_jwt_identity())
    except (ValueError, TypeError):
        return None

@journals_bp.route('/journals', methods=['GET'])
@jwt_required()
def get_all_journals():
    """Get all journals for the current user."""
    current_user_id = get_user_id_from_token()
    if current_user_id is None:
        return jsonify({'message': 'Invalid user identity'}), HTTPStatus.UNAUTHORIZED
    
    try:
        journals = Journal.query.filter_by(user_id=current_user_id).order_by(Journal.created_at.desc()).all()
        
        response = []
        for journal in journals:
            journal_data = {
                'id': journal.id,
                'text': journal.text,
                'created_at': journal.created_at.isoformat(),
                'updated_at': journal.updated_at.isoformat() if hasattr(journal, 'updated_at') and journal.updated_at else None
            }
            
            response.append(journal_data)
        
        return jsonify(response), HTTPStatus.OK
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_all_journals: {str(e)}")
        return jsonify({'message': 'Failed to retrieve journals'}), HTTPStatus.INTERNAL_SERVER_ERROR

@journals_bp.route('/journals', methods=['POST'])
@jwt_required()
def create_journal():
    """Create a new journal entry."""
    current_user_id = get_user_id_from_token()
    if current_user_id is None:
        return jsonify({'message': 'Invalid user identity'}), HTTPStatus.UNAUTHORIZED
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), HTTPStatus.BAD_REQUEST
        
        schema = JournalSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({'message': 'Invalid input', 'errors': err.messages}), HTTPStatus.BAD_REQUEST
        
        if not validated_data['text'].strip():
            return jsonify({'message': 'Journal text cannot be empty'}), HTTPStatus.BAD_REQUEST
        
        journal = Journal(text=validated_data['text'], user_id=current_user_id)
        db.session.add(journal)
        db.session.flush()
        
        scores = TextAnalyzer.analyze_text(validated_data['text'])
        
        journal_score = JournalScore(
            journal_id=journal.id,
            positive_emotion=scores.get('positive_emotion', 0),
            negative_emotion=scores.get('negative_emotion', 0),
            social=scores.get('social', 0),
            cognitive=scores.get('cognitive', 0),
            total_score=scores.get('total', 0)
        )
        
        db.session.add(journal_score)
        db.session.commit()
        
        return jsonify({
            'journal_id': journal.id,
            'score': {
                'positive_emotion': journal_score.positive_emotion,
                'negative_emotion': journal_score.negative_emotion,
                'social': journal_score.social,
                'cognitive': journal_score.cognitive,
                'total': journal_score.total_score
            }
        }), HTTPStatus.CREATED
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error in create_journal: {str(e)}")
        return jsonify({'message': 'Failed to create journal entry'}), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error in create_journal: {str(e)}")
        return jsonify({'message': 'An unexpected error occurred'}), HTTPStatus.INTERNAL_SERVER_ERROR

@journals_bp.route('/journals/<int:journal_id>/score', methods=['GET'])
@jwt_required()
def get_journal_score(journal_id):
    """Get score for a specific journal entry."""
    current_user_id = get_user_id_from_token()
    if current_user_id is None:
        return jsonify({'message': 'Invalid user identity'}), HTTPStatus.UNAUTHORIZED
    
    try:
        journal = Journal.query.filter_by(id=journal_id, user_id=current_user_id).first()
        
        if not journal:
            return jsonify({'message': 'Journal not found or unauthorized'}), HTTPStatus.NOT_FOUND
        
        journal_score = journal.scores
        
        if not journal_score:
            return jsonify({'message': 'No score available for this journal'}), HTTPStatus.NOT_FOUND
        
        return jsonify({
            'journal_id': journal.id,
            'score': {
                'positive_emotion': journal_score.positive_emotion,
                'negative_emotion': journal_score.negative_emotion,
                'social': journal_score.social,
                'cognitive': journal_score.cognitive,
                'total': journal_score.total_score
            }
        }), HTTPStatus.OK
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_journal_score: {str(e)}")
        return jsonify({'message': 'Failed to retrieve journal score'}), HTTPStatus.INTERNAL_SERVER_ERROR
    """Get a specific journal entry with its score."""
    current_user_id = get_user_id_from_token()
    if current_user_id is None:
        return jsonify({'message': 'Invalid user identity'}), HTTPStatus.UNAUTHORIZED
    
    try:
        journal = Journal.query.filter_by(id=journal_id, user_id=current_user_id).first()
        
        if not journal:
            return jsonify({'message': 'Journal not found or unauthorized'}), HTTPStatus.NOT_FOUND
        
        journal_score = journal.scores
        
        response = {
            'id': journal.id,
            'text': journal.text,
            'created_at': journal.created_at.isoformat(),
            'updated_at': journal.updated_at.isoformat() if hasattr(journal, 'updated_at') and journal.updated_at else None
        }
        
        if journal_score:
            response['score'] = {
                'positive_emotion': journal_score.positive_emotion,
                'negative_emotion': journal_score.negative_emotion,
                'social': journal_score.social,
                'cognitive': journal_score.cognitive,
                'total': journal_score.total_score
            }
        
        return jsonify(response), HTTPStatus.OK
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_journal: {str(e)}")
        return jsonify({'message': 'Failed to retrieve journal'}), HTTPStatus.INTERNAL_SERVER_ERROR 