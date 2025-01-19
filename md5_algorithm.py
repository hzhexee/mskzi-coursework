import math
import binascii

def text_to_bytearray(text: str) -> bytes:
    """
    Преобразует текст в байтовый массив.
    """
    return text.encode('utf-8')

def bytearray_visualize_with_chars(byte_data: bytes) -> str:
    """
    Визуализирует байтовый массив с отображением символов.
    Используется для первого шага алгоритма.
    """
    hex_line = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    hex_values = hex_line.split('-')
    result = []
    
    # Add the full line of bytes first
    result.append(hex_line)
    result.append("")  # Empty line for better readability
    
    # Decode the full byte array to get proper Unicode characters
    try:
        decoded_text = byte_data.decode('utf-8')
        chars = list(decoded_text)
        char_index = 0
        bytes_per_char = []
        
        # Calculate how many bytes each character uses
        temp_data = byte_data
        while temp_data:
            for i in range(1, 5):  # UTF-8 uses 1-4 bytes per character
                try:
                    temp_data[:i].decode('utf-8')
                    bytes_per_char.append(i)
                    temp_data = temp_data[i:]
                    break
                except UnicodeDecodeError:
                    continue
        
        # Add detailed visualization
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
        # Fallback for non-text data
        for i, hex_val in enumerate(hex_values):
            byte = byte_data[i]
            char = chr(byte) if 32 <= byte <= 126 else '.'
            result.append(f"Байт: {hex_val}")
    
    return '\n'.join(result)

def bytearray_visualize_simple(byte_data: bytes) -> str:
    """
    Простая визуализация байтового массива без отображения символов.
    Используется для второго шага алгоритма и далее.
    """
    hex_line = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    return hex_line

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

def md5_process_block_with_details(block, buffers):
    """Обрабатывает блок с подробной визуализацией."""
    M = [int.from_bytes(block[i:i + 4], byteorder='little') for i in range(0, 64, 4)]
    A, B, C, D = buffers
    original_buffers = buffers.copy()
    
    details = []
    details.append("Исходные значения буферов:")
    details.append(f"A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}\n")

    for round_index, func in enumerate([F, G, H, I]):
        details.append(f"=== Раунд {round_index + 1} ===")
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

            details.append(f"Шаг {step + 1}:")
            details.append(f"Функция: {func.__name__}")
            details.append(f"M[{k}] = {M[k]:#010x}, T[{step}] = {T[step]:#010x}, S = {s}")
            details.append(f"До: A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}")
            details.append(f"После: A = {new_A:#010x}\n")

            A, D, C, B = D, C, B, new_A

    buffers[0] = (buffers[0] + A) & 0xFFFFFFFF
    buffers[1] = (buffers[1] + B) & 0xFFFFFFFF
    buffers[2] = (buffers[2] + C) & 0xFFFFFFFF
    buffers[3] = (buffers[3] + D) & 0xFFFFFFFF

    details.append("Финальные значения буферов:")
    details.append(f"A = {buffers[0]:#010x}, B = {buffers[1]:#010x}, C = {buffers[2]:#010x}, D = {buffers[3]:#010x}")
    
    return buffers, '\n'.join(details)

def process_blocks(data: bytes, buffers):
    """
    Обрабатывает все блоки данных.
    Возвращает финальные значения буферов.
    """
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        buffers = md5_process_block(block, buffers)
    return buffers

def process_blocks_with_detailed_visualization(data: bytes, buffers, callback=None):
    """Обрабатывает блоки с подробной визуализацией."""
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        block_hex = bytearray_visualize_simple(block)
        details = f"\n=== Обработка блока {i//64 + 1} ===\n"
        details += f"Данные блока:\n{block_hex}\n"
        
        buffers, block_details = md5_process_block_with_details(block, buffers)
        if callback:
            callback(details + block_details)
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

def visualize_padding(original: bytes, padded: bytearray) -> str:
    """Visualizes the padding process."""
    original_hex = bytearray_visualize_simple(original)
    padded_hex = bytearray_visualize_simple(padded)
    return f"Начальное количество байт ({len(original)} байт):\n{original_hex}\n\nКоличество байт после добавления padding ({len(padded)} байт):\n{padded_hex}"

def visualize_block_process(block_number: int, block: bytes, buffers_before: list, buffers_after: list) -> str:
    """Visualizes the processing of one block."""
    block_hex = bytearray_visualize_simple(block)
    before = [f"{b:08x}" for b in buffers_before]
    after = [f"{b:08x}" for b in buffers_after]
    return (f"Блок {block_number}:\n{block_hex}\n\n"
            f"Буферы до:\nA: {before[0]}\nB: {before[1]}\nC: {before[2]}\nD: {before[3]}\n\n"
            f"Буферы после:\nA: {after[0]}\nB: {after[1]}\nC: {after[2]}\nD: {after[3]}")

def process_blocks_with_visualization(data: bytes, buffers, callback=None):
    """Process blocks with visualization callback."""
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        buffers_before = buffers.copy()
        buffers = md5_process_block(block, buffers)
        if callback:
            block_info = visualize_block_process(i//64 + 1, block, buffers_before, buffers)
            callback(block_info)
    return buffers
