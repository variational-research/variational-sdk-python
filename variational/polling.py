from time import sleep
from typing import Callable, List

from .client import Client
from .models import (SettlementPoolStatus, TransferStatus, ClearingStatus, SettlementPool,
                     Transfer, Quote, RFQ)


class PollingHelper(object):
    def __init__(self, client: Client, interval=1, attempts=10):
        assert attempts > 0
        self.client = client
        self.interval = interval
        self.attempts = attempts

    def wait_for_settlement_pool(self, pool_location: str,
                                 status: SettlementPoolStatus = SettlementPoolStatus.OPEN) \
            -> SettlementPool:
        return self.__poll_for_status(
            object_type='settlement pool',
            object_id=pool_location,
            status=status,
            fetch_objs=lambda: self.client.get_settlement_pools(id=pool_location).result,
            get_status=lambda obj: obj['data']['status'],
            is_final=lambda s: s in (SettlementPoolStatus.OPEN, SettlementPoolStatus.CANCELED)
        )

    def wait_for_transfer(self, id: str,
                          status: TransferStatus = TransferStatus.CONFIRMED) -> Transfer:
        return self.__poll_for_status(
            object_type='transfer',
            object_id=id,
            status=status,
            fetch_objs=lambda: self.client.get_portfolio_transfers(id=id).result,
            get_status=lambda obj: obj['status'],
            is_final=lambda s: s in (TransferStatus.CONFIRMED, TransferStatus.FAILED)
        )

    def wait_for_quote_sent(self, id: str, status: ClearingStatus) -> Quote:
        return self.__poll_for_status(
            object_type='sent quote',
            object_id=id,
            status=status,
            fetch_objs=lambda: self.client.get_quotes_sent(id=id).result,
            get_status=lambda obj: obj['clearing_status'],
            is_final=lambda s: (s == ClearingStatus.SUCCESS_TRADES_BOOKED_INTO_POOL or
                                s is not None and s.startswith('rejected_'))
        )

    def wait_for_quote_received(self, id: str, status: ClearingStatus) -> Quote:
        return self.__poll_for_status(
            object_type='received quote',
            object_id=id,
            status=status,
            fetch_objs=lambda: self.client.get_quotes_received(id=id).result,
            get_status=lambda obj: obj['clearing_status'],
            is_final=lambda s: (s == ClearingStatus.SUCCESS_TRADES_BOOKED_INTO_POOL or
                                s is not None and s.startswith('rejected_'))
        )

    def wait_for_rfq_sent(self, id: str, status: ClearingStatus) -> RFQ:
        return self.__poll_for_status(
            object_type='sent rfq',
            object_id=id,
            status=status,
            fetch_objs=lambda: self.client.get_rfqs_sent(id=id).result,
            get_status=lambda obj: obj['clearing_status'],
            is_final=lambda s: (s == ClearingStatus.SUCCESS_TRADES_BOOKED_INTO_POOL or
                                s is not None and s.startswith('rejected_'))
        )

    def wait_for_rfq_received(self, id: str, status: ClearingStatus) -> RFQ:
        return self.__poll_for_status(
            object_type='received rfq',
            object_id=id,
            status=status,
            fetch_objs=lambda: self.client.get_rfqs_received(id=id).result,
            get_status=lambda obj: obj['clearing_status'],
            is_final=lambda s: (s == ClearingStatus.SUCCESS_TRADES_BOOKED_INTO_POOL or
                                s is not None and s.startswith('rejected_'))
        )

    def __poll_for_status(self, object_type: str, object_id: str, status: str,
                          fetch_objs: Callable[[], List[dict]],
                          get_status: Callable[[dict], str],
                          is_final: Callable[[str], bool]):
        for i in range(self.attempts):
            if i > 0:
                sleep(self.interval)

            objs = fetch_objs()
            if len(objs) < 1:
                raise ObjectNotFound(msg=f"{object_type} '{object_id}' not found")
            obj = objs[0]

            current_status = get_status(obj)
            if current_status == status:
                return obj

            if is_final(current_status):
                raise UnexpectedStatus(
                    msg=f"unexpected final status '{current_status}' "
                        f"for {object_type} '{object_id}'",
                    status=current_status)

        raise PollTimeout(msg=f"timeout waiting for {object_type} '{object_id}'"
                              f" to become '{status}'")


class ObjectNotFound(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnexpectedStatus(Exception):
    def __init__(self, msg: str, status: str):
        self.status = status
        self.msg = msg

    def __str__(self):
        return self.msg


class PollTimeout(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg
