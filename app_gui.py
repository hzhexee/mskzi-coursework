import sys
import os
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
    QScrollArea,
    QMessageBox,
    QFileDialog,
    QDialog,
    QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QClipboard
from md5_algorithm import (
    text_to_bytearray,
    add_padding,
    buffer_init,
    process_blocks_with_detailed_visualization,
    finalize_hash,
    visualize_padding,
    bytearray_visualize_with_chars
)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("MD5 Step By Step")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        description = QLabel(
            "Визуализатор алгоритма хеширования MD5.\n"
            "Версия: 1.0\n\n"
            "© 2025 MD5StepByStep\n\n"
            "Это приложение демонстрирует пошаговую работу алгоритма MD5,\n"
            "позволяя увидеть все этапы преобразования данных\n"
            "от исходного текста до финального хеш-значения."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(close_button)

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Руководство пользователя")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h2>Как использовать визуализатор MD5</h2>
            <ol>
                <li><b>Введите текст</b> в поле ввода.</li>
                <li>Нажмите кнопку <b>Вычислить хеш</b>.</li>
                <li>Используйте кнопки <b>Предыдущий шаг</b> и <b>Следующий шаг</b> для навигации по этапам алгоритма.</li>
                <li>Для сброса визуализации нажмите кнопку <b>Сбросить</b>.</li>
            </ol>
            
            <h3>Сохранение результатов:</h3>
            <p>В меню <b>Файл</b> вы можете:</p>
            <ul>
                <li>Сохранить текущий шаг в файл</li>
                <li>Скопировать в буфер обмена</li>
            </ul>
            
            <h3>Этапы алгоритма MD5:</h3>
            <ol>
                <li><b>Преобразование текста в байты</b> - исходный текст преобразуется в последовательность байтов.</li>
                <li><b>Добавление padding</b> - дополнение данных до размера, кратного 512 битам.</li>
                <li><b>Инициализация буферов</b> - инициализация четырех 32-битных регистров A, B, C и D.</li>
                <li><b>Обработка блоков</b> - последовательная обработка 512-битных блоков данных.</li>
                <li><b>Финальный хеш</b> - формирование 128-битного хеш-значения из буферов.</li>
            </ol>
        """)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(title)
        layout.addWidget(help_text)
        layout.addWidget(close_button)

class StyledFrame(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("styled")
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("title")
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
        
        # File menu
        file_menu = menubar.addMenu("Файл")
        
        save_action = QAction("Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_to_file)
        
        copy_action = QAction("Копировать", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_to_clipboard)
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        
        file_menu.addAction(save_action)
        file_menu.addAction(copy_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about_dialog)
        
        help_action = QAction("Справка", self)
        help_action.triggered.connect(self.show_help_dialog)
        
        help_menu.addAction(help_action)
        help_menu.addAction(about_action)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Input section
        input_frame = StyledFrame("Ввод данных")
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите текст для хеширования...")
        
        self.hash_button = QPushButton("Вычислить хеш")
        self.hash_button.clicked.connect(self.calculate_md5)
        self.hash_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_visualization)
        self.reset_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.hash_button)
        input_layout.addWidget(self.reset_button)
        
        input_frame.layout.addLayout(input_layout)
        main_layout.addWidget(input_frame)

        # Visualization section
        viz_frame = StyledFrame("Визуализация алгоритма")
        
        # Add navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Предыдущий шаг") 
        self.next_button = QPushButton("Следующий шаг ▶")
        
        self.prev_button.clicked.connect(self.show_previous_step)
        self.next_button.clicked.connect(self.show_next_step)
        
        self.step_label = QLabel("Шаг 0/0")
        self.step_label.setObjectName("stepLabel")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.step_label)
        nav_layout.addWidget(self.next_button)
        
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
        self.visualization.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.visualization.setTextFormat(Qt.TextFormat.PlainText)
        self.visualization.setFont(QFont("Consolas", 12))
        self.visualization.setStyleSheet("""
            padding: 20px;
            line-height: 1.5;
            background: transparent;
            color: #333333;
        """)
        
        content_layout.addWidget(self.visualization)
        content_layout.addStretch()  # Добавляем растяжку снизу
        
        scroll_area.setWidget(content_widget)
        viz_frame.layout.addWidget(scroll_area)
        
        main_layout.addWidget(viz_frame, 1)  # 1 = stretch factor

        # Initialize step tracking
        self.current_step = 0
        self.steps = []
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        if not self.steps:
            self.prev_button.hide()
            self.next_button.hide()
            self.step_label.hide()
            return

        # Show prev button only if not on first step
        self.prev_button.setVisible(self.current_step > 0)
        self.next_button.setVisible(self.current_step < len(self.steps) - 1)
        self.step_label.show()
        
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
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите текст для хеширования.")
            return

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
    
    def reset_visualization(self):
        """Сброс визуализации и очистка интерфейса"""
        self.visualization.clear()
        self.input_field.clear()
        self.steps = []
        self.current_step = 0
        self.update_navigation_buttons()
    
    def save_to_file(self):
        """Сохраняет текущий шаг визуализации в файл"""
        if not self.steps or self.current_step >= len(self.steps):
            QMessageBox.information(self, "Информация", "Нет данных для сохранения.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить визуализацию",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.steps[self.current_step])
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def copy_to_clipboard(self):
        """Копирует текущий шаг визуализации в буфер обмена"""
        if not self.steps or self.current_step >= len(self.steps):
            QMessageBox.information(self, "Информация", "Нет данных для копирования.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.steps[self.current_step])
        QMessageBox.information(self, "Успех", "Данные скопированы в буфер обмена.")
    
    def show_about_dialog(self):
        """Отображает диалог с информацией о программе"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_help_dialog(self):
        """Отображает диалог со справочной информацией"""
        dialog = HelpDialog(self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Load and apply CSS styles
    try:
        with open(os.path.join(os.path.dirname(__file__), 'app_gui_styles.css'), 'r') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Error loading styles: {e}")
    
    window = MD5VisualizerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
