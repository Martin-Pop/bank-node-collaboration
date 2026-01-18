from commands.commands import Command

def parse_command(message: str):
    parts = message.strip().split()
    if not parts:
        return 'ER', ()

    return parts[0], tuple(parts[1:])


class CommandFactory:
    def __init__(self, default_command: Command):
        self._default_code = default_command.code
        self._commands = {
            self._default_code: default_command,
        }

    def register(self, command: Command):
        if command.code not in self._commands:
            self._commands[command.code] = command

    def create_command(self, code: str) -> Command:
        return self._commands.get(code, self._commands[self._default_code])