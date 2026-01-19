import logging
import socket
from multiprocessing import Queue, Manager

from commands.commands import BankCodeCommand
from commands.contexts import BankCodeContext
from commands.factory import CommandFactory
from bank.gateway import Gateway
from bank.storages import BankCacheStorage, BankPersistentStorage, prepare_storage_structure, load_data_to_shared_memory
from workers.worker_manager import WorkerManager

log = logging.getLogger("BANK")


class Bank:
    def __init__(self, config: dict, log_queue: Queue):
        self._config = config
        self._log_queue = log_queue

        manager = Manager()
        shared_memory = manager.dict()

        self._cache_storage = BankCacheStorage(shared_memory)
        self._persistent_storage = BankPersistentStorage(self._config["storage"], self._config["storage_timeout"])
        self._gateway = Gateway(self._config["host"], self._config["port"])
        self._command_factory = self._create_command_factory()
        self._worker_manager = WorkerManager(self._config, self._log_queue, self._cache_storage, self._command_factory)

        success = prepare_storage_structure(self._config["storage"])
        if not success:
            exit(1)

        success = load_data_to_shared_memory(self._config["storage"], shared_memory)
        if not success:
            exit(1)

        log.info("Bank initialized")

    def open_bank(self):
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

    def _create_command_factory(self):
        factory = CommandFactory()

        bank_code_context = BankCodeContext("FAKE_BANK_CODE_FOR_NOW")
        factory.register("BC", BankCodeCommand, bank_code_context)

        return factory