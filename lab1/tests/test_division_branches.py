import pytest
from lab1 import divide_in_direct_code, direct_code_to_decimal


def test_division_negative():
    bits = divide_in_direct_code(-10, 2)
    assert direct_code_to_decimal(bits) == -5


def test_division_remainder():
    bits = divide_in_direct_code(10, 3)
    assert direct_code_to_decimal(bits) == 3


def test_division_zero():
    with pytest.raises(ZeroDivisionError):
        divide_in_direct_code(5, 0)