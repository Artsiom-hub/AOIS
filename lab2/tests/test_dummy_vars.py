from core.truth_table import build_truth_table
from algebra.dummy_vars import find_dummy_variables


def test_dummy_var_for_a():
    table, variables = build_truth_table("a")
    assert find_dummy_variables(table, variables) == []


def test_dummy_var_for_a_with_extra_b():
    table = [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 1],
        [1, 1, 1],
    ]
    variables = ["a", "b"]
    assert find_dummy_variables(table, variables) == ["b"]


def test_no_dummy_vars_for_and():
    table, variables = build_truth_table("a&b")
    assert find_dummy_variables(table, variables) == []


def test_all_dummy_vars_for_constant_one():
    table = [
        [0, 0, 1],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]
    variables = ["a", "b"]
    assert find_dummy_variables(table, variables) == ["a", "b"]