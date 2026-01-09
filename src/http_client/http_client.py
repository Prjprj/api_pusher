import json
import logging
from urllib import request, error


def _build_request(url, method, headers, body):
    req = request.Request(url=url, data=body, headers=headers or {}, method=method)
    return req


def send_json(url, payload, headers, timeout, method = 'POST'):
    data_bytes = json.dumps(payload).encode('utf-8')
    hdrs = headers
    hdrs.setdefault('Content-Type', 'application/json')

    try:
        req = _build_request(url, method, hdrs, data_bytes)
        logging.debug(f"Payload {payload})")
        logging.info(f"Send {method} to {url}")
        with request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8')
            logging.info(f"HTTP answer {status}")
            return {
                'status': status,
                'body': body,
                'headers': dict(resp.headers.items()),
            }
    except error.HTTPError as e:
        content = e.read().decode('utf-8') if e.fp else ''
        logging.error(f"HTTPError {e.code}: {content}")
    except error.URLError as e:
        logging.error(f"URLError: {e}")
    except Exception:
        logging.exception(f"Unknown error {Exception}")
