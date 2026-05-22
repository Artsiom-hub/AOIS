OFFSET = 6
BIT_MASK_4 = 0b1111


def to_bin4(value: int) -> str:
    return format(value & BIT_MASK_4, "04b")


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


def main() -> None:
    print("Одноразрядный сумматор десятично-двоичного кода со смещением 6")
    print("Допустимые коды:")
    print("0=0110, 1=0111, 2=1000, 3=1001, 4=1010")
    print("5=1011, 6=1100, 7=1101, 8=1110, 9=1111")
    print()

    a_code = read_shift6_code("A")
    b_code = read_shift6_code("B")

    a_digit = a_code - OFFSET
    b_digit = b_code - OFFSET


    first_sum = a_code + b_code
    p = first_sum & BIT_MASK_4
    c = 1 if first_sum > BIT_MASK_4 else 0

    p3 = (p >> 3) & 1
    p2 = (p >> 2) & 1
    p1 = (p >> 1) & 1
    p0 = p & 1


    t = c & (p3 | (p2 & p1))


    k = 0b1010 if t == 0 else 0b0000

 
    second_sum = p + k
    s0_code = second_sum & BIT_MASK_4


    s1_code = 0b0110 | t

    s0_digit = s0_code - OFFSET
    s1_digit = s1_code - OFFSET

    total = a_digit + b_digit

    print()
    print("Расшифровка входов:")
    print(f"A[3:0] = {to_bin4(a_code)} => A = {a_digit}")
    print(f"B[3:0] = {to_bin4(b_code)} => B = {b_digit}")

    print()
    print("Промежуточные сигналы схемы:")
    print(f"A + B = {to_bin4(a_code)} + {to_bin4(b_code)}")
    print(f"Первый сумматор: C = {c}, P[3:0] = {to_bin4(p)}")
    print(f"P3 = {p3}, P2 = {p2}, P1 = {p1}, P0 = {p0}")
    print(f"T = C AND (P3 OR (P2 AND P1)) = {t}")
    print(f"K[3:0] = {to_bin4(k)}")

    print()
    print("Выходы схемы:")
    print(f"S1[3:0] = {to_bin4(s1_code)} => старший разряд = {s1_digit}")
    print(f"S0[3:0] = {to_bin4(s0_code)} => младший разряд = {s0_digit}")
    print(f"Cout = {t}")

    print()
    print("Проверка в десятичном виде:")
    print(f"{a_digit} + {b_digit} = {total}")
    print(f"Результат схемы: {s1_digit}{s0_digit}")

    if total == s1_digit * 10 + s0_digit:
        print("Результат корректен.")
    else:
        print("Ошибка: результат схемы не совпал с десятичной проверкой.")


if __name__ == "__main__":
    main()