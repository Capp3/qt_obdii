#!/usr/bin/env python3
import sys
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui.main_window import MainWindow
import qasync

def setup_logging():
    """Configure logging to both console and file."""
    # Create log directory if it doesn't exist
    log_dir = Path(MainWindow.log_directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"obd_diagnostic_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting OBD Diagnostic Tool")
    
    # Create Qt application
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Run the application
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
