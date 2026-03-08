import pytest
import lab1



def test_main_choice_1(monkeypatch):
    inputs = iter(["1","5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    import lab1
    lab1.main()


def test_main_choice_2(monkeypatch):
    inputs = iter(["2","5","3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    import lab1
    lab1.main()


def test_main_choice_3(monkeypatch):
    inputs = iter(["3","5","2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    import lab1
    lab1.main()
def test_validate_range_ok():
    lab1.validate_range(0)
    lab1.validate_range(lab1.MIN_INT)
    lab1.validate_range(lab1.MAX_INT)


def test_validate_range_error():
    with pytest.raises(ValueError):
        lab1.validate_range(lab1.MAX_INT + 1)

    with pytest.raises(ValueError):
        lab1.validate_range(lab1.MIN_INT - 1)


def test_zeros():
    z = lab1.zeros(10)
    assert z == [0] * 10


def test_copy_bits():
    bits = [1, 0, 1]
    copied = lab1.copy_bits(bits)
    assert copied == bits
    assert copied is not bits


def test_bits_to_str():
    assert lab1.bits_to_str([1, 0, 1]) == "101"


def test_abs_int():
    assert lab1.abs_int(-5) == 5
    assert lab1.abs_int(5) == 5




def test_direct_code_positive():
    bits = lab1.to_direct_code(5)
    assert bits[0] == 0


def test_direct_code_negative():
    bits = lab1.to_direct_code(-5)
    assert bits[0] == 1


def test_inverse_code_positive():
    bits = lab1.to_inverse_code(5)
    assert bits[0] == 0


def test_inverse_code_negative():
    bits = lab1.to_inverse_code(-5)
    assert bits[0] == 1


def test_additional_code_positive():
    bits = lab1.to_additional_code(7)
    assert bits[0] == 0


def test_additional_code_negative():
    bits = lab1.to_additional_code(-7)
    assert bits[0] == 1




def test_addition_simple():
    result_bits = lab1.add_two_in_twos_complement(5, 3)
    assert lab1.from_additional_code(result_bits) == 8


def test_addition_negative():
    result_bits = lab1.add_two_in_twos_complement(-5, 3)
    assert lab1.from_additional_code(result_bits) == -2


def test_subtraction():
    result_bits = lab1.subtract_in_twos_complement(10, 3)
    assert lab1.from_additional_code(result_bits) == 7


def test_subtraction_negative():
    result_bits = lab1.subtract_in_twos_complement(3, 10)
    assert lab1.from_additional_code(result_bits) == -7




def test_multiply_positive():
    bits = lab1.multiply_in_direct_code(4, 3)
    assert lab1.direct_code_to_decimal(bits) == 12


def test_multiply_negative():
    bits = lab1.multiply_in_direct_code(-4, 3)
    assert lab1.direct_code_to_decimal(bits) == -12




def test_division_basic():
    q, sign, bits = lab1.divide_in_direct_code(10, 2)
    assert q == 5
    assert sign == 0


def test_division_negative():
    q, sign, bits = lab1.divide_in_direct_code(-10, 2)
    assert q == -5
    assert sign == 1


def test_division_zero_error():
    with pytest.raises(ZeroDivisionError):
        lab1.divide_in_direct_code(5, 0)




def test_bits_to_int():
    assert lab1.bits_to_int([1, 0, 1]) == 5


def test_direct_code_to_decimal():
    bits = lab1.to_direct_code(-9)
    assert lab1.direct_code_to_decimal(bits) == -9



def test_run_show_codes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "5")
    lab1.run_show_codes()


def test_run_addition(monkeypatch):
    inputs = iter(["5", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1.run_addition()


def test_run_substraction(monkeypatch):
    inputs = iter(["5", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1.run_substraction()


def test_set_magnitude_zero():
    bits = lab1.set_magnitude_bits(0)
    assert sum(bits) == 0


def test_invert_bits_with_start():
    bits = [1, 1, 0, 0]
    inv = lab1.invert_bits(bits, start=1)
    assert inv == [1, 0, 1, 1]


def test_add_one_full_carry():
    bits = [1, 1, 1]
    result = lab1.add_one(bits)
    assert result == [0, 0, 0]


def test_from_additional_positive_branch():
    bits = lab1.to_additional_code(6)
    assert lab1.from_additional_code(bits) == 6


def test_from_additional_negative_branch():
    bits = lab1.to_additional_code(-6)
    assert lab1.from_additional_code(bits) == -6


def test_direct_code_to_decimal_length_error():
    with pytest.raises(ValueError):
        lab1.direct_code_to_decimal([1, 0, 1])


def test_multiply_zero():
    bits = lab1.multiply_in_direct_code(0, 100)
    assert lab1.direct_code_to_decimal(bits) == 0


def test_division_precision():
    q, sign, bits = lab1.divide_in_direct_code(1, 3, precision=2)
    assert round(q, 2) == 0.33


def test_main_invalid_choice(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "99")
    lab1.main()


def test_run_show_codes_invalid_input(monkeypatch):
    inputs = iter(["abc", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1.run_show_codes()


def test_run_addition_invalid_input(monkeypatch):
    inputs = iter(["abc"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1.run_addition()