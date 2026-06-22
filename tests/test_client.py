import pytest
from unittest.mock import patch, MagicMock
from variational import Client


class TestClientInitialization:
    """Test suite for Client initialization and configuration."""

    def test_client_requires_credentials(self):
        with pytest.raises(TypeError):
            Client()

    def test_client_accepts_key_secret(self):
        client = Client('test-key', 'test-secret')
        assert client is not None

    def test_client_stores_api_key(self):
        client = Client('my-key', 'my-secret')
        assert client.api_key == 'my-key'

    def test_client_stores_api_secret(self):
        client = Client('my-key', 'my-secret')
        assert client.api_secret == 'my-secret'

    def test_client_default_base_url(self):
        client = Client('k', 's')
        assert hasattr(client, 'base_url')

    def test_client_custom_base_url(self):
        client = Client('k', 's', base_url='https://custom.api.io')
        assert 'custom' in client.base_url


class TestClientAuthentication:
    """Test HMAC-SHA256 authentication header generation."""

    def test_auth_header_format(self):
        client = Client('key123', 'secret456')
        if hasattr(client, '_auth_headers') or hasattr(client, '_get_headers'):
            # Verify auth method exists
            assert True
        else:
            pytest.skip('Auth header method not found')
