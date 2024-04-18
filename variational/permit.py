from typing import Optional

from eth_account import Account
from eth_account.messages import encode_typed_data

from .models import H160, Allowance, AllowanceType, StrDecimal
from .client import Client


class TransferPermitHelper(object):
    def __init__(self, client: Client, private_key: str):
        self.client = client
        self.__private_key = private_key

    def sign_and_submit_decimal(self, pool_address: H160, allowance: StrDecimal,
                                seconds_until_expiry: Optional[int] = None):
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                'type': AllowanceType.DECIMAL,
                'value': allowance,
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def sign_and_submit_base(self, pool_address: H160, allowance: int,
                             seconds_until_expiry: Optional[int] = None):
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                'type': AllowanceType.BASE,
                'value': allowance,
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def sign_and_submit_unlimited(self, pool_address: H160,
                                  seconds_until_expiry: Optional[int] = None):
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                'type': AllowanceType.BASE,
                'value': 2 ** 256 - 1,
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def _sign_and_submit(self, pool_address: H160, allowance: Allowance,
                         seconds_until_expiry: Optional[int] = None):
        msg = self.client.generate_transfer_permit(
            pool_address=pool_address,
            allowance=allowance,
            seconds_until_expiry=seconds_until_expiry).result
        msg['domain']['chainId'] = int(msg['domain']['chainId'], 16)
        signed = Account.sign_message(encode_typed_data(full_message=msg), self.__private_key)
        self.client.submit_transfer_permit(message=msg, signature=signed.signature.hex())
