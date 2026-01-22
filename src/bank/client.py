import logging
import time
from threading import Thread
from dataclasses import dataclass
import socket
from multiprocessing import Value

from bank.security import SecurityGuard
from commands.factory import CommandFactory
from commands.parser import parse_command, is_command_for_us

log = logging.getLogger('WORKER')

@dataclass
class ClientContext:
    socket: socket.socket
    config: dict
    factory: CommandFactory
    active_connections: Value
    security: SecurityGuard

class ClientConnection(Thread):
    """
    Client class (thread)
    """

    def __init__(self, context: ClientContext):
        super().__init__()

        self._socket = context.socket
        self._configuration = context.config
        self._factory = context.factory
        self._active_connections = context.active_connections
        self._security = context.security

        self._MAX_RPM = self._configuration['max_requests_per_minute']
        self._MAX_BAD_COMMANDS = self._configuration['max_bad_commands']

        self.daemon = True

    def run(self):
        """
        Main client loop, handles data received from socket
        """
        try:
            ip_address, port = self._socket.getpeername()
        except OSError:
            log.warning("Client disconnected before handling started.")
            return

        request_timestamps = []
        bad_commands_count = 0

        with self._active_connections.get_lock():
            self._active_connections.value += 1

        try:
            client_timeout = self._configuration.get('client_timeout', 5)
            self._socket.settimeout(client_timeout)

            while True:
                data = self._socket.recv(1024)
                if not data:
                    break

                if self._security.is_banned(ip_address):
                    self._socket.sendall("ER Banned\r\n".encode('utf-8'))
                    break

                now = time.time()
                request_timestamps = [t for t in request_timestamps if t > now - 60]
                request_timestamps.append(now)

                if len(request_timestamps) > self._MAX_RPM:
                    self._security.ban_ip(ip_address)
                    self._socket.sendall("ER Rate limit exceeded\r\n".encode('utf-8'))
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
                            bad_commands_count += 1
                        else:
                            response = cmd.execute()
                            bad_commands_count = max(0, bad_commands_count - 1)

                    except TypeError:
                        response = "ER invalid arguments"
                        bad_commands_count += 1

                    except ValueError:
                        response = "ER argument value error"
                        bad_commands_count += 1
                else:
                    #TODO: add relaying
                    response = "RELAYING"

                if bad_commands_count >= self._MAX_BAD_COMMANDS:
                    self._security.ban_ip(ip_address)
                    self._socket.sendall("ER Too many errors. \r\n".encode('utf-8'))
                    break

                self._socket.sendall(f"{response}\r\n".encode('utf-8'))

        except socket.timeout:
            log.warning("Client timed out.")
        except ConnectionResetError:
            log.warning("Client connection reset.")
        except Exception as e:
            log.error(f"Error handling client: {e}", exc_info=True)
        finally:
            with self._active_connections.get_lock():
                self._active_connections.value -= 1
            self._close_connection()

    def _close_connection(self):
        """
        Close the socket connection
        """
        try:
            self._socket.close()
            log.info("Connection closed.")
        except Exception:
            pass