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
    QSizePolicy,
    QProgressBar)
from PyQt6.QtCore import Qt, QSize, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
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
    """
    Диалоговое окно "О программе".
    
    Отображает информацию о приложении, версии и авторских правах.
    """
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
    """
    Диалоговое окно справки.
    
    Содержит подробное руководство пользователя по использованию
    визуализатора MD5 и описание этапов алгоритма MD5.
    """
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
            <li><b>Обработка блоков</b> - последовательная обработка 512-битных блоков данных:
                <ul>
                <li>Каждый блок из 512 бит разбивается на 16 слов по 32 бита</li>
                <li>Выполняется 4 раунда по 16 шагов каждый (всего 64 операции)</li>
                <li>В каждом раунде используется своя нелинейная функция:
                    <ul>
                    <li><b>Раунд 1 (F):</b> F(B,C,D) = (B ∧ C) ∨ (¬B ∧ D) - выбор между C и D в зависимости от B</li>
                    <li><b>Раунд 2 (G):</b> G(B,C,D) = (B ∧ D) ∨ (C ∧ ¬D) - выбор между B и C в зависимости от D</li>
                    <li><b>Раунд 3 (H):</b> H(B,C,D) = B ⊕ C ⊕ D - битовое XOR (исключающее ИЛИ)</li>
                    <li><b>Раунд 4 (I):</b> I(B,C,D) = C ⊕ (B ∨ ¬D) - нелинейная функция</li>
                    </ul>
                </li>
                <li>Каждый шаг включает в себя:
                    <ul>
                    <li>Применение соответствующей функции (F, G, H или I)</li>
                    <li>Сложение результата с текущим элементом данных и константой</li>
                    <li>Циклический сдвиг влево</li>
                    <li>Сложение с другим буфером</li>
                    </ul>
                </li>
                <li>После каждого блока обновляются четыре буфера (A, B, C, D)</li>
                </ul>
            </li>
            <li><b>Финальный хеш</b> - формирование 128-битного хеш-значения из буферов.</li>
            </ol>
        """)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(title)
        layout.addWidget(help_text)
        layout.addWidget(close_button)

class StyledFrame(QFrame):
    """
    Стилизованный фрейм с заголовком.
    
    Создает контейнер с рамкой, заголовком и внутренним отступом
    для группировки связанных элементов интерфейса.
    
    Args:
        title: Заголовок фрейма.
        parent: Родительский виджет.
    """
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

class CollapsibleSection(QWidget):
    """
    Реализация раскрывающегося (drop-down) виджета.
    
    Создает виджет с кнопкой, при клике на которую отображается или
    скрывается содержимое секции с анимацией.
    
    Args:
        title: Заголовок секции.
        parent: Родительский виджет.
    """
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        
        self.animation_duration = 300
        self.toggle_animation = QParallelAnimationGroup(self)
        
        # Основной layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Заголовок (кнопка для раскрытия/скрытия)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setObjectName("collapsible_button")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.toggle_content)
        
        # Иконка для кнопки
        self.toggle_button.setStyleSheet("""
            QPushButton#collapsible_button {
                text-align: left;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #eaeefa;
                border: none;
                color: #2c3e50;
            }
            QPushButton#collapsible_button:hover {
                background-color: #d0d4f7;
            }
            QPushButton#collapsible_button:checked {
                background-color: #7158e2;
                color: white;
            }
        """)
        
        # Контейнер для содержимого
        self.content_area = QScrollArea()
        self.content_area.setObjectName("collapsible_content")
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setWidgetResizable(True)
        
        # Виджет для содержимого
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(10)
        
        self.content_area.setWidget(self.content_widget)
        
        # Добавляем компоненты в основной layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        
        # Animation setup
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(self.animation_duration)
        self.animation.setStartValue(0)
        self.toggle_animation.addAnimation(self.animation)
        
    def add_content(self, widget):
        """
        Добавляет виджет в содержимое секции.
        
        Args:
            widget: Виджет для добавления в содержимое.
        """
        self.content_layout.addWidget(widget)
        
    def toggle_content(self, checked):
        """
        Показывает/скрывает содержимое секции.
        
        Вызывается при нажатии на кнопку раскрытия секции.
        
        Args:
            checked: Флаг, указывающий на новое состояние кнопки.
        """
        if checked:
            self.show_content()
        else:
            self.hide_content()
    
    def show_content(self):
        """
        Показывает содержимое секции с анимацией.
        
        Анимирует раскрытие содержимого и устанавливает кнопку в нажатое состояние.
        """
        content_height = self.content_widget.sizeHint().height()
        self.animation.setEndValue(content_height)
        self.toggle_animation.setDirection(QAbstractAnimation.Direction.Forward)
        self.toggle_animation.start()
        self.toggle_button.setChecked(True)
    
    def hide_content(self):
        """
        Скрывает содержимое секции с анимацией.
        
        Анимирует сворачивание содержимого и сбрасывает состояние кнопки.
        """
        self.animation.setEndValue(0)
        self.toggle_animation.setDirection(QAbstractAnimation.Direction.Backward)
        self.toggle_animation.start()
        self.toggle_button.setChecked(False)
        
    def add_text(self, text):
        """
        Добавляет текстовую метку в содержимое.
        
        Создает QLabel с указанным текстом, настраивает перенос слов и шрифт,
        и добавляет его в содержимое секции.
        
        Args:
            text: Текст для отображения.
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Consolas", 11))
        self.add_content(label)

