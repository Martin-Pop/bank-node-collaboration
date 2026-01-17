import logging
from logger.configure import configure_logger_queue, add_queue_handler_to_root
from config import ConfigurationManager
from core.storages import prepare_storage_structure

if __name__ == "__main__":

    log_queue, listener = configure_logger_queue()
    add_queue_handler_to_root(log_queue)
    listener.start()

    log = logging.getLogger("SYSTEM")
    try:
        config_manager = ConfigurationManager("config/config.json")
        config = config_manager.get_config()
        if not config:
            exit(1)

        success = prepare_storage_structure(config["storage"])
        if not success:
            exit(1)

        #open bank here

    finally:
        listener.stop()
