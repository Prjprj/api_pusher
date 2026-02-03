"""
Data Generation management
"""

import json
import logging
import random
import time

import urllib.request
import urllib.error

from business import allowed_comments


def str_time_prop(start, end, time_format, prop):
    """
    Get a time at a proportion of a range of two formatted times.

    :param start: start of the interval
    :param end: end of the interval
    :param time_format: format of date
    :param prop: proportion of time between end and start
    :return: return a random date between start and end, the returned time will be in the specified format
    """
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    """
    Get a time at a proportion of a range of two formatted times.

    :param start: start of the interval
    :param end: end of the interval
    :param prop: proportion of time between end and start
    :return: return a random date between start and end
    """
    return str_time_prop(start, end, '%Y-%m-%d', prop)


def generate_random_feedback(
    feedbacks_to_push,
    payload
):
    """
    Generate random feedbacks

    :param feedbacks_to_push: number of feedbacks to push
    :param payload: existing payload
    :return: returns the payload given with the number of feedbacks to push appended
    """
    i = 0
    while i < feedbacks_to_push:
        # Get random values to add to payload
        user_number = random.randint(1, 4999)
        campaign_date = random_date("2024-1-1", "2026-12-31", random.random())
        campaign_number = random.randint(1, 999)

        # Determine random comment
        comment_number = random.randint(1, len(allowed_comments))
        comment = allowed_comments[comment_number]
        logging.debug(f"Random comment number: {comment_number}, comment: {comment}")

        # Build JSON to add to payload
        item_to_add = {
            "username": f"user_{user_number}",
            "feedback_date": f"{campaign_date}",
            "campaign_id": f"CAMP{campaign_number}",
            "comment": f"{comment}"
        }

        logging.debug(f"Manual generation, item: {item_to_add}")

        # Append JSON to payload
        payload.append(item_to_add)
        i = i + 1

    return payload


def generate_feedback_via_ollama(
        count,
        model = "llama3.2",
        host = "127.0.0.1:11434",
        temperature = 0.7,
        timeout = 30,
):
    """
    Generate `count` feedback objects thru Ollama API, setting a
    JSON schema (objects array) and deactivating streaming.

    :param count: number of entry to generate
    :param model: model name (ex. 'llama3.2', 'mistral', etc.)
    :param host: Ollama base URL (ex. '127.0.0.1:11434')
    :param temperature: model creativity
    :param timeout: timeout HTTP in seconds
    :return: objects list (dict) at asked model
    """

    if count <= 0:
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
                "feedback_date": {
                    "type": "string",
                    "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
                },
                "campaign_id": {
                    "type": "string"
                },
                "comment": {
                    "type": "integer"
                }
            },
            "required": ["username", "feedback_date", "campaign_id", "comment"],
            "additionalProperties": False
        },
        "minItems": count,
        "maxItems": count
    }

    # Prompt (system + user) to instruct model what to do
    system_prompt = (
        "You are a data generator. Output strictly JSON that matches the schema. "
        "Do not include explanations or extra text."
    )

    user_prompt = f"""
Generate {count} distinct feedback objects as a JSON array.
Rules:
- "username": random usernames like in social network, no obsene name.
- "feedback_date": valid date "YYYY-MM-DD" in the year 2024, 2025 and 2026.
- "campaign_id": "CAMP" followed by three digits (e.g. CAMP147).
- "comment": choose a random number between 1 and 40
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

    result = []
    for item in items:
        result_to_add = {
            "username": f"{item['username']}",
            "feedback_date": f"{item['feedback_date']}",
            "campaign_id": f"{item['campaign_id']}",
            "comment": f"{allowed_comments[int(item['comment'])]}"
        }
        logging.debug(f"Ollama response item: {result_to_add}")
        result.append(result_to_add)

    return result
