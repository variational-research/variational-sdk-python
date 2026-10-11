import hashlib
import hmac
import time

import requests


def sign_prepared_request(
    req: requests.PreparedRequest, key: str, secret: str
) -> requests.PreparedRequest:
    """Sign a prepared HTTP request with Variational API key and HMAC secret."""
    timestamp_ms = int(time.time() * 1000)
    message = f"{key}|{timestamp_ms}|{req.method}|{req.path_url}"
    secret_hex = secret[2:] if secret.startswith(("0x", "0X")) else secret
    signer = hmac.new(bytes.fromhex(secret_hex), message.encode(), hashlib.sha256)

    # if request has body, append another pipe and the entire request body as bytes
    if req.body:
        if isinstance(req.body, str):
            req.body = req.body.encode("utf-8")
            req.headers["Content-Length"] = str(len(req.body))

        body_bytes = bytes(req.body)
        signer.update(b"|")
        signer.update(body_bytes)

    req.prepare_headers(
        dict(
            req.headers,
            **{
                "X-Request-Timestamp-Ms": str(timestamp_ms),
                "X-Variational-Key": key,
                "X-Variational-Signature": signer.hexdigest(),
            },
        )
    )

    return req
