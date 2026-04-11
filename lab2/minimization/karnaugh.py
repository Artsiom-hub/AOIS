from itertools import combinations


def minimize_karnaugh(table, variables):
    dnf_text = _minimize_karnaugh_generic(table, variables, target_value=1)
    cnf_text = _minimize_karnaugh_generic(table, variables, target_value=0)

    return (
        "=== ТАБЛИЧНЫЙ МЕТОД (КАРТА КАРНО): ДНФ ===\n"
        + dnf_text
        + "\n\n"
        + "=== ТАБЛИЧНЫЙ МЕТОД (КАРТА КАРНО): КНФ ===\n"
        + cnf_text
    )


def _minimize_karnaugh_generic(table, variables, target_value):
    var_count = len(variables)

    if var_count == 0:
        return "Нет переменных"



    source_terms = [tuple(row[:-1]) for row in table if row[-1] == target_value]

    if target_value == 1:
        if not source_terms:
            return "Функция тождественно равна 0"
        if len(source_terms) == len(table):
            return "Функция тождественно равна 1"
        title = "Карта Карно для минимизации ДНФ"
        explanation = (
            "Выделим на карте Карно прямоугольные области из единиц наибольшей площади, "
            "являющиеся степенями двойки, и выпишем соответствующие им конъюнкции."
        )
        join_symbol = " ∨ "
    else:
        if not source_terms:
            return "Функция тождественно равна 1"
        if len(source_terms) == len(table):
            return "Функция тождественно равна 0"
        title = "Карта Карно для минимизации КНФ"
        explanation = (
            "Выделим на карте Карно прямоугольные области из нулей наибольшей площади, "
            "являющиеся степенями двойки, и выпишем соответствующие им дизъюнкции."
        )
        join_symbol = " ∧ "

    if var_count == 5:
        return _minimize_karnaugh_5(table, variables, target_value)

    row_vars, col_vars = split_variables(variables)
    row_codes = gray_codes(len(row_vars))
    col_codes = gray_codes(len(col_vars))

    grid = build_kmap_grid(table, variables, row_vars, col_vars, row_codes, col_codes)

    all_groups = find_all_valid_groups(
        grid, row_codes, col_codes, row_vars, col_vars, variables, target_value
    )
    prime_groups = filter_prime_groups(all_groups)

    essential = find_essential_groups(prime_groups, source_terms)
    chosen = exact_cover_groups(prime_groups, source_terms, essential, target_value)

    lines = []
    lines.append(title)
    lines.append("")
    lines.append("Карта Карно:")
    lines.extend(render_kmap(grid, row_vars, col_vars, row_codes, col_codes))
    lines.append("")
    lines.append(explanation)
    lines.append("")

    for idx, group in enumerate(chosen, start=1):
        lines.append(f"Область {idx}:")
        lines.extend(render_group_map(grid, row_vars, col_vars, row_codes, col_codes, group["cells"]))
        lines.append("")
        marker = "K" if target_value == 1 else "M"
        lines.append(f"{marker}{idx}: {group['expr']}")
        lines.append("")

    result_expr = join_symbol.join(group["expr"] for group in chosen)
    if target_value == 1:
        lines.append("Объединим их с помощью операции ИЛИ и получим минимизированную ДНФ:")
    else:
        lines.append("Объединим их с помощью операции И и получим минимизированную КНФ:")
    lines.append(result_expr)

    return "\n".join(lines)


def split_variables(variables):
    n = len(variables)

    if n == 1:
        return [variables[0]], []
    if n == 2:
        return [variables[0]], [variables[1]]
    if n == 3:
        return [variables[0]], [variables[1], variables[2]]
    if n == 4:
        return [variables[0], variables[1]], [variables[2], variables[3]]
    if n == 5:
        return [variables[0], variables[1]], [variables[2], variables[3]]    

    raise ValueError("Карта Карно поддерживается только для 1–5 переменных")


def gray_codes(bits):
    if bits == 0:
        return [()]
    if bits == 1:
        return [(0,), (1,)]
    if bits == 2:
        return [(0, 0), (0, 1), (1, 1), (1, 0)]

    return [tuple(int(x) for x in format(i ^ (i >> 1), f"0{bits}b")) for i in range(2 ** bits)]


