def check_post_classes(table):
    """
    table: список строк [x1, x2, ..., xn, F]
    """

    results = {
        "T0": False,
        "T1": False,
        "S": False,
        "M": False,
        "L": False,
    }

    n = len(table[0]) - 1  # число переменных

    # =========================
    # T0
    # =========================
    results["T0"] = table[0][-1] == 0

    # =========================
    # T1
    # =========================
    results["T1"] = table[-1][-1] == 1

    # =========================
    # S (самодвойственная)
    # =========================
    is_self_dual = True
    for i in range(len(table)):
        j = len(table) - 1 - i
        if table[i][-1] == table[j][-1]:
            is_self_dual = False
            break

    results["S"] = is_self_dual

    # =========================
    # M (монотонная)
    # =========================
    is_monotone = True

    for i in range(len(table)):
        for j in range(len(table)):
            x = table[i][:-1]
            y = table[j][:-1]

            # проверяем x <= y (покомпонентно)
            if all(x[k] <= y[k] for k in range(n)):
                if table[i][-1] > table[j][-1]:
                    is_monotone = False
                    break
        if not is_monotone:
            break

    results["M"] = is_monotone

    # =========================
    # L (линейная)
    # =========================
    results["L"] = is_linear(table)

    return results

def is_linear(table):
    """
    Проверка линейности через полином Жегалкина
    Линейная функция = нет произведений переменных
    """

    values = [row[-1] for row in table]
    n = len(values)

    # строим треугольник Жегалкина
    triangle = [values]

    for i in range(1, n):
        prev = triangle[-1]
        curr = [(prev[j] ^ prev[j + 1]) for j in range(len(prev) - 1)]
        triangle.append(curr)

    # коэффициенты = первый столбец
    coeffs = [row[0] for row in triangle]

    # проверка: степени двойки (1,2,4,8...) допустимы
    for i in range(len(coeffs)):
        if coeffs[i] == 1:
            if i == 0:
                continue
            if (i & (i - 1)) != 0:  # не степень двойки
                return False

    return True