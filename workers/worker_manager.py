import socket
from multiprocessing import Queue, Pipe

from core.storages import BankCacheStorage
from workers.worker import WorkerContext, Worker


class WorkerManager:

    def __init__(self, config: dict, log_queue: Queue, bank_cache_storage: BankCacheStorage):

        self._config = config
        self._worker_count = config["bank_workers"]
        self._log_queue = log_queue
        self._bank_cache_storage = bank_cache_storage

        self._workers = []
        self._worker_pipes = []
        self._worker_index = 0

    def create_workers(self):

        for _ in range(self._worker_count):
            parent_connection, child_connection = Pipe()

            context = WorkerContext(
                bank_cache=self._bank_cache_storage,
                log_queue=self._log_queue,
                pipe=child_connection,
                config=self._config
            )

            worker = Worker(context)
            self._workers.append(worker)
            self._worker_pipes.append(parent_connection)

    def start_workers(self):
        for worker in self._workers:
            worker.start()

    def distribute_socket(self, client_socket: socket.socket):
        try:
            self._worker_pipes[self._worker_index].send(client_socket)
        finally:
            client_socket.close()
