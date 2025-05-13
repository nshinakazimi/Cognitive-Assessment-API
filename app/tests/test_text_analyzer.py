import pytest
from app.services.text_analyzer import TextAnalyzer

def test_tokenize_text():
    """Test the tokenization function."""
    text = "Hello, world! This is a test."
    tokens = TextAnalyzer.tokenize_text(text)
    
    assert tokens == ['hello', 'world', 'this', 'is', 'a', 'test']

def test_analyze_text(app):
    """Test text analysis with known words."""
    with app.app_context():
        text = "I am happy and I know it."
        scores = TextAnalyzer.analyze_text(text)
        
        assert scores['positive_emotion'] == 1
        assert scores['cognitive'] == 1
        assert scores['total'] == 2
        
        text = "I believe my friend is happy but my family is sad."
        scores = TextAnalyzer.analyze_text(text)
        
        assert scores['positive_emotion'] == 1
        assert scores['negative_emotion'] == 1
        assert scores['social'] == 2
        assert scores['cognitive'] == 1
        assert scores['total'] == 5
