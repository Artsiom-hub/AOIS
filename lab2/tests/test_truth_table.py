from core.truth_table import build_truth_table


def test_truth_table_for_and():
    table, variables = build_truth_table("a&b")

    assert variables == ["a", "b"]
    assert table == [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
    ]


def test_truth_table_for_or():
    table, variables = build_truth_table("a|b")

    assert variables == ["a", "b"]
    assert table == [
        [0, 0, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]


def test_truth_table_for_not():
    table, variables = build_truth_table("!a")
    assert variables == ["a"]
    assert table == [
        [0, 1],
        [1, 0],
    ]


def test_truth_table_for_equivalence():
    table, variables = build_truth_table("a~b")
    assert table == [
        [0, 0, 1],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
    ]


def test_truth_table_for_implication():
    table, variables = build_truth_table("a->b")
    assert table == [
        [0, 0, 1],
        [0, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
    ]