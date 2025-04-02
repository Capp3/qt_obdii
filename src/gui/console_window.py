from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Signal
import logging
import sys
from datetime import datetime

class ConsoleWindow(QDialog):
    """Dialog for displaying console output."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Console Output")
        self.setMinimumSize(600, 400)
        
        # Setup UI
        self._setup_ui()
        
        # Setup logging handler
        self._setup_logging()
        
        # Log initial message
        logging.info("Console window opened")
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Console Output")
        layout.addWidget(self.status_label)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.console_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear")
        self.close_button = QPushButton("Close")
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.clear_button.clicked.connect(self.clear_console)
        self.close_button.clicked.connect(self.close)
    
    def _setup_logging(self):
        """Setup logging handler for console output."""
        # Create a custom handler that writes to the console output
        class ConsoleHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.setFormatter(logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                ))
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.append(msg)
        
        # Add the handler to the root logger
        self.console_handler = ConsoleHandler(self.console_output)
        logging.getLogger().addHandler(self.console_handler)
    
    def clear_console(self):
        """Clear the console output."""
        self.console_output.clear()
        logging.info("Console cleared")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Remove the console handler from the root logger
        logging.getLogger().removeHandler(self.console_handler)
        logging.info("Console window closed")
        super().closeEvent(event) 