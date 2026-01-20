import logging
import sqlite3
import threading
import random
import multiprocessing.managers as managers

log = logging.getLogger("STORAGE")
BOTTOM_ACCOUNT_NUMBER = 10_000
TOP_ACCOUNT_NUMBER = 99_999
MAX_ENTRIES = 5

class BankCacheStorage:
    def __init__(self, shared_memory: managers.DictProxy):
        self._shared_memory = shared_memory

    def update(self, account_number: int, value: int) -> None:
        self._shared_memory[account_number] = value


class BankStorage:

    def __init__(self, file_path, timeout, shared_cache: managers.DictProxy):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(self._file_path, check_same_thread=False, timeout=timeout)
        self._cache = shared_cache

    def _update_cache(self, account_number: str, value: int) -> None:
        self._cache[account_number] = value

    def create_account(self) -> str | None:

        account_number = None

        with self._lock:
            for _ in range(MAX_ENTRIES):
                candidate = str(random.randint(BOTTOM_ACCOUNT_NUMBER, TOP_ACCOUNT_NUMBER))

                try:
                    with self._connection:
                        self._connection.execute("insert into accounts (account_number) values (?)", (candidate,))

                        account_number = candidate
                        self._update_cache(account_number, 0)
                        break
                except sqlite3.IntegrityError:
                    log.warning(f"Collision detected for {candidate}")
                    continue
                except Exception as e:
                    log.error(f"Error while creating account: {e}")
                    break

        return account_number

    def remove_account(self, account_number: str) -> str:
        with self._lock:
            try:
                with self._connection:
                    cursor = self._connection.execute("delete from accounts where account_number = ?", (account_number,))

                if cursor.rowcount > 0:
                    self._cache.pop(account_number, None)
                    return ''
            except Exception as e:
                log.error(f"Error while removing account: {e}")
                return "Error while removing account"

        return "Account not found"

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
        log.info(shared_memory)
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
                    account_number TEXT PRIMARY KEY,
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
