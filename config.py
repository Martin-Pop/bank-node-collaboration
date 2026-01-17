import logging
import json
import ipaddress

from logger.types import LOG_TYPES

log = logging.getLogger(LOG_TYPES.SYSTEM)

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

        try:
            with open(config_file_path) as config_file:
                config = json.load(config_file)
                self._validate_config(config)

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

        required_keys = ["host", "port"]

        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise InvalidConfiguration(f"Configuration is missing key/s: {missing_keys}")

        try:
            ip_obj = ipaddress.ip_address(config["host"])
            if not isinstance(ip_obj, ipaddress.IPv4Address):
                raise ValueError

        except ValueError:
            raise InvalidConfiguration("Host must be a valid IPv4 address.")

        if not isinstance(config["port"], int) or not (1 <= config["port"] <= 65535):
            raise InvalidConfiguration(f"Port must be in range from 1 to 65535. Found: {config["port"]}")

    def get_config(self) -> dict | None:
        return self._config
