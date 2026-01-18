from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import  Any, Tuple, Generic, TypeVar


@dataclass
class CommandContext:
    pass


T = TypeVar('T', bound=CommandContext)


class Command(ABC, Generic[T]):
    def __init__(self, code: str, context: T):
        self._code = code
        self._context = context

    @property
    def code(self) -> str:
        return self._code

    @abstractmethod
    def execute(self, args: Tuple) -> str:
        pass

    def _success_response(self, message: str) -> str:
        return f"{self._code} {message}"

    def _error_response(self, message: str) -> str:
        return f"ER {message}"


@dataclass
class BankCodeContext(CommandContext):
    bank_code: str


class BankCodeCommand(Command[BankCodeContext]):

    def execute(self, args: Tuple) -> str:
        return self._success_response(self._context.bank_code)


@dataclass
class AccountCreateContext(CommandContext):
    storage: Any

class AccountCreateCommand(Command[AccountCreateContext]):
    pass


