import logging
import socket

log = logging.getLogger("NETWORK")


class BankConnector:
    """
    Handles connection to other banks in P2P network
    """

    def __init__(self, timeout: float = 5.0):
        self._timeout = timeout

    def send_command(self, bank_ip: str, port: int, command: str) -> str | None:
        """
        Sends command to another bank and returns response
        :param bank_ip: IP address of target bank
        :param port: Port of target bank
        :param command: Command to send
        :return: Response string or None if failed
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect((bank_ip, port))

            sock.sendall(f"{command}\r\n".encode('utf-8'))

            response = sock.recv(1024).decode('utf-8').strip()

            return response

        except socket.timeout:
            log.warning(f"Timeout connecting to {bank_ip}:{port}")
            return None
        except socket.error as e:
            log.warning(f"Connection error to {bank_ip}:{port}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error communicating with {bank_ip}:{port}: {e}")
            return None
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    def get_bank_code(self, bank_ip: str, port: int) -> str | None:
        """
        Gets bank code (BC command) from another bank
        :param bank_ip: IP address of target bank
        :param port: Port of target bank
        :return: Bank code or None
        """
        response = self.send_command(bank_ip, port, "BC")
        if response and response.startswith("BC "):
            return response[3:].strip()
        return None

    def get_bank_amount(self, bank_ip: str, port: int) -> int | None:
        """
        Gets total amount in bank (BA command)
        :param bank_ip: IP address of target bank
        :param port: Port of target bank
        :return: Total amount or None
        """
        response = self.send_command(bank_ip, port, "BA")
        if response and response.startswith("BA "):
            try:
                return int(response[3:].strip())
            except ValueError:
                return None
        return None

    def get_client_count(self, bank_ip: str, port: int) -> int | None:
        """
        Gets number of clients in bank (BN command)
        :param bank_ip: IP address of target bank
        :param port: Port of target bank
        :return: Client count or None
        """
        response = self.send_command(bank_ip, port, "BN")
        if response and response.startswith("BN "):
            try:
                return int(response[3:].strip())
            except ValueError:
                return None
        return None