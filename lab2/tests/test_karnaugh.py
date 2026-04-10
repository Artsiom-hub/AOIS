from core.truth_table import build_truth_table
from minimization.karnaugh import minimize_karnaugh


def test_karnaugh_for_and():
    table, variables = build_truth_table("a&b")
    result = minimize_karnaugh(table, variables)

    assert "ТАБЛИЧНЫЙ МЕТОД" in result
    assert "Карта Карно" in result
    assert "ab" in result or "(a ∧ b)" in result


def test_karnaugh_for_example_a_or_bc_shape():
    expr = "a|(b&c)"
    table, variables = build_truth_table(expr)
    result = minimize_karnaugh(table, variables)

    assert "Область 1" in result
    assert "a" in result and "bc" in result


def test_karnaugh_5_vars():
    table, variables = build_truth_table("a&b&c&d&e")
    result = minimize_karnaugh(table, variables)

    assert "Карта Карно (5 переменных)" in result
    assert "Результат" in result


def test_karnaugh_zero_case():
    table = [
        [0, 0],
        [1, 0],
    ]
    variables = ["a"]
    result = minimize_karnaugh(table, variables)

    assert "тождественно равна 0" in result