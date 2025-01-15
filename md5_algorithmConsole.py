import math
import binascii

def visualize_text_to_bytearray(text: str):
    """
    Преобразует текст в байтовый массив с визуализацией.
    """
    print(f"Шаг 1. Исходный текст: {text}")
    byte_data = text.encode('utf-8')
    print(f"Шаг 2. Преобразование в байты (UTF-8): {byte_data}")
    hex_representation = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    print(f"Шаг 3. Шестнадцатеричное представление байтов: {hex_representation}")
    return byte_data

def visualize_padding(byte_data: bytes) -> bytearray:
    """
    Добавляет padding к байтовому массиву для MD5.
    """
    original_length_bits = len(byte_data) * 8
    print(f"Шаг 4. Длина исходных данных в битах: {original_length_bits}")

    padded_data = bytearray(byte_data)
    padded_data.append(0x80)
    padding_length = (56 - (len(padded_data) % 64)) % 64
    padded_data.extend([0x00] * padding_length)
    padded_data.extend(original_length_bits.to_bytes(8, byteorder='little'))

    print(f"Шаг 5. Данные с добавленным padding: {padded_data}")
    return padded_data

def F(x, y, z):
    return (x & y) | (~x & z)

def G(x, y, z):
    return (x & z) | (y & ~z)

def H(x, y, z):
    return x ^ y ^ z

def I(x, y, z):
    return y ^ (x | ~z)

def buffer_init():
    return [
        0x67452301,  # A
        0xEFCDAB89,  # B
        0x98BADCFE,  # C
        0x10325476   # D
    ]

def left_rotate(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF

T = [int((2 ** 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]

S = [
    [7, 12, 17, 22],
    [5, 9, 14, 20],
    [4, 11, 16, 23],
    [6, 10, 15, 21]
]

def md5_process_block(block, buffers):
    M = [int.from_bytes(block[i:i + 4], byteorder='little') for i in range(0, 64, 4)]
    A, B, C, D = buffers

    print("\n=== Обработка нового блока ===")
    print("Исходные значения буферов:")
    print(f"  A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}")

    for round_index, func in enumerate([F, G, H, I]):
        print(f"\n-- Раунд {round_index + 1} --")
        for i in range(16):
            step = round_index * 16 + i
            if round_index == 0:
                k = i
            elif round_index == 1:
                k = (5 * i + 1) % 16
            elif round_index == 2:
                k = (3 * i + 5) % 16
            else:
                k = (7 * i) % 16

            s = S[round_index][i % 4]
            temp = (A + func(B, C, D) + M[k] + T[step]) & 0xFFFFFFFF
            new_A = (B + left_rotate(temp, s)) & 0xFFFFFFFF

            print(f"  Шаг {step + 1}:")
            print(f"    Функция: {func.__name__}")
            print(f"    M[{k}] = {M[k]:#010x}, T[{step}] = {T[step]:#010x}, S = {s}")
            print(f"    До: A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}")
            print(f"    После: A = {new_A:#010x}")

            A, D, C, B = D, C, B, new_A

    buffers[0] = (buffers[0] + A) & 0xFFFFFFFF
    buffers[1] = (buffers[1] + B) & 0xFFFFFFFF
    buffers[2] = (buffers[2] + C) & 0xFFFFFFFF
    buffers[3] = (buffers[3] + D) & 0xFFFFFFFF

    print("\nОбновленные значения буферов:")
    print(f"  A = {buffers[0]:#010x}, B = {buffers[1]:#010x}, C = {buffers[2]:#010x}, D = {buffers[3]:#010x}")
    # Show in little-endian with separators
    le_buffers = [x.to_bytes(4, 'little').hex('-') for x in buffers]
    print(f"  Буфферы в порядке записи хеша: {', '.join(le_buffers)}")

    return buffers

def process_blocks(data: bytes, buffers):
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        print(f"\n=== Обработка блока {i // 64 + 1} ===")
        buffers = md5_process_block(block, buffers)
    return buffers

def finalize_hash(buffers):
    return ''.join(buffer.to_bytes(4, byteorder='little').hex() for buffer in buffers)

if __name__ == "__main__":
    text = "фф"
    byte_data = visualize_text_to_bytearray(text)
    padded_data = visualize_padding(byte_data)
    buffers = buffer_init()
    final_buffers = process_blocks(padded_data, buffers)
    result_hash = finalize_hash(final_buffers)
    print(f"\nИтоговый хеш (MD5): {result_hash}")
