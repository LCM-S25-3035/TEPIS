# WSGI entry point for Flask app
# Maintained by Sunny Aiden (sangsunlee.aiden@gmail.com)

from app.app import create_app

app = create_app()
