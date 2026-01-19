from dataclasses import dataclass

@dataclass
class CommandContext:
    pass

@dataclass
class BankCodeContext(CommandContext):
    bank_code: str #ip address
