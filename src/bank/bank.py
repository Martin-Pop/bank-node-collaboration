import logging
import socket
from multiprocessing import Queue, Manager
from bank.gateway import Gateway
from bank.storages import prepare_storage_structure, load_data_to_shared_memory, BankStorage
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

        self._shared_memory = shared_memory
        self._shared_lock = shared_lock
        self._storage = None

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
            self._storage = BankStorage(
                self._config["storage"],
                self._config["storage_timeout"],
                self._shared_memory,
                self._shared_lock
            )

            self._worker_manager.create_workers()
            self._worker_manager.start_workers()

            server_socket = self._gateway.open()
            self._start_listening_for_clients(server_socket)
        except BaseException as e:  # fallback
            log.critical(e)

    def close_bank(self):
        """
        Closes bank - stops workers, closes gateway and storage
        """
        log.info("Closing bank...")
        self._worker_manager.stop_workers()
        self._gateway.close()
        if self._storage:
            self._storage.close()
        log.info("Bank closed successfully")

    def _start_listening_for_clients(self, server_socket: socket.socket):
        while True:
            client_socket, client_address = server_socket.accept()

            # security here
            self._worker_manager.distribute_socket(client_socket)

    def get_stats(self) -> dict:
        """
        Gets bank statistics for monitoring
        :return: dictionary with bank stats
        """
        if not self._storage:
            return {
                "bank_code": self._config.get('bank_code', 'N/A'),
                "total_amount": 0,
                "client_count": 0,
                "active_connections": 0
            }

        return {
            "bank_code": self._config.get('bank_code', 'N/A'),
            "total_amount": self._storage.get_total_amount(),
            "client_count": self._storage.get_client_count(),
            "active_connections": self._worker_manager.get_active_connections_count()
        }

    def get_all_accounts(self) -> list:
        """
        Gets all accounts with their balances
        :return: list of dictionaries with account info
        """
        if not self._storage:
            return []

        accounts = []
        with self._shared_lock:
            for account_number, balance in self._shared_memory.items():
                accounts.append({
                    "account_number": account_number,
                    "bank_code": self._config.get('bank_code', 'N/A'),
                    "balance": balance
                })

        return accounts