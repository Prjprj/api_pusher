import json
import logging
from typing import List, Dict

import urllib.request
import urllib.error


def generate_feedback_via_ollama(
        count: int,
        model: str = "llama3.2",
        host: str = "127.0.0.1:11434",
        temperature: float = 0.7,
        timeout: int = 30,
) -> List[Dict]:
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
                    "pattern": r"^\d{4}-\d{2}-\d{2}$"
                },
                "campaign_id": {
                    "type": "string"
                },
                "comment": {
                    "type": "string"
                }
            },
            "required": ["username", "feedback_date", "campaign_id", "comment"],
            "additionalProperties": False
        },
        "minItems": count,
        "maxItems": count
    }

    # Allowed Comments
    allowed_comments = [
        "Great campaign!",
        "Not very engaging.",
        "Loved the product presentation.",
        "Too many details, hard to follow.",
        "Creative and fun approach!",
        "Clear and concise message.",
        "Excellent marketing strategy.",
        "Could be better organized.",
        "Excellente campagne !",
        "Pas très engageant.",
        "J’ai adoré la présentation du produit.",
        "Trop de détails, difficile à suivre.",
        "Approche créative et amusante !",
        "Message clair et concis.",
        "Excellente stratégie marketing.",
        "Pourrait être mieux organisé.",
        "बेहतरीन अभियान!",
        "इतना आकर्षक नहीं।",
        "मुझे उत्पाद की प्रस्तुति बहुत पसंद आई।",
        "बहुत ज़्यादा विवरण हैं, समझना मुश्किल है।",
        "रचनात्मक और मज़ेदार तरीका!",
        "स्पष्ट और संक्षिप्त संदेश।",
        "उत्कृष्ट विपणन रणनीति।",
        "इसे और बेहतर तरीके से संगठित किया जा सकता है।",
        "很棒的活动！",
        "不太有吸引力。",
        "很喜欢产品的展示。",
        "细节太多，难以跟上。",
        "有创意又有趣的方法！",
        "信息清晰简洁。",
        "出色的营销策略。",
        "组织得可以更好一些。",
        "素晴らしいキャンペーンです！",
        "あまり惹きつけられないです。",
        "製品のプレゼンテーションがとても良かったです。",
        "詳細が多すぎて、ついていくのが大変です。",
        "創造的で楽しいアプローチです！",
        "明確で簡潔なメッセージです。",
        "優れたマーケティング戦略です。",
        "もっと整理できると思います。"
    ]

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
- "comment": choose ONLY from this set (exact strings):
  {allowed_comments}
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
        req = urllib.request.Request(
            url=url,
            data=json.dumps(ollama_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        logging.error(f"Ollama call error: {e}")
        raise RuntimeError(f"Ollama call error: {e}")

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

    return items
