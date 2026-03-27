from itertools import combinations


def minimize_qm(table, variables):
    """
    Расчетный метод минимизации по СДНФ
    с выводом стадий склеивания и удалением лишних импликант.
    """

    minterms = [row[:-1] for row in table if row[-1] == 1]

    if not minterms:
        return "Функция тождественно равна 0"

    if len(minterms) == len(table):
        return "Функция тождественно равна 1"

    current_terms = []
    for idx, values in enumerate(minterms, start=1):
        current_terms.append({
            "pattern": tuple(values),          # например (1,0,1)
            "covers": {tuple(values)},         # какие наборы покрывает
            "label": idx                       # номер для красивого вывода
        })

    lines = []

    # =========================
    # 1. Исходная СДНФ
    # =========================
    original_sdnf = " ∨ ".join(
        f"({pattern_to_expr(term['pattern'], variables)}){i}"
        for i, term in enumerate(current_terms, start=1)
    )
    lines.append("Расчетный метод")
    lines.append(f"Исходная СДНФ: {original_sdnf}")
    lines.append(" ".join(pattern_to_vector_str(term["pattern"]) for term in current_terms))

    # =========================
    # 2. Стадии склеивания
    # =========================
    all_prime_implicants = []

    stage_number = 1
    while True:
        glued, next_terms, used_patterns = glue_stage(current_terms, variables)

        if not glued:
            # всё, что осталось и не было склеено, — простые импликанты
            all_prime_implicants.extend(unique_terms(current_terms))
            break

        lines.append("")
        lines.append("Этап склеивания")
        if current_terms:
            active_var_count = count_active_vars(current_terms[0]["pattern"])
            lines.append(
                f"Ищем скобки в которых n-1 одинаковых переменных "
                f"(n - общее число переменных, у нас это {active_var_count}) "
                f"и склеиваем их по общим переменным"
            )

        for left_term, right_term, glued_term in glued:
            left_expr = pattern_to_expr(left_term["pattern"], variables)
            right_expr = pattern_to_expr(right_term["pattern"], variables)
            glued_expr = pattern_to_expr(glued_term["pattern"], variables)

            left_label = left_term.get("label", "")
            right_label = right_term.get("label", "")
            lines.append(
                f"({left_expr}){left_label} ∨ ({right_expr}){right_label} => ({glued_expr})"
            )

        # неиспользованные текущие — простые импликанты
        for term in current_terms:
            if term["pattern"] not in used_patterns:
                all_prime_implicants.append(term)

        next_terms = unique_terms(next_terms)

        for i, term in enumerate(next_terms, start=1):
            term["label"] = i

        lines.append("Результат:")
        lines.append(
            " ∨ ".join(
                f"({pattern_to_expr(term['pattern'], variables)}){i}"
                for i, term in enumerate(next_terms, start=1)
            )
        )
        lines.append(" ".join(pattern_to_vector_str(term["pattern"]) for term in next_terms))

        current_terms = next_terms
        stage_number += 1

    all_prime_implicants = unique_terms(all_prime_implicants)

    # =========================
    # 3. Удаление лишних импликант
    # =========================
    essential, redundant, chosen = remove_redundant_implicants(all_prime_implicants, minterms)

    lines.append("")
    lines.append("Проверка на наличие лишних импликант")

    for idx, term in enumerate(all_prime_implicants, start=1):
        expr = pattern_to_expr(term["pattern"], variables)
        sample = find_sample_covered_minterm(term, minterms)

        if sample is None:
            lines.append(f"{idx}) ({expr}) не покрывает ни одного минтерма — лишняя")
            continue

        sample_str = "(" + ", ".join(map(str, sample)) + ")"

        if term in redundant:
            lines.append(
                f"{idx}) ({expr}) = 1 на наборе {sample_str}, "
                f"и этот набор уже покрывается другими импликантами => ({expr}) лишняя"
            )
        else:
            lines.append(
                f"{idx}) ({expr}) = 1 на наборе {sample_str}, "
                f"и существует набор, который без неё не покрывается => ({expr}) не лишняя"
            )

    lines.append("")
    lines.append("Убираем лишние импликанты и получаем:")
    final_expr = " ∨ ".join(
        format_term_with_optional_brackets(term["pattern"], variables)
        for term in chosen
    )
    lines.append(final_expr)

    return "\n".join(lines)


# =========================================================
# СКЛЕИВАНИЕ
# =========================================================

