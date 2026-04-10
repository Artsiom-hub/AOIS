from itertools import combinations


def minimize_tabular(table, variables):
    dnf_text = _minimize_tabular_generic(table, variables, target_value=1)
    cnf_text = _minimize_tabular_generic(table, variables, target_value=0)

    return (
        "=== РАСЧЕТНО-ТАБЛИЧНЫЙ МЕТОД: ДНФ ===\n"
        + dnf_text
        + "\n\n"
        + "=== РАСЧЕТНО-ТАБЛИЧНЫЙ МЕТОД: КНФ ===\n"
        + cnf_text
    )


def _minimize_tabular_generic(table, variables, target_value):
    source_terms = [tuple(row[:-1]) for row in table if row[-1] == target_value]

    if target_value == 1:
        if not source_terms:
            return "Расчетно-табличный\n\nФункция тождественно равна 0"
        if len(source_terms) == len(table):
            return "Расчетно-табличный\n\nФункция тождественно равна 1"
        form_join = " ∨ "
    else:
        if not source_terms:
            return "Расчетно-табличный\n\nФункция тождественно равна 1"
        if len(source_terms) == len(table):
            return "Расчетно-табличный\n\nФункция тождественно равна 0"
        form_join = " ∧ "

    current_terms = [
        {
            "pattern": m,
            "covers": {m},
            "label": i + 1
        }
        for i, m in enumerate(source_terms)
    ]

    lines = []
    lines.append("Расчетно-табличный")
    lines.append("")
    lines.append("Этап склеивания")

    gluing_lines, prime_implicants = run_gluing_with_trace(current_terms, variables, target_value)

    if gluing_lines:
        lines.extend(gluing_lines)
    else:
        lines.append("Склеивание не выполняется")

    lines.append("")
    lines.append("Построение таблицы")

    prime_implicants = sort_terms(prime_implicants, variables, target_value)

    essential = find_essential_prime_implicants(prime_implicants, source_terms)
    chosen = exact_minimal_cover(prime_implicants, source_terms, essential, variables, target_value)

    lines.append("")
    lines.extend(build_cover_table(
        prime_implicants=prime_implicants,
        source_terms=source_terms,
        variables=variables,
        chosen=chosen,
        target_value=target_value
    ))

    lines.append("")
    lines.append("Убираем лишние импликанты и получаем:")
    final_expr = form_join.join(format_term_for_result(term["pattern"], variables, target_value) for term in chosen)
    lines.append(final_expr)

    return "\n".join(lines)


