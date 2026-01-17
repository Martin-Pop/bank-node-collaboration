import logging
import sys
from logging.handlers import QueueListener, QueueHandler
from multiprocessing import Queue

LOG_FORMAT = "%(asctime)s | P:%(process)d | %(name)-10s | %(levelname)-8s | %(message)s"


def configure_logger_queue(file_path: str = 'app.log', suppress_console: bool = False) -> tuple:
    """
    Configures logger handlers for queue logging (QueueListener, QueueHandler)
    :param file_path: log file path
    :param suppress_console: Disables console if True
    :return: multiprocessing queue and QueueListener
    """

    formatter = logging.Formatter(LOG_FORMAT)

    # FILE
    file_handler = logging.FileHandler(file_path, encoding="utf-8", mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # CONSOLE
    if not suppress_console:

        console_info_handler = logging.StreamHandler(sys.stdout)
        console_info_handler.setLevel(logging.INFO)
        console_info_handler.setFormatter(formatter)

        handlers = (file_handler, console_info_handler)
    else:
        handlers = (file_handler,)

    log_queue = Queue()
    listener = QueueListener(log_queue, *handlers, respect_handler_level=True)

    return log_queue, listener


def add_queue_handler_to_root(queue: Queue) -> None:
    """
    Adds queue to QueueHandler for root logger
    This function is called from processes.
    :param queue: queue through which logs are connected to the same listener
    """
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    root.addHandler(QueueHandler(queue))
