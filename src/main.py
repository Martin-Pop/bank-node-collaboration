import logging
import multiprocessing

from bank.bank import Bank
from logger.configure import configure_logger_queue, add_queue_handler_to_root
from utils.configurations import ConfigurationManager
from utils.paths import resolve_path

if __name__ == "__main__":

    multiprocessing.freeze_support()

    log_queue, listener = configure_logger_queue(resolve_path('app.log'))
    add_queue_handler_to_root(log_queue)
    listener.start()

    log = logging.getLogger("SYSTEM")
    try:

        config_manager = ConfigurationManager("config/config.json")
        config = config_manager.get_config()
        if not config:
            exit(1)

        bank = Bank(config, log_queue)
        bank.open_bank()

    except KeyboardInterrupt:
        exit(1)
    except BaseException as e:
        log.critical(e)

    finally:
        listener.stop()
