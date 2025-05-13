from app import create_app
from app.seed_db import seed_database

app = create_app()

with app.app_context():
    seed_database()

if __name__ == "__main__":
    from waitress import serve
    print("Serving application on http://localhost:5000")
    serve(app, host="localhost", port=5000)