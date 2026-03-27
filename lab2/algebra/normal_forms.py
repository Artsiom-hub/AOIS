def build_sdnf(table, variables):
    terms = []

    for row in table:
        if row[-1] == 1:
            term = []
            for v, val in zip(variables, row[:-1]):
                term.append(v if val else f"!{v}")

            if len(term) > 1:
                terms.append("(" + " & ".join(term) + ")")
            else:
                terms.append(term[0])

    if not terms:
        return "0"

    return " | ".join(terms)


def build_sknf(table, variables):
    terms = []

    for row in table:
        if row[-1] == 0:
            term = []
            for v, val in zip(variables, row[:-1]):
                term.append(f"!{v}" if val else v)

            if len(term) > 1:
                terms.append("(" + " | ".join(term) + ")")
            else:
                terms.append(term[0])

    if not terms:
        return "1"

    return " & ".join(terms)
def build_sdnf_numeric(table):
    """
    Возвращает индексы строк, где F = 1
    """
    return [i for i, row in enumerate(table) if row[-1] == 1]


def build_sknf_numeric(table):
    """
    Возвращает индексы строк, где F = 0
    """
    return [i for i, row in enumerate(table) if row[-1] == 0]


def format_sdnf_numeric(indices):
    if not indices:
        return "F = 0"
    return f"F = Σ({', '.join(map(str, indices))})"


def format_sknf_numeric(indices):
    if not indices:
        return "F = 1"
    return f"F = Π({', '.join(map(str, indices))})"

def build_index_form(table):
    """
    Возвращает:
    - бинарный вектор значений функции
    - десятичный индекс
    """

    vector = [row[-1] for row in table]
    binary_str = "".join(map(str, vector))
    index = int(binary_str, 2)

    return vector, index


def format_index_form(vector, index):
    n = len(vector)
    vector_str = "".join(map(str, vector))

    return f"F = i{n} = {vector_str}₂ = {index}₁₀"