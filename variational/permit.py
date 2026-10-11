from typing import Optional

from eth_account import Account
from eth_account.messages import encode_typed_data

from .models import H160, Allowance, AllowanceType, StrDecimal
from .client import Client
from .wrappers import ApiSingle


class TransferPermitHelper(object):
    """Helper for generating, EIP-712 signing, and submitting transfer permits.

    Normalizes the EIP-712 domain chain ID returned by the API template across
    integer, decimal string, and hexadecimal string representations to ensure
    valid on-chain cryptographic signature verification.
    """

    def __init__(self, client: Client, private_key: str):
        """Initialize helper with API client and Ethereum private key.

        :param client: Initialized Variational API Client instance.
        :param private_key: Hex-encoded Ethereum private key (with or without '0x' prefix).
        """
        self.client = client
        self.__private_key = private_key

    def sign_and_submit_decimal(
        self,
        pool_address: H160,
        allowance: StrDecimal,
        seconds_until_expiry: Optional[int] = None,
    ) -> ApiSingle[bool]:
        """Sign and submit a transfer permit with allowance in decimal string format.

        :param pool_address: Target settlement pool contract address (0x-prefixed H160).
        :param allowance: Allowance amount represented as human-readable decimal string.
        :param seconds_until_expiry: Optional validity duration in seconds.
        :return: ApiSingle[bool] indicating successful permit submission and acceptance.
        """
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                "type": AllowanceType.DECIMAL,
                "value": allowance,
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def sign_and_submit_base(
        self,
        pool_address: H160,
        allowance: int,
        seconds_until_expiry: Optional[int] = None,
    ) -> ApiSingle[bool]:
        """Sign and submit a transfer permit with allowance in integer base units.

        :param pool_address: Target settlement pool contract address (0x-prefixed H160).
        :param allowance: Allowance amount in smallest token base units (e.g. 6 decimals for USDC).
        :param seconds_until_expiry: Optional validity duration in seconds.
        :return: ApiSingle[bool] indicating successful permit submission and acceptance.
        """
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                "type": AllowanceType.BASE,
                "value": allowance,
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def sign_and_submit_unlimited(
        self, pool_address: H160, seconds_until_expiry: Optional[int] = None
    ) -> ApiSingle[bool]:
        """Sign and submit an unlimited transfer permit (max uint256 base units).

        :param pool_address: Target settlement pool contract address (0x-prefixed H160).
        :param seconds_until_expiry: Optional validity duration in seconds.
        :return: ApiSingle[bool] indicating successful permit submission and acceptance.
        """
        return self._sign_and_submit(
            pool_address=pool_address,
            allowance={
                "type": AllowanceType.BASE,
                "value": hex(2**256 - 1),
            },
            seconds_until_expiry=seconds_until_expiry,
        )

    def _sign_and_submit(
        self,
        pool_address: H160,
        allowance: Allowance,
        seconds_until_expiry: Optional[int] = None,
    ) -> ApiSingle[bool]:
        """Fetch template, normalize EIP-712 domain chainId, sign, and submit permit.

        Normalizes raw chain ID representations (e.g., integer 42161, decimal string '42161',
        or hex string '0xa4b1') into native integer format required for correct EIP-712
        domain separator computation and on-chain ecrecover validation.

        :param pool_address: Target settlement pool contract address.
        :param allowance: Allowance payload dictionary with type and value.
        :param seconds_until_expiry: Optional validity duration in seconds.
        :return: ApiSingle[bool] containing the API response confirming permit acceptance.
        """
        msg = self.client.generate_transfer_permit(
            pool_address=pool_address,
            allowance=allowance,
            seconds_until_expiry=seconds_until_expiry,
        ).result

        raw_chain_id = msg["domain"]["chainId"]
        if isinstance(raw_chain_id, str):
            raw_chain_id = raw_chain_id.strip()
            if raw_chain_id.startswith(("0x", "0X")):
                msg["domain"]["chainId"] = int(raw_chain_id, 16)
            elif raw_chain_id.isdigit():
                msg["domain"]["chainId"] = int(raw_chain_id, 10)
            else:
                msg["domain"]["chainId"] = int(raw_chain_id, 16)
        else:
            msg["domain"]["chainId"] = int(raw_chain_id)

        signed = Account.sign_message(
            encode_typed_data(full_message=msg), self.__private_key
        )
        return self.client.submit_transfer_permit(
            message=msg, signature=signed.signature.hex()
        )
