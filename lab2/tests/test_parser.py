from core.parser import tokenize, to_rpn


def test_tokenize_simple_and():
    assert tokenize("a&b") == ["a", "AND", "b"]


def test_tokenize_with_not_or_impl_eq():
    tokens = tokenize("!(a|b)->c~d")
    assert tokens == ["NOT", "(", "a", "OR", "b", ")", "IMPL", "c", "EQ", "d"]


def test_to_rpn_and_or_priority():
    tokens = tokenize("a|b&c")
    rpn = to_rpn(tokens)
    assert rpn == ["a", "b", "c", "AND", "OR"]


def test_to_rpn_not_priority():
    tokens = tokenize("!a&b")
    rpn = to_rpn(tokens)
    assert rpn == ["a", "NOT", "b", "AND"]


def test_to_rpn_parentheses():
    tokens = tokenize("(a|b)&c")
    rpn = to_rpn(tokens)
    assert rpn == ["a", "b", "OR", "c", "AND"]