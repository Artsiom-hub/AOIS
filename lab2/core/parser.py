import re

OPERATORS = {
    "NOT": (3, "right"),
    "AND": (2, "left"),
    "OR": (1, "left"),
    "IMPL": (0, "right"),
    "EQ": (0, "left"),
}


def tokenize(expr):
    expr = expr.replace(" ", "")
    expr = expr.replace("->", " IMPL ")
    expr = expr.replace("~", " EQ ")
    expr = expr.replace("!", " NOT ")
    expr = expr.replace("&", " AND ")
    expr = expr.replace("|", " OR ")

    tokens = re.findall(r"[A-Za-z]+|\(|\)|AND|OR|NOT|IMPL|EQ", expr)
    return tokens


def to_rpn(tokens):
    output = []
    stack = []

    for token in tokens:
        if token in "abcde":
            output.append(token)

        elif token in OPERATORS:
            while (
                stack
                and stack[-1] in OPERATORS
                and (
                    OPERATORS[token][0] < OPERATORS[stack[-1]][0]
                    or (
                        OPERATORS[token][0] == OPERATORS[stack[-1]][0]
                        and OPERATORS[token][1] == "left"
                    )
                )
            ):
                output.append(stack.pop())
            stack.append(token)

        elif token == "(":
            stack.append(token)

        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()

    while stack:
        output.append(stack.pop())

    return output