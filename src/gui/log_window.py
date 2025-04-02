from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QFileDialog, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
import logging
from pathlib import Path
from datetime import datetime
import glob

class LogWindow(QDialog):
    """Dialog for viewing log files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(800, 600)
        
        # Store the log directory
        self.log_directory = Path(parent.log_directory)
        
        # Setup UI
        self._setup_ui()
        
        # Load log files
        self._load_log_files()
        
        # Log initial message
        logging.info("Log viewer opened")
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Log file selector
        selector_layout = QHBoxLayout()
        
        self.log_selector = QComboBox()
        self.log_selector.currentIndexChanged.connect(self._on_log_selected)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_log_files)
        
        selector_layout.addWidget(QLabel("Log File:"))
        selector_layout.addWidget(self.log_selector)
        selector_layout.addWidget(self.refresh_button)
        
        layout.addLayout(selector_layout)
        
        # Log content
        self.log_content = QTextEdit()
        self.log_content.setReadOnly(True)
        self.log_content.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.log_content)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open in External Editor")
        self.close_button = QPushButton("Close")
        
        button_layout.addWidget(self.open_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.open_button.clicked.connect(self._open_external)
        self.close_button.clicked.connect(self.close)
    
    def _load_log_files(self):
        """Load available log files into the selector."""
        self.log_selector.clear()
        
        # Find all log files in the log directory
        log_files = glob.glob(str(self.log_directory / "obd_diagnostic_*.log"))
        
        # Sort by modification time, newest first
        log_files.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        
        # Add to selector
        for log_file in log_files:
            path = Path(log_file)
            # Show filename and modification time
            timestamp = datetime.fromtimestamp(path.stat().st_mtime)
            display_text = f"{path.name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
            self.log_selector.addItem(display_text, str(path))
        
        # Select the most recent log file if available
        if self.log_selector.count() > 0:
            self.log_selector.setCurrentIndex(0)
    
    def _on_log_selected(self, index):
        """Handle log file selection."""
        if index < 0:
            return
        
        log_path = self.log_selector.currentData()
        if not log_path:
            return
        
        try:
            # Read and display the log file
            with open(log_path, 'r') as f:
                content = f.read()
                self.log_content.setText(content)
                
                # Scroll to the end
                self.log_content.verticalScrollBar().setValue(
                    self.log_content.verticalScrollBar().maximum()
                )
        except Exception as e:
            logging.error(f"Error reading log file: {str(e)}")
            self.log_content.setText(f"Error reading log file: {str(e)}")
    
    def _open_external(self):
        """Open the current log file in the system's default text editor."""
        log_path = self.log_selector.currentData()
        if not log_path:
            return
        
        try:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(log_path))
        except Exception as e:
            logging.error(f"Error opening log file externally: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open log file: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        logging.info("Log viewer closed")
        super().closeEvent(event) 