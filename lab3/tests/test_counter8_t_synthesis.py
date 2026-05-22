from pathlib import Path
from unittest.mock import patch

import pytest
from sympy import And, Not, Or, Symbol, false, true

import counter8_t_synthesis as counter


def test_int_to_bits_default_and_custom_width():
    assert counter.int_to_bits(0) == (0, 0, 0)
    assert counter.int_to_bits(5) == (1, 0, 1)
    assert counter.int_to_bits(7) == (1, 1, 1)
    assert counter.int_to_bits(5, width=4) == (0, 1, 0, 1)


@pytest.mark.parametrize(
    ("bits", "expected"),
    [
        ([], 0),
        ([0, 0, 0], 0),
        ([1, 0, 1], 5),
        ((1, 1, 1), 7),
        ([1, 0, 0, 1], 9),
    ],
)
def test_bits_to_int(bits, expected):
    assert counter.bits_to_int(bits) == expected


def test_build_counter_truth_table_has_expected_cycle_and_t_values():
    rows = counter.build_counter_truth_table()

    assert len(rows) == 8
    assert rows[0].state == 0
    assert rows[0].q == (0, 0, 0)
    assert rows[0].q_next == (0, 0, 1)
    assert rows[0].t == (0, 0, 1)

    assert rows[3].q == (0, 1, 1)
    assert rows[3].q_next == (1, 0, 0)
    assert rows[3].t == (1, 1, 1)

    assert rows[7].q == (1, 1, 1)
    assert rows[7].next_state == 0
    assert rows[7].q_next == (0, 0, 0)
    assert rows[7].t == (1, 1, 1)


def test_full_sdnf_empty_and_non_empty():
    assert counter.full_sdnf([], ["Q2", "Q1", "Q0"]) == "0"
    assert counter.full_sdnf(
        [(0, 0, 1), (1, 1, 1)], ["Q2", "Q1", "Q0"]
    ) == "(!Q2 /\\ !Q1 /\\ Q0) \\/ (Q2 /\\ Q1 /\\ Q0)"


def test_format_expr_all_supported_expression_types():
    q2 = Symbol("Q2")
    q1 = Symbol("Q1")
    q0 = Symbol("Q0")

    assert counter.format_expr(true) == "1"
    assert counter.format_expr(false) == "0"
    assert counter.format_expr(q0) == "Q0"
    assert counter.format_expr(Not(q0)) == "!Q0"
    assert counter.format_expr(Not(And(q1, q0))) == "!((Q0 /\\ Q1))"
    assert counter.format_expr(And(q1, q0)) == "(Q0 /\\ Q1)"
    assert counter.format_expr(Or(q2, And(q1, q0))) == "Q2 \\/ (Q0 /\\ Q1)"


# Проверяем fallback-ветку: объект не является Symbol/Not/And/Or/true/false.
class DummyExpr:
    func = object()

    def __str__(self):
        return "dummy"


def test_format_expr_fallback_branch():
    assert counter.format_expr(DummyExpr()) == "dummy"


def test_minimize_t_functions_for_counter():
    rows = counter.build_counter_truth_table()
    q2, q1, q0 = Symbol("Q2"), Symbol("Q1"), Symbol("Q0")
    variables = [q2, q1, q0]

    t2_minterms, t2_expr = counter.minimize_t_function(rows, 0, variables)
    t1_minterms, t1_expr = counter.minimize_t_function(rows, 1, variables)
    t0_minterms, t0_expr = counter.minimize_t_function(rows, 2, variables)

    assert [counter.bits_to_int(bits) for bits in t2_minterms] == [3, 7]
    assert counter.format_expr(t2_expr) == "(Q0 /\\ Q1)"

    assert [counter.bits_to_int(bits) for bits in t1_minterms] == [1, 3, 5, 7]
    assert counter.format_expr(t1_expr) == "Q0"

    assert [counter.bits_to_int(bits) for bits in t0_minterms] == list(range(8))
    assert counter.format_expr(t0_expr) == "1"


def test_print_truth_table(capsys):
    counter.print_truth_table(counter.build_counter_truth_table())
    output = capsys.readouterr().out
    assert "Таблица истинности / таблица переходов автомата" in output
    assert "Сост. | Q2 Q1 Q0" in output
    assert "    7 | 1  1  1  | 0   0   0   | 1  1  1" in output


@pytest.mark.parametrize("show_sdnf", [True, False])
def test_print_synthesis_with_and_without_sdnf(show_sdnf, capsys):
    counter.print_synthesis(counter.build_counter_truth_table(), show_sdnf=show_sdnf)
    output = capsys.readouterr().out

    assert "T2:" in output
    assert "T1:" in output
    assert "T0:" in output
    assert "T2 = (Q0 /\\ Q1)" in output
    assert "T1 = Q0" in output
    assert "T0 = 1" in output

    if show_sdnf:
        assert "СДНФ" in output
    else:
        assert "СДНФ" not in output


def test_simulate_counter(capsys):
    counter.simulate_counter(9)
    output = capsys.readouterr().out
    assert "000 (0) -> 001 (1)" in output
    assert "111 (7) -> 000 (0)" in output
    assert "000 (0) -> 001 (1)" in output


def test_save_csv(tmp_path):
    rows = counter.build_counter_truth_table()
    csv_path = tmp_path / "counter.csv"

    counter.save_csv(rows, str(csv_path))

    text = csv_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "state;Q2;Q1;Q0;next_state;Q2+;Q1+;Q0+;T2;T1;T0"
    assert lines[1] == "0;0;0;0;1;0;0;1;0;0;1"
    assert lines[-1] == "7;1;1;1;0;0;0;0;1;1;1"


def test_main_default_run(capsys):
    with patch("sys.argv", ["counter8_t_synthesis.py", "--simulate", "2"]):
        counter.main()

    output = capsys.readouterr().out
    assert "Таблица истинности" in output
    assert "СДНФ" in output
    assert "000 (0) -> 001 (1)" in output
    assert "001 (1) -> 010 (2)" in output


def test_main_no_sdnf_and_csv(tmp_path, capsys):
    csv_path = tmp_path / "table.csv"

    with patch(
        "sys.argv",
        [
            "counter8_t_synthesis.py",
            "--no-sdnf",
            "--simulate",
            "1",
            "--csv",
            str(csv_path),
        ],
    ):
        counter.main()

    output = capsys.readouterr().out
    assert "СДНФ" not in output
    assert f"Таблица сохранена в файл: {csv_path}" in output
    assert csv_path.exists()
