import sys

if sys.version_info[0:2] >= (3, 10):
    from typing import TypeAlias

    AssetToken: TypeAlias = str  # e.g. "BTC", "ETH", etc
    DateTimeRFC3339: TypeAlias = str  # e.g. "2024-02-02T06:13:45.323432Z"
    H160: TypeAlias = str  # e.g. "0x3d68316712565ccb7f14a2bfc6aa785d6d2d12d5"
    StrDecimal: TypeAlias = str  # e.g. "218205.58082"
    UUIDv4: TypeAlias = str  # e.g. "bdd68c99-65fe-4500-baae-5bc09b4af183"
else:
    AssetToken = str
    DateTimeRFC3339 = str
    H160 = str
    StrDecimal = str
    UUIDv4 = str
