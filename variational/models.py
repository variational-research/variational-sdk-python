from enum import StrEnum
from typing import TypeAlias, TypedDict, Optional, Union, Dict, List

AssetToken: TypeAlias = str  # e.g. "BTC", "ETH", etc
DateTimeRFC3339: TypeAlias = str  # e.g. "2024-02-02T06:13:45.323432Z"
H160: TypeAlias = str  # e.g. "0x3d68316712565ccb7f14a2bfc6aa785d6d2d12d5"
StrDecimal: TypeAlias = str  # e.g. "218205.58082"
UUIDv4: TypeAlias = str  # e.g. "bdd68c99-65fe-4500-baae-5bc09b4af183"


# Enums

class ApiRole(StrEnum):
    READER = "reader"
    WRITER = "writer"


class ClearingStatus(StrEnum):
    PENDING_TAKER_DEPOSIT_APPROVAL = "pending_taker_deposit_approval"
    PENDING_MAKER_DEPOSIT_APPROVAL = "pending_maker_deposit_approval"
    PENDING_MAKER_LAST_LOOK = "pending_maker_last_look"
    PENDING_POOL_CREATION = "pending_pool_creation"
    PENDING_ATOMIC_DEPOSIT = "pending_atomic_deposit"
    REJECTED_FAILED_TAKER_DEPOSIT_APPROVAL = "rejected_failed_taker_deposit_approval"
    REJECTED_FAILED_MAKER_DEPOSIT_APPROVAL = "rejected_failed_maker_deposit_approval"
    REJECTED_MAKER_LAST_LOOK_REJECTED = "rejected_maker_last_look_rejected"
    REJECTED_MAKER_LAST_LOOK_EXPIRED = "rejected_maker_last_look_expired"
    REJECTED_FAILED_POOL_CREATION = "rejected_failed_pool_creation"
    REJECTED_FAILED_TAKER_FUNDING = "rejected_failed_taker_funding"
    REJECTED_FAILED_MAKER_FUNDING = "rejected_failed_maker_funding"
    REJECTED_FAILED_ATOMIC_DEPOSIT = "rejected_failed_atomic_deposit"
    SUCCESS_TRADES_BOOKED_INTO_POOL = "success_trades_booked_into_pool"


class ExerciseType(StrEnum):
    EUROPEAN = "european"
    AMERICAN = "american"


class InstrumentType(StrEnum):
    SPOT = "spot"
    DATED_FUTURE = "dated_future"
    PERPETUAL_FUTURE = "perpetual_future"
    VANILLA_OPTION = "vanilla_option"


class MarginMode(StrEnum):
    SIMPLE = "simple"
    PORTFOLIO = "portfolio"


class PayoffType(StrEnum):
    PUT = "put"
    CALL = "call"


class PoolStrategyType(StrEnum):
    USE_EXISTING = "use_existing"
    CREATE_NEW = "create_new"


class RFQStatus(StrEnum):
    OPEN = "open"
    EXPIRED = "expired"
    CANCELED = "canceled"
    CLOSED = "closed"


class RequestAction(StrEnum):
    REJECT = "reject"
    ACCEPT = "accept"


class SettlementPoolStatus(StrEnum):
    OPEN = "open"
    PENDING = "pending"
    CANCELED = "canceled"


class TradeRole(StrEnum):
    MAKER = "maker"
    TAKER = "taker"


class TradeSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class TradeType(StrEnum):
    TRADE = "trade"
    SETTLEMENT = "settlement"
    LIQUIDATION = "liquidation"


class TransferStatus(StrEnum):
    PENDING = "pending"
    FAILED = "failed"
    CONFIRMED = "confirmed"


class TransferType(StrEnum):
    PREMIUM = "premium"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SETTLEMENT = "settlement"
    LIQUIDATION = "liquidation"
    REALIZED_PNL = "realized_pnl"
    INITIAL_MARGIN = "initial_margin"


# Nested models

class AtomicDepositDetails(TypedDict):
    rfq_id: UUIDv4
    parent_quote_id: UUIDv4
    pool_address: H160
    creator_address: H160
    creator_transfer_amount: StrDecimal
    other_address: H160
    other_transfer_amount: StrDecimal


