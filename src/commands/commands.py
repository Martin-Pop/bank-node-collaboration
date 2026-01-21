from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from commands.contexts import CommandContext, BankCodeContext, StorageContext
from commands.parser import parse_address

T = TypeVar('T', bound=CommandContext)

class BaseCommand(ABC, Generic[T]):
    """
    Base command class
    """
    def __init__(self, code: str, context: T):
        self._code = code
        self._context = context

    @property
    def code(self) -> str:
        return self._code

    @abstractmethod
    def execute(self) -> str:
        """
        Execute the command
        :return: always returns result message
        """
        pass

    def _success_response(self, message: str | None = None ) -> str:
        """
        Success response
        :param message: message to add
        :return: new successful response
        """
        if not message:
            return self._code
        return f"{self._code} {message}"

    def _error_response(self, message: str) -> str:
        """
        Error response
        :param message: message to add
        :return: new error response
        """
        return f"ER {message}"


class BankCodeCommand(BaseCommand[BankCodeContext]):
    """
    Bank code command, just returns our bank code.
    """

    def execute(self) -> str:
        return self._success_response(self._context.bank_code)

class CreateAccountCommand(BaseCommand[StorageContext]):
    """
    Command to create a new account
    """

    def execute(self) -> str:
        account = self._context.storage.create_account()
        if account:
            return self._success_response(f"{account}/{self._context.bank_code}")
        else:
            return self._error_response("Failed to create account, try again later")

class RemoveAccountCommand(BaseCommand[StorageContext]):
    """
    Command to remove an account
    """

    def __init__(self, code: str, context: StorageContext, account_number: str):
        super().__init__(code, context)
        self._account_number = account_number

    def execute(self) -> str:
        message = self._context.storage.remove_account(self._account_number)
        if message:
            return self._error_response(message)
        return self._success_response()

class AccountDepositCommand(BaseCommand[StorageContext]):
    """
    Deposits money into an account
    """

    def __init__(self, code: str, context: StorageContext, account_address: str, value: str):
        super().__init__(code, context)
        try:
            self._value = int(value)

            account, _ = parse_address(account_address)
            if account:
                self._account_number = account
            else: raise ValueError
        except ValueError:
            self._value = None
            self._account_number = None

    def execute(self) -> str:
        if self._value is None or self._account_number is None:
            return self._error_response("Invalid parameters")

        message = self._context.storage.deposit(self._account_number, self._value)
        if message:
            return self._error_response(message)
        return self._success_response()


class AccountWithdrawCommand(BaseCommand[StorageContext]):
    """
    Withdraws money from an account
    """

    def __init__(self, code: str, context: StorageContext, account_address: str, value: str):
        super().__init__(code, context)
        try:
            self._value = int(value)

            account, _ = parse_address(account_address)
            if account:
                self._account_number = account
            else:
                raise ValueError
        except ValueError:
            self._value = None
            self._account_number = None

    def execute(self) -> str:
        if self._value is None or self._account_number is None:
            return self._error_response("Invalid parameters")

        message = self._context.storage.withdraw(self._account_number, self._value)
        if message:
            return self._error_response(message)

        return self._success_response()


class AccountBalanceCommand(BaseCommand[StorageContext]):
    """
    Gets account balance
    """

    def __init__(self, code: str, context: StorageContext, account_address: str):
        super().__init__(code, context)
        try:
            account, _ = parse_address(account_address)
            if account:
                acc_num = int(account)
                if 10000 <= acc_num <= 99999:
                    self._account_number = account
                else:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            self._account_number = None

    def execute(self) -> str:
        if self._account_number is None:
            return self._error_response("Invalid account number format")

        balance = self._context.storage.get_balance(self._account_number)
        if balance is None:
            return self._error_response("Account not found")
        return self._success_response(str(balance))


class BankAmountCommand(BaseCommand[StorageContext]):
    """
    Gets total amount in bank
    """

    def execute(self) -> str:
        total = self._context.storage.get_total_amount()
        return self._success_response(str(total))


class BankNumberCommand(BaseCommand[StorageContext]):
    """
    Gets number of clients
    """

    def execute(self) -> str:
        count = self._context.storage.get_client_count()
        return self._success_response(str(count))
