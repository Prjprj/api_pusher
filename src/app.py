import json
import logging
from json import load

from business.generate_campaign_feedback import generate_feedback_via_ollama
from http_client.http_client import send_json


def load_default_schema():
    with open('resources/schemas/default_feedback_schema.json', 'r', encoding='utf-8') as f:
        return load(f)


def test(
        api_endpoint_url,
        api_rest_method,
        api_timeout_seconds,
        ollama_url,
        ollama_model,
        api_username,
        api_password,
):
    url = api_endpoint_url
    method = api_rest_method
    timeout = api_timeout_seconds

    headers = {}

    # Example payload
    payload = {
        "username": "user_demo",
        "feedback_date": "2025-01-01",
        "campaign_id": "CAMP000",
        "comment": "demo"
    }

    # IA Generated feedback
    payload = generate_feedback_via_ollama(count=5,model=ollama_model,host=ollama_url,temperature=0.7,timeout=300)

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
