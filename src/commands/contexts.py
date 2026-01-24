from dataclasses import dataclass

from bank.storages import BankStorage


@dataclass
class CommandContext:
    """
    Base command context class, made just for IDE typing
    """
    pass


@dataclass
class BankCodeContext(CommandContext):
    bank_code: str  # ip address


@dataclass
class StorageContext(CommandContext):
    bank_code: str
    storage: BankStorage

@dataclass
class NetworkContext(CommandContext):
    our_ip: str
    scanner: 'NetworkScanner'
