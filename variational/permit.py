from typing import Optional

from eth_account import Account
from eth_account.messages import encode_typed_data

from .models import H160, Allowance
from .client import Client


class TransferPermitHelper(object):
    def __init__(self, client: Client, private_key: str):
        self.client = client
        self.__private_key = private_key

    def sign_and_submit(self, pool_address: H160, allowance: Allowance,
                        seconds_until_expiry: Optional[int] = None):
        msg = self.client.generate_transfer_permit(
            pool_address=pool_address,
            allowance=allowance,
            seconds_until_expiry=seconds_until_expiry).result
        msg['domain']['chainId'] = int(msg['domain']['chainId'], 16)
        signed = Account.sign_message(encode_typed_data(full_message=msg), self.__private_key)
        self.client.submit_transfer_permit(message=msg, signature=signed.signature.hex())
