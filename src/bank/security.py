import time
import logging

log = logging.getLogger("SECURITY")

class SecurityGuard:
    def __init__(self, manager, ban_duration):
        self._blacklist = manager.dict()
        self._lock = manager.Lock()
        self.BAN_DURATION = ban_duration

    def is_banned(self, ip_address: str) -> bool:
        ban_end = self._blacklist.get(ip_address)
        if ban_end:
            if time.time() < ban_end:
                return True
            else:
                try:
                    del self._blacklist[ip_address]
                except KeyError:
                    pass
        return False

    def ban_ip(self, ip_address: str):
        with self._lock:
            end_time = time.time() + self.BAN_DURATION
            self._blacklist[ip_address] = end_time

        log.warning(f"Banning {ip_address} for {self.BAN_DURATION} seconds")
