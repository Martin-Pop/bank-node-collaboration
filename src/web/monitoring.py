import logging
from threading import Thread
from flask import Blueprint, render_template, jsonify, current_app, request

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


@monitoring_bp.route('/api/control', methods=['POST'])
def control_bank():
    """
    Endpoints to Start or Stop the bank logic without killing the app.
    Payload: {"action": "start"} or {"action": "stop"}
    """
    try:
        data = request.get_json()
        action = data.get('action')
        bank = current_app.config['BANK']

        if action == 'start':
            if getattr(bank, '_is_open', False):
                return jsonify({"message": "Bank is already running"}), 200

            t = Thread(target=bank.open_bank, daemon=True)
            t.start()
            return jsonify({"status": "started"}), 200

        elif action == 'stop':
            log.info("Stopping bank via web control...")
            bank.close_bank()
            return jsonify({"status": "stopped"}), 200

        else:
            return jsonify({"error": "Invalid action"}), 400

    except Exception as e:
        log.error(f"Error controlling bank: {e}")
        return jsonify({"error": str(e)}), 500


@monitoring_bp.route('/api/shutdown', methods=['POST'])
def shutdown():
    try:
        log.info("Shutdown request received")
        bank = current_app.config['BANK']
        bank.close_bank()
        stop_event = current_app.config.get('STOP_EVENT')

        if stop_event:
            stop_event.set()
            return jsonify({"status": "shutting_down"}), 200
        else:
            return jsonify({"error": "Stop event not configured"}), 500
    except Exception as e:
        log.error(f"Error during shutdown: {e}")
        return jsonify({"error": str(e)}), 500