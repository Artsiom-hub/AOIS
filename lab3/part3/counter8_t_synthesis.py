from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from typing import Iterable

try:
    from sympy import SOPform, Symbol, true, false
    from sympy.logic.boolalg import And, Or, Not
except ImportError:
    sys.exit("Ошибка: установи sympy командой: pip install sympy")


@dataclass(frozen=True)
class TruthRow:
    state: int
    q: tuple[int, int, int]
    next_state: int
    q_next: tuple[int, int, int]
    t: tuple[int, int, int]


def int_to_bits(value: int, width: int = 3) -> tuple[int, ...]:
    return tuple((value >> i) & 1 for i in reversed(range(width)))


def bits_to_int(bits: Iterable[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def build_counter_truth_table() -> list[TruthRow]:


    rows: list[TruthRow] = []

    for state in range(8):
        q = int_to_bits(state, 3)
        next_state = (state + 1) % 8
        q_next = int_to_bits(next_state, 3)


        t = tuple(q_i ^ q_next_i for q_i, q_next_i in zip(q, q_next))

        rows.append(
            TruthRow(
                state=state,
                q=q,
                next_state=next_state,
                q_next=q_next,
                t=t,
            )
        )

    return rows


def full_sdnf(minterms: list[tuple[int, int, int]], var_names: list[str]) -> str:


    if not minterms:
        return "0"

    terms: list[str] = []

    for bits in minterms:
        literals: list[str] = []

        for bit, var in zip(bits, var_names):
            if bit == 1:
                literals.append(var)
            else:
                literals.append(f"!{var}")

        terms.append("(" + " /\\ ".join(literals) + ")")

    return " \\/ ".join(terms)


def format_expr(expr) -> str:


    if expr == true:
        return "1"

    if expr == false:
        return "0"

    if isinstance(expr, Symbol):
        return str(expr)

    if expr.func == Not:
        arg = expr.args[0]
        inner = format_expr(arg)

        if isinstance(arg, Symbol):
            return f"!{inner}"

        return f"!({inner})"

    if expr.func == And:
        parts = [format_expr(arg) for arg in expr.args]
        return "(" + " /\\ ".join(parts) + ")"

    if expr.func == Or:
        parts = [format_expr(arg) for arg in expr.args]
        return " \\/ ".join(parts)

    return str(expr)


def minimize_t_function(
    rows: list[TruthRow],
    t_index: int,
    variables,
) -> tuple[list[tuple[int, int, int]], object]:

    minterms = [row.q for row in rows if row.t[t_index] == 1]

    minimized = SOPform(
        variables,
        minterms,
    )

    return minterms, minimized


def print_truth_table(rows: list[TruthRow]) -> None:
    print("Таблица истинности / таблица переходов автомата")
    print()
    print("Сост. | Q2 Q1 Q0 | Q2+ Q1+ Q0+ | T2 T1 T0")
    print("------+----------+--------------+---------")

    for row in rows:
        q2, q1, q0 = row.q
        nq2, nq1, nq0 = row.q_next
        t2, t1, t0 = row.t

        print(
            f"{row.state:>5} | "
            f"{q2}  {q1}  {q0}  | "
            f"{nq2}   {nq1}   {nq0}   | "
            f"{t2}  {t1}  {t0}"
        )


def print_synthesis(rows: list[TruthRow], show_sdnf: bool = True) -> None:
    var_names = ["Q2", "Q1", "Q0"]
    variables = symbols = [Symbol(name) for name in var_names]

    t_names = ["T2", "T1", "T0"]

    print()
    print("Синтез и минимизация функций возбуждения T-триггеров")
    print()

    for index, t_name in enumerate(t_names):
        minterms, minimized = minimize_t_function(rows, index, variables)

        minterm_numbers = [bits_to_int(bits) for bits in minterms]

        print(f"{t_name}:")
        print(f"  Единичные наборы: {minterm_numbers}")

        if show_sdnf:
            print(f"  СДНФ: {full_sdnf(minterms, var_names)}")

        print(f"  Минимизированная функция: {t_name} = {format_expr(minimized)}")
        print()


def simulate_counter(cycles: int = 10) -> None:
    print("Проверка работы счётчика")
    print()

    state = 0

    for _ in range(cycles):
        current_bits = "".join(map(str, int_to_bits(state, 3)))
        next_state = (state + 1) % 8
        next_bits = "".join(map(str, int_to_bits(next_state, 3)))

        print(f"{current_bits} ({state}) -> {next_bits} ({next_state})")

        state = next_state


def save_csv(rows: list[TruthRow], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(
            [
                "state",
                "Q2",
                "Q1",
                "Q0",
                "next_state",
                "Q2+",
                "Q1+",
                "Q0+",
                "T2",
                "T1",
                "T0",
            ]
        )

        for row in rows:
            writer.writerow(
                [
                    row.state,
                    *row.q,
                    row.next_state,
                    *row.q_next,
                    *row.t,
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Синтез и минимизация двоичного счётчика на 8 состояний на T-триггерах."
    )

    parser.add_argument(
        "--no-sdnf",
        action="store_true",
        help="Не выводить полную СДНФ, а показать только минимизированные функции.",
    )

    parser.add_argument(
        "--simulate",
        type=int,
        default=10,
        help="Количество тактов для проверки работы счётчика.",
    )

    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Сохранить таблицу истинности в CSV-файл.",
    )

    args = parser.parse_args()

    rows = build_counter_truth_table()

    print_truth_table(rows)
    print_synthesis(rows, show_sdnf=not args.no_sdnf)
    simulate_counter(args.simulate)

    if args.csv:
        save_csv(rows, args.csv)
        print()
        print(f"Таблица сохранена в файл: {args.csv}")


if __name__ == "__main__":
    main()