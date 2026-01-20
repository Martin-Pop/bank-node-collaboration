import logging
from threading import Thread
from dataclasses import dataclass
import socket

from commands.factory import CommandFactory
from commands.parser import parse_command, is_command_for_us

log = logging.getLogger('WORKER')

@dataclass
class ClientContext:
    socket: socket.socket
    config: dict
    factory: CommandFactory

class ClientConnection(Thread):

    def __init__(self, context: ClientContext):
        super().__init__()

        self._socket = context.socket
        self._configuration = context.config
        self._factory = context.factory

        self.daemon = True

    def run(self):
        try:
            self._socket.settimeout(60)  # load this

            while True:
                data = self._socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()
                if not message:
                    continue

                code, args = parse_command(message)
                is_for_our_bank = is_command_for_us(self._configuration['bank_code'] , args[0] if args else None)

                if is_for_our_bank:
                    try:
                        cmd = self._factory.create(code, *args)
                        if cmd is None:
                            response = "ER Invalid command"
                        else:
                            response = cmd.execute()
                    except TypeError: # when not enough args are passed
                        response = "ER invalid arguments"
                else:
                    #TODO: add relaying
                    response = "RELAYING"

                self._socket.sendall(f"{response}\r\n".encode('utf-8'))

        except socket.timeout:
            log.warning("Client timed out.")
        except ConnectionResetError:
            log.warning("Client connection reset.")
        except Exception as e:
            log.error(f"Error handling client: {e}", exc_info=True)
        finally:
            self._close_connection()

    def _close_connection(self):
        try:
            self._socket.close()
            log.info("Connection closed.")
        except Exception:
            pass