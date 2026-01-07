
import json
import time
import logging
from typing import Dict, Optional
from urllib import request, error


def _build_request(url: str, method: str, headers: Dict[str, str], body: Optional[bytes]):
    req = request.Request(url=url, data=body, headers=headers or {}, method=method)
    return req

def send_json(url: str, payload: Dict, headers: Dict[str, str], timeout: int, method: str = 'POST',
              max_retries: int = 3, backoff_seconds: float = 1.0) -> Dict:
    data_bytes = json.dumps(payload).encode('utf-8')
    hdrs = {}
    hdrs.setdefault('Content-Type', 'application/json')

    attempt = 0
    while True:
        attempt += 1
        try:
            req = _build_request(url, method, hdrs, data_bytes)
            logging.debug(f"Payload {payload})")
            logging.info(f"Envoi {method} vers {url} (tentative {attempt})")
            with request.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                body = resp.read().decode('utf-8')
                logging.info(f"Réponse HTTP {status}")
                return {
                    'status': status,
                    'body': body,
                    'headers': dict(resp.headers.items()),
                }
        except error.HTTPError as e:
            content = e.read().decode('utf-8') if e.fp else ''
            logging.error(f"HTTPError {e.code}: {content}")
            if attempt > max_retries:
                raise
        except error.URLError as e:
            logging.error(f"URLError: {e}")
            if attempt > max_retries:
                raise
        except Exception:
            logging.exception("Erreur inattendue lors de l'envoi")
            if attempt > max_retries:
                raise

        sleep_s = backoff_seconds * (2 ** (attempt - 1))
        logging.info(f"Retry dans {sleep_s:.1f}s...")
        time.sleep(sleep_s)
