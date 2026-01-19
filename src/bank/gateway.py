import logging
import socket

log = logging.getLogger("SYSTEM")

class Gateway:

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

        self._server_socket = None

    def open(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen()
        except socket.error as msg:
            log.error(msg)
            return None

        log.info(f"Server is listening at {self._host}:{self._port}")
        return self._server_socket

    def close(self):
        self._server_socket.close()