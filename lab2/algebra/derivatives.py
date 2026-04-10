from core.parser import tokenize, to_rpn
from core.evaluator import eval_rpn
import itertools


def compute_derivatives(expr, variables):
    tokens = tokenize(expr)
    rpn = to_rpn(tokens)

    results = {}

    var_count = len(variables)


    for i, var in enumerate(variables):
        results[f"∂({var})"] = derivative_single(rpn, variables, i)


    max_order = min(4, var_count)

    for order in range(2, max_order + 1):
        for combo in itertools.combinations(range(var_count), order):
            name = "∂(" + "".join(variables[i] for i in combo) + ")"
            results[name] = derivative_multi(rpn, variables, combo)

    return results



def derivative_single(rpn, variables, var_index):
    other_vars = [v for i, v in enumerate(variables) if i != var_index]

    values = []

    for combo in itertools.product([0, 1], repeat=len(other_vars)):
        env0 = {}
        env1 = {}

        idx = 0
        for i, v in enumerate(variables):
            if i == var_index:
                env0[v] = 0
                env1[v] = 1
            else:
                env0[v] = combo[idx]
                env1[v] = combo[idx]
                idx += 1

        f0 = eval_rpn(rpn, env0)
        f1 = eval_rpn(rpn, env1)

        values.append(f0 ^ f1)

    return values



def derivative_multi(rpn, variables, var_indices):
    other_vars = [v for i, v in enumerate(variables) if i not in var_indices]

    values = []

    for combo in itertools.product([0, 1], repeat=len(other_vars)):
        xor_sum = 0

        
        for mask in range(1 << len(var_indices)):
            env = {}
            idx = 0

            for i, v in enumerate(variables):
                if i in var_indices:
                    bit_pos = var_indices.index(i)
                    env[v] = (mask >> bit_pos) & 1
                else:
                    env[v] = combo[idx]
                    idx += 1

            xor_sum ^= eval_rpn(rpn, env)

        values.append(xor_sum)

    return values