def build_kmap_grid(table, variables, row_vars, col_vars, row_codes, col_codes):
    value_map = {tuple(row[:-1]): row[-1] for row in table}

    grid = []
    for r_code in row_codes:
        row = []
        for c_code in col_codes:
            assignment = {}

            for v, bit in zip(row_vars, r_code):
                assignment[v] = bit
            for v, bit in zip(col_vars, c_code):
                assignment[v] = bit

            full_tuple = tuple(assignment[v] for v in variables)
            row.append({
                "assignment": full_tuple,
                "value": value_map[full_tuple]
            })
        grid.append(row)

    return grid


def powers_of_two_up_to(n):
    result = []
    x = 1
    while x <= n:
        result.append(x)
        x *= 2
    return result


def find_all_valid_groups(grid, row_codes, col_codes, row_vars, col_vars, variables, target_value):
    rows = len(row_codes)
    cols = len(col_codes)

    valid_groups = []
    seen = set()

    row_sizes = powers_of_two_up_to(rows)
    col_sizes = powers_of_two_up_to(cols)

    for h in row_sizes:
        for w in col_sizes:
            for r0 in range(rows):
                for c0 in range(cols):
                    cells = []
                    assignments = []

                    ok = True

                    for dr in range(h):
                        for dc in range(w):
                            rr = (r0 + dr) % rows
                            cc = (c0 + dc) % cols
                            cell = grid[rr][cc]

                            if cell["value"] != target_value:
                                ok = False
                                break

                            cells.append((rr, cc))
                            assignments.append(cell["assignment"])
                        if not ok:
                            break

                    if not ok:
                        continue

                    cells_key = frozenset(cells)
                    if cells_key in seen:
                        continue
                    seen.add(cells_key)

                    pattern = assignments_to_pattern(assignments)
                    expr = pattern_to_expr(pattern, variables, target_value)

                    valid_groups.append({
                        "cells": cells_key,
                        "assignments": frozenset(assignments),
                        "pattern": pattern,
                        "expr": expr,
                        "size": len(cells_key)
                    })

    return valid_groups


def assignments_to_pattern(assignments):
    assignments = list(assignments)
    var_count = len(assignments[0])

    pattern = []
    for i in range(var_count):
        vals = {a[i] for a in assignments}
        if len(vals) == 1:
            pattern.append(next(iter(vals)))
        else:
            pattern.append(None)
    return tuple(pattern)


def filter_prime_groups(groups):
    prime = []

    for g in groups:
        is_subset = False
        for h in groups:
            if g is h:
                continue
            if g["cells"].issubset(h["cells"]) and len(g["cells"]) < len(h["cells"]):
                is_subset = True
                break
        if not is_subset:
            prime.append(g)

    unique = {}
    for g in prime:
        key = (g["pattern"], g["assignments"])
        if key not in unique:
            unique[key] = g

    return list(unique.values())


def find_essential_groups(groups, source_terms):
    essential = []

    for m in source_terms:
        covering = [g for g in groups if m in g["assignments"]]
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    return essential


def exact_cover_groups(groups, source_terms, essential, target_value):
    essential_set = list(essential)

    covered = set()
    for g in essential_set:
        covered |= set(g["assignments"])

    uncovered = [m for m in source_terms if m not in covered]

    if not uncovered:
        return sort_groups(essential_set)

    candidates = [g for g in groups if g not in essential_set]

    best_solution = None
    best_key = None

    for r in range(len(candidates) + 1):
        for subset in combinations(candidates, r):
            covered_now = set()
            for g in subset:
                covered_now |= set(g["assignments"])

            if all(m in covered_now for m in uncovered):
                full = essential_set + list(subset)

                key = (
                    len(full),
                    -sum(g["size"] for g in full),
                    sum(count_literals(g["pattern"]) for g in full),
                    [g["expr"] for g in sort_groups(full)]
                )

                if best_key is None or key < best_key:
                    best_key = key
                    best_solution = full

        if best_solution is not None:
            break

    return sort_groups(best_solution if best_solution is not None else essential_set)


