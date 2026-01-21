import logging
import sqlite3
from dataclasses import dataclass
from multiprocessing import Queue, Process, managers
from multiprocessing.connection import PipeConnection
from typing import Any

from commands.commands import (
BankCodeCommand, CreateAccountCommand, RemoveAccountCommand,
AccountDepositCommand, AccountWithdrawCommand, AccountBalanceCommand,
BankAmountCommand, BankNumberCommand)

from commands.contexts import BankCodeContext, StorageContext
from commands.factory import CommandFactory

from bank.client import ClientConnection, ClientContext
from bank.storages import BankStorage
from logger.configure import add_queue_handler_to_root


@dataclass
class WorkerContext:
    log_queue: Queue
    shared_memory: managers.DictProxy
    pipe: PipeConnection
    config: dict
    lock: Any #AcquirerProxy - dynamically generated class ?


class Worker(Process):
    """
    Worker process
    """

    def __init__(self, worker_context: WorkerContext):
        super().__init__()

        self._log_queue = worker_context.log_queue
        self._cache = worker_context.shared_memory
        self._pipe = worker_context.pipe
        self._configuration = worker_context.config
        self._lock = worker_context.lock

        self._factory = None
        self._storage = None
        self._log = None

    def run(self):
        """
        Called when .start() is called.
        Initializes storage and starts accepting sockets.
        """

        add_queue_handler_to_root(self._log_queue)
        self._log = logging.getLogger(f"WORKER-{self.pid}")

        try:
            self._storage = BankStorage(self._configuration["storage"], self._configuration["storage_timeout"], self._cache, self._lock)
            self._factory = self._init_command_factory()
        except sqlite3.Error as e:
            self._log.critical(f"Worker could not connect to storage: {e}")
            return
        except Exception as e:
            self._log.critical(f"Failed to create command factory: {e}")
            return

        self._log.info(f"Worker {self.pid} started")

        try:
            self._accept_clients()
        except Exception as e:
            self._log.error(e)
        finally:
            self._storage.close()

    def _init_command_factory(self):
        """
        Initializes command factory
        Factory is created here because some commands need storage context, which contains lock, which is unpickable
        :return: new factory
        """
        factory = CommandFactory()

        bank_code = self._configuration['bank_code']

        bank_code_context = BankCodeContext(bank_code)
        factory.register("BC", BankCodeCommand, bank_code_context)

        storage_context = StorageContext(bank_code, self._storage)
        factory.register("AC", CreateAccountCommand, storage_context)
        factory.register("AR", RemoveAccountCommand, storage_context)
        factory.register("AD", AccountDepositCommand, storage_context)
        factory.register("AW", AccountWithdrawCommand, storage_context)
        factory.register("AB", AccountBalanceCommand, storage_context)
        factory.register("BA", BankAmountCommand, storage_context)
        factory.register("BN", BankNumberCommand, storage_context)

        return factory

    def _accept_clients(self):
        """
        Accepts sockets from one side of the pipe, For every socket it starts a new client thread.
        """
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
