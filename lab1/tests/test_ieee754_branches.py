import pytest
import lab1_6


def test_shift_right_edge_cases():
    bits = [1,0,1,0]

    # n = 0
    assert lab1_6.shift_right(bits,0) == bits

    # n > len
    assert lab1_6.shift_right(bits,10) == [0]*len(bits)


def test_compare_bits_cases():
    assert lab1_6.compare_bits([1,0,1],[1,0,1]) == 0
    assert lab1_6.compare_bits([1,1,0],[1,0,1]) == 1
    assert lab1_6.compare_bits([0,1,0],[1,0,0]) == -1


def test_subtract_bits_branch():
    a = [1,0,1,0]
    b = [0,1,1,0]

    res = lab1_6.subtract_bits(a,b)

    assert isinstance(res,list)
    assert len(res) == len(a)


def test_normalize_overflow_case():
    sign = 0
    exp = lab1_6.int_to_bits(130,8)

    # длинная мантисса
    mant = [1]*40

    s,e,m = lab1_6.normalize(sign,exp,mant)

    assert len(m) == 23


def test_ieee_div_rounding():
    s,e,m = lab1_6.ieee754_div_manual(7.0,3.0)

    bits = lab1_6.ieee754_to_32bit(s,e,m)

    assert len(bits) == 32


def test_cli_exit(monkeypatch):
    inputs = iter(["0"])

    monkeypatch.setattr("builtins.input",lambda _:next(inputs))

    lab1_6.main()