class ClearingEvent(TypedDict):
    rfq_id: UUIDv4
    parent_quote_id: UUIDv4
    status: ClearingStatus
    created_at: DateTimeRFC3339
    taker_side: Optional[TradeSide]


class CreateNewPool(TypedDict):
    strategy: PoolStrategyType  # == CREATE_NEW
    name: str
    creator_params: 'MarginParams'
    other_params: 'MarginParams'


class DatedFuture(TypedDict):
    instrument_type: InstrumentType  # == DATED_FUTURE
    underlying: str
    settlement_asset: str
    expiry: DateTimeRFC3339


class FundingRateParams(TypedDict):
    normal_threshold: StrDecimal
    high_threshold: StrDecimal
    extreme_threshold: StrDecimal
    normal_slope: StrDecimal
    high_slope: StrDecimal
    extreme_slope: StrDecimal
    min_imbalance_dollars: StrDecimal
    funding_exponent_factor: StrDecimal


class Leg(TypedDict):
    side: TradeSide
    ratio: int
    instrument: 'Instrument'


class MarginUsage(TypedDict):
    initial_margin: StrDecimal
    maintenance_margin: StrDecimal


class PerpetualFuture(TypedDict):
    instrument_type: InstrumentType  # == PERPETUAL_FUTURE
    underlying: str
    settlement_asset: str
    funding_interval_s: int


class PoolMarginUsageStats(TypedDict):
    company: UUIDv4
    balance: StrDecimal
    margin_params: 'MarginParams'
    margin_usage: MarginUsage


class PortfolioMarginAssetParam(TypedDict):
    vol_range_up: StrDecimal
    vol_range_down: StrDecimal
    short_vega_power: StrDecimal
    long_vega_power: StrDecimal
    price_range: StrDecimal
    opt_sum_contingency: StrDecimal
    opt_contingency: StrDecimal
    futures_contingency: StrDecimal
    atm_range: StrDecimal


class PortfolioMarginParams(TypedDict):
    asset_params: Dict[AssetToken, PortfolioMarginAssetParam]
    default_asset_param: PortfolioMarginAssetParam
    decorrelation_risk: StrDecimal
    initial_margin_factor: StrDecimal
    liquidation_penalty: StrDecimal
    auto_liquidation: bool


class PortfolioMarginParamsTag(TypedDict):
    margin_mode: MarginMode  # == PORTFOLIO
    params: PortfolioMarginParams


class QuoteCommonMetadata(TypedDict):
    parent_quote_id: UUIDv4
    maker_company: UUIDv4
    clearing_status: Optional[ClearingStatus]
    expires_at: DateTimeRFC3339
    pool_location: Optional[UUIDv4]
    new_pool_name: Optional[str]
    creator_params: Optional['MarginParams']
    other_params: Optional['MarginParams']
    pool_creator_company: Optional[UUIDv4]
    pool_other_company: Optional[UUIDv4]
    pool_creator_params: Optional['MarginParams']
    pool_other_params: Optional['MarginParams']
    clearing_events: List[ClearingEvent]


class QuoteWithMarginRequirements(TypedDict):
    parent_quote_id: UUIDv4
    quote_price: StrDecimal
    counter_factual_margin_requirements: Optional[MarginUsage]
    existing_margin_requirements: Optional[MarginUsage]
    additional_margin_requirements: Optional[MarginUsage]
    margin_requirements_counter_factual_request_id: UUIDv4
    existing_margin_requirements_request_id: UUIDv4


class RFQLeg(TypedDict):
    rfq_leg_id: UUIDv4
    rfq_id: UUIDv4
    instrument: 'Instrument'
    side: TradeSide
    qty: StrDecimal


class SettlementPoolData(TypedDict):
    status: SettlementPoolStatus
    pool_name: str
    pool_address: Optional[H160]
    creator_address: H160
    other_address: H160
    positions: List['AggregatedPosition']
    creator_company_margin_usage: PoolMarginUsageStats
    other_company_margin_usage: PoolMarginUsageStats


