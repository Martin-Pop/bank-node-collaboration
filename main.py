import logging

from logger.configure import configure_logger_queue, add_queue_handler_to_root
from logger.types import LOG_TYPES
from config import ConfigurationManager

if __name__ == "__main__":

    log_queue, listener = configure_logger_queue()
    add_queue_handler_to_root(log_queue)
    listener.start()

    log = logging.getLogger(LOG_TYPES.SYSTEM)

    config_manager = ConfigurationManager("config/config.json")
    config = config_manager.get_config()
    if not config:
        exit(1)

    log.info('Configuration loaded')
    listener.stop()
