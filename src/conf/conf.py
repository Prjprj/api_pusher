import sys
import configparser
import logging


# Read config file for technical configuration
def load_config(config_file):
    """
    Function to read parameters to load in the program and sending it back as a tuple for technical configuration

    :param config_file: String containing the path to access to the configuration file
    :return: Tuple containing the following elements:
            api_endpoint_url,
            api_rest_method,
            api_timeout_seconds,
            api_username,
            api_password,
            ollama_url,
            ollama_model,
            log_file,
            log_level,
            log_format,
    """
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
        if not config.sections():
            raise ValueError("Empty or invalid config file")

        api_endpoint_url = config["API"]["endpoint_url"]
        api_rest_method = config["API"]["method"]
        api_timeout_seconds = int(config["API"]["timeout_seconds"])

        api_username = config["API_AUTH"]["username"]
        api_password = config["API_AUTH"]["password"]

        ollama_url = config["OLLAMA"]["ollama_url"]
        ollama_model = config["OLLAMA"]["ollama_model"]

        log_file = config["LOG"]["log_file"]
        log_level = config["LOG"]["log_level"]
        log_format = config["LOG"]["log_format"]

        # For multivalued, use split
        # mv_list = config["XYZ"]["list"].split(",")

        return (
            api_endpoint_url,
            api_rest_method,
            api_timeout_seconds,
            api_username,
            api_password,
            ollama_url,
            ollama_model,
            log_file,
            log_level,
            log_format,
        )
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_file}")
        logging.exception(f"Config file not found: {config_file}")
        sys.exit(5)
    except configparser.Error as e:
        logging.error(f"Error when reading config file: {e}")
        logging.exception(f"Error when reading config file: {e}")
        sys.exit(5)
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        logging.exception(f"Configuration error: {e}")
        sys.exit(5)
