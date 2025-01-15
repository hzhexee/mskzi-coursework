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
        self.visualization = QTextEdit()
        self.visualization.setReadOnly(True)
        self.visualization.setFont(QFont("Courier New", 10))
        viz_frame.layout.addWidget(self.visualization)
        main_layout.addWidget(viz_frame)

    def show_step(self, text):
        self.visualization.append(f"{text}\n{'='*50}\n")
        self.visualization.verticalScrollBar().setValue(
            self.visualization.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    def calculate_md5(self):
        self.visualization.clear()
        text = self.input_field.text()

        # Step 1: Convert to bytes
        byte_data = text_to_bytearray(text)
        self.show_step(f"Step 1: Converting text to bytes\n{bytearray_visualize(byte_data)}")

        # Step 2: Add padding
        padded_data = add_padding(byte_data)
        self.show_step(f"Step 2: Adding padding\n{visualize_padding(byte_data, padded_data)}")

        # Step 3: Initialize buffers
        buffers = buffer_init()
        self.show_step("Step 3: Initializing buffers\n" + 
                      "\n".join(f"{name}: {value:08x}" for name, value in 
                              zip(['A', 'B', 'C', 'D'], buffers)))

        # Step 4: Process blocks with detailed visualization
        final_buffers = process_blocks_with_detailed_visualization(padded_data, buffers, self.show_step)

        # Step 5: Final hash
        result = finalize_hash(final_buffers)
        self.show_step(f"Final MD5 Hash:\n{result}")

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
