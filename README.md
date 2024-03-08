# Variational SDK for Python 

## Documentation

https://docs.variational.io/for-developers/api

## Quickstart

### 1. Create API credentials

Navigate to the API settings page at https://testnet.variational.io/app/settings

<img width="1033" alt="Variational / Settings / API" src="https://github.com/variational-research/variational-sdk-python/assets/155017661/b2cb472b-7742-4c74-9836-12dee28dcfb8">

Add a descriptive label, create your key, and make sure to save the secret as it's only displayed once.

### 2. Install Python SDK

```
pip install variational
```

### 3. Make some requests!

```python
from variational import Client, TESTNET
from pprint import pprint

# FIXME: load from environment variables
API_KEY = "your-api-key"
API_SECRET = "your-api-secret"

client = Client(API_KEY, API_SECRET, base_url=TESTNET)
summary = client.get_portfolio_summary().result
pprint(summary)
```

**Client parameters:**
 - `key`: str (required) — your API key
 - `secret`: str (required) — your API secret
 - `base_url`: str (optional) — prefix of Variational API endpoints
 - `request_timeout`: float (default=None) — timeout for individual HTTP requests
 - `retry_rate_limits`: bool (default=True) — enables automatic retry on HTTP 429 errors


### 4. Explore

Visit [Endpoint Reference](https://docs.variational.io/for-developers/api/endpoints) to learn which API calls are supported.

Read about the [Pagination](https://docs.variational.io/for-developers/api/pagination) mechanism used by Variational API.

Learn how [Rate Limits](https://docs.variational.io/for-developers/api/rate-limits) and [Authentication](https://docs.variational.io/for-developers/api/authentication) are applied to your calls.
