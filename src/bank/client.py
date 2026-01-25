import logging
import time
from threading import Thread
from dataclasses import dataclass
import socket
from multiprocessing import Value

from bank.security import SecurityGuard
from commands.factory import CommandFactory
from commands.parser import parse_command, is_command_for_us, parse_address
from network.connector import BankConnector

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

        self._connector = BankConnector(timeout=self._configuration.get('network_timeout', 5.0))

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

                is_for_our_bank = is_command_for_us(
                    self._configuration['host'],
                    args[0] if args else None
                )

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
                    response = self._handle_proxy_request(code, args)

                if bad_commands_count >= self._MAX_BAD_COMMANDS:
                    self._security.ban_ip(ip_address)
                    self._socket.sendall("ER Too many errors. \r\n".encode('utf-8'))
                    break

                self._socket.sendall(f"{response}\r\n".encode('utf-8'))

        except socket.timeout:
            pass #log.warning("Client timed out.")
        except ConnectionResetError:
            pass #log.warning("Client connection reset.")
        except Exception as e:
            log.error(f"Error handling client: {e}", exc_info=True)
        finally:
            with self._active_connections.get_lock():
                self._active_connections.value -= 1
            self._close_connection()

    def _handle_proxy_request(self, code: str, args: list) -> str:
        """
        Handles proxy requests by relaying commands to another bank.
        First tries a cached port if available, otherwise scans the configured range.
        :param code: Command code
        :param args: List of command arguments
        :return: Response string from the target bank or an error message
        """

        if code not in ['AD', 'AW', 'AB']:
            return "ER Command cannot be proxied"

        if not args:
            return "ER Missing arguments for proxy request"

        target_ip = args[0].split('/')[-1]
        original_message = f"{code} {' '.join(args)}".strip()

        scan_config = self._configuration.get('network_scan_port_range', [65525, 65535])
        port_range = range(scan_config[0], scan_config[1] + 1)

        cached_port = self._security.get_known_port(target_ip)
        ports_to_try = [cached_port] if cached_port else port_range

        for port in ports_to_try:
            log.debug(f"Relaying {code} to {target_ip}:{port}")
            response = self._connector.send_command(target_ip, port, original_message)

            if response and not response.startswith("ER"):
                self._security.save_known_port(target_ip, port)
                return response

            if cached_port and port == cached_port:
                return self._scan_ports_and_relay(target_ip, original_message)

        return "ER Target bank unreachable"

    def _scan_ports_and_relay(self, ip: str, message: str) -> str:
        """
        Scans a range of ports on a target IP and relays the message to the first responding port.
        :param ip: Target IP address to scan
        :param message: Full command message to relay
        :return: Response from the discovered bank or error if not found
        """

        scan_config = self._configuration.get('network_scan_port_range', [65525, 65535])
        for port in range(scan_config[0], scan_config[1] + 1):
            res = self._connector.send_command(ip, port, message)
            if res and not res.startswith("ER"):
                self._security.save_known_port(ip, port)
                return res
        return "ER Bank not found on any allowed port"

    def _close_connection(self):
        """
        Close the socket connection
        """
        try:
            self._socket.close()
            log.info("Connection closed.")
        except Exception:
            pass