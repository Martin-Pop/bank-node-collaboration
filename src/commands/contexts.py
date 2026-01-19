from dataclasses import dataclass

from bank.storages import BankCacheStorage, BankPersistentStorage


@dataclass
class CommandContext:
    pass


@dataclass
class BankCodeContext(CommandContext):
    bank_code: str  # ip address


@dataclass
class StorageContext(CommandContext):
    bank_code: str
    storage: BankPersistentStorage
    cache: BankCacheStorage
