
SIGN_BITS = 1
EXP_BITS = 8
MANT_BITS = 23
BIAS = (1 << (EXP_BITS - 1)) - 1  


def zeros(n):
    return [0] * n

def int_to_bits(x, n):
    arr = zeros(n)
    i = n - 1
    while i >= 0 and x > 0:
        arr[i] = x % 2
        x //= 2
        i -= 1
    return arr

def bits_to_int(bits):
    v = 0
    for b in bits:
        v = v * 2 + b
    return v

def print_bits(bits):
    print("".join(str(b) for b in bits))



def float_to_ieee754_manual(x):
    sign = 1 if x < 0 else 0
    x = abs(x)

    int_part = int(x)
    frac_part = x - int_part

  
    if int_part == 0:
        int_bits = [0]
    else:
        int_bits = []
        t = int_part
        while t > 0:
            int_bits.insert(0, t % 2)
            t //= 2

    frac_bits = []
    f = frac_part
    for _ in range(MANT_BITS + 2):
        f *= 2
        bit = 1 if f >= 1 else 0
        frac_bits.append(bit)
        if f >= 1:
            f -= 1

    if any(int_bits):
        shift = len(int_bits) - 1
        exp_val = shift + BIAS
        mant = int_bits[1:] + frac_bits
    else:
        shift = 0
        while shift < len(frac_bits) and frac_bits[shift] == 0:
            shift += 1
        exp_val = BIAS - (shift + 1)
        mant = frac_bits[shift+1:]

    mant = mant[:MANT_BITS]
    exp_bits = int_to_bits(exp_val, EXP_BITS)

    return sign, exp_bits, mant

def normalize(sign, exp_bits, mant):
    exp = bits_to_int(exp_bits)
    m = mant
    while len(m) > MANT_BITS:
        extra = m[MANT_BITS:]
        m = m[:MANT_BITS]
        if extra[0] == 1:
            carry = 1
            for i in range(MANT_BITS-1, -1, -1):
                s = m[i] + carry
                m[i] = s % 2
                carry = s // 2
            if carry:
                exp += 1
    return sign, int_to_bits(exp, EXP_BITS), m



def shift_right(bits, n):
   
    if n <= 0:
        return bits[:]
    return [0]*n + bits[:-n] if n < len(bits) else [0]*len(bits)


def compare_bits(a, b):
    
    for x, y in zip(a, b):
        if x > y:
            return 1
        if x < y:
            return -1
    return 0


def subtract_bits(a, b):
   
    res = a[:]
    borrow = 0
    for i in range(len(a)-1, -1, -1):
        diff = res[i] - b[i] - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        res[i] = diff
    return res


def ieee754_add_manual(a, b):
    sa, ea, ma = float_to_ieee754_manual(a)
    sb, eb, mb = float_to_ieee754_manual(b)

    eai = bits_to_int(ea)
    ebi = bits_to_int(eb)

   
    m1 = [1] + ma
    m2 = [1] + mb


    if eai > ebi:
        m2 = shift_right(m2, eai - ebi)
        exp_res = eai
    else:
        m1 = shift_right(m1, ebi - eai)
        exp_res = ebi

   
    if sa == sb:
        res = []
        carry = 0
        for i in range(len(m1)-1, -1, -1):
            s = m1[i] + m2[i] + carry
            res.insert(0, s % 2)
            carry = s // 2

        if carry:
            exp_res += 1
            res = [carry] + res[:-1]

        sign_res = sa

    else:
        
        cmp = compare_bits(m1, m2)

        if cmp == 0:
            return 0, int_to_bits(0, EXP_BITS), zeros(MANT_BITS)

        if cmp > 0:
            res = subtract_bits(m1, m2)
            sign_res = sa
        else:
            res = subtract_bits(m2, m1)
            sign_res = sb

      
        while res[0] == 0 and exp_res > 0:
            res = res[1:] + [0]
            exp_res -= 1

    return normalize(sign_res, int_to_bits(exp_res, EXP_BITS), res[1:])

def ieee754_sub_manual(a, b):
    return ieee754_add_manual(a, -b)

