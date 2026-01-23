import logging
from dataclasses import dataclass
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from network.connector import BankConnector

log = logging.getLogger("NETWORK")


@dataclass
class BankInfo:
    """
    Information about discovered bank
    """

    ip: str
    port: int
    total_amount: int
    client_count: int


class NetworkScanner:
    """
    Scans P2P network for active banks
    """

    def __init__(self, port_range: tuple, timeout: float = 2.0, subnet: str = "10.1.2", security=None):
        """
        :param port_range: Tuple (min_port, max_port) to scan
        :param timeout: Connection timeout in seconds
        :param subnet: First 3 octets of IP to scan
        """
        self._port_range = port_range
        self._timeout = timeout
        self._subnet = subnet
        self._connector = BankConnector(timeout)
        self._security = security

    def scan_network(self, our_ip: str) -> List[BankInfo]:
        """
        Scans network for active banks
        :param our_ip: Our own IP to skip
        :return: List of discovered banks
        """
        banks = []

        ips_to_scan = [f"{self._subnet}.{i}" for i in range(1, 255)]

        ports_to_scan = range(self._port_range[0], self._port_range[1] + 1)

        targets = [(ip, port) for ip in ips_to_scan for port in ports_to_scan]

        log.info(f"Scanning {len(targets)} targets in subnet {self._subnet}.0/24")

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(self._check_target, ip, port, our_ip): (ip, port)
                for ip, port in targets
            }

            for future in as_completed(futures):
                result = future.result()
                if result:
                    banks.append(result)

        log.info(f"Found {len(banks)} active banks")
        return banks

    def _check_target(self, ip: str, port: int, our_ip: str) -> BankInfo | None:
        """
        Checks if target is an active bank
        :param ip: IP to check
        :param port: Port to check
        :param our_ip: Our own IP to skip
        :return: BankInfo if active bank, None otherwise
        """
        if ip == our_ip:
            return None

        try:
            bank_code = self._connector.get_bank_code(ip, port)
            if not bank_code:
                return None

            self._security.save_known_port(ip, port)

            amount = self._connector.get_bank_amount(ip, port)
            clients = self._connector.get_client_count(ip, port)

            if amount is not None and clients is not None:
                log.info(f"Found bank at {ip}:{port} - Amount: {amount}, Clients: {clients}")
                return BankInfo(ip=ip, port=port, total_amount=amount, client_count=clients)

        except Exception:
            return None
        return None

    def find_robbery_targets(self, target_amount: int, banks: List[BankInfo]) -> List[BankInfo]:
        """
        Finds optimal combination of banks to rob
        :param target_amount: Target amount to steal
        :param banks: List of available banks
        :return: List of banks to rob
        """
        if not banks:
            return []

        banks_sorted = sorted(banks, key=lambda b: b.total_amount / max(b.client_count, 1), reverse=True)

        selected = []
        total_stolen = 0
        total_clients = 0

        for bank in banks_sorted:
            if total_stolen >= target_amount:
                break

            selected.append(bank)
            total_stolen += bank.total_amount
            total_clients += bank.client_count

        return selected