from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QTextEdit, 
                            QMenuBar, QMenu, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
import sys
from md5_algorithm import (text_to_bytearray, add_padding, buffer_init,
                         process_blocks_with_detailed_visualization, finalize_hash,
                         visualize_padding, bytearray_visualize)

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
        self.setWindowTitle("MD5 Visualizer")
        self.setMinimumSize(1200, 800)
        self.setupUI()

    def setupUI(self):
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        # Add menu actions
        hash_string_action = QAction("Hash String", self)
        hash_string_action.setShortcut("Ctrl+H")
        exit_action = QAction("Exit", self)
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
        input_frame = StyledFrame("Input")
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter text to hash...")
        
        self.hash_button = QPushButton("Calculate Hash")
        self.hash_button.clicked.connect(self.calculate_md5)
        
        input_layout.addWidget(self.input_field, stretch=4)
        input_layout.addWidget(self.hash_button, stretch=1)
        input_frame.layout.addLayout(input_layout)
        main_layout.addWidget(input_frame)

        # Visualization section
        viz_frame = StyledFrame("Visualization")
        
        # Add navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Previous")
        self.next_button = QPushButton("Next ▶")
        self.prev_button.clicked.connect(self.show_previous_step)
        self.next_button.clicked.connect(self.show_next_step)
        self.step_label = QLabel("Step 0/0")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.step_label)
        nav_layout.addWidget(self.next_button)
        viz_frame.layout.addLayout(nav_layout)
        
        self.visualization = QTextEdit()
        self.visualization.setReadOnly(True)
        # Update font and styling
        self.visualization.setFont(QFont("Segoe UI", 12))
        self.visualization.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualization.setStyleSheet("""
            QTextEdit {
                padding: 20px;
                line-height: 1.5;
            }
        """)
        viz_frame.layout.addWidget(self.visualization)
        main_layout.addWidget(viz_frame)

        # Initialize step tracking
        self.current_step = 0
        self.steps = []
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self.prev_button.setVisible(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < len(self.steps) - 1)
        self.step_label.setText(f"Step {self.current_step + 1}/{len(self.steps)}" if self.steps else "Step 0/0")

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

        # Step 1: Convert to bytes
        byte_data = text_to_bytearray(text)
        self.store_step(f"Step 1: Converting text to bytes\n{bytearray_visualize(byte_data)}")

        # Step 2: Add padding
        padded_data = add_padding(byte_data)
        self.store_step(f"Step 2: Adding padding\n{visualize_padding(byte_data, padded_data)}")

        # Step 3: Initialize buffers
        buffers = buffer_init()
        self.store_step("Step 3: Initializing buffers\n" + 
                      "\n".join(f"{name}: {value:08x}" for name, value in 
                              zip(['A', 'B', 'C', 'D'], buffers)))

        # Step 4: Process blocks with detailed visualization
        final_buffers = process_blocks_with_detailed_visualization(padded_data, buffers, self.store_step)

        # Step 5: Final hash
        result = finalize_hash(final_buffers)
        self.store_step(f"Final MD5 Hash:\n{result}")

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
