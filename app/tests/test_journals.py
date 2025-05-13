import pytest
from app.models.journal import Journal, JournalScore

def test_create_journal(client, auth_headers):
    """Test journal creation and scoring."""
    response = client.post('/journals', 
                          json={'text': 'I am happy today, but I was sad yesterday.'},
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert 'journal_id' in data
    assert 'score' in data
    assert data['score']['positive_emotion'] == 1
    assert data['score']['negative_emotion'] == 1
    
    with client.application.app_context():
        journal = Journal.query.get(data['journal_id'])
        assert journal is not None
        assert journal.text == 'I am happy today, but I was sad yesterday.'
        
        score = journal.scores
        assert score is not None
        assert score.positive_emotion == 1
        assert score.negative_emotion == 1

def test_get_journal_score(client, auth_headers):
    """Test retrieving journal score."""
    response = client.post('/journals', 
                          json={'text': 'I think about my friend often.'},
                          headers=auth_headers)
    
    journal_id = response.get_json()['journal_id']
    
    response = client.get(f'/journals/{journal_id}/score', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['journal_id'] == journal_id
    assert data['score']['cognitive'] == 1
    assert data['score']['social'] == 1

def test_get_nonexistent_journal(client, auth_headers):
    """Test retrieving a nonexistent journal."""
    response = client.get('/journals/9999/score', headers=auth_headers)
    
    assert response.status_code == 404
    assert 'not found' in response.get_json()['message']

def test_unauthorized_access(client):
    """Test accessing journal without authentication."""
    response = client.post('/journals', json={'text': 'This should fail.'})
    
    assert response.status_code == 401