import logging
import random
import time
from typing import Optional, Dict, Mapping, List
from urllib.parse import urlencode

import requests

from .auth import sign_prepared_request
from .models import (StrDecimal, DateTimeRFC3339, H160, Allowance, AssetToken, UUIDv4, Company,
                     Address, SettlementPool, Asset, Position, AggregatedPosition, Trade, Transfer,
                     PortfolioSummary, Quote, RFQ, SupportedAssetDetails, AuthContext, Status,
                     Structure, PoolStrategy, LegQuote, QuoteAcceptResponse, MakerLastLookResponse,
                     MarginParams, TradeSide, TransferType, RequestAction, StructurePriceResponse,
                     Instrument, InstrumentPrice)
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

    def accept_quote(self, rfq_id: UUIDv4, parent_quote_id: UUIDv4,
                     side: TradeSide) -> ApiSingle[QuoteAcceptResponse]:
        payload = {
            "parent_quote_id": parent_quote_id,
            "rfq_id": rfq_id,
            "side": side,
        }

        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/accept",
                                                           method="POST", payload=payload))

    def cancel_all_quotes(self) -> ApiSingle[bool]:
        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/cancel_all",
                                                           method="POST"))

    def cancel_quote(self, id: UUIDv4) -> ApiSingle[bool]:
        payload = {'id': id}
        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/cancel",
                                                           method="POST", payload=payload))

    def cancel_rfq(self, id: UUIDv4) -> ApiSingle[bool]:
        payload = {'id': id}
        return ApiSingle.from_response(self.__send_request(endpoint="/rfqs/cancel",
                                                           method="POST", payload=payload))

    def create_quote(self, rfq_id: UUIDv4, expires_at: DateTimeRFC3339, leg_quotes: List[LegQuote],
                     pool_strategy: PoolStrategy,
                     client_quote_id: Optional[str] = None) -> ApiSingle[Quote]:
        payload = {
            "rfq_id": rfq_id,
            "expires_at": expires_at,
            "leg_quotes": leg_quotes,
            "pool_strategy": pool_strategy,
            "client_quote_id": client_quote_id,
        }

        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/new",
                                                           method="POST", payload=payload))

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

    def create_settlement_pool(self, pool_name: str, company_other: UUIDv4,
                               creator_params: MarginParams,
                               other_params: MarginParams) -> ApiSingle[SettlementPool]:
        payload = {
            "pool_name": pool_name,
            "company_other": company_other,
            "creator_params": creator_params,
            "other_params": other_params,
        }
        return ApiSingle.from_response(self.__send_request(endpoint="/settlement_pools/new",
                                                           method="POST", payload=payload))

    def create_transfer(self, asset: AssetToken, qty: StrDecimal,
                        target_pool_location: UUIDv4,
                        transfer_type: TransferType) -> ApiSingle[Transfer]:
        payload = {
            'asset': asset,
            'qty': qty,
            'target_pool_location': target_pool_location,
            'transfer_type': transfer_type,
        }
        return ApiSingle.from_response(self.__send_request(endpoint="/transfers/new",
                                                           method="POST", payload=payload))

    def generate_transfer_permit(self, pool_address: H160, allowance: Allowance,
                                 seconds_until_expiry: Optional[int] = None) -> ApiSingle[dict]:
        payload = {
            "pool_address": pool_address,
            "allowance": allowance,
            "seconds_until_expiry": seconds_until_expiry,
        }
        return ApiSingle.from_response(self.__send_request(
            endpoint="/transfers/permit/template", method="POST", payload=payload))

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

    def get_me(self) -> ApiSingle[AuthContext]:
        return ApiSingle.from_response(self.__send_request(endpoint="/me"))

    def get_portfolio_aggregated_positions(self,
                                           page: Optional[Dict] = None
                                           ) -> ApiPage[AggregatedPosition]:
        return ApiPage.from_response(self.__send_request(
            endpoint="/portfolio/positions/aggregated", page=page))

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

    def get_portfolio_summary(self) -> ApiSingle[PortfolioSummary]:
        return ApiSingle.from_response(self.__send_request(endpoint="/portfolio/summary"))

    def get_portfolio_trades(self, pool: Optional[UUIDv4] = None, id: Optional[UUIDv4] = None,
                             page: Optional[Dict] = None) -> ApiPage[Trade]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/portfolio/trades",
                                                         filter=filter, page=page))

    def get_transfers(self, pool: Optional[UUIDv4] = None, id: Optional[UUIDv4] = None,
                      page: Optional[Dict] = None) -> ApiPage[Transfer]:
        filter = {}
        if pool:
            filter['pool'] = pool
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/transfers",
                                                         filter=filter, page=page))

    def get_quotes(self, id: Optional[UUIDv4] = None,
                   page: Optional[Dict] = None) -> ApiPage[Quote]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/quotes",
                                                         filter=filter, page=page))

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

    def get_rfqs_sent(self, id: Optional[UUIDv4] = None,
                      page: Optional[Dict] = None) -> ApiPage[RFQ]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/rfqs/sent",
                                                         filter=filter, page=page))

    def get_settlement_pools(self, id: Optional[UUIDv4] = None,
                             page: Optional[Dict] = None) -> ApiPage[SettlementPool]:
        filter = {}
        if id:
            filter['id'] = id
        return ApiPage.from_response(self.__send_request(endpoint="/settlement_pools",
                                                         filter=filter, page=page))

    def get_status(self) -> ApiSingle[Status]:
        return ApiSingle.from_response(self.__send_request(endpoint="/status"))

    def get_supported_assets(self, verified: Optional[bool] = False) \
            -> ApiSingle[Dict[AssetToken, List[SupportedAssetDetails]]]:
        filter = {}
        if verified:
            filter['verified'] = 'true'
        return ApiSingle.from_response(self.__send_request(
            endpoint="/metadata/supported_assets", filter=filter))

    def maker_last_look(self, rfq_id: UUIDv4, parent_quote_id: UUIDv4,
                        action: RequestAction) -> ApiSingle[MakerLastLookResponse]:
        payload = {
            "parent_quote_id": parent_quote_id,
            "rfq_id": rfq_id,
            "action": action,
        }
        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/maker_last_look",
                                                           method="POST", payload=payload))

    def price_instrument(self, instrument: Instrument) -> ApiSingle[InstrumentPrice]:
        return ApiSingle.from_response(self.__send_request(
            endpoint="/price/instrument", method="POST", payload=instrument))

    def price_structure(self, structure: Structure) -> ApiSingle[StructurePriceResponse]:
        return ApiSingle.from_response(self.__send_request(endpoint="/price/structure",
                                                           method="POST", payload=structure))

    def replace_quote(self, parent_quote_id: UUIDv4, rfq_id: UUIDv4, expires_at: DateTimeRFC3339,
                      leg_quotes: List[LegQuote],
                      pool_strategy: PoolStrategy,
                      client_quote_id: Optional[str] = None) -> ApiSingle[Quote]:
        payload = {
            "parent_quote_id": parent_quote_id,
            "rfq_id": rfq_id,
            "expires_at": expires_at,
            "leg_quotes": leg_quotes,
            "pool_strategy": pool_strategy,
            "client_quote_id": client_quote_id,
        }

        return ApiSingle.from_response(self.__send_request(endpoint="/quotes/replace",
                                                           method="POST", payload=payload))

    def submit_transfer_permit(self, message: dict, signature: str) -> ApiSingle[bool]:
        payload = {
            "message": message,
            "signature": signature,
        }
        return ApiSingle.from_response(self.__send_request(endpoint="/transfers/permit",
                                                           method="POST", payload=payload))

    def __send_request(self, endpoint: str, method: str = "GET",
                       payload: Optional[Dict | List] = None, filter: Optional[Dict] = None,
                       page: Optional[Dict] = None) -> requests.Response:
        params = {}
        if filter:
            params.update(filter)
        if page:
            params.update(page)

        qs = ("?" + urlencode(params)) if params else ''
        backoff = ExpBackoff()

        full_url = self.base_url + endpoint + qs
        while True:
            req = requests.Request(method=method, url=full_url, json=payload).prepare()
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
            raise ApiError(url=full_url, status_code=resp.status_code,
                           api_code=data['error']['code'], message=data['error']['message'])


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
