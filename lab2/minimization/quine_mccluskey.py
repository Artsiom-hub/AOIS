from itertools import combinations


def minimize_qm(table, variables):
    dnf_text = _minimize_qm_generic(table, variables, target_value=1)
    cnf_text = _minimize_qm_generic(table, variables, target_value=0)

    return (
        "=== РАСЧЕТНЫЙ МЕТОД: ДНФ ===\n"
        + dnf_text
        + "\n\n"
        + "=== РАСЧЕТНЫЙ МЕТОД: КНФ ===\n"
        + cnf_text
    )


def _minimize_qm_generic(table, variables, target_value):
    terms_source = [tuple(row[:-1]) for row in table if row[-1] == target_value]

    if target_value == 1:
        if not terms_source:
            return "Функция тождественно равна 0"
        if len(terms_source) == len(table):
            return "Функция тождественно равна 1"
        form_name = "СДНФ"
        join_symbol = " ∨ "
    else:
        if not terms_source:
            return "Функция тождественно равна 1"
        if len(terms_source) == len(table):
            return "Функция тождественно равна 0"
        form_name = "СКНФ"
        join_symbol = " ∧ "

    current_terms = []
    for idx, values in enumerate(terms_source, start=1):
        current_terms.append({
            "pattern": tuple(values),
            "covers": {tuple(values)},
            "label": idx
        })

    lines = []

    original_expr = join_symbol.join(
        f"{format_term_with_index(term['pattern'], variables, target_value)}{i}"
        for i, term in enumerate(current_terms, start=1)
    )
    lines.append("Расчетный метод")
    lines.append(f"Исходная {form_name}: {original_expr}")
    lines.append(" ".join(pattern_to_vector_str(term["pattern"]) for term in current_terms))

    all_prime_implicants = []

    while True:
        glued, next_terms, used_patterns = glue_stage(current_terms)

        if not glued:
            all_prime_implicants.extend(unique_terms(current_terms))
            break

        lines.append("")
        lines.append("Этап склеивания")
        if current_terms:
            active_var_count = count_active_vars(current_terms[0]["pattern"])
            lines.append(
                f"Ищем скобки, в которых n-1 одинаковых переменных "
                f"(n - число активных переменных, сейчас {active_var_count}), "
                f"и склеиваем их по общим переменным"
            )

        for left_term, right_term, glued_term in glued:
            left_expr = pattern_to_expr(left_term["pattern"], variables, target_value)
            right_expr = pattern_to_expr(right_term["pattern"], variables, target_value)
            glued_expr = pattern_to_expr(glued_term["pattern"], variables, target_value)

            left_label = left_term.get("label", "")
            right_label = right_term.get("label", "")

            lines.append(
                f"{format_term_raw(left_expr, target_value)}{left_label} "
                f"{join_symbol} "
                f"{format_term_raw(right_expr, target_value)}{right_label} "
                f"=> {format_term_raw(glued_expr, target_value)}"
            )

        for term in current_terms:
            if term["pattern"] not in used_patterns:
                all_prime_implicants.append(term)

        next_terms = unique_terms(next_terms)

        for i, term in enumerate(next_terms, start=1):
            term["label"] = i

        lines.append("Результат:")
        lines.append(
            join_symbol.join(
                f"{format_term_with_index(term['pattern'], variables, target_value)}{i}"
                for i, term in enumerate(next_terms, start=1)
            )
        )
        lines.append(" ".join(pattern_to_vector_str(term["pattern"]) for term in next_terms))

        current_terms = next_terms

    all_prime_implicants = unique_terms(all_prime_implicants)

    essential, redundant, chosen = remove_redundant_implicants(all_prime_implicants, terms_source)

    lines.append("")
    lines.append("Проверка на наличие лишних импликант")

    for idx, term in enumerate(all_prime_implicants, start=1):
        expr = pattern_to_expr(term["pattern"], variables, target_value)
        sample = find_sample_covered_term(term, terms_source)

        if sample is None:
            lines.append(f"{idx}) {format_term_raw(expr, target_value)} не покрывает ни одного набора — лишняя")
            continue

        sample_str = "(" + ", ".join(map(str, sample)) + ")"

        if term in redundant:
            lines.append(
                f"{idx}) {format_term_raw(expr, target_value)} "
                f"покрывает набор {sample_str}, но он уже покрывается другими => лишняя"
            )
        else:
            lines.append(
                f"{idx}) {format_term_raw(expr, target_value)} "
                f"покрывает набор {sample_str}, и без неё покрытие нарушится => не лишняя"
            )

    lines.append("")
    lines.append("Убираем лишние импликанты и получаем:")
    final_expr = join_symbol.join(
        format_term_for_result(term["pattern"], variables, target_value)
        for term in chosen
    )
    lines.append(final_expr)

    return "\n".join(lines)


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


def count_active_vars(pattern):
    return sum(1 for x in pattern if x is not None)


def covers_pattern(term_pattern, source_term):
    for t, m in zip(term_pattern, source_term):
        if t is None:
            continue
        if t != m:
            return False
    return True


def find_sample_covered_term(term, source_terms):
    for m in source_terms:
        if covers_pattern(term["pattern"], m):
            return m
    return None


def remove_redundant_implicants(prime_implicants, source_terms):
    coverage_map = {}
    for m in source_terms:
        m_tuple = tuple(m)
        coverage_map[m_tuple] = []
        for imp in prime_implicants:
            if covers_pattern(imp["pattern"], m):
                coverage_map[m_tuple].append(imp)

    chosen = []

    essential = []
    for m, covering in coverage_map.items():
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    chosen.extend(essential)

    covered = set()
    for imp in chosen:
        for m in source_terms:
            if covers_pattern(imp["pattern"], m):
                covered.add(tuple(m))

    uncovered = set(tuple(m) for m in source_terms) - covered

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

    final_chosen = chosen[:]
    changed = True

    while changed:
        changed = False
        for imp in final_chosen[:]:
            others = [x for x in final_chosen if x != imp]

            all_covered = True
            for m in source_terms:
                if covers_pattern(imp["pattern"], m):
                    if not any(covers_pattern(other["pattern"], m) for other in others):
                        all_covered = False
                        break

            if all_covered:
                final_chosen.remove(imp)
                changed = True

    redundant = [imp for imp in prime_implicants if imp not in final_chosen]
    return essential, redundant, final_chosen


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


def format_term_raw(expr, target_value):
    if target_value == 1:
        return f"({expr})"
    return f"({expr})"


def format_term_with_index(pattern, variables, target_value):
    expr = pattern_to_expr(pattern, variables, target_value)
    return format_term_raw(expr, target_value)


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