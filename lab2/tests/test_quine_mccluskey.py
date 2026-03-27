from core.truth_table import build_truth_table
from minimization.quine_mccluskey import minimize_qm


def test_qm_for_and():
    table, variables = build_truth_table("a&b")
    result = minimize_qm(table, variables)

    assert "Расчетный метод" in result
    assert "(ab)" in result or "ab" in result


def test_qm_for_zero():
    table = [
        [0, 0],
        [1, 0],
    ]
    variables = ["a"]
    result = minimize_qm(table, variables)
    assert "тождественно равна 0" in result


def test_qm_for_one():
    table = [
        [0, 1],
        [1, 1],
    ]
    variables = ["a"]
    result = minimize_qm(table, variables)
    assert "тождественно равна 1" in result


def test_qm_example_like_methodical_case():
    expr = "(a&b)|(!a&b&c)"
    table, variables = build_truth_table(expr)
    result = minimize_qm(table, variables)

    assert "Этап склеивания" in result
    assert "Убираем лишние импликанты" in result