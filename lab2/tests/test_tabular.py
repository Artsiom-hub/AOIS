from core.truth_table import build_truth_table
from minimization.tabular import minimize_tabular


def test_tabular_for_and():
    table, variables = build_truth_table("a&b")
    result = minimize_tabular(table, variables)

    assert "Расчетно-табличный" in result
    assert "Построение таблицы" in result or "Конституэнты" in result
    assert "ab" in result


def test_tabular_example_with_two_implicants():
    expr = "(a&b)|(!a&c&d)"
    table, variables = build_truth_table(expr)
    result = minimize_tabular(table, variables)

    assert "Конституэнты" in result
    assert "Убираем лишние импликанты" in result


def test_tabular_zero():
    table = [
        [0, 0],
        [1, 0],
    ]
    variables = ["a"]
    result = minimize_tabular(table, variables)
    assert "тождественно равна 0" in result