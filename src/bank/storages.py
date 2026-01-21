import logging
import sqlite3
import random
import multiprocessing.managers as managers

log = logging.getLogger("STORAGE")
BOTTOM_ACCOUNT_NUMBER = 10_000
TOP_ACCOUNT_NUMBER = 99_999
MAX_ENTRIES = 5


class BankStorage:
    """
    Main storage for data
    """

    def __init__(self, file_path, timeout, shared_cache: managers.DictProxy, shared_lock):
        self._file_path = file_path
        self._lock = shared_lock
        self._connection = sqlite3.connect(self._file_path, check_same_thread=False, timeout=timeout)
        self._cache = shared_cache


    def create_account(self) -> str | None:

        for _ in range(MAX_ENTRIES):
            candidate = str(random.randint(BOTTOM_ACCOUNT_NUMBER, TOP_ACCOUNT_NUMBER))

            try:
                with self._connection:
                    self._connection.execute("insert into accounts (account_number) values (?)", (candidate,))

                account_number = candidate

                with self._lock:
                    self._cache[account_number] = 0

                return account_number

            except sqlite3.IntegrityError:
                log.warning(f"Collision detected for {candidate}")
                continue
            except Exception as e:
                log.error(f"Error while creating account: {e}")
                break

        return None

    def remove_account(self, account_number: str) -> str:
        try:
            with self._connection:
                cursor = self._connection.execute("delete from accounts where account_number = ?", (account_number,))

            if cursor.rowcount > 0:
                with self._lock:
                    self._cache.pop(account_number, None)
                return ''

        except Exception as e:
            log.error(f"Error while removing account: {e}")
            return "Error while removing account"

        return "Account not found"

    def deposit(self, account_number: str, value: int) -> str:
        try:
            with self._connection:
                cursor = self._connection.execute(
                    "update accounts set balance = balance + ? where account_number = ?", (value, account_number))

            if cursor.rowcount > 0:
                with self._lock:
                    if account_number in self._cache:
                        self._cache[account_number] += value
                return ''

        except Exception as e:
            log.error(f"Error while depositing: {e}")
            return "Error while depositing"

        return "Invalid account number"

    def withdraw(self, account_number: str, value: int) -> str:
        try:
            with self._connection:
                cursor = self._connection.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE account_number = ? AND balance >= ?",
                    (value, account_number, value)
                )

            if cursor.rowcount > 0:
                with self._lock:
                    if account_number in self._cache:
                        self._cache[account_number] -= value
                return ''
            else:
                cursor = self._connection.execute("SELECT 1 FROM accounts WHERE account_number = ?", (account_number,))
                if not cursor.fetchone():
                    return "Account not found"
                return "Lack of funds"

        except Exception as e:
            log.error(f"Error: {e}")
            return "Database error"

    def get_balance(self, account_number: str) -> int | None:
        """
        Gets account balance directly from shared cache.
        """
        with self._lock:
            return self._cache.get(account_number)

    def get_total_amount(self) -> int:
        """
        Gets total amount in all accounts
        :return: total amount
        """
        try:
            cursor = self._connection.execute("SELECT SUM(balance) FROM accounts")
            result = cursor.fetchone()[0]
            return result if result else 0
        except Exception as e:
            log.error(f"Error getting total amount: {e}")
            return 0

    def get_client_count(self) -> int:
        """
        Gets number of clients (accounts)
        :return: client count
        """
        try:
            cursor = self._connection.execute("SELECT COUNT(*) FROM accounts")
            return cursor.fetchone()[0]
        except Exception as e:
            log.error(f"Error getting client count: {e}")
        return 0

    def close(self):
        """
        Closes storage (connection to db)
        """
        if self._connection:
            self._connection.close()


def load_data_to_shared_memory(file_path: str, shared_memory: managers.DictProxy) -> bool:
    """
    Loads data from sqlite database into provided shared dictionary
    :param file_path: database filepath
    :param shared_memory: shared memory object
    :return: true if successfully loaded
    """
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
    """
    Prepares storage structure (db structure)
    :param file_path: database filepath
    :return: true if successfully created
    """
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