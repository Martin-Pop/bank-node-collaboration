import socket
from multiprocessing import Queue, Pipe, managers

from workers.worker import WorkerContext, Worker


class WorkerManager:
    """
    Class that manages workers (Processes).
    """

    def __init__(self, config: dict, log_queue: Queue, shared_memory: managers.DictProxy):

        self._config = config
        self._worker_count = config["bank_workers"]
        self._log_queue = log_queue
        self._shared_memory = shared_memory

        self._workers = []
        self._worker_pipes = []
        self._worker_index = 0

    def create_workers(self):
        """
        Creates new workers. New pipe between is created that provides way to pass data.
        """

        for _ in range(self._worker_count):
            parent_connection, child_connection = Pipe()

            context = WorkerContext(
                shared_memory=self._shared_memory,
                log_queue=self._log_queue,
                pipe=child_connection,
                config=self._config,
            )

            worker = Worker(context)
            self._workers.append(worker)
            self._worker_pipes.append(parent_connection)

    def start_workers(self):
        """
        Starts all workers.
        """
        for worker in self._workers:
            worker.start()

    def stop_workers(self):
        """
        Stops all workers by sending None through the pipe.
        """
        for pipe in self._worker_pipes:
            pipe.send(None)

    def distribute_socket(self, client_socket: socket.socket):
        """
        Distributes socket between workers, socket in this process must be closed.
        :param client_socket: socket to distribute.
        """
        #Todo implement distribution
        try:
            self._worker_pipes[self._worker_index].send(client_socket)
        finally:
            client_socket.close()
