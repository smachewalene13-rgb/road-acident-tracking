# backend/wsgi.py - Entry point for Gunicorn on Render
from app import app

# This is the application object that Gunicorn will use
# It's explicitly named 'app' so Gunicorn can find it

if __name__ == "__main__":
    app.run()
