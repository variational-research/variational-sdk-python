import pytest
import responses

from variational import Client, ApiError
import variational.client

URL = "https://api.test/v1/status"


def make_client(**kwargs):
    return Client("key", "00ff", base_url="https://api.test/v1", **kwargs)


@responses.activate
def test_json_error_envelope():
    responses.get(URL, status=400, json={"error": {"code": 42, "message": "bad"}})

    with pytest.raises(ApiError) as e:
        make_client().get_status()

    assert e.value.status_code == 400
    assert e.value.api_code == 42
    assert e.value.message == "bad"


@responses.activate
def test_non_json_error_body():
    responses.get(URL, status=502, body="<html>502 Bad Gateway</html>")

    with pytest.raises(ApiError) as e:
        make_client().get_status()

    assert e.value.status_code == 502
    assert e.value.api_code == -1
    assert "502 Bad Gateway" in e.value.message


@responses.activate
def test_empty_error_body():
    responses.get(URL, status=503, body="")

    with pytest.raises(ApiError) as e:
        make_client().get_status()

    assert e.value.status_code == 503
    assert e.value.api_code == -1


@responses.activate
def test_rate_limit_retries_are_bounded(monkeypatch):
    monkeypatch.setattr(variational.client.time, "sleep", lambda _: None)
    responses.get(
        URL,
        status=429,
        headers={"x-rate-limit-resets-in-ms": "10"},
        json={"error": {"code": 429, "message": "rate limited"}},
    )

    with pytest.raises(ApiError) as e:
        make_client(max_rate_limit_retries=3).get_status()

    assert e.value.status_code == 429
    # the first attempt plus three retries
    assert len(responses.calls) == 4


@responses.activate
def test_rate_limit_retry_then_success(monkeypatch):
    monkeypatch.setattr(variational.client.time, "sleep", lambda _: None)
    responses.get(URL, status=429, headers={"x-rate-limit-resets-in-ms": "10"})
    responses.get(
        URL,
        status=200,
        headers={"x-request-received-ms": "1700000000000"},
        json={"result": {"ok": True}},
    )

    assert make_client().get_status().result == {"ok": True}
    assert len(responses.calls) == 2
