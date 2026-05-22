from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

try:
    from sympy import SOPform, symbols
except ImportError as exc:
    raise SystemExit(
        "Для минимизации нужен пакет sympy. Установи его командой: pip install sympy"
    ) from exc

OFFSET = 6
BIT_MASK_4 = 0b1111

INPUT_NAMES = ["A3", "A2", "A1", "A0", "B3", "B2", "B1", "B0"]
OUTPUT_NAMES = [
    "Cout",
    "S1_3", "S1_2", "S1_1", "S1_0",
    "S0_3", "S0_2", "S0_1", "S0_0",
]


@dataclass(frozen=True)
class Result:
    a_code: int
    b_code: int
    a_digit: int
    b_digit: int
    total: int
    first_sum: int
    c: int
    p: int
    p3: int
    p2: int
    p1: int
    p0: int
    cout: int
    k: int
    s1_code: int
    s0_code: int
    s1_digit: int
    s0_digit: int

    @property
    def output_bits(self) -> dict[str, int]:
        return {
            "Cout": self.cout,
            "S1_3": (self.s1_code >> 3) & 1,
            "S1_2": (self.s1_code >> 2) & 1,
            "S1_1": (self.s1_code >> 1) & 1,
            "S1_0": self.s1_code & 1,
            "S0_3": (self.s0_code >> 3) & 1,
            "S0_2": (self.s0_code >> 2) & 1,
            "S0_1": (self.s0_code >> 1) & 1,
            "S0_0": self.s0_code & 1,
        }


def to_bin4(value: int) -> str:
    return format(value & BIT_MASK_4, "04b")


def to_bin8(value: int) -> str:
    return format(value & 0xFF, "08b")


def digit_to_shift6_code(digit: int) -> int:
    if not 0 <= digit <= 9:
        raise ValueError("Десятичная цифра должна быть в диапазоне 0..9.")
    return digit + OFFSET


def is_valid_shift6_code(code: int) -> bool:
    return 0 <= code - OFFSET <= 9


def read_shift6_code(name: str) -> int:
    while True:
        raw = input(f"Введите {name}[3:0] в двоичном виде: ").strip()

        if len(raw) != 4 or any(ch not in "01" for ch in raw):
            print("Ошибка: нужно ввести ровно 4 бита, например 1010.")
            continue

        code = int(raw, 2)
        digit = code - OFFSET

        if not 0 <= digit <= 9:
            print(
                f"Ошибка: код {raw} недопустим для кода со смещением 6. "
                f"Допустимые коды: 0110..1111."
            )
            continue

        return code


def calculate(a_code: int, b_code: int) -> Result:
    if not is_valid_shift6_code(a_code):
        raise ValueError(f"Недопустимый код A: {to_bin4(a_code)}")
    if not is_valid_shift6_code(b_code):
        raise ValueError(f"Недопустимый код B: {to_bin4(b_code)}")

    a_digit = a_code - OFFSET
    b_digit = b_code - OFFSET
    total = a_digit + b_digit

    # Первый двоичный сумматор: складываем сами входные коды.
    first_sum = a_code + b_code
    p = first_sum & BIT_MASK_4
    c = 1 if first_sum > BIT_MASK_4 else 0

    p3 = (p >> 3) & 1
    p2 = (p >> 2) & 1
    p1 = (p >> 1) & 1
    p0 = p & 1

    # Минимизированная функция десятичного переноса.
    cout = c & (p3 | (p2 & p1))

    # Коррекция младшей тетрады:
    # если Cout = 0, прибавляем 1010;
    # если Cout = 1, прибавляем 0000.
    k = 0b1010 if cout == 0 else 0b0000
    second_sum = p + k
    s0_code = second_sum & BIT_MASK_4

    # Старшая тетрада результата: 0 -> 0110, 1 -> 0111.
    s1_code = 0b0110 | cout

    s0_digit = s0_code - OFFSET
    s1_digit = s1_code - OFFSET

    return Result(
        a_code=a_code,
        b_code=b_code,
        a_digit=a_digit,
        b_digit=b_digit,
        total=total,
        first_sum=first_sum,
        c=c,
        p=p,
        p3=p3,
        p2=p2,
        p1=p1,
        p0=p0,
        cout=cout,
        k=k,
        s1_code=s1_code,
        s0_code=s0_code,
        s1_digit=s1_digit,
        s0_digit=s0_digit,
    )


