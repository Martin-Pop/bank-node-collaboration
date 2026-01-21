import logging
import socket
from multiprocessing import Queue, Manager
from bank.gateway import Gateway
from bank.storages import prepare_storage_structure, load_data_to_shared_memory
from workers.worker_manager import WorkerManager

log = logging.getLogger("BANK")


class Bank:
    """
    Main bank class
    """
    def __init__(self, config: dict, log_queue: Queue):
        self._config = config
        self._log_queue = log_queue

        manager = Manager()
        shared_memory = manager.dict()
        shared_lock = manager.Lock()

        self._gateway = Gateway(self._config["host"], self._config["port"])
        self._worker_manager = WorkerManager(self._config, self._log_queue, shared_memory, shared_lock)

        success = prepare_storage_structure(self._config["storage"])
        if not success:
            exit(1)

        success = load_data_to_shared_memory(self._config["storage"], shared_memory)
        if not success:
            exit(1)

        log.info("Bank initialized")

    def open_bank(self):
        """
        Bank gets open by accepting clients from gateway (main loop).
        """
        try:
            self._worker_manager.create_workers()
            self._worker_manager.start_workers()

            server_socket = self._gateway.open()
            self._start_listening_for_clients(server_socket)
        except BaseException as e:  # fallback
            log.critical(e)

    def _start_listening_for_clients(self, server_socket: socket.socket):
        while True:
            client_socket, client_address = server_socket.accept()

            # security here
            self._worker_manager.distribute_socket(client_socket)