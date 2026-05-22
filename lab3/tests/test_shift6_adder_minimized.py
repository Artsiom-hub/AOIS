from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from sympy import And, Or, Not, symbols

import shift6_adder_minimized as shift6_adder


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
def test_to_bin4_uses_low_four_bits(value: int, expected: str) -> None:
    assert shift6_adder.to_bin4(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "00000000"),
        (127, "01111111"),
        (255, "11111111"),
        (256, "00000000"),
        (-1, "11111111"),
    ],
)
def test_to_bin8_uses_low_eight_bits(value: int, expected: str) -> None:
    assert shift6_adder.to_bin8(value) == expected


@pytest.mark.parametrize(
    ("digit", "expected_code"),
    [(0, 0b0110), (1, 0b0111), (4, 0b1010), (9, 0b1111)],
)
def test_digit_to_shift6_code_valid(digit: int, expected_code: int) -> None:
    assert shift6_adder.digit_to_shift6_code(digit) == expected_code


@pytest.mark.parametrize("digit", [-1, 10])
def test_digit_to_shift6_code_rejects_invalid_digits(digit: int) -> None:
    with pytest.raises(ValueError, match="0..9"):
        shift6_adder.digit_to_shift6_code(digit)


@pytest.mark.parametrize(
    ("code", "is_valid"),
    [(0b0101, False), (0b0110, True), (0b1010, True), (0b1111, True), (0b10000, False)],
)
def test_is_valid_shift6_code(code: int, is_valid: bool) -> None:
    assert shift6_adder.is_valid_shift6_code(code) is is_valid


def test_read_shift6_code_accepts_valid_code() -> None:
    with patch("builtins.input", return_value="1010"):
        assert shift6_adder.read_shift6_code("A") == 0b1010


