def zhegalkin_polynomial(table):
    """
    Возвращает строку полинома Жегалкина
    """

    values = [row[-1] for row in table]
    n = len(values)

    # =========================
    # 1. Треугольник Жегалкина
    # =========================
    triangle = [values]

    for i in range(1, n):
        prev = triangle[-1]
        curr = [(prev[j] ^ prev[j + 1]) for j in range(len(prev) - 1)]
        triangle.append(curr)

    # =========================
    # 2. Коэффициенты
    # =========================
    coeffs = [row[0] for row in triangle]

    # =========================
    # 3. Получаем переменные
    # =========================
    var_count = len(table[0]) - 1
    variables = ["a", "b", "c", "d", "e"][:var_count]

    # =========================
    # 4. Сборка полинома
    # =========================
    terms = []

    for i, coef in enumerate(coeffs):
        if coef == 0:
            continue

        if i == 0:
            terms.append("1")
            continue

        term_vars = []

        # бинарное представление индекса
        for bit in range(var_count):
            if (i >> bit) & 1:
                term_vars.append(variables[var_count - 1 - bit])

        term_vars.sort(key=lambda x: variables.index(x))
        terms.append("".join(term_vars))

    if not terms:
        return "0"

    return " ⊕ ".join(terms)