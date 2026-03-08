import pytest
from lab1_6 import (
    float_to_ieee754_manual,
    ieee754_add_manual,
    ieee754_sub_manual,
    ieee754_mul_manual,
    ieee754_div_manual,
    ieee754_to_32bit,
    bits_to_int,
)


@pytest.mark.parametrize("value", [
    0.0,
    1.0,
    -1.0,
    3.5,
    -2.25,
])

def test_float_to_bits_basic(value):
    sign, exp, mant = float_to_ieee754_manual(value)
    bits = ieee754_to_32bit(sign, exp, mant)

    assert bits[0] == (1 if value < 0 else 0)
   
    assert 0 <= bits_to_int(bits[1:1+8]) <= 255
   
    assert len(bits) == 32


@pytest.mark.parametrize("a, b", [
    (1.0, 2.0),
    (3.5, -1.25),
    (-2.0, -3.0),
])
def test_ieee754_add(a, b):
    s, e, m = ieee754_add_manual(a, b)
    result_bits = ieee754_to_32bit(s, e, m)
   
    expected = a + b
    
    sign = result_bits[0]
    exp_val = bits_to_int(result_bits[1:9])
    mant_val = bits_to_int(result_bits[9:])
   
    assert pytest.approx(expected, rel=1e-6) == ((-1)**sign) * (1 + mant_val/(1<<23)) * (2**(exp_val - 127))

@pytest.mark.parametrize("a, b", [
    (2.0, 1.0),
    (5.5, 3.25),
    (-1.0, -2.0),
])
def test_ieee754_sub(a, b):
    s, e, m = ieee754_sub_manual(a, b)
    result_bits = ieee754_to_32bit(s, e, m)
    expected = a - b
    sign = result_bits[0]
    exp_val = bits_to_int(result_bits[1:9])
    mant_val = bits_to_int(result_bits[9:])
    assert pytest.approx(expected, rel=1e-6) == ((-1)**sign) * (1 + mant_val/(1<<23)) * (2**(exp_val - 127))


@pytest.mark.parametrize("a, b", [
    (1.5, 2.0),
    (-3.0, 4.0),
    (-2.5, -2.0),
])
def test_ieee754_mul(a, b):
    s, e, m = ieee754_mul_manual(a, b)
    result_bits = ieee754_to_32bit(s, e, m)
    expected = a * b
    sign = result_bits[0]
    exp_val = bits_to_int(result_bits[1:9])
    mant_val = bits_to_int(result_bits[9:])
    assert pytest.approx(expected, rel=1e-6) == ((-1)**sign) * (1 + mant_val/(1<<23)) * (2**(exp_val - 127))


@pytest.mark.parametrize("a, b", [
    (1.0, 2.0),
    (3.5, -1.75),
    (-4.0, -2.0),
])
def test_ieee754_div(a, b):
    s, e, m = ieee754_div_manual(a, b)
    result_bits = ieee754_to_32bit(s, e, m)
    expected = a / b
    sign = result_bits[0]
    exp_val = bits_to_int(result_bits[1:9])
    mant_val = bits_to_int(result_bits[9:])
    assert pytest.approx(expected, rel=1e-6) == ((-1)**sign) * (1 + mant_val/(1<<23)) * (2**(exp_val - 127))