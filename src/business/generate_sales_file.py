"""
Data Generation management
"""

import json
import logging
import random

import urllib.request
import urllib.error

from business import allowed_comments, random_date, allowed_countries, allowed_products


def generate_random_sales(
    lines_to_create,
    already_existing_sales,
    already_existing_campaign_product,
):
    """
    Generate random sales

    :param lines_to_create: number of lines to create
    :param already_existing_sales: existing lines for sales
    :param already_existing_campaign_product: existing lines for campaign / product mapping
    :return: returns the lines given with the number of sales appended
    """
    result_sales = already_existing_sales
    result_campaign_product = already_existing_campaign_product
    i = 0
    while i < lines_to_create:
        # Get random values to add to lines
        user_number = random.randint(1, 4999)
        sale_date = random_date("2024-1-1", "2026-12-31", random.random())
        quantity = random.randint(1, 999)
        unit_price = round(random.uniform(1.00, 200.00), 2)
        total_amount = round(quantity * unit_price, 2)

        campaign_number = random.randint(1, 999)

        # Determine random country
        country_number = random.randint(1, len(allowed_countries))
        country = allowed_countries[country_number-1]
        logging.debug(f"Random country number: {country_number}, country: {country}")

        # Determine random product
        product_number = random.randint(1, len(allowed_products))
        product = allowed_products[product_number-1]
        logging.debug(f"Random product number: {product_number}, product: {product}")

        # Build line to add
        line_to_add_sales = f"user_{user_number},{sale_date},{country},{product},{quantity},{unit_price},{total_amount}\n"
        line_to_add_campaign_product = f"CAMP{campaign_number},{product}\n"

        logging.debug(f"Manual generation, line: {line_to_add_sales} & {line_to_add_campaign_product}")

        # Append JSON to payload
        result_sales = result_sales + line_to_add_sales
        result_campaign_product = result_campaign_product + line_to_add_campaign_product
        i = i + 1

    return result_sales, result_campaign_product

def generate_sales_via_ollama(
        lines_to_create,
        already_existing_sales,
        already_existing_campaign_product,
        model = "llama3.2",
        host = "127.0.0.1:11434",
        temperature = 0.7,
        timeout = 30
):
    """
    Generate `lines_to_create` sales objects thru Ollama API, setting a
    JSON schema (objects array) and deactivating streaming.
    JSON is transformed to a csv file as a result for sales and campaign/product mapping

    :param lines_to_create: number of lines to generate
    :param already_existing_sales: existing lines for sales
    :param already_existing_campaign_product: existing lines for campaign / product mapping
    :param model: model name (ex. 'llama3.2', 'mistral', etc.)
    :param host: Ollama base URL (ex. '127.0.0.1:11434')
    :param temperature: model creativity
    :param timeout: timeout HTTP in seconds
    :return: tuple of string containing the sales & campaign/product mapping
    """
    result_sales = already_existing_sales
    result_campaign_product = already_existing_campaign_product

    if lines_to_create <= 0:
        return []

    # JSON Schema forced for output (Ollama "format": JSON schema)
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string"
                },
                "sale_date": {
                    "type": "string",
                    "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
                },
                "campaign_id": {
                    "type": "string"
                },
                "product_id": {
                    "type": "integer"
                },
                "country_id": {
                    "type": "integer"
                },
                "quantity": {
                    "type": "integer"
                },
                "unit_price_part1": {
                    "type": "integer"
                },
                "unit_price_part2": {
                    "type": "integer"
                }
            },
            "required": ["username", "sale_date", "campaign_id", "product_id", "country_id", "quantity", "unit_price_part1", "unit_price_part2"],
            "additionalProperties": False
        },
        "minItems": lines_to_create,
        "maxItems": lines_to_create
    }

    # Prompt (system + user) to instruct model what to do
    system_prompt = (
        "You are a data generator. Output strictly JSON that matches the schema. "
        "Do not include explanations or extra text."
    )

    user_prompt = f"""
Generate {lines_to_create} distinct sales as a JSON array.
Rules:
- "username": random usernames like in social network, no obsene name.
- "sale_date": valid date "YYYY-MM-DD" in the year 2024, 2025 and 2026.
- "campaign_id": "CAMP" followed by three digits (e.g. CAMP147).
- "product_id": choose a random number between 1 and {len(allowed_products)}
- "country_id": choose a random number between 1 and {len(allowed_countries)}
- "quantity": choose a random number between 1 and 1000
- "unit_price_part1": choose a random number between 1 and 199
- "unit_price_part2": choose a random number between 1 and 99
Ensure all items are valid and diverse. Return only JSON.
"""

    url = f"http://{host}/api/generate"  # Ollama endpoint for generation (https://docs.ollama.com/api/generate)

    ollama_payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "format": schema,
        # structured JSON schema supported by Ollama (https://docs.ollama.com/api/generate)(https://github.com/ollama/ollama/blob/main/docs/api.md)
        "stream": False,  # non-streaming to simplify parsing (https://docs.ollama.com/api/streaming)
        "options": {
            "temperature": temperature
        }
    }

    logging.debug(f"Schema: {schema}")
    logging.debug(f"System Prompt: {system_prompt}")
    logging.debug(f"User Prompt: {user_prompt}")
    logging.debug(f"URL: {url}")
    logging.debug(f"Payload: {ollama_payload}")

    # HTTP call
    try:
        headers = {"Content-Type": "application/json"}
        method = "POST"
        logging.debug(f"data: {json.dumps(ollama_payload).encode("utf-8")}")
        logging.debug(f"data: {headers}")
        logging.debug(f"data: {method}")
        req = urllib.request.Request(
            url=url,
            data=json.dumps(ollama_payload).encode("utf-8"),
            headers=headers,
            method=method
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            data = json.loads(raw)
            logging.debug(f"Raw: {raw}")
            logging.debug(f"Data: {data}")
    except Exception as e:
        logging.error(f"Ollama call error: {e}")
        raise RuntimeError(f"Ollama call error: {e}")

    # Parsing ollama answer
    # Key 'response' can contain JSON string or an already parsed object
    response = data.get("response")
    if isinstance(response, str):
        try:
            items = json.loads(response)
        except Exception as e:
            logging.error(f"Non JSON Response: {e}\nContent: {response[:200]}...")
            raise ValueError(f"Non JSON Response: {e}\nContent: {response[:200]}...")
    else:
        items = response

    logging.debug(f"Ollama answer: {items}")

    for item in items:
        user_number = item['username']
        sale_date = item['sale_date']
        campaign_number = item['campaign_id']
        country = allowed_countries[int(item['country_id']) % len(allowed_countries)]
        product = allowed_products[int(item['product_id']) % len(allowed_products)]
        quantity = item['quantity']
        unit_price = round(item['unit_price_part1'] + (item['unit_price_part2']/100),2)
        total_amount = round(quantity * unit_price,2)

        # Build lines to add
        line_to_add_sales = f"user_{user_number},{sale_date},{country},{product},{quantity},{unit_price},{total_amount}\n"
        line_to_add_campaign_product = f"{campaign_number},{product}\n"

        logging.debug(f"Ollama response line: {line_to_add_sales} & {line_to_add_campaign_product}")

        result_sales = result_sales + line_to_add_sales
        result_campaign_product = result_campaign_product + line_to_add_campaign_product

    return result_sales, result_campaign_product
