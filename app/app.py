# Main application entry for TEPIS
# Maintained by Sunny Aiden (sangsunlee.aiden@gmail.com)


from flask import Flask, render_template
from app.routes import main


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    @app.route("/")
    def home():
        return render_template("eventsphere_website.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
# This code initializes the Flask application for TEPIS, registering the main blueprint
# and defining the home route that serves the main HTML page.