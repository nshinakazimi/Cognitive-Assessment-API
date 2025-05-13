# Cognitive Journal Backend

A Flask-based REST API for a cognitive journaling application that allows users to track their thoughts, analyze sentiment, and gain insights into their cognitive patterns.

## Tech Stack

- **Backend Framework**: Flask 2.3.3
- **Database**: SQLAlchemy with SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: pytest
- **Deployment**: Docker with Gunicorn

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Docker (optional for containerized setup)

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/nshinakazimi/Cognitive-Assessment-API
   cd Cognitive-Assessment-API
   ```

2. Create and activate a virtual environment(Optional):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables by creating a `.env` file at the root of the project:
   ```
   SECRET_KEY=
   DATABASE_URI=sqlite:///instance/cognitive_app.db
   FLASK_ENV=development
   ```

5. Initialize the database:
   ```
   python -m app.seed_db
   ```

6. Run the application:
   ```
   python app.py
   ```

The API will be available at http://localhost:5000.

## Docker Commands

### Build Docker Image

```
docker build -t cognitive-journal-api .
```

### Run Docker Container

```
docker run -p 5000:5000 --name cognitive-journal cognitive-journal-api
```

The API will be available at http://localhost:5000.

### Run Docker Container with Custom Environment Variables

```
docker run -p 5000:5000 -e SECRET_KEY=custom_secret -e DATABASE_URI=sqlite:///custom.db cognitive-journal-api
```

## Testing Instructions

### Running Unit Tests

```
pytest
```

### Running Tests with Coverage Report

```
pytest --cov=app
```

### API Testing Examples

#### Authentication

**Login:**
```
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password123"}'
```

**Register:**
```
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "new_user@example.com", "password": "password123", "name": "New User"}'
```

#### Journal Entries

**Create a journal entry:**
```
curl -X POST http://localhost:5000/api/journals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "My Thoughts", "content": "Today was a productive day.", "tags": ["work", "productive"]}'
```

**Get all journal entries:**
```
curl -X GET http://localhost:5000/api/journals \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Frontend API Testing

The application includes a built-in frontend interface for testing API endpoints directly in the browser.

### Features

- Interactive UI for sending API requests
- Authentication token management
- Visualize and parse JSON responses
- Test different HTTP methods (GET, POST)
- Save and reuse frequently used API calls

### Accessing the API Test Interface

1. Start the application as described in the setup instructions
2. Navigate to http://localhost:5000/test in your web browser
3. Use the interface to test various API endpoints

The frontend testing interface provides a more user-friendly alternative to command-line tools like curl for testing and debugging API functionality.

## Project Structure

- `app/`: Main application package
  - `models/`: Database models
  - `routes/`: API endpoints
  - `services/`: Business logic
  - `templates/`: HTML templates
  - `static/`: Static assets
  - `tests/`: Test suite

## API Endpoints

### Authentication
- `/login` - Login and receive JWT token
- `/users` - Register a new user

### Journal Entries
- `GET /journals` - Get all journal entries for the authenticated user
- `POST /journals` - Create a new journal entry with sentiment analysis
- `GET /journals/<journal_id>` - Get a specific journal entry by ID
- `GET /journals/<journal_id>/score` - Get sentiment analysis scores for a specific journal entry

### UI Routes
- `/` - Main UI testing interface
- `/test` - Alternative UI testing interface

## Video Demo

<video width="640" height="360" controls>
  <source src="assets/bio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>