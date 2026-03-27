from itertools import combinations


def minimize_tabular(table, variables):
    minterms = [tuple(row[:-1]) for row in table if row[-1] == 1]

    if not minterms:
        return "Расчетно-табличный\n\nФункция тождественно равна 0"

    if len(minterms) == len(table):
        return "Расчетно-табличный\n\nФункция тождественно равна 1"

    # =========================================================
    # 1. Исходные конституэнты
    # =========================================================
    current_terms = [
        {
            "pattern": m,
            "covers": {m},
            "label": i + 1
        }
        for i, m in enumerate(minterms)
    ]

    lines = []
    lines.append("Расчетно-табличный")
    lines.append("")
    lines.append("Этап склеивания")

    # =========================================================
    # 2. Склеивание (как в расчетном методе)
    # =========================================================
    gluing_lines, prime_implicants = run_gluing_with_trace(current_terms, variables)

    if gluing_lines:
        lines.extend(gluing_lines)
    else:
        lines.append("Склеивание не выполняется")

    # =========================================================
    # 3. Таблица покрытия
    # =========================================================
    lines.append("")
    lines.append("Построение таблицы")

    # сортировка импликант для более адекватного вывода
    prime_implicants = sort_terms(prime_implicants, variables)

    coverage_matrix = []
    for imp in prime_implicants:
        row = []
        for m in minterms:
            row.append(covers_pattern(imp["pattern"], m))
        coverage_matrix.append(row)

    # =========================================================
    # 4. Существенные импликанты
    # =========================================================
    essential = find_essential_prime_implicants(prime_implicants, minterms)

    # =========================================================
    # 5. Точное минимальное покрытие
    # =========================================================
    chosen = exact_minimal_cover(prime_implicants, minterms, essential, variables)

    # =========================================================
    # 6. Таблица в текстовом виде
    # =========================================================
    lines.append("")
    lines.extend(build_cover_table(
        prime_implicants=prime_implicants,
        minterms=minterms,
        variables=variables,
        chosen=chosen
    ))

    # =========================================================
    # 7. Финальный результат
    # =========================================================
    lines.append("")
    lines.append("Убираем лишние импликанты и получаем:")

    final_expr = " v ".join(format_term_for_result(term["pattern"], variables) for term in chosen)
    lines.append(final_expr)

    return "\n".join(lines)


# =========================================================
# СКЛЕИВАНИЕ
# =========================================================

def run_gluing_with_trace(initial_terms, variables):
    current_terms = initial_terms[:]
    all_prime_implicants = []
    lines = []

    while True:
        glued_pairs, next_terms, used_patterns = glue_stage(current_terms)

        if not glued_pairs:
            for term in current_terms:
                if term["pattern"] not in [t["pattern"] for t in all_prime_implicants]:
                    all_prime_implicants.append(term)
            break

        active_var_count = count_active_vars(current_terms[0]["pattern"])
        lines.append(
            f"Ищем скобки, в которых n-1 одинаковых переменных "
            f"(n - общее число переменных, у нас это {active_var_count}), "
            f"и склеиваем их по общим переменным"
        )

        for left_term, right_term, glued_term in glued_pairs:
            left_expr = pattern_to_expr(left_term["pattern"], variables)
            right_expr = pattern_to_expr(right_term["pattern"], variables)
            glued_expr = pattern_to_expr(glued_term["pattern"], variables)

            left_label = left_term.get("label", "")
            right_label = right_term.get("label", "")

            lines.append(
                f"({left_expr}){left_label} ∨ ({right_expr}){right_label} => ({glued_expr})"
            )

        for term in current_terms:
            if term["pattern"] not in used_patterns:
                if term["pattern"] not in [t["pattern"] for t in all_prime_implicants]:
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
        lines.append("")

        current_terms = next_terms

    all_prime_implicants = unique_terms(all_prime_implicants)
    return lines, all_prime_implicants


def glue_stage(current_terms):
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


# =========================================================
# ПОКРЫТИЕ
# =========================================================