def render_kmap(grid, row_vars, col_vars, row_codes, col_codes):
    rows = len(row_codes)
    cols = len(col_codes)

    row_header = "".join(row_vars) if row_vars else "-"
    col_header = "".join(col_vars) if col_vars else "-"

    col_labels = ["".join(map(str, code)) if code else "-" for code in col_codes]
    row_labels = ["".join(map(str, code)) if code else "-" for code in row_codes]

    first_col_width = max(len(f"{row_header}\\{col_header}"), max(len(x) for x in row_labels))
    col_width = max(2, max(len(x) for x in col_labels), 1)

    total_width = first_col_width + 3 + cols * (col_width + 3) + 1
    lines = []
    lines.append("-" * total_width)

    header = f"| {pad_right(f'{row_header}\\{col_header}', first_col_width)} | "
    header += " | ".join(center_text(lbl, col_width) for lbl in col_labels)
    header += " |"
    lines.append(header)
    lines.append("-" * total_width)

    for r in range(rows):
        line = f"| {pad_right(row_labels[r], first_col_width)} | "
        vals = [str(grid[r][c]['value']) for c in range(cols)]
        line += " | ".join(center_text(v, col_width) for v in vals)
        line += " |"
        lines.append(line)

    lines.append("-" * total_width)
    return lines


def render_group_map(grid, row_vars, col_vars, row_codes, col_codes, group_cells):
    rows = len(row_codes)
    cols = len(col_codes)

    row_header = "".join(row_vars) if row_vars else "-"
    col_header = "".join(col_vars) if col_vars else "-"

    col_labels = ["".join(map(str, code)) if code else "-" for code in col_codes]
    row_labels = ["".join(map(str, code)) if code else "-" for code in row_codes]

    first_col_width = max(len(f"{row_header}\\{col_header}"), max(len(x) for x in row_labels))
    col_width = max(3, max(len(x) for x in col_labels), 1)

    total_width = first_col_width + 3 + cols * (col_width + 3) + 1
    lines = []
    lines.append("-" * total_width)

    header = f"| {pad_right(f'{row_header}\\{col_header}', first_col_width)} | "
    header += " | ".join(center_text(lbl, col_width) for lbl in col_labels)
    header += " |"
    lines.append(header)
    lines.append("-" * total_width)

    for r in range(rows):
        line = f"| {pad_right(row_labels[r], first_col_width)} | "
        vals = []
        for c in range(cols):
            v = str(grid[r][c]["value"])
            if (r, c) in group_cells:
                v = f"[{v}]"
            vals.append(center_text(v, col_width))
        line += " | ".join(vals)
        line += " |"
        lines.append(line)

    lines.append("-" * total_width)
    return lines


def pattern_to_expr(pattern, variables, target_value):
    if target_value == 1:
        parts = []
        for val, var in zip(pattern, variables):
            if val is None:
                continue
            if val == 1:
                parts.append(var)
            else:
                parts.append(f"¬{var}")
        return "".join(parts) if parts else "1"

    parts = []
    for val, var in zip(pattern, variables):
        if val is None:
            continue
        if val == 1:
            parts.append(f"¬{var}")
        else:
            parts.append(var)

    if not parts:
        return "0"

    return "(" + " ∨ ".join(parts) + ")"


def count_literals(pattern):
    return sum(1 for x in pattern if x is not None)


def sort_groups(groups):
    return sorted(
        groups,
        key=lambda g: (
            count_literals(g["pattern"]),
            g["expr"]
        )
    )


def pad_right(text, width):
    return text + " " * (width - len(text))


def center_text(text, width):
    total = width - len(text)
    left = total // 2
    right = total - left
    return " " * left + text + " " * right
def dominates(p1, p2):
    """
    p1 доминирует p2 если:
    все фиксированные переменные p1 совпадают с p2
    и p1 менее конкретен
    """
    for a, b in zip(p1, p2):
        if a is None:
            continue
        if a != b:
            return False
    return True


def simplify_groups(groups):
    result = []

    for g1 in groups:
        dominated = False
        for g2 in groups:
            if g1 == g2:
                continue
            if dominates(g2["pattern"], g1["pattern"]):
                if count_literals(g2["pattern"]) <= count_literals(g1["pattern"]):
                    dominated = True
                    break
        if not dominated:
            result.append(g1)

    return result