class SimpleMarginAssetParam(TypedDict):
    futures_initial_margin: StrDecimal
    futures_maintenance_margin: StrDecimal
    futures_leverage: StrDecimal
    option_initial_margin: StrDecimal
    option_initial_margin_min: StrDecimal
    option_maintenance_margin: StrDecimal


class SimpleMarginParams(TypedDict):
    asset_params: Dict[AssetToken, SimpleMarginAssetParam]
    default_asset_param: SimpleMarginAssetParam
    liquidation_penalty: StrDecimal
    auto_liquidation: bool


class SimpleMarginParamsTag(TypedDict):
    margin_mode: MarginMode  # == SIMPLE
    params: SimpleMarginParams


class Spot(TypedDict):
    instrument_type: InstrumentType  # == SPOT
    underlying: str
    settlement_asset: str


class StructurePrice(TypedDict):
    price: StrDecimal
    native_price: StrDecimal
    delta: StrDecimal
    gamma: StrDecimal
    theta: StrDecimal
    vega: StrDecimal
    rho: StrDecimal
    timestamp: DateTimeRFC3339


class UseExistingPool(TypedDict):
    strategy: PoolStrategyType  # == USE_EXISTING
    pool_id: UUIDv4


class VanillaOption(TypedDict):
    instrument_type: InstrumentType  # == VANILLA_OPTION
    underlying: str
    settlement_asset: str
    expiry: DateTimeRFC3339
    strike: StrDecimal
    payoff: PayoffType
    exercise: ExerciseType


# Top-level models

class Address(TypedDict):
    created_at: Optional[DateTimeRFC3339]
    company: UUIDv4
    address: H160
    enabled: bool


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
    position_info: 'Position'


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


Instrument = Union[Spot, DatedFuture, PerpetualFuture, VanillaOption]


class InstrumentPrice(TypedDict):
    price: StrDecimal
    native_price: StrDecimal
    delta: StrDecimal
    gamma: StrDecimal
    theta: StrDecimal
    vega: StrDecimal
    rho: StrDecimal
    iv: StrDecimal
    underlying_price: StrDecimal
    interest_rate: StrDecimal
    timestamp: DateTimeRFC3339


class LegQuote(TypedDict):
    target_rfq_leg_id: UUIDv4
    ask: Optional[StrDecimal]
    bid: Optional[StrDecimal]


class MakerLastLookResponse(TypedDict):
    new_clearing_status: ClearingStatus
    pending_deposits_sum_qty: StrDecimal
    atomic_deposit_details: Optional[AtomicDepositDetails]


MarginParams = Union[SimpleMarginParamsTag, PortfolioMarginParamsTag]


PoolStrategy = Union[UseExistingPool, CreateNewPool]


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


class Position(TypedDict):
    company: UUIDv4
    pool_location: UUIDv4
    instrument: Instrument
    updated_at: Optional[DateTimeRFC3339]
    qty: StrDecimal
    avg_entry_price: StrDecimal


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


class QuoteAcceptResponse(TypedDict):
    pending_deposits_sum_qty: StrDecimal
    pending_settlement_pool: Optional['SettlementPool']
    new_clearing_status: ClearingStatus


class RFQ(TypedDict):
    rfq_id: UUIDv4
    created_at: DateTimeRFC3339
    structure: 'Structure'
    structure_price: Optional[StructurePrice]
    rfq_expires_at: DateTimeRFC3339
    taker_company: UUIDv4
    rfq_status: RFQStatus
    qty: StrDecimal
    rfq_legs: List[RFQLeg]
    quotes_common_metadata: Dict[UUIDv4, QuoteCommonMetadata]
    bids: List[QuoteWithMarginRequirements]
    asks: List[QuoteWithMarginRequirements]


class SettlementPool(TypedDict):
    pool_id: UUIDv4
    company_id: UUIDv4
    data: Optional[SettlementPoolData]
    error: Optional[str]


class Status(TypedDict):
    auth: Optional[AuthContext]
    server_timestamp_ms: int


class Structure(TypedDict):
    legs: List[Leg]


class StructurePriceResponse(TypedDict):
    legs: List[InstrumentPrice]
    structure: StructurePrice


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
