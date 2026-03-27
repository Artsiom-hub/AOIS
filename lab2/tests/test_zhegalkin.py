from core.truth_table import build_truth_table
from algebra.zhegalkin import zhegalkin_polynomial


def test_zhegalkin_for_and():
    table, _ = build_truth_table("a&b")
    assert zhegalkin_polynomial(table) == "ab"


def test_zhegalkin_for_not_a():
    table, _ = build_truth_table("!a")
    assert zhegalkin_polynomial(table) == "1 ⊕ a"


def test_zhegalkin_for_equivalence():
    table, _ = build_truth_table("a~b")
    assert set(zhegalkin_polynomial(table).split(" ⊕ ")) == {"1", "a", "b"}


def test_zhegalkin_complex_case():
    expr = "((a~b)~((((c&a)&d)|(!a))->b))"
    table, _ = build_truth_table(expr)
    assert set(zhegalkin_polynomial(table).split(" ⊕ ")) == {"ab", "acd", "abcd"}