def _minimize_karnaugh_5(table, variables, target_value):
    a, b, c, d, e = variables

    # строим 2 карты
    row_vars = [a, b]
    col_vars = [c, d]

    row_codes = gray_codes(2)
    col_codes = gray_codes(2)

    value_map = {tuple(row[:-1]): row[-1] for row in table}

    grids = {}

    for e_val in [0, 1]:
        grid = []

        for r_code in row_codes:
            row = []
            for c_code in col_codes:
                assignment = {
                    a: r_code[0],
                    b: r_code[1],
                    c: c_code[0],
                    d: c_code[1],
                    e: e_val
                }

                key = tuple(assignment[v] for v in variables)

                row.append({
                    "assignment": key,
                    "value": value_map[key]
                })

            grid.append(row)

        grids[e_val] = grid

    # =====================
    # ищем группы ВНУТРИ слоев
    # =====================
    all_groups = []

    for e_val in [0, 1]:
        groups = find_all_valid_groups(
            grids[e_val],
            row_codes,
            col_codes,
            row_vars,
            col_vars,
            variables,
            target_value
        )
        all_groups.extend(groups)


    # =====================
    # ПОЛНАЯ СКЛЕЙКА МЕЖДУ СЛОЯМИ (3D группы)
    # =====================

    rows = len(row_codes)
    cols = len(col_codes)

    row_sizes = powers_of_two_up_to(rows)
    col_sizes = powers_of_two_up_to(cols)

    for h in row_sizes:
        for w in col_sizes:
            for r0 in range(rows):
                for c0 in range(cols):

                    cells = []
                    assignments = []
                    ok = True

                    for dr in range(h):
                        for dc in range(w):
                            rr = (r0 + dr) % rows
                            cc = (c0 + dc) % cols

                            cell0 = grids[0][rr][cc]
                            cell1 = grids[1][rr][cc]

                            if cell0["value"] != target_value or cell1["value"] != target_value:
                                ok = False
                                break

                            cells.append((rr, cc, 0))
                            cells.append((rr, cc, 1))

                            assignments.append(cell0["assignment"])
                            assignments.append(cell1["assignment"])

                        if not ok:
                            break

                    if not ok:
                        continue

                    pattern = assignments_to_pattern(assignments)
                    expr = pattern_to_expr(pattern, variables, target_value)

                    all_groups.append({
                        "cells": frozenset(cells),
                        "assignments": frozenset(assignments),
                        "pattern": pattern,
                        "expr": expr,
                        "size": len(cells)
                    })

    # дальше всё как обычно
    prime_groups = filter_prime_groups(all_groups)

    source_terms = [tuple(row[:-1]) for row in table if row[-1] == target_value]

    essential = find_essential_groups(prime_groups, source_terms)
    chosen = exact_cover_groups(prime_groups, source_terms, essential, target_value)

    lines = []
    lines.append("Карта Карно (5 переменных)")
    lines.append("")

    lines.append("Слой e=0:")
    lines.extend(render_kmap(grids[0], row_vars, col_vars, row_codes, col_codes))
    lines.append("")

    lines.append("Слой e=1:")
    lines.extend(render_kmap(grids[1], row_vars, col_vars, row_codes, col_codes))
    lines.append("")
    chosen = simplify_groups(chosen)
    for idx, group in enumerate(chosen, start=1):
        lines.append(f"Область {idx}:")
        
        # показать карту с выделением группы
        if isinstance(next(iter(group["cells"])), tuple) and len(next(iter(group["cells"]))) == 3:
            # 5 переменных (3D)
            cells_2d = {(r, c) for (r, c, _) in group["cells"]}
        else:
            cells_2d = group["cells"]

        lines.extend(render_group_map(
            grids[0],  # можно e=0, для простоты
            row_vars,
            col_vars,
            row_codes,
            col_codes,
            cells_2d
        ))

        lines.append("")
        lines.append(f"K{idx}: {group['expr']}")
        lines.append("")

    join_symbol = " ∨ " if target_value == 1 else " ∧ "

    
    exprs = [g["expr"] for g in chosen]
    result_expr = join_symbol.join(exprs)

    lines.append("")
    lines.append("Результат:")
    lines.append(result_expr)

    return "\n".join(lines)