import logging
import socket
import time
from multiprocessing import Queue, Manager
from bank.gateway import Gateway
from bank.storages import prepare_storage_structure, load_data_to_shared_memory, BankStorage
from workers.worker_manager import WorkerManager

log = logging.getLogger("BANK")


class Bank:
    """
    Main bank class
    """
    def __init__(self, config: dict, log_queue: Queue, manager, security):
        self._config = config
        self._log_queue = log_queue
        self._shared_memory = manager.dict()
        self._shared_lock = manager.Lock()
        self._security = security

        self._gateway = Gateway(self._config["host"], self._config["port"])
        self._worker_manager = WorkerManager(
            self._config,
            self._log_queue,
            self._shared_memory,
            self._shared_lock,
            self._security
        )

        self._storage = None
        self._start_time = None

        success = prepare_storage_structure(self._config["storage_path"])
        if not success:
            exit(1)

        success = load_data_to_shared_memory(self._config["storage_path"], self._shared_memory)
        if not success:
            exit(1)

        log.info("Bank initialized")

    def open_bank(self):
        """
        Bank gets open by accepting clients from gateway (main loop).
        """
        try:
            self._storage = BankStorage(
                self._config["storage_path"],
                self._config["storage_timeout"],
                self._shared_memory,
                self._shared_lock
            )

            self._worker_manager.create_workers()
            self._worker_manager.start_workers()

            server_socket = self._gateway.open()
            if server_socket is None:
                raise Exception("Failed to open server socket. Gateway returned None.")

            self._start_time = time.time()
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
            try:
                client_socket, address = server_socket.accept()
                ip_address = address[0]

                if self._security.is_banned(ip_address):
                    log.warning(f"Connection rejected from banned IP: {ip_address}")
                    client_socket.close()
                    continue

                self._worker_manager.distribute_socket(client_socket)

            except OSError as e:
                if e.errno == 10038 or e.errno == 9:
                    log.info("Listener socket closed, stopping loop.")
                    break
                log.error(f"Listener socket error: {e}")
                break

            except Exception as e:
                log.error(f"Listener error: {e}")

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

    #deprecated
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

    def get_accounts_paged(self, offset: int, limit: int) -> list:
        """
        Gets a subset of accounts based on parameters,
        :param offset: number of items to skip
        :param limit: max number of items to return
        :return: list of dictionaries with account info
        """
        if not self._storage:
            return []

        with self._shared_lock:
            snapshot = list(self._shared_memory.items())

        snapshot.sort(key=lambda x: x[0])
        paged_items = snapshot[offset: offset + limit]

        accounts = []
        bank_code = self._config.get('bank_code', 'N/A')

        for account_number, balance in paged_items:
            accounts.append({
                "account_number": account_number,
                "bank_code": bank_code,
                "balance": balance
            })

        return accounts

    def get_accounts_count(self) -> int:
        """
        Gets the total number of active accounts.
        """
        if not self._storage:
            return 0

        with self._shared_lock:
            return len(self._shared_memory)

    def get_gateway_address(self) -> str:
        return self._config["host"] + ":" + str(self._config["port"])

    def get_start_time(self):
        return self._start_time