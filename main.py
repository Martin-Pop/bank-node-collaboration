from config import ConfigurationManager

if __name__ == "__main__":
    config_manager = ConfigurationManager("config/config.json")
    config = config_manager.get_config()
    if not config:
        exit(1)

    print('yeah')
