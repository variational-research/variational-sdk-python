import hashlib
import hmac
import requests

from variational.auth import sign_prepared_request

KEY = "test-api-key"
RAW_SECRET = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
SECRET_WITH_0X = "0x" + RAW_SECRET
SECRET_WITH_UPPER_0X = "0X" + RAW_SECRET


def test_sign_prepared_request_without_body():
    """Test signing a prepared request without a body."""
    req = requests.Request(
        method="GET",
        url="https://api.variational.io/v1/portfolio/summary",
    ).prepare()

    signed_req = sign_prepared_request(req, KEY, RAW_SECRET)

    timestamp_ms = signed_req.headers.get("X-Request-Timestamp-Ms")
    assert timestamp_ms is not None
    assert signed_req.headers.get("X-Variational-Key") == KEY

    expected_msg = f"{KEY}|{timestamp_ms}|GET|/v1/portfolio/summary"
    expected_sig = hmac.new(
        bytes.fromhex(RAW_SECRET), expected_msg.encode(), hashlib.sha256
    ).hexdigest()

    assert signed_req.headers.get("X-Variational-Signature") == expected_sig


def test_sign_prepared_request_with_bytes_body():
    """Test signing a prepared request with a bytes body payload."""
    body = b'{"qty":"100","side":"buy"}'
    req = requests.Request(
        method="POST",
        url="https://api.variational.io/v1/quotes/accept",
        data=body,
    ).prepare()

    signed_req = sign_prepared_request(req, KEY, RAW_SECRET)

    timestamp_ms = signed_req.headers.get("X-Request-Timestamp-Ms")
    expected_msg = f"{KEY}|{timestamp_ms}|POST|/v1/quotes/accept".encode() + b"|" + body
    expected_sig = hmac.new(
        bytes.fromhex(RAW_SECRET), expected_msg, hashlib.sha256
    ).hexdigest()

    assert signed_req.headers.get("X-Variational-Signature") == expected_sig


def test_sign_prepared_request_with_str_body():
    """Test signing a prepared request with a string body payload."""
    str_body = '{"qty":"100","side":"buy"}'
    req_str = requests.Request(
        method="POST",
        url="https://api.variational.io/v1/quotes/accept",
        data=str_body,
    ).prepare()

    signed_req = sign_prepared_request(req_str, KEY, RAW_SECRET)

    timestamp_ms = signed_req.headers.get("X-Request-Timestamp-Ms")
    expected_msg = (
        f"{KEY}|{timestamp_ms}|POST|/v1/quotes/accept".encode()
        + b"|"
        + str_body.encode("utf-8")
    )
    expected_sig = hmac.new(
        bytes.fromhex(RAW_SECRET), expected_msg, hashlib.sha256
    ).hexdigest()

    assert signed_req.headers.get("X-Variational-Signature") == expected_sig


def test_sign_prepared_request_with_non_ascii_str_body():
    """Test signing a prepared request with a non-ASCII string body and verifying UTF-8 encoding."""
    non_ascii_body = '{"name":"Variational-€-テスト"}'
    req = requests.Request(
        method="POST",
        url="https://api.variational.io/v1/test",
        data=non_ascii_body,
    ).prepare()

    signed_req = sign_prepared_request(req, KEY, RAW_SECRET)

    # Verify that req.body was normalized to UTF-8 bytes and Content-Length matches
    expected_bytes = non_ascii_body.encode("utf-8")
    assert isinstance(signed_req.body, bytes)
    assert signed_req.body == expected_bytes
    assert signed_req.headers.get("Content-Length") == str(len(expected_bytes))

    timestamp_ms = signed_req.headers.get("X-Request-Timestamp-Ms")
    expected_msg = (
        f"{KEY}|{timestamp_ms}|POST|/v1/test".encode()
        + b"|"
        + expected_bytes
    )
    expected_sig = hmac.new(
        bytes.fromhex(RAW_SECRET), expected_msg, hashlib.sha256
    ).hexdigest()

    assert signed_req.headers.get("X-Variational-Signature") == expected_sig


def test_sign_prepared_request_with_0x_secret_prefix():
    """Test signing a prepared request with a secret having a 0x prefix."""
    req1 = requests.Request(
        method="GET",
        url="https://api.variational.io/v1/status",
    ).prepare()
    req2 = requests.Request(
        method="GET",
        url="https://api.variational.io/v1/status",
    ).prepare()

    signed1 = sign_prepared_request(req1, KEY, RAW_SECRET)
    signed2 = sign_prepared_request(req2, KEY, SECRET_WITH_0X)

    # Both should produce valid 64-character hexadecimal signatures
    assert len(signed1.headers.get("X-Variational-Signature")) == 64
    assert len(signed2.headers.get("X-Variational-Signature")) == 64
    assert signed1.headers.get("X-Variational-Key") == KEY
    assert signed2.headers.get("X-Variational-Key") == KEY


def test_sign_prepared_request_with_0x_and_body():
    """Test signing a request with a 0X-prefixed secret and body payload."""
    body = '{"id":"test-id"}'
    req = requests.Request(
        method="POST",
        url="https://api.variational.io/v1/quotes/cancel",
        data=body,
    ).prepare()

    signed = sign_prepared_request(req, KEY, SECRET_WITH_UPPER_0X)

    timestamp_ms = signed.headers.get("X-Request-Timestamp-Ms")
    expected_msg = (
        f"{KEY}|{timestamp_ms}|POST|/v1/quotes/cancel".encode()
        + b"|"
        + body.encode("utf-8")
    )
    expected_sig = hmac.new(
        bytes.fromhex(RAW_SECRET), expected_msg, hashlib.sha256
    ).hexdigest()

    assert signed.headers.get("X-Variational-Signature") == expected_sig


def test_sign_prepared_request_preserves_headers():
    """Test that existing request headers are preserved after signing."""
    req = requests.Request(
        method="GET",
        url="https://api.variational.io/v1/metadata/limits",
        headers={"Custom-Header": "custom-value"},
    ).prepare()

    signed = sign_prepared_request(req, KEY, RAW_SECRET)

    assert signed.headers.get("Custom-Header") == "custom-value"
    assert "X-Variational-Signature" in signed.headers
