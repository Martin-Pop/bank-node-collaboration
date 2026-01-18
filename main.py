import logging
import multiprocessing

from core.bank import Bank
from logger.configure import configure_logger_queue, add_queue_handler_to_root
from config import ConfigurationManager


if __name__ == "__main__":

    multiprocessing.freeze_support()

    log_queue, listener = configure_logger_queue()
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

        #open bank here
    except KeyboardInterrupt:
        exit(1)

    finally:
        listener.stop()
