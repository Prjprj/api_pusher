"""
Business logic file, creates the main functions and assembles other packages
"""

import json
import logging

from business.generate_campaign_feedback import generate_feedback_via_ollama, generate_random_feedback
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
