def find_dummy_variables(table, variables):
    """
    Возвращает список фиктивных переменных
    """

    dummy_vars = []
    var_count = len(variables)

    for var_index in range(var_count):
        is_dummy = True

        for i in range(len(table)):
            for j in range(len(table)):
                row_i = table[i]
                row_j = table[j]

                # проверяем: отличаются только по одной переменной
                differs_only_in_var = True

                for k in range(var_count):
                    if k == var_index:
                        # должна отличаться
                        if row_i[k] == row_j[k]:
                            differs_only_in_var = False
                            break
                    else:
                        # остальные должны совпадать
                        if row_i[k] != row_j[k]:
                            differs_only_in_var = False
                            break

                if differs_only_in_var:
                    # если нашли разницу в F → переменная не фиктивная
                    if row_i[-1] != row_j[-1]:
                        is_dummy = False
                        break

            if not is_dummy:
                break

        if is_dummy:
            dummy_vars.append(variables[var_index])

    return dummy_vars