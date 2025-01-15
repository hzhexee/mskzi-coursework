import math
import binascii

def text_to_bytearray(text: str) -> bytes:
    """
    Преобразует текст в байтовый массив.
    """
    return text.encode('utf-8')

def bytearray_visualize(byte_data: bytes) -> str:
    """
    Визуализирует байтовый массив.
    """
    return binascii.hexlify(byte_data, sep='-').decode('utf-8')

def add_padding(byte_data: bytes) -> bytearray:
    """
    Добавляет padding к байтовому массиву для MD5.
    """
    original_length_bits = len(byte_data) * 8
    padded_data = bytearray(byte_data)
    padded_data.append(0x80)
    padding_length = (56 - (len(padded_data) % 64)) % 64
    padded_data.extend([0x00] * padding_length)
    padded_data.extend(original_length_bits.to_bytes(8, byteorder='little'))
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
    """
    Обрабатывает один 512-битный блок данных.
    Возвращает обновленные значения буферов.
    """
    M = [int.from_bytes(block[i:i + 4], byteorder='little') for i in range(0, 64, 4)]
    A, B, C, D = buffers

    for round_index, func in enumerate([F, G, H, I]):
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
            A, D, C, B = D, C, B, new_A

    buffers[0] = (buffers[0] + A) & 0xFFFFFFFF
    buffers[1] = (buffers[1] + B) & 0xFFFFFFFF
    buffers[2] = (buffers[2] + C) & 0xFFFFFFFF
    buffers[3] = (buffers[3] + D) & 0xFFFFFFFF

    return buffers

def process_blocks(data: bytes, buffers):
    """
    Обрабатывает все блоки данных.
    Возвращает финальные значения буферов.
    """
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        buffers = md5_process_block(block, buffers)
    return buffers

def finalize_hash(buffers):
    """
    Преобразует финальные значения буферов в MD5 хеш.
    """
    return ''.join(buffer.to_bytes(4, byteorder='little').hex() for buffer in buffers)

def calculate_md5(text: str) -> str:
    """
    Вычисляет MD5 хеш для входного текста.
    """
    byte_data = text_to_bytearray(text)
    padded_data = add_padding(byte_data)
    buffers = buffer_init()
    final_buffers = process_blocks(padded_data, buffers)
    return finalize_hash(final_buffers)
