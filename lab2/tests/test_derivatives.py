from algebra.derivatives import compute_derivatives


def test_derivatives_for_and():
    result = compute_derivatives("a&b", ["a", "b"])

    assert result["∂(a)"] == [0, 1]
    assert result["∂(b)"] == [0, 1]
    assert result["∂(ab)"] == [1]


def test_derivatives_for_not_a():
    result = compute_derivatives("!a", ["a"])

    assert result["∂(a)"] == [1]


def test_derivatives_complex_expression():
    expr = "((a~b)~((((c&a)&d)|(!a))->b))"
    result = compute_derivatives(expr, ["a", "b", "c", "d"])

    assert result["∂(a)"] == [0, 0, 0, 1, 1, 1, 1, 1]
    assert result["∂(b)"] == [0, 0, 0, 0, 1, 1, 1, 0]
    assert result["∂(c)"] == [0, 0, 0, 0, 0, 1, 0, 0]
    assert result["∂(d)"] == [0, 0, 0, 0, 0, 1, 0, 0]
    assert result["∂(ab)"] == [1, 1, 1, 0]
    assert result["∂(ac)"] == [0, 1, 0, 0]
    assert result["∂(ad)"] == [0, 1, 0, 0]
    assert result["∂(bc)"] == [0, 0, 0, 1]
    assert result["∂(bd)"] == [0, 0, 0, 1]
    assert result["∂(cd)"] == [0, 0, 1, 0]
    assert result["∂(abc)"] == [0, 1]
    assert result["∂(abd)"] == [0, 1]
    assert result["∂(acd)"] == [1, 0]
    assert result["∂(bcd)"] == [0, 1]
    assert result["∂(abcd)"] == [1]