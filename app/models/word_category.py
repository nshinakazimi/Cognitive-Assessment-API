from app import db

class WordCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    words = db.relationship('Word', backref='category', lazy=True)

    def __repr__(self):
        return f'<WordCategory {self.name}>'

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('word_category.id'), nullable=False)

    def __repr__(self):
        return f'<Word {self.word}>' 