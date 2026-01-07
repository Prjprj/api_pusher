import json
import logging
from json import load

from http_client.http_client import send_json
from schema_adapter.openapi import fetch_openapi, find_request_schema
from schema_adapter.utils import build_minimal_payload, minimal_validate


def load_default_schema():
    with open('resources/schemas/default_feedback_schema.json', 'r', encoding='utf-8') as f:
        return load(f)


def test(
        api_endpoint_url,
        api_swagger_url,
        api_rest_method,
        api_timeout_seconds,
        api_username,
        api_password,
):

    url = api_endpoint_url
    method = api_rest_method
    timeout = api_timeout_seconds

    headers = None
    auto_fill = False
    dry_run = False

    # --- Schéma (Swagger ou défaut) ---
    schema = None
    swagger_url = api_swagger_url

    if swagger_url:
        try:
            openapi = fetch_openapi(swagger_url, timeout=timeout)
            schema = find_request_schema(openapi, url, method)
        except Exception:
            logging.exception("Échec de la récupération/lecture du Swagger. Utilisation du schéma par défaut.")
    if not schema:
        schema = load_default_schema()
        logging.info('Schéma par défaut chargé (schemas/default_feedback_schema.json)')

#    # Payload
#    payload = None
#    if args.json:
#        payload = json.loads(args.json)
#    elif args.data_file:
#        payload = load_payload_from_file(args.data_file)
#    elif cfg['data']['file']:
#        payload = load_payload_from_file(cfg['data']['file'])
#    else:
#        payload = {}
    payload = {
        "username": "user_demo",
        "feedback_date": "2025-01-01",
        "campaign_id": "CAMP000",
        "comment": "demo"
    }

    # Validation minimale et auto-fill
    if auto_fill:
        missing_payload = build_minimal_payload(schema)
        for k, v in missing_payload.items():
            if k not in payload:
                payload[k] = v
        logging.info('Auto-remplissage appliqué sur le payload de sortie')

    valid = minimal_validate(schema, payload)
    if not valid:
        logging.error('Payload invalide au regard du schéma. Corrigez ou utilisez --auto-fill si possible.')
        if not dry_run:
            return 2

    logging.info(f"Préparation de l'envoi vers {url} avec méthode {method}")
    if dry_run:
        print(json.dumps({
            'url': url,
            'method': method,
#            'headers': headers,
            'timeout': timeout,
#            'retries': retries,
#            'backoff': backoff,
            'payload': payload,
            'schema_source': 'swagger' if swagger_url else 'default'
        }, indent=2, ensure_ascii=False))
        return 0

    try:
        resp = send_json(
            url=url,
            payload=payload,
            headers=headers,
            timeout=timeout,
            method=method,
#            max_retries=retries,
#            backoff_seconds=backoff
        )
        logging.info('Envoi terminé avec succès')
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return 0
    except Exception:
        logging.exception("Échec de l'envoi")
        return 1