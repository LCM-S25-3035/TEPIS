def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)
    app.register_blueprint(main)
    return app
# Flask app factory and initialization
