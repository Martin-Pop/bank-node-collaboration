from commands.commands import BaseCommand
from commands.contexts import CommandContext
from typing import Type


class CommandFactory:
    """
    Command factory, creates new command objects from registered commands
    """
    def __init__(self):
        """
        stores commands in this format:
        {"code" : (command_class, command_context), ...}
        """
        self._commands = {}

    def register(self, code: str, command_class: Type[BaseCommand], context: CommandContext):
        """
        Registers a new command
        :param code: command code
        :param command_class: command class
        :param context: commands context
        """
        if code not in self._commands:
            self._commands[code] = (command_class, context)

    def create(self, code: str, *args) -> BaseCommand | None:
        """
        Creates a new command, passes in stored context and other arguments
        :param code: code to determine which command to create
        :param args: other arguments to pass in command
        :return: new command object if command with this code is registered
        """
        if code in self._commands:
            cmd_class, context = self._commands[code]
            return cmd_class(code, context, *args)
        return None
