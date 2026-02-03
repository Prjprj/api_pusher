"""
Main file of the program, entry point
Loads config file and inits logger
Start the business logic in app.py
"""

import logging
import sys

from conf.conf import load_config
from logs.logs import compute_log_level
from app import push_campaign_feedbacks_to_api, create_sales_csv_file


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
    if len(arguments) > 3:
        usage()
        exit(1)
    else:
        config_file = "src/config.ini"

        # Load config file
        (
            api_endpoint_url,
            api_rest_method,
            api_timeout_seconds,
            api_auth_active,
            api_username,
            api_password,
            sales_csv_file,
            campaign_product_csv_file,
            ollama_url,
            ollama_model,
            log_file,
            log_level,
            log_format,
            generation_mode,
        ) = load_config(config_file=config_file)

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
                feedbacks_to_push = int(arguments[2])
                push_campaign_feedbacks_to_api(
                    api_endpoint_url=api_endpoint_url,
                    api_rest_method=api_rest_method,
                    api_timeout_seconds=api_timeout_seconds,
                    api_auth_active=api_auth_active,
                    api_username=api_username,
                    api_password=api_password,
                    generation_mode=generation_mode,
                    ollama_url=ollama_url,
                    ollama_model=ollama_model,
                    feedbacks_to_push=feedbacks_to_push
                )
            case "CSV":
                lines_to_create = int(arguments[2])
                create_sales_csv_file(
                    sales_csv_file=sales_csv_file,
                    campaign_product_csv_file=campaign_product_csv_file,
                    generation_mode=generation_mode,
                    ollama_url=ollama_url,
                    ollama_model=ollama_model,
                    lines_to_create=lines_to_create
                )


# Program entry point
if __name__ == "__main__":
    exit(main(sys.argv))
