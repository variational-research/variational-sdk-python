from typing import TypedDict, Optional, Union, Dict, List

from .aliases import (UUIDv4, H160, StrDecimal, DateTimeRFC3339, AssetToken)
from .enums import (ClearingStatus, TradeSide, InstrumentType, PayoffType, ExerciseType, MarginMode,
                    PoolStrategyType)


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


class FundingRateParams(TypedDict):
    normal_threshold: StrDecimal
    high_threshold: StrDecimal
    extreme_threshold: StrDecimal
    normal_slope: StrDecimal
    high_slope: StrDecimal
    extreme_slope: StrDecimal
    min_imbalance_dollars: StrDecimal


class Spot(TypedDict):
    instrument_type: InstrumentType  # == SPOT
    underlying: str
    settlement_asset: str


class DatedFuture(TypedDict):
    instrument_type: InstrumentType  # == DATED_FUTURE
    underlying: str
    settlement_asset: str
    expiry: DateTimeRFC3339


class PerpetualFuture(TypedDict):
    instrument_type: InstrumentType  # == PERPETUAL_FUTURE
    underlying: str
    settlement_asset: str
    funding_interval_s: int


class VanillaOption(TypedDict):
    instrument_type: InstrumentType  # == VANILLA_OPTION
    underlying: str
    settlement_asset: str
    expiry: DateTimeRFC3339
    strike: StrDecimal
    payoff: PayoffType
    exercise: ExerciseType


Instrument = Union[Spot, DatedFuture, PerpetualFuture, VanillaOption]


class SimpleMarginAssetParam(TypedDict):
    futures_initial_margin: StrDecimal
    futures_maintenance_margin: StrDecimal
    futures_leverage: StrDecimal
    option_initial_margin: StrDecimal
    option_initial_margin_min: StrDecimal
    option_maintenance_margin: StrDecimal


class SimpleMarginParams(TypedDict):
    asset_params: Dict[AssetToken, SimpleMarginAssetParam]
    liquidation_penalty: StrDecimal
    auto_liquidation: bool


class SimpleMarginParamsTag(TypedDict):
    margin_mode: MarginMode  # == SIMPLE
    params: SimpleMarginParams


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
    decorrelation_risk: StrDecimal
    initial_margin_factor: StrDecimal
    liquidation_penalty: StrDecimal
    auto_liquidation: bool


class PortfolioMarginParamsTag(TypedDict):
    margin_mode: MarginMode  # == PORTFOLIO
    params: PortfolioMarginParams


MarginParams = Union[SimpleMarginParamsTag, PortfolioMarginParamsTag]


class UseExistingPool(TypedDict):
    strategy: PoolStrategyType  # == USE_EXISTING
    pool_id: UUIDv4


class CreateNewPool(TypedDict):
    strategy: PoolStrategyType  # == CREATE_NEW
    name: str
    creator_params: MarginParams
    other_params: MarginParams


PoolStrategy = Union[UseExistingPool, CreateNewPool]


class Leg(TypedDict):
    side: TradeSide
    ratio: int
    instrument: Instrument


class StructurePrice(TypedDict):
    price: StrDecimal
    native_price: StrDecimal
    delta: StrDecimal
    gamma: StrDecimal
    theta: StrDecimal
    vega: StrDecimal
    rho: StrDecimal
    timestamp: DateTimeRFC3339


class RFQLeg(TypedDict):
    rfq_leg_id: UUIDv4
    rfq_id: UUIDv4
    instrument: Instrument
    side: TradeSide
    qty: StrDecimal


class MarginUsage(TypedDict):
    initial_margin: StrDecimal
    maintenance_margin: StrDecimal


class QuoteCommonMetadata(TypedDict):
    parent_quote_id: UUIDv4
    maker_company: UUIDv4
    clearing_status: Optional[ClearingStatus]
    expires_at: DateTimeRFC3339
    pool_location: Optional[UUIDv4]
    new_pool_name: Optional[str]
    creator_params: Optional[MarginParams]
    other_params: Optional[MarginParams]
    pool_creator_company: Optional[UUIDv4]
    pool_other_company: Optional[UUIDv4]
    pool_creator_params: Optional[MarginParams]
    pool_other_params: Optional[MarginParams]
    clearing_events: List[ClearingEvent]


class QuoteWithMarginRequirements(TypedDict):
    parent_quote_id: UUIDv4
    quote_price: StrDecimal
    counter_factual_margin_requirements: Optional[MarginUsage]
    existing_margin_requirements: Optional[MarginUsage]
    additional_margin_requirements: Optional[MarginUsage]
    margin_requirements_counter_factual_request_id: UUIDv4
    existing_margin_requirements_request_id: UUIDv4


class PoolMarginUsageStats(TypedDict):
    company: UUIDv4
    balance: StrDecimal
    margin_params: MarginParams
    margin_usage: MarginUsage
