"""
HTTP requests management
"""

import json
import logging
from urllib import request, error


def _build_request(url, method, headers, body):
    """
    Build an http request

    :param url: request url
    :param method: request method
    :param headers: request headers
    :param body: request body
    :return: returns the request
    """
    req = request.Request(url=url, data=body, headers=headers or {}, method=method)
    return req


def send_json(url, payload, headers, timeout, method = 'POST'):
    """
    Sends JSON payload to an API

    :param url: API endpoint
    :param payload: payload
    :param headers: query headers
    :param timeout: query timeout
    :param method: query method
    :return: returns the result sent by the endpoint
    """
    data_bytes = json.dumps(payload).encode('utf-8')
    hdrs = headers
    hdrs.setdefault('Content-Type', 'application/json')

    logging.debug(f"Payload {payload})")

    try:
        req = _build_request(url, method, hdrs, data_bytes)
        logging.info(f"Send {method} to {url}")
        logging.debug(f"Request {req})")

        # Send query
        with request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8')
            logging.info(f"HTTP answer {status}")
            logging.debug(f"HTTP answer {body}, Headers: {dict(resp.headers.items())}")
            return {
                'status': status,
                'body': body,
                'headers': dict(resp.headers.items()),
            }
    # Exception management
    except error.HTTPError as e:
        content = e.read().decode('utf-8') if e.fp else ''
        logging.error(f"HTTPError {e.code}: {content}")
    except error.URLError as e:
        logging.error(f"URLError: {e}")
    except Exception:
        logging.exception(f"Unknown error {Exception}")
