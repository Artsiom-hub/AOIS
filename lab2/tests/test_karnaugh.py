from core.truth_table import build_truth_table
from minimization.karnaugh import minimize_karnaugh


def test_karnaugh_for_and():
    table, variables = build_truth_table("a&b")
    result = minimize_karnaugh(table, variables)

    assert "Табличный метод" in result
    assert "Карта Карно" in result
    assert "ab" in result


def test_karnaugh_for_example_a_or_bc_shape():
    expr = "a|(b&c)"
    table, variables = build_truth_table(expr)
    result = minimize_karnaugh(table, variables)

    assert "Область 1" in result
    assert "минимизированную ДНФ" in result


def test_karnaugh_for_more_than_4_vars():
    table = []
    variables = ["a", "b", "c", "d", "e"]
    result = minimize_karnaugh(table, variables)
    assert "только для 2–4 переменных" in result or "2–4 переменных" in result


def test_karnaugh_zero_case():
    table = [
        [0, 0],
        [1, 0],
    ]
    variables = ["a"]
    result = minimize_karnaugh(table, variables)
    assert "тождественно равна 0" in result