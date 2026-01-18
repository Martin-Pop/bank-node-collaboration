import logging
import sqlite3
import threading
import multiprocessing.managers as managers


class BankCacheStorage:
    def __init__(self, shared_memory: managers.DictProxy):
        self._shared_memory = shared_memory


class BankPersistentStorage:

    def __init__(self, file_path, timeout):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(self._file_path, check_same_thread=False, timeout=timeout)

    def create_account(self):
        raise NotImplementedError()

    def remove_account(self):
        raise NotImplementedError()

    def deposit(self):
        raise NotImplementedError()

    def withdraw(self):
        raise NotImplementedError()

    def close(self):
        if self._connection:
            self._connection.close()

def load_data_to_shared_memory(file_path: str, shared_memory: managers.DictProxy) -> bool:
    log = logging.getLogger("SYSTEM")
    conn = None
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("select account_number, balance from accounts")
        rows = cursor.fetchall()

        if not rows:
            log.warning("Database does not contain any data.")
            return True

        shared_memory.update(dict(rows))
        log.info(f"Shared memory has been loaded")
        return True

    except sqlite3.Error as e:
        log.critical(f"Could not load data into shared memory: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def prepare_storage_structure(file_path: str) -> bool:
    log = logging.getLogger("SYSTEM")
    conn = None
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0
                )
            """)

        conn.commit()
        log.info(f"Database storage structure is ready.")
        return True

    except sqlite3.Error as e:
        log.critical(f"Could not create database structure: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
