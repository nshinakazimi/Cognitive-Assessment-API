import re
from app.models.word_category import WordCategory, Word
from app import db

class TextAnalyzer:
    @staticmethod
    def tokenize_text(text):
        """Convert text to lowercase and split into words."""
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return words
    
    @staticmethod
    def get_category_words():
        """Get all words by category from the database."""
        categories = {}
        word_categories = WordCategory.query.all()
        
        for category in word_categories:
            categories[category.name] = [word.word for word in category.words]
        
        return categories
    
    @staticmethod
    def analyze_text(text):
        """Analyze text and return scores by category."""
        words = TextAnalyzer.tokenize_text(text)
        category_words = TextAnalyzer.get_category_words()
        
        scores = {category: 0 for category in category_words}
        
        for word in words:
            for category, category_word_list in category_words.items():
                if word in category_word_list:
                    scores[category] += 1
        
        total_score = sum(scores.values())
        scores['total'] = total_score
        
        return scores 