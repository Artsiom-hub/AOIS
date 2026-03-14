import pytest
import lab1_7


def test_to_4bit_zero():
    assert lab1_7.to_4bit(0) == [0,0,0,0]


def test_bcd_add_digit_with_carry():
    a = lab1_7.dec_to_5421[9]
    b = lab1_7.dec_to_5421[9]

    res, carry = lab1_7.bcd5421_add_digit(a,b,0)

    assert carry == 1


def test_bcd_add_digit_with_input_carry():
    a = lab1_7.dec_to_5421[4]
    b = lab1_7.dec_to_5421[5]

    res, carry = lab1_7.bcd5421_add_digit(a,b,1)

    assert carry in (0,1)


def test_add_5421_with_padding():
    dec,bcd = lab1_7.add_5421_bcd("5","15")

    assert dec == "20"


def test_cli_invalid(monkeypatch):
    inputs = iter(["abc","123","456","0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    lab1_7.main()