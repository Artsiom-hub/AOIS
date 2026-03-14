import pytest
from lab1_6 import (
    shift_right,
    compare_bits,
    subtract_bits,
    normalize,
    ieee754_to_float_decimal,
    ieee754_to_32bit,
    int_to_bits,
    ieee754_div_manual,
    ieee754_add_manual
)
import lab1_6
def test_cli_add(monkeypatch):
    inputs=iter(["1","2","3","0"])
    monkeypatch.setattr("builtins.input",lambda _:next(inputs))
    lab1_6.main()


def test_cli_invalid(monkeypatch):
    inputs=iter(["9","1","1","0"])
    monkeypatch.setattr("builtins.input",lambda _:next(inputs))
    lab1_6.main()
def test_div_zero():
    with pytest.raises(ZeroDivisionError):
        ieee754_div_manual(5.0, 0.0)
def test_add_cancel_to_zero():
    s,e,m = ieee754_add_manual(5.0,-5.0)
    assert s == 0


def test_shift_right_zero():
    bits=[1,0,1]
    assert shift_right(bits,0)==bits
def test_shift_right_basic():
    bits = [1, 0, 1, 1]
    assert shift_right(bits, 1) == [0, 1, 0, 1]

def test_shift_right_big_shift():
    bits = [1, 0, 1]
    assert shift_right(bits, 10) == [0, 0, 0]




def test_compare_bits_equal():
    assert compare_bits([1,0,1], [1,0,1]) == 0

def test_compare_bits_greater():
    assert compare_bits([1,1,0], [1,0,1]) == 1

def test_compare_bits_less():
    assert compare_bits([0,1,0], [1,0,0]) == -1




def test_subtract_bits():
    a = [1,0,1,0]  # 10
    b = [0,1,1,0]  # 6
    res = subtract_bits(a, b)
    assert res == [0,1,0,0]  # 4




def test_normalize_overflow():
    sign = 0
    exp = int_to_bits(130, 8)
    mant = [1]*30
    s,e,m = normalize(sign, exp, mant)
    assert len(m) == 23




def test_ieee754_to_decimal():
    sign = 0
    exp = int_to_bits(127, 8) 
    mant = [0]*23
    bits = ieee754_to_32bit(sign, exp, mant)
    val = ieee754_to_float_decimal(bits)
    assert val == 1.0