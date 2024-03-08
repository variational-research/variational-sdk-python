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
from variational import Client, TESTNET, paginate

client = Client(API_KEY, API_SECRET, base_url=TESTNET)
trades = list(paginate(client.get_portfolio_trades))
```

Note: if you have a lot of trades in the account, it might make multiple requests and take a significant amount of time
to fetch all of them.  
See [Pagination](https://docs.variational.io/for-developers/api/pagination) for potential debugging steps.

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