def covers_pattern(term_pattern, minterm):
    for t, m in zip(term_pattern, minterm):
        if t is None:
            continue
        if t != m:
            return False
    return True


def find_essential_prime_implicants(prime_implicants, minterms):
    essential = []

    for m in minterms:
        covering = [imp for imp in prime_implicants if covers_pattern(imp["pattern"], m)]
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    return essential


def exact_minimal_cover(prime_implicants, minterms, essential, variables):
    essential_set = list(essential)

    covered_by_essential = set()
    for m in minterms:
        if any(covers_pattern(imp["pattern"], m) for imp in essential_set):
            covered_by_essential.add(m)

    uncovered = [m for m in minterms if m not in covered_by_essential]

    if not uncovered:
        return sort_terms(essential_set, variables)

    candidates = [imp for imp in prime_implicants if imp not in essential_set]

    best_subset = None
    best_key = None

    for r in range(len(candidates) + 1):
        for subset in combinations(candidates, r):
            if all(any(covers_pattern(imp["pattern"], m) for imp in subset) for m in uncovered):
                full = essential_set + list(subset)
                key = (
                    len(full),                              # минимизируем число импликант
                    sum(count_active_vars(x["pattern"]) for x in full),  # потом число литералов
                    [pattern_to_expr(x["pattern"], variables) for x in sort_terms(full, variables)]
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best_subset = full

        if best_subset is not None:
            break

    if best_subset is None:
        best_subset = essential_set

    return sort_terms(best_subset, variables)


# =========================================================
# ТАБЛИЦА
# =========================================================

def build_cover_table(prime_implicants, minterms, variables, chosen):
    chosen_patterns = {term["pattern"] for term in chosen}

    constituent_headers = [f"({pattern_to_expr(m, variables)})" for m in minterms]
    row_names = [format_term_for_result(term["pattern"], variables) for term in prime_implicants]

    first_col_width = max(
        len("Импликанты"),
        max(len(name) for name in row_names) if row_names else 0
    )

    col_widths = []
    for header in constituent_headers:
        col_widths.append(max(len(header), 3))

    lines = []

    # Верхняя шапка
    total_table_width = first_col_width + 3 + sum(w + 3 for w in col_widths)
    lines.append("-" * total_table_width)

    title_width = sum(w + 3 for w in col_widths) - 1
    lines.append(
        f"| {' ' * first_col_width} | "
        f"{center_text('Конституэнты', title_width)} |"
    )
    lines.append("-" * total_table_width)

    # Строка заголовков
    header_line = f"| {pad_right('', first_col_width)} | "
    header_line += " | ".join(center_text(h, w) for h, w in zip(constituent_headers, col_widths))
    header_line += " |"
    lines.append(header_line)
    lines.append("-" * total_table_width)

    # Строки таблицы
    for imp in prime_implicants:
        row_name = format_term_for_result(imp["pattern"], variables)

        # отметка лишней импликанты
        if imp["pattern"] not in chosen_patterns:
            row_name = f"*{row_name}"

        line = f"| {pad_right(row_name, first_col_width)} | "
        cells = []
        for m, w in zip(minterms, col_widths):
            mark = "X" if covers_pattern(imp["pattern"], m) else ""
            cells.append(center_text(mark, w))
        line += " | ".join(cells)
        line += " |"
        lines.append(line)

    lines.append("-" * total_table_width)
    lines.append("* — лишняя импликанта")

    return lines


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


def count_active_vars(pattern):
    return sum(1 for x in pattern if x is not None)


def format_term_for_result(pattern, variables):
    expr = pattern_to_expr(pattern, variables)

    if expr == "1":
        return "1"

    if count_active_vars(pattern) <= 1:
        return expr

    return f"({expr})"


def pad_right(text, width):
    return text + " " * (width - len(text))


def center_text(text, width):
    total = width - len(text)
    left = total // 2
    right = total - left
    return " " * left + text + " " * right


def sort_terms(terms, variables):
    return sorted(
        terms,
        key=lambda t: (
            count_active_vars(t["pattern"]),
            pattern_to_expr(t["pattern"], variables)
        )
    )