def test_read_shift6_code_retries_on_wrong_length_symbols_and_range(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("builtins.input", side_effect=["101", "10a0", "0011", "1111"]):
        assert shift6_adder.read_shift6_code("B") == 0b1111

    output = capsys.readouterr().out
    assert "ровно 4 бита" in output
    assert "недопустим" in output


@pytest.mark.parametrize(
    ("a_code", "b_code", "total", "s1", "s0", "cout", "k"),
    [
        (0b0110, 0b0110, 0, 0b0110, 0b0110, 0, 0b1010),
        (0b1010, 0b1011, 9, 0b0110, 0b1111, 0, 0b1010),
        (0b1110, 0b1100, 14, 0b0111, 0b1010, 1, 0b0000),
        (0b1111, 0b1111, 18, 0b0111, 0b1110, 1, 0b0000),
    ],
)
def test_calculate_returns_correct_structural_result(
    a_code: int,
    b_code: int,
    total: int,
    s1: int,
    s0: int,
    cout: int,
    k: int,
) -> None:
    result = shift6_adder.calculate(a_code, b_code)

    assert result.total == total
    assert result.s1_code == s1
    assert result.s0_code == s0
    assert result.cout == cout
    assert result.k == k
    assert result.s1_digit * 10 + result.s0_digit == total
    assert result.output_bits["Cout"] == cout
    assert result.output_bits["S1_3"] == ((s1 >> 3) & 1)
    assert result.output_bits["S0_0"] == (s0 & 1)


def test_calculate_rejects_invalid_a_code() -> None:
    with pytest.raises(ValueError, match="Недопустимый код A"):
        shift6_adder.calculate(0b0000, 0b0110)


def test_calculate_rejects_invalid_b_code() -> None:
    with pytest.raises(ValueError, match="Недопустимый код B"):
        shift6_adder.calculate(0b0110, 0b0000)


@pytest.mark.parametrize(
    ("a_code", "b_code", "expected"),
    [(0b0110, 0b0110, 0b01100110), (0b1110, 0b1100, 0b11101100)],
)
def test_minterm_index(a_code: int, b_code: int, expected: int) -> None:
    assert shift6_adder.minterm_index(a_code, b_code) == expected


def test_minterm_to_conjunction_uses_input_variable_order() -> None:
    # 127 = 01111111, порядок переменных: A3 A2 A1 A0 B3 B2 B1 B0.
    assert shift6_adder.minterm_to_conjunction(127) == (
        "(!A3 /\\ A2 /\\ A1 /\\ A0 /\\ B3 /\\ B2 /\\ B1 /\\ B0)"
    )


def test_build_sdnf_expression_empty_and_non_empty() -> None:
    assert shift6_adder.build_sdnf_expression([]) == "0"

    expression = shift6_adder.build_sdnf_expression([127, 102])
    assert expression.startswith("(!A3 /\\ A2 /\\ A1 /\\ !A0")
    assert "\\/" in expression
    assert "(!A3 /\\ A2 /\\ A1 /\\ A0" in expression


def test_expression_to_text_replaces_sympy_operators() -> None:
    a, b, c = symbols("A B C")
    expression = Or(And(a, Not(b)), c)

    assert shift6_adder.expression_to_text(expression) == "C \\/ (A /\\ !B)"
    assert shift6_adder.expression_to_text(True) == "1"
    assert shift6_adder.expression_to_text(False) == "0"


def test_build_truth_data_counts_and_key_minterms() -> None:
    rows, ones, dont_cares = shift6_adder.build_truth_data()

    assert len(rows) == 100
    assert len(dont_cares) == 156
    assert set(ones) == set(shift6_adder.OUTPUT_NAMES)

    # 0 + 0: A=0110, B=0110 => minterm 102, Cout=0, S1=0110, S0=0110.
    m_0_plus_0 = shift6_adder.minterm_index(0b0110, 0b0110)
    assert m_0_plus_0 not in ones["Cout"]
    assert m_0_plus_0 in ones["S1_2"]
    assert m_0_plus_0 in ones["S1_1"]
    assert m_0_plus_0 in ones["S0_2"]
    assert m_0_plus_0 in ones["S0_1"]

    # 8 + 6: A=1110, B=1100 => Cout=1, S1=0111, S0=1010.
    m_8_plus_6 = shift6_adder.minterm_index(0b1110, 0b1100)
    assert m_8_plus_6 in ones["Cout"]
    assert m_8_plus_6 in ones["S1_0"]
    assert m_8_plus_6 in ones["S0_3"]
    assert m_8_plus_6 not in ones["S0_2"]


def test_validate_structural_model_accepts_generated_rows() -> None:
    rows, _, _ = shift6_adder.build_truth_data()

    shift6_adder.validate_structural_model(rows)


def test_validate_structural_model_rejects_broken_row() -> None:
    row = shift6_adder.calculate(0b1110, 0b1100)
    broken = replace(row, s0_code=0b0110, s0_digit=0)

    with pytest.raises(AssertionError, match="Ошибка внутренней проверки"):
        shift6_adder.validate_structural_model([broken])


def test_make_code_table_text_contains_all_boundary_codes() -> None:
    text = shift6_adder.make_code_table_text()

    assert "0   | 0110" in text
    assert "9   | 1111" in text


def test_make_result_text_for_case_with_carry() -> None:
    result = shift6_adder.calculate(0b1110, 0b1100)
    text = shift6_adder.make_result_text(result)

    assert "A[3:0] = 1110 => A = 8" in text
    assert "B[3:0] = 1100 => B = 6" in text
    assert "Cout = C /\\ (P3 \\/ (P2 /\\ P1)) = 1" in text
    assert "Результат схемы: 14" in text
    assert "Результат корректен." in text


def test_make_result_text_can_show_failed_decimal_check() -> None:
    result = shift6_adder.calculate(0b0110, 0b0110)
    broken = replace(result, s0_digit=1)

    text = shift6_adder.make_result_text(broken)

    assert "Ошибка: результат схемы не совпал" in text


def test_make_truth_table_text_contains_header_and_expected_rows() -> None:
    rows = [shift6_adder.calculate(0b0110, 0b0110), shift6_adder.calculate(0b1111, 0b1111)]

    text = shift6_adder.make_truth_table_text(rows)

    assert "Таблица истинности" in text
    assert "0110  0 | 0110  0" in text
    assert "1111  9 | 1111  9" in text
    assert "18" in text


def _tiny_ones() -> dict[str, list[int]]:
    ones = {name: [] for name in shift6_adder.OUTPUT_NAMES}
    ones["Cout"] = [127]
    ones["S1_2"] = [102]
    return ones


def test_make_minimization_text_with_compact_sdnf() -> None:
    text = shift6_adder.make_minimization_text(_tiny_ones(), [], include_sdnf=False)

    assert "Синтез и минимизация" in text
    assert "Количество don't care наборов: 0" in text
    assert "Cout:" in text
    assert "СДНФ в компактной форме: Σm(127)" in text
    assert "Минимизированная ДНФ" in text


def test_make_minimization_text_with_full_sdnf() -> None:
    text = shift6_adder.make_minimization_text(_tiny_ones(), [], include_sdnf=True)

    assert "СДНФ:" in text
    assert "(!A3 /\\ A2 /\\ A1 /\\ A0 /\\ B3 /\\ B2 /\\ B1 /\\ B0)" in text
    assert "Минимизированная ДНФ" in text


def test_make_structural_minimization_text_contains_final_scheme() -> None:
    text = shift6_adder.make_structural_minimization_text()

    assert "Cout = C /\\ (P3 \\/ (P2 /\\ P1))" in text
    assert "S1 = 011Cout" in text
    assert "K3 = !Cout" in text


def test_parse_args_defaults_and_flags() -> None:
    with patch.object(sys, "argv", ["prog"]):
        args = shift6_adder.parse_args()

    assert args.no_table is False
    assert args.compact_sdnf is False
    assert args.report is None

    with patch.object(sys, "argv", ["prog", "--no-table", "--compact-sdnf", "--report", "out.txt"]):
        args = shift6_adder.parse_args()

    assert args.no_table is True
    assert args.compact_sdnf is True
    assert args.report == Path("out.txt")


def test_main_outputs_result_minimization_and_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    report_path = tmp_path / "report.txt"

    with patch.object(
        sys,
        "argv",
        ["prog", "--no-table", "--compact-sdnf", "--report", str(report_path)],
    ), patch("builtins.input", side_effect=["1110", "1100"]):
        shift6_adder.main()

    output = capsys.readouterr().out
    report_text = report_path.read_text(encoding="utf-8")

    assert "Одноразрядный сумматор" in output
    assert "8 + 6 = 14" in output
    assert "Результат схемы: 14" in output
    assert "Синтез и минимизация" in output
    assert "СДНФ в компактной форме" in output
    assert "Отчёт сохранён" in output
    assert "8 + 6 = 14" in report_text
    assert "Компактная структурная реализация" in report_text


def test_main_with_table_and_full_sdnf_smoke(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["prog"]), patch("builtins.input", side_effect=["0110", "0111"]):
        shift6_adder.main()

    output = capsys.readouterr().out
    assert "Таблица истинности" in output
    assert "СДНФ:" in output
    assert "0 + 1 = 1" in output
    assert "Результат схемы: 01" in output