def glue_stage(current_terms, variables):
    glued_pairs = []
    next_terms = []
    used_patterns = set()

    for i in range(len(current_terms)):
        for j in range(i + 1, len(current_terms)):
            p1 = current_terms[i]["pattern"]
            p2 = current_terms[j]["pattern"]

            glued_pattern = try_glue(p1, p2)
            if glued_pattern is not None:
                new_term = {
                    "pattern": glued_pattern,
                    "covers": current_terms[i]["covers"] | current_terms[j]["covers"]
                }

                glued_pairs.append((current_terms[i], current_terms[j], new_term))
                next_terms.append(new_term)

                used_patterns.add(p1)
                used_patterns.add(p2)

    return glued_pairs, next_terms, used_patterns


def try_glue(p1, p2):
    """
    Склеивание возможно, если термы отличаются ровно в одной активной позиции,
    а во всех остальных совпадают.
    None = уже склеенная позиция (X).
    """
    diff_count = 0
    result = []

    for a, b in zip(p1, p2):
        if a == b:
            result.append(a)
        else:
            if a is None or b is None:
                return None
            diff_count += 1
            result.append(None)

    if diff_count == 1:
        return tuple(result)

    return None


# =========================================================
# РАБОТА С ИМПЛИКАНТАМИ
# =========================================================

def unique_terms(terms):
    unique = {}
    for term in terms:
        pattern = term["pattern"]
        if pattern not in unique:
            unique[pattern] = {
                "pattern": pattern,
                "covers": set(term["covers"])
            }
            if "label" in term:
                unique[pattern]["label"] = term["label"]
        else:
            unique[pattern]["covers"] |= set(term["covers"])
    return list(unique.values())


def count_active_vars(pattern):
    return sum(1 for x in pattern if x is not None)


def covers_pattern(term_pattern, minterm):
    for t, m in zip(term_pattern, minterm):
        if t is None:
            continue
        if t != m:
            return False
    return True


def find_sample_covered_minterm(term, minterms):
    for m in minterms:
        if covers_pattern(term["pattern"], m):
            return m
    return None


# =========================================================
# УДАЛЕНИЕ ЛИШНИХ ИМПЛИКАНТ
# =========================================================

def remove_redundant_implicants(prime_implicants, minterms):
    """
    Сначала берём обязательные импликанты,
    потом добираем недостающие жадно,
    потом проверяем избыточность.
    """

    coverage_map = {}
    for m in minterms:
        m_tuple = tuple(m)
        coverage_map[m_tuple] = []
        for imp in prime_implicants:
            if covers_pattern(imp["pattern"], m):
                coverage_map[m_tuple].append(imp)

    chosen = []

    # 1. Существенные простые импликанты
    essential = []
    for m, covering in coverage_map.items():
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    chosen.extend(essential)

    # 2. Какие минтермы уже покрыты
    covered = set()
    for imp in chosen:
        for m in minterms:
            if covers_pattern(imp["pattern"], m):
                covered.add(tuple(m))

    # 3. Добираем остальные жадно
    uncovered = set(tuple(m) for m in minterms) - covered

    while uncovered:
        best_imp = None
        best_count = -1

        for imp in prime_implicants:
            if imp in chosen:
                continue

            count = sum(1 for m in uncovered if covers_pattern(imp["pattern"], m))
            if count > best_count:
                best_count = count
                best_imp = imp

        if best_imp is None:
            break

        chosen.append(best_imp)
        for m in list(uncovered):
            if covers_pattern(best_imp["pattern"], m):
                uncovered.discard(m)

    # 4. Выкидываем лишние
    final_chosen = chosen[:]
    changed = True

    while changed:
        changed = False
        for imp in final_chosen[:]:
            others = [x for x in final_chosen if x != imp]

            all_covered = True
            for m in minterms:
                if covers_pattern(imp["pattern"], m):
                    if not any(covers_pattern(other["pattern"], m) for other in others):
                        all_covered = False
                        break

            if all_covered:
                final_chosen.remove(imp)
                changed = True

    redundant = [imp for imp in prime_implicants if imp not in final_chosen]

    return essential, redundant, final_chosen


# =========================================================
# ФОРМАТИРОВАНИЕ
# =========================================================

def pattern_to_expr(pattern, variables):
    parts = []
    for value, var in zip(pattern, variables):
        if value is None:
            continue
        if value == 1:
            parts.append(var)
        else:
            parts.append(f"¬{var}")

    if not parts:
        return "1"

    return "".join(parts)


def pattern_to_vector_str(pattern):
    return "(" + ",".join("X" if x is None else str(x) for x in pattern) + ")"


def format_term_with_optional_brackets(pattern, variables):
    expr = pattern_to_expr(pattern, variables)
    active_count = count_active_vars(pattern)

    if expr == "1":
        return "1"

    if active_count <= 1:
        return expr

    return f"({expr})"