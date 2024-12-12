from decimal import Decimal

from variational import round_to_requirements, default_min_qty_tick

DEFAULT_REQUIREMENTS = {
    "min_decimal_figures": 2,
    "max_decimal_only_figures": 4,
    "max_significant_figures": 6,
}

MIN_ORDER_NOTIONAL = Decimal("0.1")


def test_round_to_requirements():
    def round_and_assert(input, expect):
        output = round_to_requirements(input, DEFAULT_REQUIREMENTS)
        assert output == expect

    round_and_assert(Decimal("0"), Decimal("0"))
    round_and_assert(Decimal("0.1"), Decimal("0.1"))
    round_and_assert(Decimal("0.00100"), Decimal("0.001"))
    round_and_assert(Decimal("0.0011230"), Decimal("0.001123"))
    round_and_assert(Decimal("-0.0011231"), Decimal("-0.001123"))
    round_and_assert(Decimal("0.00123456"), Decimal("0.001235"))
    round_and_assert(Decimal("0.654321"), Decimal("0.6543"))
    round_and_assert(Decimal("12.3456"), Decimal("12.3456"))
    round_and_assert(Decimal("12.34567"), Decimal("12.3457"))
    round_and_assert(Decimal("123"), Decimal("123"))
    round_and_assert(Decimal("123456.1"), Decimal("123456.1"))
    round_and_assert(Decimal("12345678.99"), Decimal("12345678.99"))
    round_and_assert(Decimal("1.123456789123456789"), Decimal("1.12346"))


def test_default_min_qty_tick():
    m = MIN_ORDER_NOTIONAL

    # assert_eq!(default_min_qty_tick(dec!(0)), dec!(1));
    # assert_eq!(default_min_qty_tick(dec!(456)), dec!(0.0001));
    # assert_eq!(default_min_qty_tick(dec!(68000)), dec!(0.000001));
    # assert_eq!(default_min_qty_tick(dec!(0.00002528)), dec!(1));

    assert default_min_qty_tick(m, Decimal("0")) == Decimal("1")
    assert default_min_qty_tick(m, Decimal("456")) == Decimal("0.0001")
    assert default_min_qty_tick(m, Decimal("68000")) == Decimal("0.000001")
    assert default_min_qty_tick(m, Decimal("0.00002528")) == Decimal("1")
