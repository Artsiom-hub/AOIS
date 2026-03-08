import pytest
from lab1_7 import add_5421_bcd


@pytest.mark.parametrize("a, b, expected_dec, expected_bcd", [
    ("0", "0", "0", "0000"),
    ("1", "2", "3", "0001 0010"),      
    ("3", "4", "7", "0011 0100"),      
    ("5", "4", "9", "1000 0100"),      
])
def test_simple_add(a, b, expected_dec, expected_bcd):
    dec, bcd = add_5421_bcd(a, b)
    assert dec == expected_dec
    assert bcd.replace(" ", "") == expected_bcd.replace(" ", "")


@pytest.mark.parametrize("a, b, expected_dec, expected_bcd", [
    ("7", "5", "12", "0001 0010"),     
    ("9", "1", "10", "0001 0000"),     
    ("8", "9", "17", "0001 0111"),     
])
def test_carry_single_digit(a, b, expected_dec, expected_bcd):
    dec, bcd = add_5421_bcd(a, b)
    assert dec == expected_dec
    assert bcd.replace(" ", "") == expected_bcd.replace(" ", "")


@pytest.mark.parametrize("a, b, expected_dec, expected_bcd", [
    ("12", "34", "46", "0001 0010 0011 0100"),   
    ("27", "85", "112", "0001 0001 0010"),        
    ("99", "1", "100", "0001 0000 0000"),        
])
def test_multi_digit(a, b, expected_dec, expected_bcd):
    dec, bcd = add_5421_bcd(a, b)
    assert dec == expected_dec
    assert bcd.replace(" ", "") == expected_bcd.replace(" ", "")


def test_commutativity():
    dec1, bcd1 = add_5421_bcd("56", "78")
    dec2, bcd2 = add_5421_bcd("78", "56")
    assert dec1 == dec2
    assert bcd1.replace(" ", "") == bcd2.replace(" ", "")


@pytest.mark.parametrize("a, b", [
    ("abc", "12"),
    ("12", "x9"),
    ("!@#", "!!")
])
def test_invalid_input(a, b):
    with pytest.raises(Exception):
        add_5421_bcd(a, b)