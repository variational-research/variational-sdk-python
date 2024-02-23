from variational.client import ExpBackoff


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
