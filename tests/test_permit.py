import copy
from eth_account import Account
from eth_account.messages import encode_typed_data

from variational.models import AllowanceType
from variational.permit import TransferPermitHelper
from variational.wrappers import ApiSingle, ResponseMetadata

TEST_PRIVATE_KEY = "0x" + "11" * 32
TEST_POOL_ADDRESS = "0x" + "22" * 20

PERMIT_TEMPLATE = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "Permit": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
    },
    "primaryType": "Permit",
    "domain": {
        "name": "Variational Settlement Pool",
        "version": "1",
        "chainId": 42161,
        "verifyingContract": TEST_POOL_ADDRESS,
    },
    "message": {
        "owner": Account.from_key(TEST_PRIVATE_KEY).address,
        "spender": TEST_POOL_ADDRESS,
        "value": 1000000,
        "nonce": 0,
        "deadline": 1800000000,
    },
}


class MockClient:
    """Mock API client for testing TransferPermitHelper without network calls."""

    def __init__(self, template: dict):
        """Initialize mock client with base permit template."""
        self.template = template
        self.submitted_message = None
        self.submitted_signature = None
        self.last_allowance = None

    def generate_transfer_permit(self, pool_address, allowance, seconds_until_expiry=None):
        """Mock template generation returning deep copy of template."""
        self.last_allowance = allowance
        return ApiSingle(
            result=copy.deepcopy(self.template),
            meta=ResponseMetadata(request_received_at=1000.0),
        )

    def submit_transfer_permit(self, message: dict, signature: str) -> ApiSingle[bool]:
        """Mock permit submission recording message and signature."""
        self.submitted_message = message
        self.submitted_signature = signature
        return ApiSingle(
            result=True,
            meta=ResponseMetadata(request_received_at=1001.0),
        )


def test_sign_and_submit_with_integer_chain_id():
    """Verify that integer chainId is preserved and EIP-712 signature is recoverable."""
    template = copy.deepcopy(PERMIT_TEMPLATE)
    template["domain"]["chainId"] = 42161

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_decimal(TEST_POOL_ADDRESS, "100.50")

    assert resp.result is True
    assert mock_client.submitted_message["domain"]["chainId"] == 42161
    assert isinstance(mock_client.submitted_message["domain"]["chainId"], int)

    expected_signer = Account.from_key(TEST_PRIVATE_KEY).address
    recovered_signer = Account.recover_message(
        encode_typed_data(full_message=mock_client.submitted_message),
        signature=bytes.fromhex(mock_client.submitted_signature),
    )
    assert recovered_signer == expected_signer


def test_sign_and_submit_with_decimal_string_chain_id():
    """Verify decimal string chainId is correctly parsed to decimal base, not hex base."""
    template = copy.deepcopy(PERMIT_TEMPLATE)
    template["domain"]["chainId"] = "42161"

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_decimal(TEST_POOL_ADDRESS, "50.00")

    assert resp.result is True
    # If parsed with base 16, '42161' becomes 270689. Verify it is 42161.
    assert mock_client.submitted_message["domain"]["chainId"] == 42161

    expected_signer = Account.from_key(TEST_PRIVATE_KEY).address
    recovered_signer = Account.recover_message(
        encode_typed_data(full_message=mock_client.submitted_message),
        signature=bytes.fromhex(mock_client.submitted_signature),
    )
    assert recovered_signer == expected_signer


def test_sign_and_submit_with_hex_string_chain_id():
    """Verify 0x-prefixed hex string chainId is correctly converted to integer."""
    template = copy.deepcopy(PERMIT_TEMPLATE)
    template["domain"]["chainId"] = "0xa4b1"

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_base(TEST_POOL_ADDRESS, 1000000)

    assert resp.result is True
    assert mock_client.submitted_message["domain"]["chainId"] == 42161
    assert mock_client.last_allowance == {"type": AllowanceType.BASE, "value": 1000000}


def test_sign_and_submit_with_unprefixed_hex_chain_id():
    """Verify hex string chainId without 0x prefix is correctly converted to integer."""
    template = copy.deepcopy(PERMIT_TEMPLATE)
    template["domain"]["chainId"] = "a4b1"

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_base(TEST_POOL_ADDRESS, 500000)

    assert resp.result is True
    assert mock_client.submitted_message["domain"]["chainId"] == 42161


def test_sign_and_submit_with_arbitrum_sepolia_chain_id():
    """Verify Arbitrum Sepolia testnet decimal chainId 421614 is correctly parsed."""
    template = copy.deepcopy(PERMIT_TEMPLATE)
    template["domain"]["chainId"] = "421614"

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_decimal(TEST_POOL_ADDRESS, "25.0")

    assert resp.result is True
    # If parsed with base 16, '421614' becomes 4331028. Verify it is 421614.
    assert mock_client.submitted_message["domain"]["chainId"] == 421614


def test_sign_and_submit_unlimited():
    """Verify sign_and_submit_unlimited sets max uint256 base allowance and returns response."""
    template = copy.deepcopy(PERMIT_TEMPLATE)

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, TEST_PRIVATE_KEY)

    resp = helper.sign_and_submit_unlimited(TEST_POOL_ADDRESS)

    assert resp.result is True
    assert mock_client.last_allowance["type"] == AllowanceType.BASE
    assert mock_client.last_allowance["value"] == hex(2**256 - 1)


def test_sign_and_submit_with_raw_private_key_without_0x():
    """Verify TransferPermitHelper works with private keys lacking 0x prefix."""
    raw_pk = TEST_PRIVATE_KEY[2:]
    template = copy.deepcopy(PERMIT_TEMPLATE)

    mock_client = MockClient(template)
    helper = TransferPermitHelper(mock_client, raw_pk)

    resp = helper.sign_and_submit_decimal(TEST_POOL_ADDRESS, "10.0")

    assert resp.result is True
    expected_signer = Account.from_key(TEST_PRIVATE_KEY).address
    recovered_signer = Account.recover_message(
        encode_typed_data(full_message=mock_client.submitted_message),
        signature=bytes.fromhex(mock_client.submitted_signature),
    )
    assert recovered_signer == expected_signer
