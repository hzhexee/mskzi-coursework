import math
import binascii

def text_to_bytearray(text: str) -> bytes:
    """
    Преобразует текст в байтовый массив.
    
    Args:
        text: Входная строка текста.
        
    Returns:
        bytes: Байтовый массив, представляющий входной текст в кодировке UTF-8.
    """
    return text.encode('utf-8')

def bytearray_visualize_with_chars(byte_data: bytes) -> str:
    """
    Визуализирует байтовый массив с отображением символов.
    Используется для первого шага алгоритма.
    
    Функция создаёт строковое представление байтового массива, 
    отображая как шестнадцатеричные значения, так и соответствующие им 
    символы в кодировке UTF-8, если они являются отображаемыми.
    
    Args:
        byte_data: Байтовый массив для визуализации.
        
    Returns:
        str: Строковое представление байтового массива с отображением символов.
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
    
    Функция преобразует байтовый массив в строку шестнадцатеричных значений,
    разделённых дефисами.
    
    Args:
        byte_data: Байтовый массив для визуализации.
        
    Returns:
        str: Строка шестнадцатеричных значений, разделённых дефисами.
    """
    hex_line = binascii.hexlify(byte_data, sep='-').decode('utf-8')
    return hex_line

def add_padding(byte_data: bytes) -> bytearray:
    """
    Добавляет padding к байтовому массиву для MD5.
    
    В алгоритме MD5 исходное сообщение дополняется до размера, кратного 512 битам (64 байтам).
    Дополнение происходит следующим образом:
    1. Добавляется бит 1 (байт 0x80)
    2. Добавляются биты 0 до получения длины (размер_сообщения_в_битах + 64) % 512 = 448
    3. Добавляется 64-битное представление исходной длины сообщения в битах
    
    Args:
        byte_data: Исходный байтовый массив.
        
    Returns:
        bytearray: Байтовый массив с добавленным padding'ом.
    """
    original_length_bits = len(byte_data) * 8
    padded_data = bytearray(byte_data)
    padded_data.append(0x80)
    padding_length = (56 - (len(padded_data) % 64)) % 64
    padded_data.extend([0x00] * padding_length)
    padded_data.extend(original_length_bits.to_bytes(8, byteorder='little'))
    return padded_data

def F(x, y, z):
    """
    Функция F используется в первом раунде алгоритма MD5.
    
    Реализует булеву функцию (x AND y) OR ((NOT x) AND z),
    которая выбирает между y и z в зависимости от x.
    
    Args:
        x, y, z: 32-битные целые числа.
        
    Returns:
        int: Результат применения функции F.
    """
    return (x & y) | (~x & z)

def G(x, y, z):
    """
    Функция G используется во втором раунде алгоритма MD5.
    
    Реализует булеву функцию (x AND z) OR (y AND (NOT z)),
    которая выбирает между x и y в зависимости от z.
    
    Args:
        x, y, z: 32-битные целые числа.
        
    Returns:
        int: Результат применения функции G.
    """
    return (x & z) | (y & ~z)

def H(x, y, z):
    """
    Функция H используется в третьем раунде алгоритма MD5.
    
    Реализует булеву функцию x XOR y XOR z,
    которая вычисляет бит чётности (XOR) для каждой тройки битов.
    
    Args:
        x, y, z: 32-битные целые числа.
        
    Returns:
        int: Результат применения функции H.
    """
    return x ^ y ^ z

def I(x, y, z):
    """
    Функция I используется в четвёртом раунде алгоритма MD5.
    
    Реализует булеву функцию y XOR (x OR (NOT z)),
    которая является нелинейной функцией от всех трёх аргументов.
    
    Args:
        x, y, z: 32-битные целые числа.
        
    Returns:
        int: Результат применения функции I.
    """
    return y ^ (x | ~z)

def buffer_init():
    """
    Инициализирует буферы MD5 начальными значениями.
    
    В алгоритме MD5 используются четыре 32-битных буфера (A, B, C, D),
    которые инициализируются фиксированными константами.
    
    Returns:
        list: Список из четырёх 32-битных целых чисел, представляющих начальные значения буферов.
    """
    return [
        0x67452301,  # A
        0xEFCDAB89,  # B
        0x98BADCFE,  # C
        0x10325476   # D
    ]

def left_rotate(x, c):
    """
    Выполняет циклический сдвиг влево 32-битного числа.
    
    Args:
        x: 32-битное целое число.
        c: Количество битов для сдвига.
        
    Returns:
        int: Результат циклического сдвига влево.
    """
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
    
    Функция реализует основной цикл алгоритма MD5, который состоит из 64 шагов,
    разделённых на 4 раунда по 16 шагов. На каждом шаге используются различные 
    нелинейные функции (F, G, H, I) и выполняются операции над буферами.
    
    Args:
        block: 64-байтный блок данных для обработки.
        buffers: Текущие значения буферов MD5 [A, B, C, D].
        
    Returns:
        list: Обновленные значения буферов.
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
    """
    Обрабатывает блок с подробной визуализацией.
    
    Аналогичен функции md5_process_block, но дополнительно сохраняет
    подробную информацию о каждом шаге алгоритма для визуализации.
    
    Args:
        block: 64-байтный блок данных для обработки.
        buffers: Текущие значения буферов MD5 [A, B, C, D].
        
    Returns:
        tuple: Кортеж (обновленные буферы, данные о выполненных шагах).
    """
    M = [int.from_bytes(block[i:i + 4], byteorder='little') for i in range(0, 64, 4)]
    A, B, C, D = buffers
    original_buffers = buffers.copy()
    
    rounds_data = []
    
    # Заголовок для информации о блоке
    rounds_data.append(f"Исходные значения буферов:")
    rounds_data.append(f"A = {A:#010x}, B = {B:#010x}, C = {C:#010x}, D = {D:#010x}\n")

    for round_index, func in enumerate([F, G, H, I]):
        # Добавляем заголовок раунда (будет использоваться для разделения раундов)
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
            
            # Сохраняем состояние до изменений для визуализации
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

