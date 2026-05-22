from unittest.mock import patch

import pytest

import shift6_adder


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0000"),
        (1, "0001"),
        (6, "0110"),
        (15, "1111"),
        (16, "0000"),
        (31, "1111"),
        (-1, "1111"),
    ],
)
def test_to_bin4_uses_low_four_bits(value, expected):
    assert shift6_adder.to_bin4(value) == expected


def test_read_shift6_code_accepts_valid_code():
    with patch("builtins.input", return_value="1010"):
        assert shift6_adder.read_shift6_code("A") == 0b1010


def test_read_shift6_code_retries_on_wrong_length_symbols_and_range(capsys):
    with patch("builtins.input", side_effect=["101", "10a0", "0011", "1111"]):
        assert shift6_adder.read_shift6_code("B") == 0b1111

    output = capsys.readouterr().out
    assert "ровно 4 бита" in output
    assert "недопустим" in output


@pytest.mark.parametrize(
    ("a_code", "b_code", "expected_total_text", "expected_result_text", "expected_cout"),
    [
        ("0110", "0110", "0 + 0 = 0", "Результат схемы: 00", "Cout = 0"),
        ("1011", "1100", "5 + 6 = 11", "Результат схемы: 11", "Cout = 1"),
        ("1111", "1111", "9 + 9 = 18", "Результат схемы: 18", "Cout = 1"),
    ],
)
def test_main_outputs_correct_decimal_result(
    a_code,
    b_code,
    expected_total_text,
    expected_result_text,
    expected_cout,
    capsys,
):
    with patch("builtins.input", side_effect=[a_code, b_code]):
        shift6_adder.main()

    output = capsys.readouterr().out
    assert expected_total_text in output
    assert expected_result_text in output
    assert expected_cout in output
    assert "Результат корректен." in output


def test_main_retries_invalid_first_input_and_then_completes(capsys):
    with patch("builtins.input", side_effect=["0000", "0110", "0111"]):
        shift6_adder.main()

    output = capsys.readouterr().out
    assert "недопустим" in output
    assert "0 + 1 = 1" in output
    assert "Результат схемы: 01" in output
