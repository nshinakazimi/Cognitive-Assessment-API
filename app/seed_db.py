import json
from app import create_app, db
from app.models.word_category import WordCategory, Word

def seed_database():
    """Seed the database with word categories and word lists."""
    app = create_app()
    
    with app.app_context():
        if WordCategory.query.count() > 0:
            print("Database already seeded. Skipping.")
            return
        
        word_dict = {
            "positive_emotion": [
                "happy", "joy", "love", "excited", "content", "pleased", "grateful", "hopeful", "proud", "amused",
                "cheerful", "delighted", "optimistic", "enthusiastic", "satisfied", "blissful", "ecstatic", "gleeful",
                "jubilant", "merry", "radiant", "thrilled", "upbeat", "vivacious", "zestful", "buoyant", "elated",
                "exhilarated", "lighthearted", "overjoyed", "rapturous", "triumphant", "euphoric", "exultant", "festive",
                "jolly", "jovial", "mirthful", "peppy", "perky", "playful", "sparkling", "sunny", "vibrant", "whimsical",
                "winsome", "zany", "carefree", "ebullient", "effervescent", "exuberant"
            ],
            "negative_emotion": [
                "sad", "angry", "fear", "anxious", "depressed", "frustrated", "worried", "upset", "disappointed", "guilty",
                "ashamed", "lonely", "miserable", "gloomy", "desperate", "hopeless", "bitter", "resentful", "irritated",
                "enraged", "furious", "aggravated", "annoyed", "disgruntled", "displeased", "exasperated", "incensed",
                "indignant", "outraged", "vexed", "apprehensive", "dreadful", "frightened", "panicked", "petrified",
                "terrified", "alarmed", "shocked", "horrified", "dismayed", "distressed", "grieved", "heartbroken",
                "melancholy", "mournful", "sorrowful", "woeful", "despondent", "disheartened", "forlorn", "pessimistic"
            ],
            "social": [
                "friend", "family", "team", "community", "partner", "colleague", "neighbor", "acquaintance", "ally", "companion",
                "confidant", "mate", "peer", "supporter", "advocate", "backer", "benefactor", "comrade", "crony", "pal",
                "associate", "collaborator", "co-worker", "classmate", "roommate", "playmate", "soulmate", "spouse", "sibling",
                "parent", "child", "relative", "kin", "clan", "tribe", "group", "club", "society", "organization", "network",
                "circle", "crew", "gang", "posse", "squad", "unit", "band", "troop", "assembly", "congregation", "gathering"
            ],
            "cognitive": [
                "think", "know", "believe", "understand", "realize", "consider", "contemplate", "ponder", "reflect", "analyze",
                "evaluate", "assess", "judge", "decide", "conclude", "deduce", "infer", "reason", "rationalize", "speculate",
                "hypothesize", "theorize", "postulate", "conjecture", "surmise", "guess", "estimate", "calculate", "compute",
                "measure", "quantify", "qualify", "compare", "contrast", "differentiate", "distinguish", "identify", "recognize",
                "recall", "remember", "recollect", "retrieve", "forget", "ignore", "overlook", "neglect", "misunderstand",
                "confuse", "bewilder", "perplex", "puzzle"
            ]
        }
        
        for category_name, words in word_dict.items():
            category = WordCategory(name=category_name)
            db.session.add(category)
            db.session.flush()
            
            for word_text in words:
                word = Word(word=word_text, category_id=category.id)
                db.session.add(word)
        
        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database() 