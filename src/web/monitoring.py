import logging
import os
import signal
from flask import Blueprint, render_template, jsonify, current_app

log = logging.getLogger("WEB")

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/')
def index():
    """
    Main monitoring dashboard
    """
    bank = current_app.config['BANK']

    return render_template(
        'index.html',
        gateway_address=bank.get_gateway_address(),
        start_time=bank.get_start_time()
    )


@monitoring_bp.route('/api/stats')
def get_stats():
    try:
        bank = current_app.config['BANK']
        stats = bank.get_stats()
        return jsonify(stats)
    except Exception as e:
        log.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/api/shutdown', methods=['POST'])
def shutdown():
    try:
        log.info("Shutdown request received")
        bank = current_app.config['BANK']
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