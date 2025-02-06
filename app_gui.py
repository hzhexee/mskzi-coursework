import sys
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLineEdit, 
    QPushButton, 
    QTextEdit, 
    QMenuBar, 
    QMenu, 
    QLabel, 
    QFrame,
    QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from md5_algorithm import (
    text_to_bytearray,
    add_padding,
    buffer_init,
    process_blocks_with_detailed_visualization,
    finalize_hash,
    visualize_padding,
    bytearray_visualize_with_chars
)

## TODO: 
# 1. Добавить кнопку "Сбросить" для очистки визуализации; 
# 2. Добавить кнопку "Сохранить" в MenuBar для сохранения визуализации в файл
# 3. Добавить кнопку "Скопировать" в MenuBar для копирования визуализации в буфер обмена
# 4. Добавить кнопку "О программе" в MenuBar для отображения информации о программе
# 5. Добавить кнопку "Справка" в MenuBar для отображения справочной информации
# 6. Добавить возможность изменения размера шрифта в визуализации
# 7. Добавить темную тему и переключатель тем
# 8. Добавить возможность экспорта визуализации в PDF
# 9. Добавить анимацию при переходе между шагами
# 10. Добавить возможность ввода текста в hex формате
# 11. Добавить индикатор прогресса вычисления для больших входных данных
# 12. Добавить возможность сравнения двух хешей
# 13. Добавить визуализацию битовых операций на каждом шаге

class StyledFrame(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.layout = QVBoxLayout(self)
        if title:
            title_label = QLabel(title)
            self.layout.addWidget(title_label)

class MD5VisualizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация алгоритма хеширования MD5")
        self.setMinimumSize(1200, 800)
        self.setupUI()

    def setupUI(self):
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Настройки")
        
        # Add menu actions
        hash_string_action = QAction("Хеш от строки", self)
        hash_string_action.setShortcut("Ctrl+H")
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        
        file_menu.addAction(hash_string_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Input section
        input_frame = StyledFrame("Ввод")
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите текст...")
        
        input_layout.addWidget(self.input_field)
        input_frame.layout.addLayout(input_layout)
        main_layout.addWidget(input_frame)

        # Visualization section
        viz_frame = StyledFrame("Визуализация")
        
        # Add navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Предыдущий шаг") 
        self.next_button = QPushButton("Следующий шаг ▶")
        self.hash_button = QPushButton("Вычислить хеш")
        
        self.prev_button.clicked.connect(self.show_previous_step)
        self.next_button.clicked.connect(self.show_next_step)
        self.hash_button.clicked.connect(self.calculate_md5)
        
        self.step_label = QLabel("Шаг 0/0")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.step_label)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.hash_button)
        
        # Initially hide navigation buttons
        self.prev_button.hide()
        self.next_button.hide()
        self.step_label.hide()
        
        viz_frame.layout.addLayout(nav_layout)
        
        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Убираем границы
        
        # Создаем контейнер для содержимого
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Заменяем QTextEdit на QLabel
        self.visualization = QLabel()
        self.visualization.setWordWrap(True)
        self.visualization.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualization.setTextFormat(Qt.TextFormat.PlainText)
        self.visualization.setFont(QFont("Segoe UI", 12))
        self.visualization.setStyleSheet("""
            QLabel {
                padding: 20px;
                line-height: 1.5;
                background: transparent;
                color: #333333;
            }
        """)
        
        content_layout.addWidget(self.visualization)
        content_layout.addStretch()  # Добавляем растяжку снизу
        
        scroll_area.setWidget(content_widget)
        viz_frame.layout.addWidget(scroll_area)
        
        main_layout.addWidget(viz_frame)

        # Initialize step tracking
        self.current_step = 0
        self.steps = []
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        if not self.steps:
            self.prev_button.hide()
            self.next_button.hide()
            self.step_label.hide()
            self.hash_button.show()
            return

        self.next_button.show()
        self.step_label.show()
        self.hash_button.hide()
        
        # Show prev button only if not on first step
        if self.current_step > 0:
            self.prev_button.show()
        else:
            self.prev_button.hide()
        
        self.next_button.setEnabled(self.current_step < len(self.steps) - 1)
        self.step_label.setText(f"Шаг {self.current_step + 1}/{len(self.steps)}")

    def show_previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.visualization.setText(self.steps[self.current_step])
            self.update_navigation_buttons()

    def show_next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.visualization.setText(self.steps[self.current_step])
            self.update_navigation_buttons()

    def store_step(self, text):
        self.steps.append(f"{text}\n")

    def calculate_md5(self):
        self.visualization.clear()
        self.steps = []
        self.current_step = 0
        text = self.input_field.text()

        if not text:
            return

        # Hide hash button and show navigation
        self.update_navigation_buttons()
        
        # Step 1: Convert to bytes
        byte_data = text_to_bytearray(text)
        self.store_step(f"Шаг 1: Преобразование текста в байты\n{bytearray_visualize_with_chars(byte_data)}")

        # Step 2: Add padding
        padded_data = add_padding(byte_data)
        self.store_step(f"Шаг 2: Добавление padding\n{visualize_padding(byte_data, padded_data)}")

        # Step 3: Initialize buffers
        buffers = buffer_init()
        self.store_step(f"Шаг 3: Инициализация буферов\n" + 
                      "\n".join(f"{name}: {value:08x}" for name, value in 
                              zip(['A', 'B', 'C', 'D'], buffers)))

        # Step 4: Process blocks with detailed visualization
        final_buffers = process_blocks_with_detailed_visualization(padded_data, buffers, self.store_step)

        # Step 5: Final hash
        result = finalize_hash(final_buffers)
        buffer_visualization = []
        for buffer in final_buffers:
            # Convert to hex without '0x' prefix and pad with zeros
            hex_value = f"{buffer:08x}"
            # Group by 2 chars and reverse the groups (little-endian)
            pairs = [hex_value[i:i+2] for i in range(0, 8, 2)]
            formatted = ' '.join(pairs[::-1])
            buffer_visualization.append(formatted)
        
        self.store_step(
            f"Шаг 5: Финальный хэш\n\n"
            f"Буферы в little-endian формате:\n"
            f"A: {buffer_visualization[0]}\n"
            f"B: {buffer_visualization[1]}\n"
            f"C: {buffer_visualization[2]}\n"
            f"D: {buffer_visualization[3]}\n\n"
            f"Итоговый хэш (конкатенация буферов):\n{result}"
        )

        # Show first step and update navigation
        if self.steps:
            self.visualization.setText(self.steps[0])
            self.update_navigation_buttons()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Load and apply CSS styles
    with open('app_gui_styles.css', 'r') as f:
        app.setStyleSheet(f.read())
    
    window = MD5VisualizerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
