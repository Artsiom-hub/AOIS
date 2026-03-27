from core.truth_table import build_truth_table
from algebra.normal_forms import (
    build_sdnf,
    build_sknf,
    build_sdnf_numeric,
    build_sknf_numeric,
    format_sdnf_numeric,
    format_sknf_numeric,
)


def test_sdnf_and_sknf_for_and():
    table, variables = build_truth_table("a&b")

    assert build_sdnf(table, variables) == "(a & b)"
    assert build_sknf(table, variables) == "(a | b) & (a | !b) & (!a | b)"


def test_sdnf_and_sknf_for_or():
    table, variables = build_truth_table("a|b")

    assert build_sdnf(table, variables) == "(!a & b) | (a & !b) | (a & b)"
    assert build_sknf(table, variables) == "(a | b)"


def test_sdnf_numeric_for_and():
    table, _ = build_truth_table("a&b")
    assert build_sdnf_numeric(table) == [3]
    assert format_sdnf_numeric([3]) == "F = Σ(3)"


def test_sknf_numeric_for_and():
    table, _ = build_truth_table("a&b")
    assert build_sknf_numeric(table) == [0, 1, 2]
    assert format_sknf_numeric([0, 1, 2]) == "F = Π(0, 1, 2)"


def test_numeric_format_edge_cases():
    assert format_sdnf_numeric([]) == "F = 0"
    assert format_sknf_numeric([]) == "F = 1"


def test_sdnf_edge_case_constant_zero():
    table = [[0, 0], [1, 0]]
    variables = ["a"]
    assert build_sdnf(table, variables) == "0"


def test_sknf_edge_case_constant_one():
    table = [[0, 1], [1, 1]]
    variables = ["a"]
    assert build_sknf(table, variables) == "1"