BITS = 32
MIN_INT = -(1 << (BITS - 1))
MAX_INT = (1 << (BITS - 1)) - 1

#1
def validate_range(n: int) -> None:
    if n < MIN_INT or n > MAX_INT:
        raise ValueError(f"Число вне диапазона 32-bit signed: [{MIN_INT}, {MAX_INT}]")


def zeros(bits: int = BITS) -> list[int]:
    return [0] * bits


def copy_bits(bits: list[int]) -> list[int]:
    return [b for b in bits]


def bits_to_str(bits: list[int]) -> str:

    s = ""
    for b in bits:
        s += "1" if b == 1 else "0"
    return s


def abs_int(n: int) -> int:
    return -n if n < 0 else n


def set_magnitude_bits(value: int) -> list[int]:

    bits = zeros(BITS)
    x = value


    i = BITS - 1
    while i >= 1:
        bits[i] = x % 2
        x //= 2
        i -= 1


    return bits


def invert_bits(bits: list[int], start: int = 0) -> list[int]:
    out = copy_bits(bits)
    i = start
    while i < len(out):
        out[i] = 0 if out[i] == 1 else 1
        i += 1
    return out


def add_one(bits: list[int]) -> list[int]:

    out = copy_bits(bits)
    carry = 1
    i = len(out) - 1
    while i >= 0 and carry == 1:
        if out[i] == 0:
            out[i] = 1
            carry = 0
        else:
            out[i] = 0
            carry = 1
        i -= 1
    return out


def to_direct_code(n: int) -> list[int]:

    validate_range(n)

    sign = 1 if n < 0 else 0
    mag = abs_int(n)

    bits = set_magnitude_bits(mag)
    bits[0] = sign
    return bits


def to_inverse_code(n: int) -> list[int]:

    validate_range(n)

    direct = to_direct_code(n)
    if n >= 0:
        return direct

    out = copy_bits(direct)
    out[0] = 1

    i = 1
    while i < BITS:
        out[i] = 0 if out[i] == 1 else 1
        i += 1
    return out


def to_additional_code(n: int) -> list[int]:

    validate_range(n)

    if n >= 0:
        return to_direct_code(n)

    inv = to_inverse_code(n)
    return add_one(inv)

def add_two_in_twos_complement(a: int, b: int) -> list[int]:

    a_bits = to_additional_code(a)
    b_bits = to_additional_code(b)


    result = zeros()
    carry = 0
    for i in range(BITS - 1, -1, -1):
        s = a_bits[i] + b_bits[i] + carry
        result[i] = s % 2
        carry = s // 2


    return result

def from_additional_code(bits: list[int]) -> int:

    if bits[0] == 0:
        val = 0
        for bit in bits[1:]:
            val = val * 2 + bit
        return val


    inv = invert_bits(bits, start=1)
    mag_bits = add_one([1] + inv[1:]) 
    val = 0
    for bit in mag_bits[1:]:
        val = val * 2 + bit
    return -val
    
def show_all(n: int) -> None:
    d = to_direct_code(n)
    r = to_inverse_code(n)
    a = to_additional_code(n)

    print(f"n = {n}")
    print(f"Прямой:        {bits_to_str(d)}  (array={d})")
    print(f"Обратный:      {bits_to_str(r)}  (array={r})")
    print(f"Дополнительный:{bits_to_str(a)}  (array={a})")



def bits_to_int(bits: list[int]) -> int:
    value = 0
    for b in bits:
        value = value * 2 + b
    return value


def direct_code_to_decimal(bits: list[int]) -> int:
    if len(bits) != BITS:
        raise ValueError(f"Ожидалось {BITS} бит")

    sign = bits[0]
    magnitude_bits = bits[1:]

    magnitude = bits_to_int(magnitude_bits)

    if sign == 1:
        return -magnitude
    else:
        return magnitude


def run_show_codes() -> None:

    while True:
        s = input("Введите целое число (32-bit signed): ").strip()
        if s == "":
            print("Пустой ввод.")
            continue

        try:
            n = int(s)
        except ValueError:
            print("Ошибка: введите корректное целое число.")
            continue

        try:
            show_all(n)
        except ValueError as e:
            print(f"Ошибка: {e}")
        break


def run_addition() -> None:

    try:
        x = int(input("\nВведите первое целое: ").strip())
        y = int(input("Введите второе целое: ").strip())
    except ValueError:
        print("Ошибка: введено не целое число.")
        return

    sum_bits = add_two_in_twos_complement(x, y)

    print("\nРезультаты:")
    print(f"{x} в дополнительном коде:   {bits_to_str(to_additional_code(x))}")
    print(f"{y} в дополнительном коде:   {bits_to_str(to_additional_code(y))}")

    print("\nСумма в дополнительном коде:")
    print(bits_to_str(sum_bits))
    print("В десятичном формате:", from_additional_code(sum_bits))


