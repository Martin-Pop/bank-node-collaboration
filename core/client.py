import logging
from threading import Thread
from dataclasses import dataclass
import socket

log = logging.getLogger('WORKER')

@dataclass
class ClientContext:
    socket: socket.socket
    config: dict
    parser: None
    executor: None

class ClientConnection(Thread):

    def __init__(self, context: ClientContext):
        super().__init__()

        self._socket = context.socket
        self._configuration = context.config

        self._command_parser = context.parser
        self._command_executor = context.executor

        self.daemon = True

    def run(self):
        try:
            self._socket.settimeout(5)  # load this

            while True:
                data = self._socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()
                if not message:
                    continue

                response = 'Hi'

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