def ieee754_mul_manual(a, b):
    sa, ea, ma = float_to_ieee754_manual(a)
    sb, eb, mb = float_to_ieee754_manual(b)

    sign = sa ^ sb
    eai = bits_to_int(ea)
    ebi = bits_to_int(eb)


    sig_a = (1 << MANT_BITS) | bits_to_int(ma)
    sig_b = (1 << MANT_BITS) | bits_to_int(mb)

    prod = sig_a * sig_b

    exp = eai + ebi - BIAS


    if prod & (1 << (2 * MANT_BITS + 1)): 
        shift = MANT_BITS + 1  
        exp += 1
    else:
        shift = MANT_BITS     


    lost = prod & ((1 << shift) - 1)
    prod_main = prod >> shift  

    mant = prod_main & ((1 << MANT_BITS) - 1)

    guard = (lost >> (shift - 1)) & 1
    round_bit = (lost >> (shift - 2)) & 1 if shift >= 2 else 0
    sticky = 1 if (shift > 2 and (lost & ((1 << (shift - 2)) - 1)) != 0) else 0

    if guard and (round_bit or sticky or (mant & 1)):
        mant += 1
        if mant == (1 << MANT_BITS): 
            mant = 0
            exp += 1

    exp_bits = int_to_bits(exp, EXP_BITS)
    return sign, exp_bits, int_to_bits(mant, MANT_BITS)

def ieee754_div_manual(a, b):

    if b == 0.0:

        raise ZeroDivisionError("Деление на ноль")

    sa, ea, ma = float_to_ieee754_manual(a)
    sb, eb, mb = float_to_ieee754_manual(b)

    sign = sa ^ sb
    eai = bits_to_int(ea)
    ebi = bits_to_int(eb)

 
    sig_a = (1 << MANT_BITS) | bits_to_int(ma)
    sig_b = (1 << MANT_BITS) | bits_to_int(mb)


    exp = eai - ebi + BIAS


    EXTRA = 3
    num = sig_a << (MANT_BITS + EXTRA)
    q = num // sig_b
    r = num % sig_b


    top_pos = MANT_BITS + EXTRA
    if q >= (1 << (top_pos + 1)):      
        q >>= 1
        exp += 1
    elif q < (1 << top_pos):          
        q <<= 1
        exp -= 1

   
    mant = (q >> EXTRA) & ((1 << MANT_BITS) - 1)  
    guard = (q >> (EXTRA - 1)) & 1
    round_bit = (q >> (EXTRA - 2)) & 1 if EXTRA >= 2 else 0
    sticky = 1 if ( (q & ((1 << (EXTRA - 2)) - 1)) != 0 or r != 0 ) else 0


    if guard and (round_bit or sticky or (mant & 1)):
        mant += 1
        if mant == (1 << MANT_BITS): 
            mant = 0
            exp += 1

    exp_bits = int_to_bits(exp, EXP_BITS)
    return sign, exp_bits, int_to_bits(mant, MANT_BITS)



def ieee754_to_32bit(sign, exp_bits, mant_bits):
    return [sign] + exp_bits + mant_bits



def show_menu():
    print(
        "\nВыберите операцию:\n"
        "1 — Сложение\n"
        "2 — Вычитание\n"
        "3 — Умножение\n"
        "4 — Деление\n"
        "0 — Выход"
    )
def ieee754_to_float_decimal(bits: list[int]) -> float:
   

    sign_bit = bits[0]
    exp_bits = bits[1:1+EXP_BITS]
    mant_bits = bits[1+EXP_BITS:]


    exponent = bits_to_int(exp_bits)
    mantissa_bits_val = bits_to_int(mant_bits)


    bias = BIAS

   
    frac = 1.0 + (mantissa_bits_val / (2 ** MANT_BITS))
    real_exp = exponent - bias
    value = ((-1) ** sign_bit) * frac * (2 ** real_exp)

    return value
def main():
    while True:
        show_menu()
        choice = input("Введите номер операции: ").strip()
        if choice == "0":
            print("Выход.")
            break

        try:
            a = float(input("Введите число A: "))
            b = float(input("Введите число B: "))
        except ValueError:
            print("Некорректный ввод чисел.")
            continue

        if choice == "1":
            s, e, m = ieee754_add_manual(a, b)
            res = ieee754_to_32bit(s, e, m)
            
            print("\nСложение (32-бит):")
            print_bits(res)

            dec_value = ieee754_to_float_decimal(res)
            print("Десятичный результат:", dec_value)

        elif choice == "2":
            s, e, m = ieee754_sub_manual(a, b)
            res = ieee754_to_32bit(s, e, m)
            print("\nВычитание (32-бит):")
            print_bits(res)
            print("Десятичный результат:", ieee754_to_float_decimal(res))

        elif choice == "3":
            s, e, m = ieee754_mul_manual(a, b)
            res = ieee754_to_32bit(s, e, m)
            print("\nУмножение (32-бит):")
            print_bits(res)
            print("Десятичный результат:", ieee754_to_float_decimal(res))

        elif choice == "4":
            s, e, m = ieee754_div_manual(a, b)
            res = ieee754_to_32bit(s, e, m)
            print("\nДеление (32-бит):")
            print_bits(res)
            print("Десятичный результат:", ieee754_to_float_decimal(res))

        else:
            print("Неверный выбор операции.")

if __name__ == "__main__":
    main()