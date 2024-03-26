from enum import StrEnum


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


class RequestAction(StrEnum):
    REJECT = "reject"
    ACCEPT = "accept"


class RFQStatus(StrEnum):
    OPEN = "open"
    EXPIRED = "expired"
    CANCELED = "canceled"
    CLOSED = "closed"


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
