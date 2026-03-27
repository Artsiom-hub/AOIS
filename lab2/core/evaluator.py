def eval_rpn(rpn, env):
    stack = []

    for token in rpn:
        if token in env:
            stack.append(env[token])

        elif token == "NOT":
            a = stack.pop()
            stack.append(int(not a))

        else:
            b = stack.pop()
            a = stack.pop()

            if token == "AND":
                stack.append(a & b)
            elif token == "OR":
                stack.append(a | b)
            elif token == "IMPL":
                stack.append(int((not a) or b))
            elif token == "EQ":
                stack.append(int(a == b))

    return stack[0]