from commands.commands import BaseCommand
from commands.contexts import CommandContext
from typing import Type


def parse_command(message: str):
    parts = message.strip().split()
    if not parts:
        return 'ER', ()

    return parts[0], tuple(parts[1:])


class CommandFactory:
    def __init__(self):
        """
        stores commands in this format:
        {"code" : (command_class, command_context), ...}
        """
        self._commands = {}

    def register(self, code: str, command_class: Type[BaseCommand], context: CommandContext):
        if code not in self._commands:
            self._commands[code] = (command_class, context)

    def create(self, code: str, *args) -> BaseCommand | None:
        if code in self._commands:
            cmd_class, context = self._commands[code]
            return cmd_class(code, context, *args)
        return None
