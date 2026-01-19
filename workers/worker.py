import logging
import sqlite3
from dataclasses import dataclass
from multiprocessing import Queue, Process
from multiprocessing.connection import PipeConnection

from commands.factory import CommandFactory
from core.client import ClientConnection, ClientContext
from core.storages import BankCacheStorage, BankPersistentStorage
from logger.configure import add_queue_handler_to_root


@dataclass
class WorkerContext:
    log_queue: Queue
    bank_cache: BankCacheStorage
    pipe: PipeConnection
    config: dict
    factory: CommandFactory


class Worker(Process):

    def __init__(self, worker_context: WorkerContext):
        super().__init__()

        self._log_queue = worker_context.log_queue
        self._bank_cache = worker_context.bank_cache
        self._pipe = worker_context.pipe
        self._configuration = worker_context.config
        self._factory = worker_context.factory

        self._storage = None
        self._log = None

    def run(self):

        add_queue_handler_to_root(self._log_queue)
        self._log = logging.getLogger(f"WORKER-{self.pid}")

        try:
            self._storage = BankPersistentStorage(self._configuration["storage"], self._configuration["storage_timeout"])
        except sqlite3.Error as e:
            self._log.error(f"Worker could not connect to storage: {e}")
            return

        self._log.info(f"Worker {self.pid} started")

        try:
            self._accept_clients()
        except Exception as e:
            self._log.error(e)
        finally:
            self._storage.close()


    def _accept_clients(self):
        while True:
            try:
                client_socket = self._pipe.recv()

                # None closes worker
                if client_socket is None:
                    break

                context = ClientContext(
                    socket=client_socket,
                    config=self._configuration,
                    factory=self._factory
                )

                client = ClientConnection(context)
                client.start()

            except KeyboardInterrupt:
                break