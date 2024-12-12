from decimal import Decimal, ROUND_HALF_UP
from math import ceil, floor
from typing import Dict, List, Optional

from .models import Instrument, AssetToken, SupportedAssetDetails, PrecisionRequirements


def find_asset_details_for_instrument(
    instrument: Instrument,
    supported_assets: Dict[AssetToken, List[SupportedAssetDetails]],
) -> Optional[SupportedAssetDetails]:
    underlying = instrument["underlying"]
    dex_key = instrument.get("dex_token_details")

    for asset in supported_assets.get(underlying, []):
        if asset["asset"] != underlying:
            continue

        if dex_key:
            if asset["dex_token_details"] == dex_key:
                return asset
        else:
            return asset


def round_to_requirements(
    d: Decimal, requirements: PrecisionRequirements, rounding=ROUND_HALF_UP
) -> Decimal:
    abs_d = abs(d)
    m = abs_d

    # remove decimal point from m
    d10e = d.as_tuple().exponent
    if (m10e := m.as_tuple().exponent) < 0:
        m /= (Decimal(10) ** m10e).normalize()

    quantize_to = None
    if abs_d >= 1:
        allowed = int(ceil(m.log10())) + d10e - requirements["max_significant_figures"]
        places = min(allowed, -requirements["min_decimal_figures"])
        if places > d10e:
            quantize_to = places
    elif abs_d > 0:
        remove_places = int(ceil(m.log10())) - requirements["max_decimal_only_figures"]
        if remove_places > 0:
            quantize_to = d10e + remove_places

    if quantize_to:
        return d.quantize(Decimal(10) ** quantize_to, rounding)

    return d


def default_min_qty_tick(min_order_notional: Decimal, price: Decimal) -> Decimal:
    if price > Decimal(0):
        return min(
            Decimal(1), Decimal(10) ** floor((min_order_notional / price).log10())
        )
    else:
        return Decimal(1)
