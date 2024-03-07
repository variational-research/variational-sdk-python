import time
import random
from typing import Optional, Dict, Mapping, List
from urllib.parse import urlencode

import requests
import logging

from .auth import sign_prepared_request
from .models import (Address, Company, SettlementPool, Asset, Position, AggregatedPosition,
                     Trade, Transfer, PortfolioSummary, Quote, Status, AuthContext, RFQ, AssetToken,
                     SupportedAssetDetails)
from .wrappers import ApiSingle, ApiList, ApiPage, ApiError

RATE_LIMIT_RESET_MS_HEADER = "x-rate-limit-reset-ms"
MAINNET = "https://api.variational.io/v1"
TESTNET = "https://api.testnet.variational.io/v1"


class Client(object):
    def __init__(self, key: str, secret: str, base_url: str = MAINNET, retry_rate_limits=True):
        self.sesh = requests.session()
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.retry_rate_limits = retry_rate_limits

    def get_addresses(self, company: Optional[str] = None) -> ApiList[Address]:
        f = {}
        if company:
            f['company'] = company
        return ApiList.from_response(self.__get_resources("/addresses", filter=f))

    def get_companies(self, id: Optional[str] = None,
                      page: Optional[Dict] = None) -> ApiPage[Company]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/companies", filter, page))

    def get_settlement_pools(self, id: Optional[str] = None,
                             page: Optional[Dict] = None) -> ApiPage[SettlementPool]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/settlement_pools", filter, page))

    def get_portfolio_assets(self, pool: Optional[str] = None,
                             page: Optional[Dict] = None) -> ApiPage[Asset]:
        filter = {}
        if pool:
            filter['pool'] = pool
        return ApiPage.from_response(self.__get_resources("/portfolio/assets", filter, page))

    def get_portfolio_positions(self, pool: Optional[str] = None,
                                page: Optional[Dict] = None) -> ApiPage[Position]:
        filter = {}
        if pool:
            filter['pool'] = pool
        return ApiPage.from_response(self.__get_resources("/portfolio/positions", filter, page))

    def get_portfolio_aggregated_positions(self,
                                           page: Optional[Dict] = None
                                           ) -> ApiPage[AggregatedPosition]:
        return ApiPage.from_response(self.__get_resources(
            "/portfolio/positions/aggregated", page=page))

    def get_portfolio_trades(self, pool: Optional[str] = None, id: Optional[str] = None,
                             page: Optional[Dict] = None) -> ApiPage[Trade]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/portfolio/trades", filter, page))

    def get_portfolio_transfers(self, pool: Optional[str] = None, id: Optional[str] = None,
                                page: Optional[Dict] = None) -> ApiPage[Transfer]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/portfolio/transfers", filter, page))

    def get_portfolio_summary(self) -> ApiSingle[PortfolioSummary]:
        return ApiSingle.from_response(self.__get_resources("/portfolio/summary"))

    def get_quotes_received(self, id: Optional[str] = None,
                            page: Optional[Dict] = None) -> ApiPage[Quote]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/quotes/received", filter, page))

    def get_quotes_sent(self, id: Optional[str] = None,
                        page: Optional[Dict] = None) -> ApiPage[Quote]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/quotes/sent", filter, page))

    def get_rfqs_received(self, id: Optional[str] = None,
                          page: Optional[Dict] = None) -> ApiPage[RFQ]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/rfqs/received", filter, page))

    def get_rfqs_sent(self, id: Optional[str] = None, page: Optional[Dict] = None) -> ApiPage[RFQ]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__get_resources("/rfqs/sent", filter, page))

    def get_supported_assets(self, verified: Optional[bool] = False, page: Optional[Dict] = None) \
            -> ApiSingle[Dict[AssetToken, List[SupportedAssetDetails]]]:
        filter = {}
        if verified:
            filter['verified'] = 'true'
        return ApiSingle.from_response(self.__get_resources(
            "/metadata/supported_assets", filter, page))

    def get_status(self) -> ApiSingle[Status]:
        return ApiSingle.from_response(self.__get_resources("/status"))

    def get_me(self) -> ApiSingle[AuthContext]:
        return ApiSingle.from_response(self.__get_resources("/me"))

    def __get_resources(self, endpoint: str, filter: Optional[Dict] = None,
                        page: Optional[Dict] = None) -> requests.Response:
        params = {}
        if filter:
            params.update(filter)
        if page:
            params.update(page)

        qs = ("?" + urlencode(params)) if params else ''
        backoff = ExpBackoff()

        while True:
            req = requests.Request(method="GET", url=self.base_url + endpoint + qs).prepare()
            resp = self.sesh.send(sign_prepared_request(req, self.key, self.secret))

            if resp.status_code == 200:
                return resp

            if self.retry_rate_limits and resp.status_code == 429:
                resets_at_timestamp = _get_rate_limit_reset_timestamp(
                    resp.headers)
                if resets_at_timestamp:
                    timestamp_now = time.time()

                    # delay until at least the timestamp specified in the header
                    if timestamp_now < resets_at_timestamp:
                        hard_delay = resets_at_timestamp - timestamp_now
                    else:
                        hard_delay = 0

                    # an extra delay that's slowly increasing with each attempt
                    delay = hard_delay + backoff.next_delay()

                    logging.debug("HTTP 429 Too Many Requests was returned from the API, "
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
