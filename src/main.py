import logging
import multiprocessing
import os
import time
from threading import Thread, Event

from bank.bank import Bank
from bank.security import SecurityGuard
from logger.configure import configure_logger_queue, add_queue_handler_to_root
from utils.configurations import ConfigurationManager
from utils.paths import get_base_paths
from web.app import create_flask_app
from multiprocessing import Manager

if __name__ == "__main__":
    multiprocessing.freeze_support()

    paths = get_base_paths()

    log_queue, listener = configure_logger_queue(paths['root'] / "app.log")
    add_queue_handler_to_root(log_queue)
    listener.start()

    log = logging.getLogger("SYSTEM")
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING) #only log errors

    bank = None
    manager = Manager()

    try:
        config_manager = ConfigurationManager(paths['config_folder'] / "config.json")
        config = config_manager.get_config()
        if not config:
            exit(1)

        host = config.get('host', '127.0.0.1')
        config['bank_code'] = host

        stop_event = Event()

        security = SecurityGuard(manager, config.get('ban_duration', 300))
        bank = Bank(config, log_queue, manager, security)
        Thread(target=bank.open_bank, daemon=True).start()
        log.info("Bank logic started in background thread")

        web_host = config.get('monitoring_host', '127.0.0.1')
        web_port = config.get('monitoring_port', 8090)
        app = create_flask_app(bank, paths['public_folder'])
        app.config['STOP_EVENT'] = stop_event

        Thread(
            target=app.run,
            kwargs={'host': web_host, 'port': web_port, 'debug': False, 'use_reloader': False},
            daemon=True
        ).start()
        log.info(f"Starting web monitoring on {web_host}:{web_port}")

        while not stop_event.is_set():
            time.sleep(1)
        # app.run(host=web_host, port=web_port, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        log.info("Shutting down by user...")
    except BaseException as e:
        log.critical(f"Critical error: {e}")
    finally:
        if bank:
            bank.close_bank()

        if manager:
            manager.shutdown()

        log.info('Application is shutting down')
        listener.stop()
        os._exit(0)