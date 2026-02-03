"""
Business logic file, creates the main functions and assembles other packages
"""
import codecs
import json
import logging

from business.generate_campaign_feedback import generate_feedback_via_ollama, generate_random_feedback
from business.generate_sales_file import generate_random_sales, generate_sales_via_ollama
from http_client.http_client import send_json


def push_campaign_feedbacks_to_api(
        api_endpoint_url,
        api_rest_method,
        api_timeout_seconds,
        api_auth_active,
        api_username,
        api_password,
        generation_mode,
        ollama_url,
        ollama_model,
        feedbacks_to_push
):
    url = api_endpoint_url
    method = api_rest_method
    timeout = api_timeout_seconds

    headers = {}

    # Authentication
    if api_auth_active:
        # TODO Auth method
        logging.debug("Auth")

    # Example payload
    payload = {
        "username": "user_demo",
        "feedback_date": "2025-01-01",
        "campaign_id": "CAMP000",
        "comment": "demo"
    }

    # Init
    payload = []

    logging.info(f"Generation mode: {generation_mode}")

    # Choose generation mode and generate
    if generation_mode == "ollama":
        logging.info(f"Local AI generation mode, using ollama")
        # IA Generated feedback
        payload = generate_feedback_via_ollama(
            count=feedbacks_to_push,
            model=ollama_model,
            host=ollama_url,
            timeout=300
        )
    else:
        logging.info(f"Manual generation mode, using random functions")
        # Manual mode, default mode
        payload = generate_random_feedback(feedbacks_to_push, payload)

    # Send JSON to API Endpoint
    try:
        resp = send_json(
            url=url,
            payload=payload,
            headers=headers,
            timeout=timeout,
            method=method
        )
        logging.info("Query finished without error")
        logging.info(json.dumps(resp, indent=2, ensure_ascii=False))
        return 0
    except Exception:
        logging.exception(f"Error on query {Exception}")
        return 1


def create_sales_csv_file(
        sales_csv_file,
        campaign_product_csv_file,
        generation_mode,
        ollama_url,
        ollama_model,
        lines_to_create
):
    # Exemple line
    columns_sales = "username,sale_date,country,product,quantity,unit_price,total_amount\n"
    columns_campaign_product = "campaign_id,product\n"
    line_sales = "user149,2025-05-10,India,Chicken Nuggets,5,11.14,55.7"
    line_campaign_product = "CAMP000,Spicy Strips"

    logging.info(f"Generation mode: {generation_mode}")

    # Choose generation mode and generate
    if generation_mode == "ollama":
        logging.info(f"Local AI generation mode, using ollama")
        # IA Generated sales
        (
            csv_sales,
            campaign_product_csv
        ) = generate_sales_via_ollama(
            lines_to_create=lines_to_create,
            already_existing_sales=columns_sales,
            already_existing_campaign_product=columns_campaign_product,
            model=ollama_model,
            host=ollama_url,
            timeout=300
        )
    else:
        logging.info(f"Manual generation mode, using random functions")
        # Manual mode, default mode
        (
            csv_sales,
            campaign_product_csv
        ) = generate_random_sales(
            lines_to_create=lines_to_create,
            already_existing_sales=columns_sales,
            already_existing_campaign_product=columns_campaign_product,
        )

    with codecs.open(sales_csv_file, "w", "utf-8") as text_file:
        text_file.write(csv_sales)
        text_file.close()

    with codecs.open(campaign_product_csv_file, "w", "utf-8") as text_file:
        text_file.write(campaign_product_csv)
        text_file.close()
