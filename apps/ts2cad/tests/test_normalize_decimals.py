from ts2cad.normalizer.normalize import parse_float


def test_parse_float_decimal_comma() -> None:
    assert parse_float("123,45", decimal_comma=True) == 123.45
    assert parse_float("1.234,50", decimal_comma=True) == 1234.5


def test_parse_float_decimal_point() -> None:
    assert parse_float("123.45", decimal_comma=False) == 123.45
    assert parse_float("123,45", decimal_comma=False) == 123.45
