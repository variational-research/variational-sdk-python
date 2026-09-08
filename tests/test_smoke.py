from importlib.metadata import requires

from variational import Client


def test_smoke():
    Client("key", "secret")


def test_requests_lower_bound_metadata():
    package_requirements = requires("variational")
    assert package_requirements is not None
    assert "requests>=2.31" in package_requirements
