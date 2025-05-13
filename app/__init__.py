import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app)
    
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///cognitive_app.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            JWT_ACCESS_TOKEN_EXPIRES=86400,
            JWT_TOKEN_LOCATION=['headers'],
            JWT_HEADER_NAME='Authorization',
            JWT_HEADER_TYPE='Bearer'
        )
    else:
        app.config.from_mapping(test_config)
    
    db.init_app(app)
    jwt.init_app(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token: {jwt_payload.get('sub', 'unknown user')}")
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired',
            'user_id': jwt_payload.get('sub', 'unknown')
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({
            'message': 'Signature verification failed',
            'error': 'invalid_token',
            'details': str(error)
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token error: {error}")
        return jsonify({
            'message': 'Request does not contain an access token',
            'error': 'authorization_required',
            'details': str(error)
        }), 401
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_payload):
        print(f"Blocked token for user: {jwt_payload.get('sub', 'unknown')}")
        return False
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            user_id = int(identity)
            from app.models.user import User
            return User.query.filter_by(id=user_id).one_or_none()
        except (ValueError, TypeError):
            print(f"Error converting identity to integer: {identity}")
            return None
    
    from app.routes.auth import auth_bp
    from app.routes.journals import journals_bp
    from app.routes.ui import ui_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(journals_bp)
    app.register_blueprint(ui_bp)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    with app.app_context():
        db.create_all()

    return app 