from core.parser import tokenize, to_rpn
from core.truth_table import build_truth_table, print_truth_table
from algebra.normal_forms import (
    build_sdnf,
    build_sknf,
    build_sdnf_numeric,
    build_sknf_numeric,
    format_sdnf_numeric,
    format_sknf_numeric,
)
from algebra.normal_forms import build_index_form, format_index_form
from algebra.zhegalkin import zhegalkin_polynomial
from algebra.post_classes import check_post_classes
from algebra.derivatives import compute_derivatives
from algebra.dummy_vars import find_dummy_variables
from minimization.quine_mccluskey import minimize_qm
from minimization.tabular import minimize_tabular
from minimization.karnaugh import minimize_karnaugh


def run_cli():
    print("Введите логическую функцию:")
    expr = input("> ")



    # 2. Таблица истинности
    table, variables = build_truth_table(expr)

    print("\nТаблица истинности:")
    print_truth_table(table, variables)

    # 3. СДНФ / СКНФ
    sdnf = build_sdnf(table, variables)
    sknf = build_sknf(table, variables)

    print("\nСДНФ:", sdnf)
    print("СКНФ:", sknf)

    # 4. Числовые формы
    sdnf_nums = build_sdnf_numeric(table)
    sknf_nums = build_sknf_numeric(table)

    print("\nЧисловая форма СДНФ:")
    print(format_sdnf_numeric(sdnf_nums))

    print("\nЧисловая форма СКНФ:")
    print(format_sknf_numeric(sknf_nums))

    # 5. Индексная форма
    vector, index = build_index_form(table)

    print("\nИндексная форма функции:")
    print(format_index_form(vector, index))

    # 6. Классы Поста
    post = check_post_classes(table)
    print("\nКлассы Поста:")
    for k, v in post.items():
        print(f"{k}: {'Да' if v else 'Нет'}")

    # 7. Полином Жегалкина
    zheg = zhegalkin_polynomial(table)
    print("\nПолином Жегалкина:", zheg)

    # 8. Фиктивные переменные
    dummy = find_dummy_variables(table, variables)
    print("\nФиктивные переменные:", dummy)

    # 9. Производные
    derivatives = compute_derivatives(expr, variables)
    print("\nПроизводные:")

    for name, values in derivatives.items():
        print(f"{name}: {''.join(map(str, values))}")

    # 10. Минимизация
    print("\nМинимизация (Квайн-МакКласки):")
    print(minimize_qm(table, variables))

    print("\nМинимизация (табличный):")
    print(minimize_tabular(table, variables))

    print("\nМинимизация (Карно):")
    print(minimize_karnaugh(table, variables))