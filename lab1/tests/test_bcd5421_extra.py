import pytest
from lab1_7 import (
    to_4bit,
    bcd5421_add_digit,
)



def test_to_4bit():
    assert to_4bit(5) == [0,1,0,1]




def test_bcd_digit_no_carry():
    a = [0,0,1,0] 
    b = [0,0,1,1]  
    res, carry = bcd5421_add_digit(a,b,0)
    assert carry == 0


def test_bcd_digit_with_carry():
    a = [1,1,0,1]  
    b = [0,0,0,1]  
    res, carry = bcd5421_add_digit(a,b,0)
    assert carry == 1