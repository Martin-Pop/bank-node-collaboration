from flask import Flask, current_app
from .monitoring import monitoring_bp
from .accounts import accounts_bp

def create_flask_app(bank_instance, public_path) -> Flask:
    """
    Creates configured Flask app for monitoring bank.
    """
    app = Flask(__name__, template_folder=public_path / 'templates', static_folder=public_path / 'static')

    app.config['BANK'] = bank_instance

    app.register_blueprint(monitoring_bp)
    app.register_blueprint(accounts_bp, url_prefix='/accounts')

    return app