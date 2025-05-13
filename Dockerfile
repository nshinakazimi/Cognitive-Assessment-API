FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV SECRET_KEY=
ENV DATABASE_URI=sqlite:///cognitive_app.db

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]