def minterm_index(a_code: int, b_code: int) -> int:
    return (a_code << 4) | b_code


def minterm_to_conjunction(minterm: int) -> str:
    bits = to_bin8(minterm)
    literals: list[str] = []

    for variable, bit in zip(INPUT_NAMES, bits):
        literals.append(variable if bit == "1" else f"!{variable}")

    return "(" + " /\\ ".join(literals) + ")"


def build_sdnf_expression(minterms: list[int]) -> str:
    if not minterms:
        return "0"

    terms = [minterm_to_conjunction(minterm) for minterm in sorted(minterms)]
    return " \\/\n    ".join(terms)


def expression_to_text(expression) -> str:
    text = str(expression)
    text = text.replace("True", "1")
    text = text.replace("False", "0")
    text = text.replace("~", "!")
    text = text.replace("&", "/\\")
    text = text.replace("|", "\\/")
    return text


def build_truth_data() -> tuple[list[Result], dict[str, list[int]], list[int]]:
    rows: list[Result] = []
    ones: dict[str, list[int]] = {name: [] for name in OUTPUT_NAMES}
    dont_cares: list[int] = []

    for a_code in range(16):
        for b_code in range(16):
            minterm = minterm_index(a_code, b_code)

            if not is_valid_shift6_code(a_code) or not is_valid_shift6_code(b_code):
                dont_cares.append(minterm)
                continue

            result = calculate(a_code, b_code)
            rows.append(result)

            for output_name, output_value in result.output_bits.items():
                if output_value == 1:
                    ones[output_name].append(minterm)

    return rows, ones, dont_cares


def validate_structural_model(rows: list[Result]) -> None:
    for row in rows:
        expected_tens = row.total // 10
        expected_units = row.total % 10
        expected_s1 = digit_to_shift6_code(expected_tens)
        expected_s0 = digit_to_shift6_code(expected_units)
        expected_cout = 1 if row.total >= 10 else 0

        if row.s1_code != expected_s1 or row.s0_code != expected_s0 or row.cout != expected_cout:
            raise AssertionError(
                "Ошибка внутренней проверки: "
                f"A={to_bin4(row.a_code)}, B={to_bin4(row.b_code)}, "
                f"получено S1={to_bin4(row.s1_code)}, S0={to_bin4(row.s0_code)}, "
                f"ожидалось S1={to_bin4(expected_s1)}, S0={to_bin4(expected_s0)}"
            )


def make_code_table_text() -> str:
    lines = [
        "Кодировка десятичных цифр в коде Д8421+6:",
        "digit | code",
        "------+------",
    ]

    for digit in range(10):
        lines.append(f"  {digit:<3} | {to_bin4(digit_to_shift6_code(digit))}")

    return "\n".join(lines)


def make_result_text(result: Result) -> str:
    lines = [
        "",
        "Расшифровка входов:",
        f"A[3:0] = {to_bin4(result.a_code)} => A = {result.a_digit}",
        f"B[3:0] = {to_bin4(result.b_code)} => B = {result.b_digit}",
        "",
        "Промежуточные сигналы структурной схемы:",
        f"A + B = {to_bin4(result.a_code)} + {to_bin4(result.b_code)}",
        f"Первый сумматор: C = {result.c}, P[3:0] = {to_bin4(result.p)}",
        f"P3 = {result.p3}, P2 = {result.p2}, P1 = {result.p1}, P0 = {result.p0}",
        f"Cout = C /\\ (P3 \\/ (P2 /\\ P1)) = {result.cout}",
        f"K[3:0] = {to_bin4(result.k)}",
        "",
        "Выходы схемы:",
        f"S1[3:0] = {to_bin4(result.s1_code)} => старший разряд = {result.s1_digit}",
        f"S0[3:0] = {to_bin4(result.s0_code)} => младший разряд = {result.s0_digit}",
        f"Cout = {result.cout}",
        "",
        "Проверка в десятичном виде:",
        f"{result.a_digit} + {result.b_digit} = {result.total}",
        f"Результат схемы: {result.s1_digit}{result.s0_digit}",
        (
            "Результат корректен."
            if result.total == result.s1_digit * 10 + result.s0_digit
            else "Ошибка: результат схемы не совпал с десятичной проверкой."
        ),
    ]
    return "\n".join(lines)


