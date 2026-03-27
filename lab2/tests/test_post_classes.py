from core.truth_table import build_truth_table
from algebra.post_classes import check_post_classes


def test_post_classes_for_and():
    table, _ = build_truth_table("a&b")
    result = check_post_classes(table)

    assert result["T0"] is True
    assert result["T1"] is True
    assert result["S"] is False
    assert result["M"] is True
    assert result["L"] is False


def test_post_classes_for_xor():
    table, _ = build_truth_table("(a|b)&!(a&b)") # xor in available operations
    result = check_post_classes(table)

    assert result["T0"] is True
    assert result["T1"] is False
    assert result["M"] is False
    assert result["L"] is True


def test_post_classes_for_not_a():
    table, _ = build_truth_table("!a")
    result = check_post_classes(table)

    assert result["T0"] is False
    assert result["T1"] is False
    assert result["S"] is True
    assert result["M"] is False
    assert result["L"] is True