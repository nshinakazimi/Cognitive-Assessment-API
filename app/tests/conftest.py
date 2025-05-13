import os
import pytest
from app import create_app, db
from app.models.user import User
from app.models.word_category import WordCategory, Word

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test_secret_key'
    })
    
    with app.app_context():
        db.create_all()
        
        categories = {
            'positive_emotion': ['happy', 'joy', 'love'],
            'negative_emotion': ['sad', 'angry', 'fear'],
            'social': ['friend', 'family', 'team'],
            'cognitive': ['think', 'know', 'believe']
        }
        
        for category_name, words in categories.items():
            category = WordCategory(name=category_name)
            db.session.add(category)
            db.session.flush()
            
            for word_text in words:
                word = Word(word=word_text, category_id=category.id)
                db.session.add(word)
        
        db.session.commit()
    
    yield app

@pytest.fixture
def client(app):
    """Test client for the Flask app."""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create a user and get auth headers for testing."""
    with client.application.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/login', json={
            'username': 'testuser',
            'password': 'password'
        })
        
        token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        return headers 