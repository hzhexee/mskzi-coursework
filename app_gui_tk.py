import tkinter as tk
from tkinter import ttk
from md5_algorithm import (text_to_bytearray, add_padding, buffer_init,
                         process_blocks_with_visualization, finalize_hash,
                         visualize_padding, bytearray_visualize, process_blocks_with_detailed_visualization)

class MD5VisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация алгоритма MD5")
        self.root.geometry("1000x800")

        # Input frame
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Введите текст:").pack(side=tk.LEFT)
        self.input_text = ttk.Entry(input_frame, width=50)
        self.input_text.pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Вычислить хеш", command=self.calculate_md5).pack(side=tk.LEFT)

        # Output frame
        output_frame = ttk.Frame(root, padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)

        # Steps display
        self.steps_text = tk.Text(output_frame, wrap=tk.WORD, height=30, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.steps_text.yview)
        self.steps_text.configure(yscrollcommand=scrollbar.set)
        
        self.steps_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_step(self, text):
        self.steps_text.insert(tk.END, f"{text}\n\n{'='*50}\n\n")
        self.steps_text.see(tk.END)
        self.root.update()

    def calculate_md5(self):
        self.steps_text.delete(1.0, tk.END)
        text = self.input_text.get()

        # Step 1: Convert to bytes
        byte_data = text_to_bytearray(text)
        self.show_step(f"Шаг 1: Преобразование текста в байты\n{bytearray_visualize(byte_data)}")

        # Step 2: Add padding
        padded_data = add_padding(byte_data)
        self.show_step(f"Шаг 2: Добавление заполнения\n{visualize_padding(byte_data, padded_data)}")

        # Step 3: Initialize buffers
        buffers = buffer_init()
        self.show_step("Шаг 3: Инициализация буферов\n" + 
                      "\n".join(f"{name}: {value:08x}" for name, value in 
                              zip(['A', 'B', 'C', 'D'], buffers)))

        # Step 4: Process blocks with detailed visualization
        final_buffers = process_blocks_with_detailed_visualization(padded_data, buffers, self.show_step)

        # Step 5: Final hash
        result = finalize_hash(final_buffers)
        self.show_step(f"Итоговый MD5 хеш:\n{result}")

def main():
    root = tk.Tk()
    app = MD5VisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
