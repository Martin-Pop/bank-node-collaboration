import logging
import json
import ipaddress
from pathlib import Path

from utils.paths import resolve_path

log = logging.getLogger("SYSTEM")

class InvalidConfiguration(Exception):
    pass

class ConfigurationManager:
    """
    Class that holds configurations.
    """

    def __init__(self, config_file_path: str):
        self._config_file_path = config_file_path
        self._config = self._load_config(config_file_path)

        if self._config is not None:
            log.info("Configuration loaded successfully: " + json.dumps(self._config))

    def _load_config(self, config_file_path: str) -> dict | None:
        """
        Loads configuration from a file.
        :param config_file_path: file path
        :return: configuration dict if valid else None
        """
        config_file_path = resolve_path(config_file_path)

        try:
            with open(config_file_path) as config_file:
                config = json.load(config_file)
                self._validate_config(config)

                config['storage_path'] = resolve_path(config['storage_path'])

                return config

        except FileNotFoundError:
            log.error(f"Config file {config_file_path} was not found")

        except json.JSONDecodeError:
            log.error(f"Config file {config_file_path} could not be decoded")

        except InvalidConfiguration as ex:
            log.error(ex)


    def _validate_config(self, config: dict):
        """
        Validates the configuration
        :param config: config to validate
        """

        required_keys = [
            "host",
            "port",
            "storage_path",
            "storage_timeout",
            "bank_workers",
            "client_timeout",
            "max_requests_per_minute",
            "max_bad_commands",
            "ban_duration",
            "monitoring_host",
            "monitoring_port"
        ]

        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise InvalidConfiguration(f"Configuration is missing key/s: {missing_keys}")

        try:
            ip_obj = ipaddress.ip_address(config["host"])
            if not isinstance(ip_obj, ipaddress.IPv4Address):
                raise ValueError

        except ValueError:
            raise InvalidConfiguration("Host must be a valid IPv4 address.")

        if not isinstance(config["port"], int):
            raise InvalidConfiguration(f"Port must be an integer.")

        if not (1 <= config["port"] <= 65535):
            raise InvalidConfiguration(f"Port must be in range from 1 to 65535. Found: {config["port"]}")

        storage_path = config["storage_path"]
        if not isinstance(storage_path, str) or not storage_path.strip():
            raise InvalidConfiguration("Storage path must be a non-empty string")

        try:
            parent_dir = Path(resolve_path(storage_path)).parent
            if not parent_dir.exists():
                raise InvalidConfiguration(f"Parent directory for storage does not exist: {parent_dir}")
        except Exception as e:
            raise InvalidConfiguration(f"Invalid storage path: {e}")

        if not isinstance(config["storage_timeout"], (int, float)):
            raise InvalidConfiguration(f"storage_timeout must be a number. Found: {type(config['storage_timeout']).__name__}")

        if config["storage_timeout"] <= 0:
            raise InvalidConfiguration(f"storage_timeout must be positive. Found: {config['storage_timeout']}")

        if config["storage_timeout"] > 15:
            raise InvalidConfiguration(f"storage_timeout cant be bigger than 15. Found: {config['storage_timeout']}")

        if not isinstance(config["bank_workers"], int):
            raise InvalidConfiguration(f"bank_workers must be an integer. Found: {type(config['bank_workers']).__name__}")

        if config["bank_workers"] < 1:
            raise InvalidConfiguration(f"bank_workers must be at least 1. Found: {config['bank_workers']}")

        if config["bank_workers"] > 16:
            raise InvalidConfiguration(f"there cant be more bank_workers than 16. Found: {config['bank_workers']}")

        if not isinstance(config["client_timeout"], (int, float)):
            raise InvalidConfiguration(f"client_timeout must be a number. Found: {type(config['client_timeout']).__name__}")

        if config["client_timeout"] <= 0:
            raise InvalidConfiguration(f"client_timeout must be positive. Found: {config['client_timeout']}")

        if config["client_timeout"] > 60:
            raise InvalidConfiguration(f"client_timeout cant be bigger than 60. Found: {config['client_timeout']}")

        if not isinstance(config["max_requests_per_minute"], int):
            raise InvalidConfiguration(f"max_requests_per_minute must be a number. Found: {type(config['max_requests_per_minute']).__name__}")

        if config["max_requests_per_minute"] <= 0:
            raise InvalidConfiguration(f"max_requests_per_minute must be positive number. Found: {config['max_requests_per_minute']}")

        if not isinstance(config["max_bad_commands"], int):
            raise InvalidConfiguration(f"max_bad_commands must be a number. Found: {type(config['max_bad_commands']).__name__}")

        if config["max_bad_commands"] <= 0:
            raise InvalidConfiguration(f"max_bad_commands must be positive number. Found: {config['max_bad_commands']}")

        if not isinstance(config["ban_duration"], int):
            raise InvalidConfiguration(f"ban_duration must be a number. Found: {type(config['ban_duration']).__name__}")

        if config["ban_duration"] <= 0:
            raise InvalidConfiguration(f"ban_duration must be positive number. Found: {config['ban_duration']}")

        try:
            ip_obj = ipaddress.ip_address(config["monitoring_host"])
            if not isinstance(ip_obj, ipaddress.IPv4Address):
                raise ValueError

        except ValueError:
            raise InvalidConfiguration("monitoring_host must be a valid IPv4 address.")

        if not (1 <= config["monitoring_port"] <= 65535):
            raise InvalidConfiguration(f"monitoring_port must be in range from 1 to 65535. Found: {config["port"]}")

        net_range = config["network_scan_port_range"]
        if not isinstance(net_range, list) or len(net_range) != 2:
            raise InvalidConfiguration("network_scan_port_range must be a list of two integers [start, end]")

        start_p, end_p = net_range
        if not (1 <= start_p <= 65535) or not (1 <= end_p <= 65535):
            raise InvalidConfiguration("Scan ports must be between 1 and 65535")
        if start_p > end_p:
            raise InvalidConfiguration("Scan port start cannot be higher than end")

        subnet = config["network_scan_subnet"]
        if not isinstance(subnet, str) or subnet.count('.') != 2:
            raise InvalidConfiguration("network_scan_subnet must be in format 'X.Y.Z' ")

        if not isinstance(config["network_timeout"], (int, float)):
            raise InvalidConfiguration(
                f"network_timeout must be a number. Found: {type(config['network_timeout']).__name__}")

        if config["network_timeout"] <= 0:
            raise InvalidConfiguration(f"network_timeout must be positive. Found: {config['network_timeout']}")

        if config["network_timeout"] > 15:
            raise InvalidConfiguration(f"network_timeout cant be bigger than 15. Found: {config['network_timeout']}")

        log.info("Configuration validation passed")

    def get_config(self) -> dict | None:
        return self._config
