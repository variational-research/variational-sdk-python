import hashlib
import hmac
import time

import requests


def sign_prepared_request(req: requests.PreparedRequest,
                          key: str, secret: str) -> requests.PreparedRequest:
    timestamp_ms = int(time.time() * 1000)
    message = f"{key}|{timestamp_ms}|{req.method}|{req.path_url}"
    signer = hmac.new(bytes.fromhex(secret), message.encode(), hashlib.sha256)

    # if request has body, append another pipe and the entire request body as bytes
    if isinstance(req.body, bytes):
        # arguments need to implement Buffer protocol, so everything is bytes, not str
        signer.update(b"|")
        signer.update(req.body)

    req.prepare_headers(dict(req.headers, **{
        "X-Request-Timestamp-Ms": str(timestamp_ms),
        "X-Variational-Key": key,
        "X-Variational-Signature": signer.hexdigest(),
    }))

    return req
