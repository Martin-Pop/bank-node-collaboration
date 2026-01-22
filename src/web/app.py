from flask import Flask
from src.web.routes import web_bp

def create_flask_app(bank_instance, public_path) -> Flask:
    """
    Creates configured Flask app for monitoring bank.
    """
    app = Flask(__name__, template_folder=public_path / 'templates', static_folder=public_path / 'static')

    web_bp.bank_instance = bank_instance
    app.register_blueprint(web_bp)

    return app