from flask import Flask
from src.web.routes import web_bp

def create_flask_app(bank_instance, web_port: int = 5000) -> Flask:
    """
    Creates configured Flask app for monitoring bank.
    """
    app = Flask(__name__)

    web_bp.bank_instance = bank_instance
    app.register_blueprint(web_bp)

    return app