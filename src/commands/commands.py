from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from commands.contexts import CommandContext, BankCodeContext, StorageContext

T = TypeVar('T', bound=CommandContext)

class BaseCommand(ABC, Generic[T]):
    def __init__(self, code: str, context: T):
        self._code = code
        self._context = context

    @property
    def code(self) -> str:
        return self._code

    @abstractmethod
    def execute(self) -> str:
        pass

    def _success_response(self, message: str | None = None ) -> str:
        if not message:
            return self._code
        return f"{self._code} {message}"

    def _error_response(self, message: str) -> str:
        return f"ER {message}"


class BankCodeCommand(BaseCommand[BankCodeContext]):

    def execute(self) -> str:
        return self._success_response(self._context.bank_code)

class CreateAccountCommand(BaseCommand[StorageContext]):

    def execute(self) -> str:
        account = self._context.storage.create_account()
        if account:
            return self._success_response(f"{account}/{self._context.bank_code}")
        else:
            return self._error_response("Failed to create account, try again later")

class RemoveAccountCommand(BaseCommand[StorageContext]):

    def __init__(self, code: str, context: StorageContext, account_number: str):
        super().__init__(code, context)
        self._account_number = account_number

    def execute(self) -> str:
        message = self._context.storage.remove_account(self._account_number)
        if message:
            return self._error_response(message)
        return self._success_response()




