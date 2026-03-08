
dec_to_5421 = {
    0: [0,0,0,0],
    1: [0,0,0,1],
    2: [0,0,1,0],
    3: [0,0,1,1],
    4: [0,1,0,0],
    5: [1,0,0,0],
    6: [1,0,0,1],
    7: [1,0,1,0],
    8: [1,1,0,0],
    9: [1,1,0,1],
}
_5421_to_dec = {tuple(v): k for k,v in dec_to_5421.items()}

def to_4bit(val):
    return [(val >> 3) & 1, (val >> 2) & 1, (val >> 1) & 1, val & 1]

def bcd5421_add_digit(a_nibble, b_nibble, carry_in):

    total = 0
    for bit in a_nibble:
        total = (total << 1) | bit
    for bit in b_nibble:
        total = (total << 1) | bit
    total += carry_in
    

    if total <= 9:
        bits = to_4bit(total)
        if tuple(bits) in _5421_to_dec:
            return bits, 0
    

    corrected = total + 3
    carry_out = corrected // 10
    digit_val = corrected % 10
    return dec_to_5421[digit_val], carry_out

def add_5421_bcd(a_dec: str, b_dec: str):

    max_len = max(len(a_dec), len(b_dec))
    a_dec = a_dec.zfill(max_len)
    b_dec = b_dec.zfill(max_len)

    carry = 0
    result_nibbles = []
    for da, db in zip(a_dec[::-1], b_dec[::-1]):
        an = dec_to_5421[int(da)]
        bn = dec_to_5421[int(db)]
        res_nib, carry = bcd5421_add_digit(an, bn, carry)
        result_nibbles.insert(0, res_nib)

    if carry:

        for d in str(carry):
            result_nibbles.insert(0, dec_to_5421[int(d)])


    bcd_str = " ".join("".join(str(bit) for bit in nib) for nib in result_nibbles)

    dec_str = str(int(a_dec) + int(b_dec))
    return dec_str, bcd_str



def show_menu():
    print("\n=== Сложение в BCD 5-4-2-1 ===")
    print("Введите два положительных целых числа.")
    print("Результат будет показан в обычном и BCD-формате.")
    print("0 — выход")

def main():
    while True:
        show_menu()
        a = input("Введите число A: ").strip()
        if a == "0":
            print("Выход.")
            break
        b = input("Введите число B: ").strip()
        if b == "0":
            print("Выход.")
            break


        if not a.isdigit() or not b.isdigit():
            print("Ошибка: введите только положительные целые числа.")
            continue

        dec_res, bcd_res = add_5421_bcd(a, b)
        print("\nОбычное десятичное значение:", dec_res)
        print("BCD 5-4-2-1 код (по 4 бита на цифру):")
        print(bcd_res)

if __name__ == "__main__":
    main()