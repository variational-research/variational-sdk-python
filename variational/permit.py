from typing import Optional

from eth_account import Account
from eth_account.messages import encode_typed_data

import variational
from .models import H160, Allowance


class TransferPermitHelper(object):
    def __init__(self, client: variational.Client, private_key: str):
        self.__client = client
        self.__private_key = private_key

    def sign_and_submit(self, pool_address: H160, allowance: Allowance,
                        seconds_until_expiry: Optional[int] = None):
        msg = self.__client.generate_transfer_permit(
            pool_address=pool_address,
            allowance=allowance,
            seconds_until_expiry=seconds_until_expiry).result
        msg['domain']['chainId'] = int(msg['domain']['chainId'], 16)
        signed = Account.sign_message(encode_typed_data(full_message=msg), self.__private_key)
        self.__client.submit_transfer_permit(message=msg, signature=signed.signature.hex())
