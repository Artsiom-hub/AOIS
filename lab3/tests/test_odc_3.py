from itertools import product
from unittest.mock import patch

import pytest

import odc_3


def test_full_adder_all_input_combinations():
    for a, b, cin in product([0, 1], repeat=3):
        s, cout = odc_3.full_adder(a, b, cin)
        assert s == (a + b + cin) % 2
        assert cout == (a + b + cin) // 2


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0", 0), ("1", 1), (" 1 ", 1), ("\n0\t", 0)],
)
def test_parse_bit_valid_values(raw, expected):
    assert odc_3.parse_bit(raw) == expected


@pytest.mark.parametrize("raw", ["", "2", "10", "abc", "-1"])
def test_parse_bit_invalid_values(raw):
    with pytest.raises(ValueError, match="0 или 1"):
        odc_3.parse_bit(raw)


def test_read_bit_retries_until_valid(capsys):
    with patch("builtins.input", side_effect=["x", "2", "1"]):
        assert odc_3.read_bit("A") == 1

    output = capsys.readouterr().out
    assert output.count("Ошибка") == 2


def test_build_truth_table_contains_correct_rows():
    table = odc_3.build_truth_table()

    assert len(table) == 8
    assert table[0] == {"A": 0, "B": 0, "Cin": 0, "S": 0, "Cout": 0}
    assert table[-1] == {"A": 1, "B": 1, "Cin": 1, "S": 1, "Cout": 1}

    for row in table:
        s, cout = odc_3.full_adder(row["A"], row["B"], row["Cin"])
        assert row["S"] == s
        assert row["Cout"] == cout


def test_row_to_index_and_bits_by_index_are_consistent():
    for index in range(8):
        bits = odc_3.bits_by_index(index, 3)
        row = dict(zip(odc_3.VARIABLES, bits))
        assert odc_3.row_to_index(row) == index


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (0, "(!A /\\ !B /\\ !Cin)"),
        (3, "(!A /\\ B /\\ Cin)"),
        (7, "(A /\\ B /\\ Cin)"),
    ],
)
def test_canonical_term_by_index(index, expected):
    assert odc_3.canonical_term_by_index(index) == expected


def test_build_sdnf_empty_and_non_empty():
    assert odc_3.build_sdnf([]) == "0"
    assert odc_3.build_sdnf([1, 2]) == (
        "(!A /\\ !B /\\ Cin) \\/ (!A /\\ B /\\ !Cin)"
    )


@pytest.mark.parametrize(
    ("pattern", "bits", "expected"),
    [
        ("10-", (1, 0, 0), True),
        ("10-", (1, 0, 1), True),
        ("10-", (1, 1, 0), False),
        ("---", (0, 1, 1), True),
    ],
)
def test_pattern_matches(pattern, bits, expected):
    assert odc_3.pattern_matches(pattern, bits) is expected


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("---", "1"),
        ("10-", "(A /\\ !B)"),
        ("0-1", "(!A /\\ Cin)"),
    ],
)
def test_pattern_to_term(pattern, expected):
    assert odc_3.pattern_to_term(pattern) == expected


def test_get_minterms_for_sum_and_carry():
    table = odc_3.build_truth_table()
    assert odc_3.get_minterms(table, "S") == [1, 2, 4, 7]
    assert odc_3.get_minterms(table, "Cout") == [3, 5, 6, 7]


def test_minimize_sdnf_special_cases():
    assert odc_3.minimize_sdnf([], 3) == ([], "0")
    assert odc_3.minimize_sdnf(list(range(8)), 3) == (["---"], "1")


def test_minimize_sdnf_for_full_adder_outputs():
    table = odc_3.build_truth_table()

    s_patterns, s_expression = odc_3.minimize_sdnf(
        odc_3.get_minterms(table, "S"), 3
    )
    cout_patterns, cout_expression = odc_3.minimize_sdnf(
        odc_3.get_minterms(table, "Cout"), 3
    )

    assert s_patterns == ["001", "010", "100", "111"]
    assert s_expression == (
        "(!A /\\ !B /\\ Cin) \\/ (!A /\\ B /\\ !Cin) \\/ "
        "(A /\\ !B /\\ !Cin) \\/ (A /\\ B /\\ Cin)"
    )
    assert cout_patterns == ["-11", "1-1", "11-"]
    assert cout_expression == "(B /\\ Cin) \\/ (A /\\ Cin) \\/ (A /\\ B)"


def test_print_truth_table(capsys):
    odc_3.print_truth_table(odc_3.build_truth_table())
    output = capsys.readouterr().out
    assert "Таблица истинности ОДС-3" in output
    assert "A B Cin | S Cout" in output
    assert "1 1  1  | 1   1" in output


@pytest.mark.parametrize(
    ("output_name", "patterns", "expected_fragments"),
    [
        ("F", [], ["F = 0", "выход всегда равен 0"]),
        ("F", ["---"], ["F = 1", "выход всегда равен 1"]),
        ("F", ["1--"], ["Инверторы не требуются", "Выход напрямую"]),
        ("F", ["0-1", "11-"], ["Инверторы:", "NOT_A", "Элемент OR"]),
    ],
)
def test_print_gate_synthesis_branches(output_name, patterns, expected_fragments, capsys):
    odc_3.print_gate_synthesis(output_name, patterns)
    output = capsys.readouterr().out
    for fragment in expected_fragments:
        assert fragment in output


def test_main_runs_complete_synthesis(capsys):
    with patch("builtins.input", side_effect=["0", "1", "1"]):
        odc_3.main()

    output = capsys.readouterr().out
    assert "ОДС-3" in output
    assert "S = 0" in output
    assert "Cout = 1" in output
    assert "Функция S" in output
    assert "Функция Cout" in output
    assert "Итоговые функции ОДС-3" in output