#3
def subtract_in_twos_complement(a: int, b: int) -> list[int]:

    a_bits = to_additional_code(a)
    b_bits = to_additional_code(b)


    inverted_b = invert_bits(b_bits)


    neg_b_bits = add_one(inverted_b)

    result = zeros()
    carry = 0
    for i in range(BITS - 1, -1, -1):
        s = a_bits[i] + neg_b_bits[i] + carry
        result[i] = s % 2
        carry = s // 2

    return result

def run_substraction() -> None:
    x = int(input("Введите A: "))
    y = int(input("Введите B: "))

    res_bits = subtract_in_twos_complement(x, y)

    print(f"\nA (доп. код):        {bits_to_str(to_additional_code(x))}")
    print(f"B (доп. код):        {bits_to_str(to_additional_code(y))}")
    print(f"Результат (A - B):   {bits_to_str(res_bits)}")
    print("В десятичном формате:", from_additional_code(res_bits))


def multiply_in_direct_code(a: int, b: int) -> list[int]:

    sign_res = 1 if (a < 0) ^ (b < 0) else 0


    abs_a = abs(a)
    abs_b = abs(b)


    def to_bits31(x):
        bits = [0] * 31
        tmp = x
        i = 30
        while tmp > 0 and i >= 0:
            bits[i] = tmp % 2
            tmp //= 2
            i -= 1
        return bits

    mag_a = to_bits31(abs_a)
    mag_b = to_bits31(abs_b)


    temp = [0] * 62

    for i in range(31):

        if mag_b[30 - i] == 1:
            carry = 0
            for j in range(31):
               
                pos = (len(temp) - 1) - (i + j)
                s = temp[pos] + mag_a[30 - j] + carry
                temp[pos] = s % 2
                carry = s // 2
        
            pos -= 1
            while carry and pos >= 0:
                s = temp[pos] + carry
                temp[pos] = s % 2
                carry = s // 2
                pos -= 1


    prod_mag = temp[-31:]


    return [sign_res] + prod_mag
def main_mul():
    a = int(input("Введите A: "))
    b = int(input("Введите B: "))

    res_bits = multiply_in_direct_code(a, b)
    print(f"\nA  (direct): {bits_to_str(to_direct_code(a))}")
    print(f"B  (direct): {bits_to_str(to_direct_code(b))}")
    print("Результат умножения (direct):", bits_to_str(res_bits))
    print("В десятичном формате:", direct_code_to_decimal(res_bits))


#5
def divide_in_direct_code(a: int, b: int):

    if b == 0:
        raise ZeroDivisionError("Деление на ноль невозможно")

    # переводим числа в прямой код
    a_bits = to_direct_code(a)
    b_bits = to_direct_code(b)

    # знак результата
    sign_res = a_bits[0] ^ b_bits[0]

    # модули чисел (31 бит)
    dividend = a_bits[1:]
    divisor = b_bits[1:]

    quotient = [0] * 31
    remainder = [0] * 31

    for i in range(31):

        # сдвиг остатка
        remainder = remainder[1:] + [dividend[i]]

        # проверяем remainder >= divisor
        if bits_to_int(remainder) >= bits_to_int(divisor):

            # remainder = remainder - divisor
            r = bits_to_int(remainder) - bits_to_int(divisor)

            remainder = set_magnitude_bits(r)[1:]
            quotient[i] = 1

    # формируем прямой код результата
    result = [sign_res] + quotient

    return result


def show_division():
    a = int(input("Введите делимое A: "))
    b = int(input("Введите делитель B: "))

    try:
        bits = divide_in_direct_code(a, b)
    except ZeroDivisionError as e:
        print("Ошибка:", e)
        return

    # перевод результата обратно в десятичное число
    quotient = direct_code_to_decimal(bits)

    print(f"\nA = {a}, B = {b}")
    print("Частное (десятичное):", quotient)
    print("Частное (прямой код):", bits_to_str(bits))


def main() -> None:
    print("Выберите действие:")
    print("1 — Просмотреть коды для одного числа")
    print("2 — Сложить два числа (дополнительный код)")
    print("3 — Реализовать операцию вычитания")
    print("4 — Реализовать операцию умножения (прямой код)")
    print("5 — Реализовать операцию деления (прямой код)")
    choice = input("Ваш выбор (1,2,3,4,5): ").strip()
    if choice == "1":
        run_show_codes()
    elif choice == "2":
        run_addition()
    elif choice == "3":
        run_substraction()
    elif choice == "4":
        main_mul()
    elif choice == "5":
        show_division()
    else:
        print("Неверный выбор — должно быть 1, 2, 3, 4 или 5")



if __name__ == "__main__":
    main()