from datetime import datetime
from app import db

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scores = db.relationship('JournalScore', backref='journal', lazy=True, uselist=False)

    def __repr__(self):
        return f'<Journal {self.id}>'

class JournalScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal.id'), nullable=False)
    positive_emotion = db.Column(db.Integer, default=0)
    negative_emotion = db.Column(db.Integer, default=0)
    social = db.Column(db.Integer, default=0)
    cognitive = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JournalScore for Journal {self.journal_id}>' 