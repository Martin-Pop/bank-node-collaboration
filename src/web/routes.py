import logging
import os
import signal
from flask import Blueprint, render_template, jsonify

log = logging.getLogger("WEB")

current_dir = os.path.dirname(os.path.abspath(__file__))

web_bp = Blueprint(
    'web',
    __name__,
    template_folder='templates',
    static_folder=os.path.join(current_dir, 'static'),
    static_url_path='/assets'
)

@web_bp.route('/')
def index():
    """
    Main monitoring dashboard
    """
    return render_template('index.html')


@web_bp.route('/api/stats')
def get_stats():
    """
    API endpoint for getting bank statistics
    """
    try:
        bank = web_bp.bank_instance
        stats = bank.get_stats()
        return jsonify(stats)
    except Exception as e:
        log.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@web_bp.route('/api/shutdown', methods=['POST'])
def shutdown():
    """
    API endpoint for safe shutdown
    """
    try:
        log.info("Shutdown request received")
        bank = web_bp.bank_instance
        bank.close_bank()

        def delayed_shutdown():
            import time
            time.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)

        from threading import Thread
        Thread(target=delayed_shutdown, daemon=True).start()

        return jsonify({"status": "shutting_down"}), 200
    except Exception as e:
        log.error(f"Error during shutdown: {e}")
        return jsonify({"error": str(e)}), 500


@web_bp.route('/api/accounts')
def get_accounts():
    """
    API endpoint for getting all accounts info
    """
    try:
        bank = web_bp.bank_instance
        accounts = bank.get_all_accounts()
        return jsonify(accounts)
    except Exception as e:
        log.error(f"Error getting accounts: {e}")
        return jsonify({"error": str(e)}), 500