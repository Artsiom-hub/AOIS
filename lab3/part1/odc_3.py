from itertools import product, combinations

VARIABLES = ("A", "B", "Cin")


def full_adder(a: int, b: int, cin: int) -> tuple[int, int]:

    total = a + b + cin
    s = total % 2
    cout = total // 2
    return s, cout


def parse_bit(value: str) -> int:
    value = value.strip()

    if value not in {"0", "1"}:
        raise ValueError("Ошибка: допустимы только значения 0 или 1.")

    return int(value)


def read_bit(name: str) -> int:
    while True:
        try:
            return parse_bit(input(f"Введите {name} (0/1): "))
        except ValueError as error:
            print(error)


def build_truth_table() -> list[dict[str, int]]:
    table = []

    for a, b, cin in product([0, 1], repeat=3):
        s, cout = full_adder(a, b, cin)

        table.append(
            {
                "A": a,
                "B": b,
                "Cin": cin,
                "S": s,
                "Cout": cout,
            }
        )

    return table


def row_to_index(row: dict[str, int]) -> int:
    bits = [row[var] for var in VARIABLES]
    return int("".join(map(str, bits)), 2)


def get_minterms(table: list[dict[str, int]], output_name: str) -> list[int]:
    return [row_to_index(row) for row in table if row[output_name] == 1]


def bits_by_index(index: int, variables_count: int) -> tuple[int, ...]:
    binary = f"{index:0{variables_count}b}"
    return tuple(int(bit) for bit in binary)


def canonical_term_by_index(index: int) -> str:
    bits = bits_by_index(index, len(VARIABLES))
    literals = []

    for variable, bit in zip(VARIABLES, bits):
        if bit == 1:
            literals.append(variable)
        else:
            literals.append(f"!{variable}")

    return "(" + " /\\ ".join(literals) + ")"


def build_sdnf(minterms: list[int]) -> str:
    if not minterms:
        return "0"

    return " \\/ ".join(canonical_term_by_index(index) for index in minterms)


def pattern_matches(pattern: str, bits: tuple[int, ...]) -> bool:
    for pattern_bit, real_bit in zip(pattern, bits):
        if pattern_bit == "-":
            continue

        if int(pattern_bit) != real_bit:
            return False

    return True


def pattern_to_term(pattern: str) -> str:
    literals = []

    for variable, bit in zip(VARIABLES, pattern):
        if bit == "-":
            continue

        if bit == "1":
            literals.append(variable)
        else:
            literals.append(f"!{variable}")

    if not literals:
        return "1"

    return "(" + " /\\ ".join(literals) + ")"


def minimize_sdnf(minterms: list[int], variables_count: int) -> tuple[list[str], str]:

    on_set = set(minterms)
    all_set = set(range(2 ** variables_count))

    if not on_set:
        return [], "0"

    if on_set == all_set:
        return ["-" * variables_count], "1"

    implicants = []

    for pattern_tuple in product("01-", repeat=variables_count):
        pattern = "".join(pattern_tuple)

        covered = {
            index
            for index in all_set
            if pattern_matches(pattern, bits_by_index(index, variables_count))
        }

        if covered and covered <= on_set:
            implicants.append((pattern, covered))

    best_combo = None
    best_score = None

    for amount in range(1, len(implicants) + 1):
        for combo in combinations(implicants, amount):
            covered = set()

            for _, covered_by_implicant in combo:
                covered |= covered_by_implicant

            if on_set <= covered:
                literals_count = sum(
                    bit != "-"
                    for pattern, _ in combo
                    for bit in pattern
                )

                patterns = tuple(sorted(pattern for pattern, _ in combo))
                score = (amount, literals_count, patterns)

                if best_score is None or score < best_score:
                    best_score = score
                    best_combo = combo

        if best_combo is not None:
            break

    patterns = sorted(pattern for pattern, _ in best_combo)
    expression = " \\/ ".join(pattern_to_term(pattern) for pattern in patterns)

    return patterns, expression


def print_truth_table(table: list[dict[str, int]]) -> None:
    print("\nТаблица истинности ОДС-3:")
    print("A B Cin | S Cout")
    print("-----------------")

    for row in table:
        print(
            f"{row['A']} {row['B']}  {row['Cin']}  | "
            f"{row['S']}   {row['Cout']}"
        )


def print_gate_synthesis(output_name: str, patterns: list[str]) -> None:
    print(f"\nСинтез схемы для функции {output_name}:")

    if not patterns:
        print(f"{output_name} = 0")
        print("Схема не требует логических элементов, выход всегда равен 0.")
        return

    if patterns == ["---"]:
        print(f"{output_name} = 1")
        print("Схема не требует логических элементов, выход всегда равен 1.")
        return

    inverted_variables = sorted(
        {
            variable
            for pattern in patterns
            for variable, bit in zip(VARIABLES, pattern)
            if bit == "0"
        }
    )

    if inverted_variables:
        print("Инверторы:")
        for variable in inverted_variables:
            print(f"  NOT_{variable}: !{variable}")
    else:
        print("Инверторы не требуются.")

    print("Элементы AND:")

    and_names = []

    for index, pattern in enumerate(patterns, start=1):
        and_name = f"T{index}_{output_name}"
        and_names.append(and_name)
        print(f"  {and_name} = {pattern_to_term(pattern)}")

    if len(and_names) == 1:
        print(f"Выход напрямую берётся с {and_names[0]}:")
        print(f"  {output_name} = {and_names[0]}")
    else:
        print("Элемент OR:")
        print(f"  {output_name} = " + " \\/ ".join(and_names))


def main() -> None:
    print("ОДС-3: одноразрядный двоичный сумматор на 3 входа")
    print("Входы: A, B, Cin")
    print("Выходы: S, Cout\n")

    a = read_bit("A")
    b = read_bit("B")
    cin = read_bit("Cin")

    s, cout = full_adder(a, b, cin)

    print("\nРезультат для введённых значений:")
    print(f"A = {a}")
    print(f"B = {b}")
    print(f"Cin = {cin}")
    print(f"S = {s}")
    print(f"Cout = {cout}")

    table = build_truth_table()
    print_truth_table(table)

    for output_name in ("S", "Cout"):
        minterms = get_minterms(table, output_name)
        sdnf = build_sdnf(minterms)
        minimized_patterns, minimized_expression = minimize_sdnf(
            minterms,
            len(VARIABLES)
        )

        print(f"\nФункция {output_name}:")
        print(f"Номера минтермов: {minterms}")
        print(f"СДНФ: {output_name} = {sdnf}")
        print(f"Минимизированная форма: {output_name} = {minimized_expression}")

        print_gate_synthesis(output_name, minimized_patterns)

    print("\nИтоговые функции ОДС-3:")
    print(
        "S = (!A /\\ !B /\\ Cin) \\/ "
        "(!A /\\ B /\\ !Cin) \\/ "
        "(A /\\ !B /\\ !Cin) \\/ "
        "(A /\\ B /\\ Cin)"
    )
    print("Cout = (B /\\ Cin) \\/ (A /\\ Cin) \\/ (A /\\ B)")


if __name__ == "__main__":
    main()