# Variational SDK for Python 

> [!NOTE]
> API key generation is currently unavailable. Please contact our team via hello@variational.io if you are interested in using the API service.

## Documentation

https://docs.variational.io/for-developers/api

## Quickstart

### 1. Request API credentials

API key generation is currently unavailable through the Variational app. Please contact the Variational team at hello@variational.io to request access to the API service and obtain credentials.

### 2. Install Python SDK

```
pip install variational
```

### 3. Make some requests!

Store your API credentials in environment variables before running the example:

```bash
export VARIATIONAL_API_KEY="your-api-key"
export VARIATIONAL_API_SECRET="your-api-secret"
```

```python
import os
from pprint import pprint

from variational import Client, TESTNET

API_KEY = os.environ["VARIATIONAL_API_KEY"]
API_SECRET = os.environ["VARIATIONAL_API_SECRET"]

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
