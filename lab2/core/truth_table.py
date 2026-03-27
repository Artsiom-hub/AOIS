import itertools
from core.parser import tokenize, to_rpn
from core.evaluator import eval_rpn


def extract_variables(tokens):
    """Извлекаем переменные из токенов"""
    return sorted(set(t for t in tokens if t in ["a", "b", "c", "d", "e"]))


def generate_combinations(variables):
    """Генерация всех наборов 0/1"""
    return list(itertools.product([0, 1], repeat=len(variables)))


def build_truth_table(expr: str):
    """
    Возвращает:
    - table: список строк (значения переменных + результат)
    - variables: список переменных
    """

    tokens = tokenize(expr)
    rpn = to_rpn(tokens)

    variables = extract_variables(tokens)
    combinations = generate_combinations(variables)

    table = []

    for values in combinations:
        env = dict(zip(variables, values))
        result = eval_rpn(rpn, env)

        row = list(values) + [result]
        table.append(row)

    return table, variables

def print_truth_table(table, variables):
    header = variables + ["F"]
    print("\n" + " | ".join(header))
    print("-" * (4 * len(header)))

    for row in table:
        print(" | ".join(map(str, row)))