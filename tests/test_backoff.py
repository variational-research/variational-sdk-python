from variational import Client
from variational.client import ExpBackoff


class FakeResponse:
    def __init__(self, status_code, headers, data):
        self.status_code = status_code
        self.headers = headers
        self.data = data

    def json(self):
        return self.data


class SequenceSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    def send(self, request, timeout=None):
        self.calls += 1
        return next(self.responses)


def test_backoff():
    base = 0.2
    factor = 1.2
    randomize = 0.2

    backoff = ExpBackoff(base, factor, randomize)

    d1 = backoff.next_delay()
    b1 = base
    assert b1 * (1 - randomize) <= d1 <= b1 * (1 + randomize)

    d2 = backoff.next_delay()
    b2 = b1 * factor
    assert b2 * (1 - randomize) <= d2 <= b2 * (1 + randomize)

    d3 = backoff.next_delay()
    b3 = b2 * factor
    assert b3 * (1 - randomize) <= d3 <= b3 * (1 + randomize)


def test_zero_rate_limit_reset_is_retried(monkeypatch):
    client = Client("key", "00" * 32, retry_rate_limits=True)
    session = SequenceSession(
        [
            FakeResponse(
                429,
                {"x-rate-limit-resets-in-ms": "0"},
                {"error": {"code": 429, "message": "rate limited"}},
            ),
            FakeResponse(
                200,
                {"x-request-received-ms": "1000"},
                {"result": {"server_timestamp_ms": 1000, "auth": None}},
            ),
        ]
    )
    monkeypatch.setattr(client, "sesh", session)
    sleeps = []
    monkeypatch.setattr("variational.client.time.sleep", sleeps.append)
    monkeypatch.setattr("variational.client.ExpBackoff.next_delay", lambda self: 0.2)

    response = client.get_status()

    assert response.result["server_timestamp_ms"] == 1000
    assert session.calls == 2
    assert sleeps == [0.2]
