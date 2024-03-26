from typing import TypedDict, Optional, List, Dict

from .aliases import (DateTimeRFC3339, UUIDv4, H160, StrDecimal, AssetToken)
from .nested import (Instrument, AtomicDepositDetails, ClearingEvent, MarginParams,
                     PoolMarginUsageStats, Leg, StructurePrice, RFQLeg, QuoteCommonMetadata,
                     QuoteWithMarginRequirements, FundingRateParams)
from .enums import (ClearingStatus, SettlementPoolStatus, RFQStatus, TradeSide, TradeType,
                    TradeRole, TransferType, TransferStatus, ApiRole)


class Address(TypedDict):
    created_at: Optional[DateTimeRFC3339]
    company: UUIDv4
    address: H160
    enabled: bool


class Position(TypedDict):
    company: UUIDv4
    pool_location: UUIDv4
    instrument: Instrument
    updated_at: Optional[DateTimeRFC3339]
    qty: StrDecimal
    avg_entry_price: StrDecimal


class AggregatedPosition(TypedDict):
    price: StrDecimal
    underlying_price: StrDecimal
    iv: StrDecimal
    sum_delta: StrDecimal
    sum_gamma: StrDecimal
    upnl: StrDecimal
    notional: StrDecimal
    sum_rho: StrDecimal
    sum_theta: StrDecimal
    sum_vega: StrDecimal
    position_info: Position


class Asset(TypedDict):
    company: UUIDv4
    pool_location: UUIDv4
    asset: AssetToken
    qty: StrDecimal


class AuthContext(TypedDict):
    key_id: UUIDv4
    company_id: UUIDv4
    role: ApiRole


class Company(TypedDict):
    id: UUIDv4
    created_at: Optional[DateTimeRFC3339]
    legal_name: str
    short_name: str
    is_lp: bool


class LegQuote(TypedDict):
    target_rfq_leg_id: UUIDv4
    ask: Optional[StrDecimal]
    bid: Optional[StrDecimal]


class MakerLastLookResponse(TypedDict):
    new_clearing_status: ClearingStatus
    pending_deposits_sum_qty: StrDecimal
    atomic_deposit_details: Optional[AtomicDepositDetails]


class PortfolioSummary(TypedDict):
    sum_balance: StrDecimal
    sum_delta: StrDecimal
    sum_gamma: StrDecimal
    sum_upnl: StrDecimal
    sum_notional: StrDecimal
    sum_rho: StrDecimal
    sum_theta: StrDecimal
    sum_vega: StrDecimal
    sum_dollar_delta: StrDecimal
    sum_dollar_gamma: StrDecimal


class Quote(TypedDict):
    parent_quote_id: UUIDv4
    target_rfq_id: UUIDv4
    maker_company: UUIDv4
    expires_at: DateTimeRFC3339
    aggregated_bid: Optional[StrDecimal]
    aggregated_ask: Optional[StrDecimal]
    clearing_status: ClearingStatus
    clearing_events: List[ClearingEvent]
    new_pool_name: Optional[str]
    creator_params: Optional[MarginParams]
    other_params: Optional[MarginParams]
    pool_location: Optional[UUIDv4]
    per_leg_quotes: List[LegQuote]


class SettlementPoolData(TypedDict):
    status: SettlementPoolStatus
    pool_name: str
    pool_address: Optional[H160]
    creator_address: H160
    other_address: H160
    positions: List[AggregatedPosition]
    creator_company_margin_usage: PoolMarginUsageStats
    other_company_margin_usage: PoolMarginUsageStats


class SettlementPool(TypedDict):
    pool_id: UUIDv4
    company_id: UUIDv4
    data: Optional[SettlementPoolData]
    error: Optional[str]


class QuoteAcceptResponse(TypedDict):
    pending_deposits_sum_qty: StrDecimal
    pending_settlement_pool: Optional[SettlementPool]
    new_clearing_status: ClearingStatus


class Structure(TypedDict):
    legs: List[Leg]


class RFQ(TypedDict):
    rfq_id: UUIDv4
    created_at: DateTimeRFC3339
    structure: Structure
    structure_price: Optional[StructurePrice]
    rfq_expires_at: DateTimeRFC3339
    taker_company: UUIDv4
    rfq_status: RFQStatus
    qty: StrDecimal
    rfq_legs: List[RFQLeg]
    quotes_common_metadata: Dict[UUIDv4, QuoteCommonMetadata]
    bids: List[QuoteWithMarginRequirements]
    asks: List[QuoteWithMarginRequirements]


class Status(TypedDict):
    auth: Optional[AuthContext]
    server_timestamp_ms: int


class SupportedAssetDetails(TypedDict):
    asset: AssetToken
    asset_name: str
    is_dex: bool
    address: Optional[H160]
    verified: Optional[bool]
    precision: int
    last_updated_at: DateTimeRFC3339
    variational_funding_rate_params: FundingRateParams


class Trade(TypedDict):
    id: UUIDv4
    source_rfq: Optional[UUIDv4]
    source_rfq_leg_id: Optional[UUIDv4]
    source_quote: Optional[UUIDv4]
    company: UUIDv4
    created_at: Optional[DateTimeRFC3339]
    side: TradeSide
    instrument: Instrument
    price: StrDecimal
    qty: StrDecimal
    pool_location: UUIDv4
    role: TradeRole
    trade_type: TradeType


class Transfer(TypedDict):
    id: UUIDv4
    rfq_id: Optional[UUIDv4]
    parent_quote_id: Optional[UUIDv4]
    oracle_request_id: Optional[UUIDv4]
    created_at: DateTimeRFC3339
    company: UUIDv4
    qty: StrDecimal
    asset: AssetToken
    target_pool_location: UUIDv4
    transfer_type: TransferType
    status: TransferStatus
