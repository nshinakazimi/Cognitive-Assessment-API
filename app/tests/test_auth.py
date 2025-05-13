import pytest
from app.models.user import User

def test_register_user(client):
    """Test user registration."""
    response = client.post('/users', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    assert 'user_id' in response.get_json()
    
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'

def test_register_duplicate_username(client):
    """Test registering with a duplicate username."""
    client.post('/users', json={
        'username': 'duplicate',
        'email': 'first@example.com',
        'password': 'password123'
    })
    
    response = client.post('/users', json={
        'username': 'duplicate',
        'email': 'second@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'Username already exists' in response.get_json()['message']

def test_login_valid(client):
    """Test login with valid credentials."""
    client.post('/users', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    response = client.post('/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_login_invalid(client):
    """Test login with invalid credentials."""
    client.post('/users', json={
        'username': 'loginuser2',
        'email': 'login2@example.com',
        'password': 'password123'
    })
    
    response = client.post('/login', json={
        'username': 'loginuser2',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'Invalid username or password' in response.get_json()['message']