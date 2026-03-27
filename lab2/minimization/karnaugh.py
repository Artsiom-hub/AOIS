from itertools import combinations, product


def minimize_karnaugh(table, variables):
    var_count = len(variables)

    if var_count == 0:
        return "Табличный метод\n\nНет переменных"

    if var_count > 4:
        return (
            "Табличный метод (карта Карно)\n\n"
            "В данной реализации карта Карно поддерживается только для 2–4 переменных.\n"
            "Для 5 переменных используй расчетный или расчетно-табличный метод."
        )

    minterms = [tuple(row[:-1]) for row in table if row[-1] == 1]

    if not minterms:
        return "Табличный метод\n\nФункция тождественно равна 0"

    if len(minterms) == len(table):
        return "Табличный метод\n\nФункция тождественно равна 1"

    row_vars, col_vars = split_variables(variables)
    row_codes = gray_codes(len(row_vars))
    col_codes = gray_codes(len(col_vars))

    grid = build_kmap_grid(table, variables, row_vars, col_vars, row_codes, col_codes)

    all_groups = find_all_valid_groups(grid, row_codes, col_codes, row_vars, col_vars, variables)
    prime_groups = filter_prime_groups(all_groups)

    essential = find_essential_groups(prime_groups, minterms)
    chosen = exact_cover_groups(prime_groups, minterms, essential)

    lines = []
    lines.append("Табличный метод")
    lines.append("")
    lines.append("Карта Карно:")
    lines.extend(render_kmap(grid, row_vars, col_vars, row_codes, col_codes))
    lines.append("")
    lines.append(
        "Выделим на карте Карно прямоугольные области из единиц наибольшей площади, "
        "являющиеся степенями двойки, и выпишем соответствующие им конъюнкции."
    )
    lines.append("")

    for idx, group in enumerate(chosen, start=1):
        lines.append(f"Область {idx}:")
        lines.extend(render_group_map(grid, row_vars, col_vars, row_codes, col_codes, group["cells"]))
        lines.append("")
        lines.append(f"K{idx}: {group['expr']}")
        lines.append("")

    result_expr = " v ".join(group["expr"] for group in chosen)
    lines.append("Объединим их с помощью операции ИЛИ и получим минимизированную ДНФ:")
    lines.append(result_expr)

    return "\n".join(lines)


# =========================================================
# РАЗБИЕНИЕ ПЕРЕМЕННЫХ ПО ОСЯМ
# =========================================================

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

    raise ValueError("Карта Карно поддерживается только для 1–4 переменных")


def gray_codes(bits):
    if bits == 0:
        return [()]
    if bits == 1:
        return [(0,), (1,)]
    if bits == 2:
        return [(0, 0), (0, 1), (1, 1), (1, 0)]

    # На случай расширения
    codes = [tuple(int(x) for x in format(i ^ (i >> 1), f"0{bits}b")) for i in range(2 ** bits)]
    return codes


# =========================================================
# ПОСТРОЕНИЕ СЕТКИ КАРНО
# =========================================================

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


# =========================================================
# ПОИСК ГРУПП
# =========================================================

def powers_of_two_up_to(n):
    result = []
    x = 1
    while x <= n:
        result.append(x)
        x *= 2
    return result


def find_all_valid_groups(grid, row_codes, col_codes, row_vars, col_vars, variables):
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

                            if cell["value"] != 1:
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
                    expr = pattern_to_expr(pattern, variables)

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
    """
    Оставляем только такие группы, которые не являются подмножеством большей группы.
    """
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

    # убираем дубли по pattern+covers
    unique = {}
    for g in prime:
        key = (g["pattern"], g["assignments"])
        if key not in unique:
            unique[key] = g

    return list(unique.values())


# =========================================================
# ПОКРЫТИЕ
# =========================================================

def find_essential_groups(groups, minterms):
    essential = []

    for m in minterms:
        covering = [g for g in groups if m in g["assignments"]]
        if len(covering) == 1 and covering[0] not in essential:
            essential.append(covering[0])

    return essential


def exact_cover_groups(groups, minterms, essential):
    essential_set = list(essential)

    covered = set()
    for g in essential_set:
        covered |= set(g["assignments"])

    uncovered = [m for m in minterms if m not in covered]

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
                    len(full),                                # меньше групп
                    -sum(g["size"] for g in full),            # больше площадь групп
                    sum(count_literals(g["pattern"]) for g in full),  # меньше литералов
                    [g["expr"] for g in sort_groups(full)]
                )

                if best_key is None or key < best_key:
                    best_key = key
                    best_solution = full

        if best_solution is not None:
            break

    return sort_groups(best_solution if best_solution is not None else essential_set)


# =========================================================
# ВЫВОД КАРТЫ
# =========================================================

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
            if (r, c) in group_cells and grid[r][c]["value"] == 1:
                v = f"[{v}]"
            vals.append(center_text(v, col_width))
        line += " | ".join(vals)
        line += " |"
        lines.append(line)

    lines.append("-" * total_width)
    return lines


# =========================================================
# ВСПОМОГАТЕЛЬНОЕ
# =========================================================

def pattern_to_expr(pattern, variables):
    parts = []

    for val, var in zip(pattern, variables):
        if val is None:
            continue
        if val == 1:
            parts.append(var)
        else:
            parts.append(f"¬{var}")

    if not parts:
        return "1"

    return "".join(parts)


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