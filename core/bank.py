import logging
import socket
from multiprocessing import Queue, Manager

from core.gateway import Gateway
from core.storages import BankCacheStorage, BankPersistentStorage
from workers.worker_manager import WorkerManager

log = logging.getLogger("BANK")

class Bank:
    def __init__(self, config: dict, log_queue: Queue):
        self._config = config
        self._log_queue = log_queue

        manager = Manager()
        shared_memory = manager.dict()

        self._cache_storage = BankCacheStorage(shared_memory)
        self._persistent_storage = BankPersistentStorage(self._config["storage"], self._config["storage"])

        self._gateway = Gateway(self._config["host"], self._config["port"])
        self._worker_manager = WorkerManager()


    def open_bank(self):
        # 1. check persistent storage
        # 2. load cache storage
        # 3. initialize workers through worker manager
        # 4. open gateway
        # 5. listen for clients and pass them to worker manager

        self._worker_manager.start_workers()

        server_socket = self._gateway.open()
        self._start_listening_for_clients(server_socket)

    def _start_listening_for_clients(self, server_socket: socket.socket):
        while True:
            client_socket, client_address = server_socket.accept()

            #security here