def make_truth_table_text(rows: list[Result]) -> str:
    lines = [
        "",
        "Таблица истинности для допустимых входных комбинаций:",
        "Acode A | Bcode B | Sum | Cout | S1[3:0] | S0[3:0] | Result",
        "--------+---------+-----+------+---------+---------+-------",
    ]

    for row in rows:
        lines.append(
            f"{to_bin4(row.a_code)} {row.a_digit:>2} | "
            f"{to_bin4(row.b_code)} {row.b_digit:>2} | "
            f"{row.total:>3} | "
            f"  {row.cout}   | "
            f" {to_bin4(row.s1_code)}   | "
            f" {to_bin4(row.s0_code)}   | "
            f"{row.s1_digit}{row.s0_digit}"
        )

    return "\n".join(lines)


def make_minimization_text(
    ones: dict[str, list[int]],
    dont_cares: list[int],
    *,
    include_sdnf: bool,
) -> str:
    variables = symbols(" ".join(INPUT_NAMES))
    lines = [
        "",
        "Синтез и минимизация комбинационной схемы",
        "Входы: A3 A2 A1 A0 B3 B2 B1 B0",
        "Выходы: Cout, S1_3 S1_2 S1_1 S1_0, S0_3 S0_2 S0_1 S0_0",
        "S1 — старшая тетрада результата, S0 — младшая тетрада результата.",
        "Недопустимые входные тетрады используются как don't care.",
        "Обозначения: ! — НЕ, /\\ — И, \\/ — ИЛИ.",
        f"Количество допустимых наборов: 100",
        f"Количество don't care наборов: {len(dont_cares)}",
    ]

    for output_name in OUTPUT_NAMES:
        minterms = sorted(ones[output_name])
        minimized = SOPform(variables, minterms, dont_cares)

        lines.append("")
        lines.append(f"{output_name}:")
        lines.append(f"  Количество единичных наборов: {len(minterms)}")

        if include_sdnf:
            lines.append("  СДНФ:")
            lines.append(f"    {build_sdnf_expression(minterms)}")
        else:
            minterms_text = ", ".join(map(str, minterms)) if minterms else ""
            lines.append(f"  СДНФ в компактной форме: Σm({minterms_text})")

        lines.append(f"  Минимизированная ДНФ: {expression_to_text(minimized)}")

    return "\n".join(lines)


def make_structural_minimization_text() -> str:
    return "\n".join(
        [
            "",
            "Компактная структурная реализация после анализа минимизированных функций:",
            "1) Первый двоичный сумматор: A[3:0] + B[3:0] = C P3 P2 P1 P0.",
            "2) Десятичный перенос: Cout = C /\\ (P3 \\/ (P2 /\\ P1)).",
            "3) Старшая тетрада результата: S1 = 011Cout.",
            "   То есть S1_3 = 0, S1_2 = 1, S1_1 = 1, S1_0 = Cout.",
            "4) Корректирующая константа для младшей тетрады:",
            "   K3 = !Cout, K2 = 0, K1 = !Cout, K0 = 0.",
            "   Если Cout = 0, K = 1010; если Cout = 1, K = 0000.",
            "5) Второй двоичный сумматор: S0[3:0] = P[3:0] + K[3:0].",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Сумматор двух одноразрядных чисел в коде Д8421+6 с синтезом и минимизацией."
    )
    parser.add_argument(
        "--no-table",
        action="store_true",
        help="не выводить таблицу истинности",
    )
    parser.add_argument(
        "--compact-sdnf",
        action="store_true",
        help="выводить СДНФ как Σm(...), а не полной дизъюнкцией конъюнкций",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="сохранить полный вывод в указанный txt-файл",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Одноразрядный сумматор десятично-двоичного кода со смещением 6")
    print(make_code_table_text())
    print()

    a_code = read_shift6_code("A")
    b_code = read_shift6_code("B")

    result = calculate(a_code, b_code)
    rows, ones, dont_cares = build_truth_data()
    validate_structural_model(rows)

    sections = [
        make_result_text(result),
    ]

    if not args.no_table:
        sections.append(make_truth_table_text(rows))

    sections.append(
        make_minimization_text(
            ones,
            dont_cares,
            include_sdnf=not args.compact_sdnf,
        )
    )
    sections.append(make_structural_minimization_text())

    output_text = "\n".join(sections)
    print(output_text)

    if args.report:
        args.report.write_text(output_text, encoding="utf-8")
        print()
        print(f"Отчёт сохранён в файл: {args.report}")


if __name__ == "__main__":
    main()
