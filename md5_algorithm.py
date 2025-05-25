import math
import binascii

T = [int((2 ** 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]

S = [
    [7, 12, 17, 22],
    [5, 9, 14, 20],
    [4, 11, 16, 23],
    [6, 10, 15, 21]
]

def text_to_bytearray(text: str) -> bytes:
    return text.encode('utf-8')

def bytearray_visualize_with_chars(byte_data: bytes) -> str:
    hex_line = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    hex_values = hex_line.split('-')
    result = []
    
    result.append(hex_line)
    result.append("")
    
    try:
        decoded_text = byte_data.decode('utf-8')
        chars = list(decoded_text)
        char_index = 0
        bytes_per_char = []
        
        temp_data = byte_data
        while temp_data:
            for i in range(1, 5):
                try:
                    temp_data[:i].decode('utf-8')
                    bytes_per_char.append(i)
                    temp_data = temp_data[i:]
                    break
                except UnicodeDecodeError:
                    continue
        
        i = 0
        char_index = 0
        while i < len(hex_values) and char_index < len(chars):
            char = chars[char_index]
            num_bytes = bytes_per_char[char_index]
            hex_vals = '-'.join(hex_values[i:i+num_bytes])
            result.append(f"Символ {char}: {hex_vals}")
            i += num_bytes
            char_index += 1
                
    except UnicodeDecodeError:
        for i, hex_val in enumerate(hex_values):
            byte = byte_data[i]
            char = chr(byte) if 32 <= byte <= 126 else '.'
            result.append(f"Байт: {hex_val}")
    
    return '\n'.join(result)

def bytearray_visualize_simple(byte_data: bytes) -> str:
    hex_line = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    return hex_line

def add_padding(byte_data: bytes) -> bytearray:
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
        0x67452301,
        0xEFCDAB89,
        0x98BADCFE,
        0x10325476
    ]

def left_rotate(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF

def md5_process_block_with_details(block, buffers):
    M = [int.from_bytes(block[i:i + 4], byteorder='little') for i in range(0, 64, 4)]
    A, B, C, D = buffers
    original_buffers = buffers.copy()
    
    rounds_data = []

    rounds_data.append(f"Исходные значения буферов:")
    rounds_data.append(f"A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}\n")

    for round_index, func in enumerate([F, G, H, I]):
        rounds_data.append(f"=== Раунд {round_index + 1} ===")
        
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
            
            old_A, old_B, old_C, old_D = A, B, C, D
            
            temp = (A + func(B, C, D) + M[k] + T[step]) & 0xFFFFFFFF
            new_A = (B + left_rotate(temp, s)) & 0xFFFFFFFF

            rounds_data.append(f"Шаг {i + 1}:")
            rounds_data.append(f"Функция: {func.__name__}")
            rounds_data.append(f"M[{k}] = {M[k]:#010x}, T[{step}] = {T[step]:#010x}, S = {s}")
            rounds_data.append(f"До: A = {old_A:#010x}, B = {old_B:#010x}, C = {old_C:#010x}, D = {old_D:#010x}")
            rounds_data.append(f"После: A = {D:#010x}, B = {new_A:#010x}, C = {B:#010x}, D = {C:#010x}\n")

            A, D, C, B = D, C, B, new_A

    buffers[0] = (buffers[0] + A) & 0xFFFFFFFF
    buffers[1] = (buffers[1] + B) & 0xFFFFFFFF
    buffers[2] = (buffers[2] + C) & 0xFFFFFFFF
    buffers[3] = (buffers[3] + D) & 0xFFFFFFFF

    rounds_data.append("\nФинальные значения буферов:")
    rounds_data.append(f"A = {buffers[0]:#010x}, B = {buffers[1]:#010x}, C = {buffers[2]:#010x}, D = {buffers[3]:#010x}")
    
    return buffers, rounds_data

def process_blocks_with_detailed_visualization(data: bytes, buffers, callback=None):
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        block_hex = bytearray_visualize_simple(block)
        
        buffers, rounds_data = md5_process_block_with_details(block, buffers)
        if callback:
            callback(i // 64, block_hex, rounds_data, buffers.copy())
    
    return buffers

def finalize_hash(buffers):
    return ''.join(buffer.to_bytes(4, byteorder='little').hex() for buffer in buffers)

def visualize_padding(original: bytes, padded: bytearray) -> str:
    original_hex = bytearray_visualize_simple(original)
    

    padding_start = len(original) + 1
    length_start = len(padded) - 8

    padding_hex = bytearray_visualize_simple(padded[len(original):length_start])
    length_hex = bytearray_visualize_simple(padded[length_start:])
    full_hex = bytearray_visualize_simple(padded)
    
    separator = "-" * 50
    return (f"Полное сообщение после padding ({len(padded)} байт):\n{full_hex}\n\n"
            f"{separator}\n"
            f"Начальное сообщение ({len(original)} байт):\n{original_hex}\n\n"
            f"{separator}\n"
            f"Padding ({length_start - len(original)} байт):\n{padding_hex}\n\n"
            f"{separator}\n"
            f"Длина сообщения (8 байт):\n{length_hex}")
