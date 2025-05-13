from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import Schema, fields, ValidationError
from app.models.user import User
from app import db
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='')

class RegisterSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

@auth_bp.route('/users', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'message': 'Request must be valid JSON with Content-Type: application/json'}), HTTPStatus.BAD_REQUEST
        
        schema = RegisterSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({'message': 'Invalid input', 'errors': err.messages}), HTTPStatus.BAD_REQUEST
        
        if User.query.filter_by(username=validated_data['username']).first():
            return jsonify({'message': 'Username already exists'}), HTTPStatus.BAD_REQUEST
        
        if User.query.filter_by(email=validated_data['email']).first():
            return jsonify({'message': 'Email already exists'}), HTTPStatus.BAD_REQUEST
        
        user = User(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user_id': user.id}), HTTPStatus.CREATED
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error in register: {str(e)}")
        return jsonify({'message': 'Failed to create user'}), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error in register: {str(e)}")
        return jsonify({'message': 'An unexpected error occurred'}), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), HTTPStatus.BAD_REQUEST
        
        schema = LoginSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({'message': 'Invalid input', 'errors': err.messages}), HTTPStatus.BAD_REQUEST
        
        user = User.query.filter_by(username=validated_data['username']).first()
        
        if not user or not user.check_password(validated_data['password']):
            return jsonify({'message': 'Invalid username or password'}), HTTPStatus.UNAUTHORIZED
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'email': user.email
            }
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username
        }), HTTPStatus.OK
    except SQLAlchemyError as e:
        logging.error(f"Database error in login: {str(e)}")
        return jsonify({'message': 'Failed to authenticate user'}), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error in login: {str(e)}")
        return jsonify({'message': 'An unexpected error occurred'}), HTTPStatus.INTERNAL_SERVER_ERROR 