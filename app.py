# app.py
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import bp, seed_classes
from logger import setup_logger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    setup_logger()
    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        seed_classes()

    return app

if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0", port=5000)