def run_gluing_with_trace(initial_terms, variables, target_value):
    current_terms = initial_terms[:]
    all_prime_implicants = []
    lines = []
    join_symbol = " ∨ " if target_value == 1 else " ∧ "

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
            f"(n - число активных переменных, сейчас {active_var_count}), "
            f"и склеиваем их по общим переменным"
        )

        for left_term, right_term, glued_term in glued_pairs:
            left_expr = pattern_to_expr(left_term["pattern"], variables, target_value)
            right_expr = pattern_to_expr(right_term["pattern"], variables, target_value)
            glued_expr = pattern_to_expr(glued_term["pattern"], variables, target_value)

            left_label = left_term.get("label", "")
            right_label = right_term.get("label", "")

            lines.append(
                f"{format_term_raw(left_expr)}{left_label}"
                f"{join_symbol}"
                f"{format_term_raw(right_expr)}{right_label}"
                f" => {format_term_raw(glued_expr)}"
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
            join_symbol.join(
                f"{format_term_raw(pattern_to_expr(term['pattern'], variables, target_value))}{i}"
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


def covers_pattern(term_pattern, source_term):
    for t, m in zip(term_pattern, source_term):
        if t is None:
            continue
        if t != m:
            return False
    return True


def find_essential_prime_implicants(prime_implicants, source_terms):
    essential = []

    for m in source_terms:
        covering = [imp for imp in prime_implicants if covers_pattern(imp["pattern"], m)]
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    return essential


def exact_minimal_cover(prime_implicants, source_terms, essential, variables, target_value):
    essential_set = list(essential)

    covered_by_essential = set()
    for m in source_terms:
        if any(covers_pattern(imp["pattern"], m) for imp in essential_set):
            covered_by_essential.add(m)

    uncovered = [m for m in source_terms if m not in covered_by_essential]

    if not uncovered:
        return sort_terms(essential_set, variables, target_value)

    candidates = [imp for imp in prime_implicants if imp not in essential_set]

    best_subset = None
    best_key = None

    for r in range(len(candidates) + 1):
        for subset in combinations(candidates, r):
            if all(any(covers_pattern(imp["pattern"], m) for imp in subset) for m in uncovered):
                full = essential_set + list(subset)
                key = (
                    len(full),
                    sum(count_active_vars(x["pattern"]) for x in full),
                    [pattern_to_expr(x["pattern"], variables, target_value) for x in sort_terms(full, variables, target_value)]
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best_subset = full

        if best_subset is not None:
            break

    if best_subset is None:
        best_subset = essential_set

    return sort_terms(best_subset, variables, target_value)


def build_cover_table(prime_implicants, source_terms, variables, chosen, target_value):
    chosen_patterns = {term["pattern"] for term in chosen}

    constituent_headers = [format_term_raw(pattern_to_expr(m, variables, target_value)) for m in source_terms]
    row_names = [format_term_for_result(term["pattern"], variables, target_value) for term in prime_implicants]

    first_col_width = max(
        len("Импликанты"),
        max(len(name) for name in row_names) if row_names else 0
    )

    col_widths = [max(len(header), 3) for header in constituent_headers]

    lines = []
    total_table_width = first_col_width + 3 + sum(w + 3 for w in col_widths)
    lines.append("-" * total_table_width)

    title_width = sum(w + 3 for w in col_widths) - 1
    lines.append(
        f"| {' ' * first_col_width} | "
        f"{center_text('Конституэнты', title_width)} |"
    )
    lines.append("-" * total_table_width)

    header_line = f"| {pad_right('', first_col_width)} | "
    header_line += " | ".join(center_text(h, w) for h, w in zip(constituent_headers, col_widths))
    header_line += " |"
    lines.append(header_line)
    lines.append("-" * total_table_width)

    for imp in prime_implicants:
        row_name = format_term_for_result(imp["pattern"], variables, target_value)

        if imp["pattern"] not in chosen_patterns:
            row_name = f"*{row_name}"

        line = f"| {pad_right(row_name, first_col_width)} | "
        cells = []
        for m, w in zip(source_terms, col_widths):
            mark = "X" if covers_pattern(imp["pattern"], m) else ""
            cells.append(center_text(mark, w))
        line += " | ".join(cells)
        line += " |"
        lines.append(line)

    lines.append("-" * total_table_width)
    lines.append("* — лишняя импликанта")

    return lines


def pattern_to_expr(pattern, variables, target_value):
    if target_value == 1:
        parts = []
        for value, var in zip(pattern, variables):
            if value is None:
                continue
            if value == 1:
                parts.append(var)
            else:
                parts.append(f"¬{var}")
        return "".join(parts) if parts else "1"

    parts = []
    for value, var in zip(pattern, variables):
        if value is None:
            continue
        if value == 1:
            parts.append(f"¬{var}")
        else:
            parts.append(var)

    if not parts:
        return "0"

    return " ∨ ".join(parts)


def pattern_to_vector_str(pattern):
    return "(" + ",".join("X" if x is None else str(x) for x in pattern) + ")"


def count_active_vars(pattern):
    return sum(1 for x in pattern if x is not None)


def format_term_for_result(pattern, variables, target_value):
    expr = pattern_to_expr(pattern, variables, target_value)

    if target_value == 1:
        if expr == "1":
            return "1"
        if count_active_vars(pattern) <= 1:
            return expr
        return f"({expr})"

    if expr == "0":
        return "0"
    return f"({expr})"


def format_term_raw(expr):
    return f"({expr})"


def pad_right(text, width):
    return text + " " * (width - len(text))


def center_text(text, width):
    total = width - len(text)
    left = total // 2
    right = total - left
    return " " * left + text + " " * right


def sort_terms(terms, variables, target_value):
    return sorted(
        terms,
        key=lambda t: (
            count_active_vars(t["pattern"]),
            pattern_to_expr(t["pattern"], variables, target_value)
        )
    )