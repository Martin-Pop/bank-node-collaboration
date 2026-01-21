import logging
import multiprocessing
import os
from threading import Thread

from bank.bank import Bank
from logger.configure import configure_logger_queue, add_queue_handler_to_root
from utils.configurations import ConfigurationManager
from utils.paths import resolve_path
from web.app import create_flask_app

if __name__ == "__main__":
    multiprocessing.freeze_support()

    log_queue, listener = configure_logger_queue(resolve_path('app.log'))
    add_queue_handler_to_root(log_queue)
    listener.start()

    log = logging.getLogger("SYSTEM")
    bank = None

    try:
        config_manager = ConfigurationManager("config/config.json")
        config = config_manager.get_config()
        if not config:
            exit(1)

        config['bank_code'] = config.get('host', '127.0.0.1')

        bank = Bank(config, log_queue)

        bank_thread = Thread(target=bank.open_bank, daemon=True)
        bank_thread.start()
        log.info("Bank logic started in background thread")

        web_port = config.get('web_port', 5000)
        app = create_flask_app(bank, web_port)

        log.info(f"Starting web interface on http://localhost:{web_port}")

        app.run(host='0.0.0.0', port=web_port, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        log.info("Shutting down by user...")
    except BaseException as e:
        log.critical(f"Critical error: {e}")
    finally:
        if bank:
            bank.close_bank()
        listener.stop()
        log.info("Application terminated")
        os._exit(0)