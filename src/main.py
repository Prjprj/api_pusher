"""
Main file of the program, entry point
Loads config file and inits logger
Start the business logic in app.py
"""

import logging
import sys

from conf.conf import load_config
from logs.logs import compute_log_level
from app import test


def usage():
    """
    Print Usage message for main program

    :return: No Return
    """
    print("Usage: python3 __main__.py <ACTION>")
    print("ACTION:")
    print(
        "\tPUSH: message"
    )


def main(arguments):
    if len(arguments) != 2:
        usage()
        exit(1)
    else:
        config_file = "src/config.ini"

        (
            api_endpoint_url,
            api_swagger_url,
            api_rest_method,
            api_timeout_seconds,
            api_username,
            api_password,
            log_file,
            log_level,
            log_format
        )=load_config(config_file=config_file)

        # Init Logging
        numeric_level = compute_log_level(log_level)
        logging.basicConfig(
            handlers=[
                logging.FileHandler(filename=log_file, encoding="utf-8", mode="a+")
            ],
            level=numeric_level,
            format=log_format,
        )
        logging.info("Config File loaded")

        # Arguments Management
        action = arguments[1]

        # Start the correct process
        match action:
            case "HELP":
                usage()
            case "PUSH":
                test(
                    api_endpoint_url,
                    api_swagger_url,
                    api_rest_method,
                    api_timeout_seconds,
                    api_username,
                    api_password,
                )


# Program entry point
if __name__ == "__main__":
    exit(main(sys.argv))
