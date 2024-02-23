# Variational SDK for Python 

## Documentation

https://docs.variational.io/for-developers/api

## Quickstart

### 1. Create API credentials

Navigate to the API section at https://testnet.variational.io/app/settings

<img width="1033" alt="Variational / Settings / API" src="https://github.com/variational-research/variational-sdk-python/assets/155017661/b2cb472b-7742-4c74-9836-12dee28dcfb8">

Create your key and make sure to save the secret part as it's only displayed once.

### 2. Install Python SDK

```
pip install variational
```

### 3. Make some calls!

```python
from variational import Client, TESTNET, paginate

client = Client(API_KEY, API_SECRET, base_url=TESTNET)
# if you have a lot of trades in the account, this might make multiple requests to fetch all of them
trades = list(paginate(client.get_portfolio_trades))
```

### 4. Explore

Visit [Endpoint Reference](https://docs.variational.io/for-developers/api/endpoints) to learn which API calls are supported.

Read about the [Pagination](https://docs.variational.io/for-developers/api/pagination) mechanism used by Variational API.

Learn how [Rate Limits](https://docs.variational.io/for-developers/api/rate-limits) and [Authentication](https://docs.variational.io/for-developers/api/authentication) are applied to your calls.
