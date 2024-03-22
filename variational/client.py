import time
import random
from typing import Optional, Dict, Mapping, List
from urllib.parse import urlencode

import requests
import logging

from .auth import sign_prepared_request
from .models import (Address, Company, SettlementPool, Asset, Position, AggregatedPosition,
                     Trade, Transfer, PortfolioSummary, Quote, Status, AuthContext, RFQ, AssetToken,
                     SupportedAssetDetails, Structure, StrDecimal, DateTimeRFC3339, UUIDv4, LegQuote,
                     PoolStrategy)
from .wrappers import ApiSingle, ApiList, ApiPage, ApiError

RATE_LIMIT_RESET_MS_HEADER = "x-rate-limit-resets-in-ms"
MAINNET = "https://api.variational.io/v1"
TESTNET = "https://api.testnet.variational.io/v1"


class Client(object):
    def __init__(self, key: str, secret: str, base_url: str = MAINNET,
                 request_timeout: Optional[float] = None, retry_rate_limits=True):
        self.sesh = requests.session()
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.request_timeout = request_timeout
        self.retry_rate_limits = retry_rate_limits

    def get_addresses(self, company: Optional[UUIDv4] = None) -> ApiList[Address]:
        f = {}
        if company:
            f['company'] = company
        return ApiList.from_response(self.__send_request(endpoint="/addresses", filter=f))

    def get_companies(self, id: Optional[UUIDv4] = None,
                      page: Optional[Dict] = None) -> ApiPage[Company]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/companies",
                                                         filter=filter, page=page))

    def get_settlement_pools(self, id: Optional[UUIDv4] = None,
                             page: Optional[Dict] = None) -> ApiPage[SettlementPool]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/settlement_pools",
                                                         filter=filter, page=page))

    def get_portfolio_assets(self, pool: Optional[UUIDv4] = None,
                             page: Optional[Dict] = None) -> ApiPage[Asset]:
        filter = {}
        if pool:
            filter['pool'] = pool
        return ApiPage.from_response(self.__send_request(endpoint="/portfolio/assets",
                                                         filter=filter, page=page))

    def get_portfolio_positions(self, pool: Optional[UUIDv4] = None,
                                page: Optional[Dict] = None) -> ApiPage[Position]:
        filter = {}
        if pool:
            filter['pool'] = pool
        return ApiPage.from_response(self.__send_request(endpoint="/portfolio/positions",
                                                         filter=filter, page=page))

    def get_portfolio_aggregated_positions(self,
                                           page: Optional[Dict] = None
                                           ) -> ApiPage[AggregatedPosition]:
        return ApiPage.from_response(self.__send_request(
            endpoint="/portfolio/positions/aggregated", page=page))

    def get_portfolio_trades(self, pool: Optional[UUIDv4] = None, id: Optional[UUIDv4] = None,
                             page: Optional[Dict] = None) -> ApiPage[Trade]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/portfolio/trades",
                                                         filter=filter, page=page))

    def get_portfolio_transfers(self, pool: Optional[UUIDv4] = None, id: Optional[UUIDv4] = None,
                                page: Optional[Dict] = None) -> ApiPage[Transfer]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/portfolio/transfers",
                                                         filter=filter, page=page))

    def get_portfolio_summary(self) -> ApiSingle[PortfolioSummary]:
        return ApiSingle.from_response(self.__send_request(endpoint="/portfolio/summary"))

    def get_quotes_received(self, id: Optional[UUIDv4] = None,
                            page: Optional[Dict] = None) -> ApiPage[Quote]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/quotes/received",
                                                         filter=filter, page=page))

    def get_quotes_sent(self, id: Optional[UUIDv4] = None,
                        page: Optional[Dict] = None) -> ApiPage[Quote]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/quotes/sent",
                                                         filter=filter, page=page))

    def get_rfqs_received(self, id: Optional[UUIDv4] = None,
                          page: Optional[Dict] = None) -> ApiPage[RFQ]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/rfqs/received",
                                                         filter=filter, page=page))

    def get_rfqs_sent(self, id: Optional[UUIDv4] = None, page: Optional[Dict] = None) -> ApiPage[RFQ]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/rfqs/sent",
                                                         filter=filter, page=page))

    def get_supported_assets(self, verified: Optional[bool] = False, page: Optional[Dict] = None) \
            -> ApiSingle[Dict[AssetToken, List[SupportedAssetDetails]]]:
        filter = {}
        if verified:
            filter['verified'] = 'true'
        return ApiSingle.from_response(self.__send_request(
            endpoint="/metadata/supported_assets", filter=filter, page=page))

    def get_status(self) -> ApiSingle[Status]:
        return ApiSingle.from_response(self.__send_request(endpoint="/status"))

    def get_me(self) -> ApiSingle[AuthContext]:
        return ApiSingle.from_response(self.__send_request(endpoint="/me"))

    def create_rfq(self, structure: Structure, qty: StrDecimal, expires_at: DateTimeRFC3339,
                   target_companies: List[UUIDv4]) -> ApiSingle[RFQ]:

        payload = {
            "structure": structure,
            "qty": qty,
            "expires_at": expires_at,
            "target_companies": target_companies,
        }

        return ApiSingle.from_response(self.__send_request(endpoint="/rfqs/new",
                                                           method="POST", payload=payload))

    def create_quote(self, rfq_id: UUIDv4, expires_at: DateTimeRFC3339, leg_quotes: List[LegQuote],
                     pool_strategy: PoolStrategy,
                     client_quote_id: Optional[str] = None) -> ApiSingle[RFQ]:
        payload = {
            "rfq_id": rfq_id,
            "expires_at": expires_at,
            "leg_quotes": leg_quotes,
            "pool_strategy": pool_strategy,
            "client_quote_id": client_quote_id,
        }

        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/new",
                                                           method="POST", payload=payload))

    def __send_request(self, endpoint: str, method: str = "GET", payload: Optional[Dict] = None,
                       filter: Optional[Dict] = None,
                       page: Optional[Dict] = None) -> requests.Response:
        params = {}
        if filter:
            params.update(filter)
        if page:
            params.update(page)

        qs = ("?" + urlencode(params)) if params else ''
        backoff = ExpBackoff()

        while True:
            req = requests.Request(method=method, url=self.base_url + endpoint + qs,
                                   json=payload).prepare()
            resp = self.sesh.send(sign_prepared_request(req, self.key, self.secret),
                                  timeout=self.request_timeout)

            if resp.status_code == 200:
                return resp

            if self.retry_rate_limits and resp.status_code == 429:
                if resets_in := _get_rate_limit_reset_timestamp(resp.headers):
                    # delay for at least the amount specified in the header
                    # add an extra delay that's slowly increasing with each attempt
                    delay = resets_in + backoff.next_delay()

                    self.logger.warning("HTTP 429 Too Many Requests was returned from the API, "
                                        "will retry after delay: %.3fs", delay)
                    time.sleep(delay)
                    continue

            data = resp.json()
            raise ApiError(status_code=resp.status_code, api_code=data['error']['code'],
                           message=data['error']['message'])


class ExpBackoff:
    def __init__(self, base=0.2, factor=1.2, randomize=0.2):
        self.base = base
        self.factor = factor
        self.randomize = randomize
        self.next = base

    def next_delay(self):
        # random float in [1 - self.randomize, 1 + self.randomize)
        jitter = 1 - self.randomize + random.random() * self.randomize * 2
        delay = self.next * jitter
        self.next *= self.factor
        return delay


def _get_rate_limit_reset_timestamp(headers: Mapping) -> Optional[float]:
    for k, v in headers.items():
        if k.lower() == RATE_LIMIT_RESET_MS_HEADER:
            return int(v) / 1000
