from app import create_app
from app.seed_db import seed_database
import os
from waitress import serve

app = create_app()

with app.app_context():
    seed_database()

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    serve(app, host='localhost', port=5000) 