from core.truth_table import build_truth_table
from algebra.normal_forms import build_index_form, format_index_form


def test_index_form_for_and():
    table, _ = build_truth_table("a&b")
    vector, index = build_index_form(table)

    assert vector == [0, 0, 0, 1]
    assert index == 1
    assert format_index_form(vector, index) == "F = i4 = 0001₂ = 1₁₀"


def test_index_form_for_or():
    table, _ = build_truth_table("a|b")
    vector, index = build_index_form(table)

    assert vector == [0, 1, 1, 1]
    assert index == 7