def process_blocks(data: bytes, buffers):
    """
    Обрабатывает все блоки данных.
    
    Разделяет входные данные на блоки по 64 байта и последовательно 
    обрабатывает их с помощью функции md5_process_block.
    
    Args:
        data: Байтовый массив данных для обработки.
        buffers: Начальные значения буферов MD5 [A, B, C, D].
        
    Returns:
        list: Финальные значения буферов.
    """
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        buffers = md5_process_block(block, buffers)
    return buffers

def process_blocks_with_detailed_visualization(data: bytes, buffers, callback=None):
    """
    Обрабатывает блоки с подробной визуализацией.
    
    Функция разделяет входные данные на блоки по 64 байта и обрабатывает их,
    сохраняя подробную информацию о каждом шаге алгоритма для визуализации.
    При наличии callback-функции вызывает её после обработки каждого блока.
    
    Args:
        data: Байтовый массив данных для обработки.
        buffers: Начальные значения буферов MD5 [A, B, C, D].
        callback: Функция обратного вызова, которая принимает номер блока,
                 его шестнадцатеричное представление, данные о раундах и
                 обновлённые буферы.
        
    Returns:
        list: Финальные значения буферов.
    """
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        block_hex = bytearray_visualize_simple(block)
        
        buffers, rounds_data = md5_process_block_with_details(block, buffers)
        if callback:
            callback(i // 64, block_hex, rounds_data, buffers.copy())
    
    return buffers

def finalize_hash(buffers):
    """
    Преобразует финальные значения буферов в MD5 хеш.
    
    Конкатенирует четыре 32-битных буфера в порядке little-endian
    и представляет результат в виде шестнадцатеричной строки.
    
    Args:
        buffers: Список из четырёх 32-битных буферов [A, B, C, D].
        
    Returns:
        str: Строка, представляющая 128-битный MD5 хеш.
    """
    return ''.join(buffer.to_bytes(4, byteorder='little').hex() for buffer in buffers)

def calculate_md5(text: str) -> str:
    """
    Вычисляет MD5 хеш для входного текста.
    
    Выполняет полный процесс вычисления MD5-хеша:
    1. Преобразует текст в байтовый массив
    2. Добавляет padding
    3. Инициализирует буферы
    4. Обрабатывает все блоки данных
    5. Формирует финальный хеш
    
    Args:
        text: Входная строка текста.
        
    Returns:
        str: 32-символьная строка, представляющая MD5 хеш.
    """
    byte_data = text_to_bytearray(text)
    padded_data = add_padding(byte_data)
    buffers = buffer_init()
    final_buffers = process_blocks(padded_data, buffers)
    return finalize_hash(final_buffers)

def visualize_padding(original: bytes, padded: bytearray) -> str:
    """
    Визуализирует процесс добавления padding.
    
    Создаёт строковое представление, показывающее исходные данные,
    добавленный padding и байты длины сообщения.
    
    Args:
        original: Исходный байтовый массив до добавления padding.
        padded: Байтовый массив после добавления padding.
        
    Returns:
        str: Строковое представление процесса добавления padding.
    """
    original_hex = bytearray_visualize_simple(original)
    
    # Вычисляем границы для padding и длины сообщения
    padding_start = len(original) + 1  # +1 для байта 0x80
    length_start = len(padded) - 8     # Последние 8 байт - длина
    
    # Разделяем на части
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

def visualize_block_process(block_number: int, block: bytes, buffers_before: list, buffers_after: list) -> str:
    """
    Визуализирует обработку одного блока данных.
    
    Создаёт строковое представление, показывающее данные блока,
    значения буферов до и после его обработки.
    
    Args:
        block_number: Номер блока.
        block: Байтовый массив, представляющий блок данных.
        buffers_before: Значения буферов до обработки блока.
        buffers_after: Значения буферов после обработки блока.
        
    Returns:
        str: Строковое представление обработки блока.
    """
    block_hex = bytearray_visualize_simple(block)
    before = [f"{b:08x}" for b in buffers_before]
    after = [f"{b:08x}" for b in buffers_after]
    return (f"Блок {block_number}:\n{block_hex}\n\n"
            f"Буферы до:\nA: {before[0]}\nB: {before[1]}\nC: {before[2]}\nD: {before[3]}\n\n"
            f"Буферы после:\nA: {after[0]}\nB: {after[1]}\nC: {after[2]}\nD: {after[3]}")

def process_blocks_with_visualization(data: bytes, buffers, callback=None):
    """
    Обрабатывает блоки с простой визуализацией.
    
    Разделяет входные данные на блоки по 64 байта, обрабатывает их
    и при наличии callback-функции вызывает её с информацией о каждом блоке.
    
    Args:
        data: Байтовый массив данных для обработки.
        buffers: Начальные значения буферов MD5 [A, B, C, D].
        callback: Функция обратного вызова, которая принимает строку
                 с визуализацией обработки блока.
        
    Returns:
        list: Финальные значения буферов.
    """
    for i in range(0, len(data), 64):
        block = data[i:i + 64]
        buffers_before = buffers.copy()
        buffers = md5_process_block(block, buffers)
        if callback:
            block_info = visualize_block_process(i//64 + 1, block, buffers_before, buffers)
            callback(block_info)
    return buffers
