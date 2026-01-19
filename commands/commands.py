from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from commands.contexts import CommandContext, BankCodeContext

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

    def _success_response(self, message: str) -> str:
        return f"{self._code} {message}"

    def _error_response(self, message: str) -> str:
        return f"ER {message}"


class BankCodeCommand(BaseCommand[BankCodeContext]):

    def execute(self) -> str:
        return self._success_response(self._context.bank_code)