class MD5VisualizerWindow(QMainWindow):
    """
    Главное окно приложения визуализатора MD5.
    
    Предоставляет интерфейс для ввода текста, вычисления MD5-хеша
    и пошаговой визуализации алгоритма.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация алгоритма хеширования MD5")
        self.setMinimumSize(1200, 800)
        self.setupUI()

    def setupUI(self):
        """
        Настраивает пользовательский интерфейс главного окна.
        
        Создает меню, поля ввода, кнопки и область визуализации.
        Инициализирует отслеживание шагов визуализации.
        """
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
        
        # Прогресс-бар для отображения процесса вычисления
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% завершено")
        self.progress_bar.hide()
        viz_frame.layout.addWidget(self.progress_bar)
        
        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Убираем границы
        
        # Создаем контейнер для содержимого
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(15)
        
        # Виджет для текстовой визуализации
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
        
        # Контейнер для блоков раундов (создается динамически)
        self.rounds_container = QWidget()
        self.rounds_layout = QVBoxLayout(self.rounds_container)
        self.rounds_layout.setContentsMargins(0, 0, 0, 0)
        self.rounds_layout.setSpacing(10)
        self.rounds_container.hide()
        
        self.content_layout.addWidget(self.visualization)
        self.content_layout.addWidget(self.rounds_container)
        self.content_layout.addStretch()  # Добавляем растяжку снизу
        
        scroll_area.setWidget(content_widget)
        viz_frame.layout.addWidget(scroll_area)
        
        main_layout.addWidget(viz_frame, 1)  # 1 = stretch factor

        # Initialize step tracking
        self.current_step = 0
        self.steps = []
        self.collapsible_sections = []
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """
        Обновляет состояние кнопок навигации.
        
        Показывает или скрывает кнопки "Предыдущий шаг" и "Следующий шаг"
        в зависимости от текущего шага визуализации.
        """
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
        """
        Переходит к предыдущему шагу визуализации.
        
        Уменьшает счетчик текущего шага, отображает соответствующие данные
        и обновляет состояние кнопок навигации.
        """
        if self.current_step > 0:
            self.current_step -= 1
            self.display_current_step()
            self.update_navigation_buttons()

    def show_next_step(self):
        """
        Переходит к следующему шагу визуализации.
        
        Увеличивает счетчик текущего шага, отображает соответствующие данные
        и обновляет состояние кнопок навигации.
        """
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.display_current_step()
            self.update_navigation_buttons()
            
    def display_current_step(self):
        """
        Отображает текущий шаг визуализации.
        
        Анализирует тип данных текущего шага и отображает их соответствующим образом:
        - Текстовые данные отображаются в виде текста
        - Структурированные данные о раундах и блоках отображаются
          с использованием раскрывающихся секций
        """
        if not self.steps:
            return
            
        step_data = self.steps[self.current_step]
        
        # Проверяем тип данных шага
        if isinstance(step_data, str):
            # Обычный текстовый шаг
            self.visualization.setText(step_data)
            self.visualization.show()
            self.rounds_container.hide()
        elif isinstance(step_data, dict) and step_data.get('type') == 'rounds':
            # Структурированные данные для шага 4 (обработка блоков)
            self.visualization.hide()
            self.rounds_container.show()
            
            # Очищаем предыдущие секции
            for section in self.collapsible_sections:
                self.rounds_layout.removeWidget(section)
                section.deleteLater()
            self.collapsible_sections.clear()
            
            # Добавляем заголовок для шага 4
            step_title = QLabel("Шаг 4: Обработка блоков данных")
            step_title.setObjectName("title")
            step_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rounds_layout.addWidget(step_title)
            
            # Добавляем начальные значения буферов (перед всеми блоками)
            if step_data.get('initial_buffers'):
                buffers_label = QLabel(f"Исходные значения буферов:\n"
                                     f"A = {step_data['initial_buffers'][0]:#010x}, "
                                     f"B = {step_data['initial_buffers'][1]:#010x}, "
                                     f"C = {step_data['initial_buffers'][2]:#010x}, "
                                     f"D = {step_data['initial_buffers'][3]:#010x}")
                buffers_label.setFont(QFont("Consolas", 11))
                buffers_label.setWordWrap(True)
                buffers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                buffers_label.setStyleSheet("margin: 10px; padding: 10px;")
                self.rounds_layout.addWidget(buffers_label)
            
            # Создаем новые секции для блоков и раундов
            blocks_data = step_data.get('blocks', [])
            
            for block_idx, block_data in enumerate(blocks_data):
                # Секция для блока
                block_section = CollapsibleSection(f"Блок {block_idx + 1}")
                
                # Информация о блоке данных
                block_info = QLabel(f"Данные блока:\n{block_data['block_hex']}")
                block_info.setFont(QFont("Consolas", 11))
                block_info.setWordWrap(True)
                block_section.add_content(block_info)
                
                # Секции для раундов внутри блока
                for round_idx, round_data in enumerate(block_data['rounds']):
                    round_section = CollapsibleSection(f"Раунд {round_idx + 1}")
                    
                    # Добавляем 16 подвкладок для каждого шага в раунде
                    step_data_list = round_data['steps']
                    for step_idx, step_info in enumerate(step_data_list):
                        step_section = CollapsibleSection(f"Шаг {step_idx + 1}")
                        step_section.add_text(step_info)
                        round_section.add_content(step_section)
                    
                    block_section.add_content(round_section)
                
                # Добавляем информацию о буферах после обработки блока
                if 'final_buffers' in block_data:
                    buffers = block_data['final_buffers']
                    block_buffers = QLabel(f"\nБуферы после обработки блока {block_idx + 1}:\n"
                                          f"A = {buffers[0]:#010x}, "
                                          f"B = {buffers[1]:#010x}, "
                                          f"C = {buffers[2]:#010x}, "
                                          f"D = {buffers[3]:#010x}")
                    # Исправление: устанавливаем шрифт и перенос строк для QLabel, а не для списка buffers
                    block_buffers.setFont(QFont("Consolas", 11))
                    block_buffers.setWordWrap(True)
                    block_section.add_content(block_buffers)
                
                self.collapsible_sections.append(block_section)
                self.rounds_layout.addWidget(block_section)
            
            # Добавляем финальный хэш, если есть
            if 'final_hash' in step_data:
                final_section = CollapsibleSection("Итоговый результат")
                final_section.add_text(step_data['final_hash'])
                self.collapsible_sections.append(final_section)
                self.rounds_layout.addWidget(final_section)
        
        else:
            # Запасной вариант для неизвестного формата
            self.visualization.setText(str(step_data))
            self.visualization.show()
            self.rounds_container.hide()

    def store_step(self, text):
        """
        Сохраняет текстовый шаг визуализации.
        
        Args:
            text: Текстовое представление шага визуализации.
        """
        self.steps.append(f"{text}\n")
        
    def store_structured_step(self, step_data):
        """
        Сохраняет структурированный шаг для визуализации раундов.
        
        Args:
            step_data: Словарь с данными о блоках и раундах.
        """
        self.steps.append(step_data)

    def calculate_md5(self):
        """
        Вычисляет MD5-хеш и создает пошаговую визуализацию.
        
        Берет текст из поля ввода, выполняет последовательные шаги алгоритма MD5
        и создает визуализацию каждого шага:
        1. Преобразование текста в байты
        2. Добавление padding
        3. Инициализация буферов
        4. Обработка блоков
        5. Формирование финального хеша
        
        Отображает прогресс выполнения с помощью прогресс-бара.
        """
        self.visualization.clear()
        self.steps = []
        self.current_step = 0
        text = self.input_field.text()

        if not text:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите текст для хеширования.")
            return
            
        # Показываем прогресс-бар
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_bar.repaint()  # Форсируем обновление UI

        try:
            # Шаг 1: Преобразование в байты
            self.progress_bar.setValue(10)
            self.progress_bar.repaint()
            byte_data = text_to_bytearray(text)
            self.store_step(f"Шаг 1: Преобразование текста в байты\n{bytearray_visualize_with_chars(byte_data)}")

            # Шаг 2: Добавление padding
            self.progress_bar.setValue(20)
            self.progress_bar.repaint()
            padded_data = add_padding(byte_data)
            self.store_step(f"Шаг 2: Добавление padding\n{visualize_padding(byte_data, padded_data)}")

            # Шаг 3: Инициализация буферов
            self.progress_bar.setValue(30)
            self.progress_bar.repaint()
            buffers = buffer_init()
            self.store_step(f"Шаг 3: Инициализация буферов\n" + 
                          "\n".join(f"{name}: {value:08x}" for name, value in 
                                  zip(['A', 'B', 'C', 'D'], buffers)))

            # Шаг 4: Обработка блоков с подробной визуализацией
            self.progress_bar.setValue(40)
            self.progress_bar.repaint()
            
            # Создаем структуру для хранения данных о раундах
            blocks_data = []
            
            # Обновленная функция для хранения структурированных данных
            def block_callback(block_index, block_hex, rounds_data, buffers):
                # Преобразуем rounds_data в структуру с раундами и шагами
                structured_rounds = []
                
                # Разбиваем данные на раунды (их 4)
                round_texts = []
                current_round = -1
                
                for line in rounds_data:
                    if line.startswith("=== Раунд "):
                        if current_round >= 0:
                            round_texts.append(current_round_text)
                        current_round = int(line.split()[2]) - 1
                        current_round_text = []  # Изменено: не включаем заголовок раунда в список строк
                    elif current_round >= 0:
                        current_round_text.append(line)
                
                if current_round >= 0:
                    round_texts.append(current_round_text)
                
                # Для каждого раунда создаем структуру с шагами
                for round_idx, round_text in enumerate(round_texts):
                    steps = []
                    current_step_text = []
                    
                    for line in round_text:
                        if line.startswith("Шаг "):
                            if current_step_text:
                                steps.append("\n".join(current_step_text))
                            current_step_text = [line]
                        else:
                            current_step_text.append(line)
                    
                    if current_step_text:
                        steps.append("\n".join(current_step_text))
                    
                    structured_rounds.append({
                        'index': round_idx,
                        'steps': steps
                    })
                
                # Добавляем структурированные данные о блоке
                blocks_data.append({
                    'block_index': block_index,
                    'block_hex': block_hex,
                    'rounds': structured_rounds,
                    'final_buffers': buffers.copy()
                })
                
                # Обновляем прогресс-бар (от 40% до 80%)
                progress = 40 + int(40 * (block_index + 1) / ((len(padded_data) + 63) // 64))
                self.progress_bar.setValue(progress)
                self.progress_bar.repaint()
            
            final_buffers = process_blocks_with_detailed_visualization(
                padded_data, buffers.copy(), block_callback
            )

            # Шаг 5: Финальный хеш
            self.progress_bar.setValue(90)
            self.progress_bar.repaint()
            result = finalize_hash(final_buffers)
            buffer_visualization = []
            for buffer in final_buffers:
                # Convert to hex without '0x' prefix and pad with zeros
                hex_value = f"{buffer:08x}"
                # Group by 2 chars and reverse the groups (little-endian)
                pairs = [hex_value[i:i+2] for i in range(0, 8, 2)]
                formatted = ' ' .join(pairs[::-1])
                buffer_visualization.append(formatted)
            
            final_hash_text = (
                f"Буферы в little-endian формате:\n"
                f"A: {buffer_visualization[0]}\n"
                f"B: {buffer_visualization[1]}\n"
                f"C: {buffer_visualization[2]}\n"
                f"D: {buffer_visualization[3]}\n\n"
                f"Итоговый хеш (конкатенация буферов):\n{result}"
            )
            
            # Добавляем структурированный шаг для обработки блоков
            rounds_step = {
                'type': 'rounds',
                'initial_buffers': buffer_init(),  # Начальные значения буферов
                'blocks': blocks_data,
                'final_hash': final_hash_text
            }
            self.store_structured_step(rounds_step)
            
            # Добавляем 5 шаг как обычный текст
            self.store_step(f"Шаг 5: Финальный хэш\n\n{final_hash_text}")

            # Все готово
            self.progress_bar.setValue(100)
            self.progress_bar.repaint()

            # Скрываем прогресс-бар после выполнения
            self.progress_bar.hide()
            
            # Показываем первый шаг
            if self.steps:
                self.current_step = 0
                self.display_current_step()
                self.update_navigation_buttons()
                
        except Exception as e:
            self.progress_bar.hide()
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при вычислении хеша:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def reset_visualization(self):
        """
        Сброс визуализации и очистка интерфейса.
        
        Очищает поле ввода, список шагов визуализации и сбрасывает
        счетчик текущего шага.
        """
        self.visualization.clear()
        self.input_field.clear()
        self.steps = []
        self.current_step = 0
        self.update_navigation_buttons()
    
    def save_to_file(self):
        """
        Сохраняет текущий шаг визуализации в файл.
        
        Предлагает пользователю выбрать файл для сохранения и записывает
        в него текущий шаг визуализации.
        """
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
        """
        Копирует текущий шаг визуализации в буфер обмена.
        
        Позволяет пользователю скопировать данные для использования
        в других приложениях.
        """
        if not self.steps or self.current_step >= len(self.steps):
            QMessageBox.information(self, "Информация", "Нет данных для копирования.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.steps[self.current_step])
        QMessageBox.information(self, "Успех", "Данные скопированы в буфер обмена.")
    
    def show_about_dialog(self):
        """
        Отображает диалог с информацией о программе.
        
        Создаёт и показывает экземпляр диалога AboutDialog.
        """
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_help_dialog(self):
        """
        Отображает диалог со справочной информацией.
        
        Создаёт и показывает экземпляр диалога HelpDialog.
        """
        dialog = HelpDialog(self)
        dialog.exec()

def main():
    """
    Главная функция приложения.
    
    Инициализирует приложение Qt, применяет стили и запускает
    главное окно визуализатора MD5.
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Load and apply CSS styles
    try:
        with open(os.path.join(os.path.dirname(__file__), 'app_gui_styles.css'), 'r') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Ошибка загрузки стилей: {e}")
    
    window = MD5VisualizerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
