from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QTextEdit, QMenuBar,
    QStatusBar, QMenu, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
import logging
import asyncio
from pathlib import Path
from datetime import datetime

from gui.bluetooth_dialog import BluetoothDialog
from gui.console_window import ConsoleWindow
from gui.log_window import LogWindow
from processes.obd_handler import OBDHandler, OBDMode

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    # Default log directory is Desktop
    log_directory = str(Path.home() / "Desktop")
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBD-II Diagnostic Tool")
        self.setMinimumSize(800, 600)
        
        # Initialize handlers
        self.obd_handler = OBDHandler()
        self.bluetooth_handler = None
        
        # Initialize UI components
        self._setup_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._create_central_widget()
        
        # Setup tables
        self._setup_tables()
        
        logger.info("Main window initialized")

    def _setup_ui(self):
        """Setup the main UI components."""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

    def _create_menu_bar(self):
        """Create the menu bar with System and View menus."""
        menubar = self.menuBar()
        
        # System menu
        system_menu = menubar.addMenu("System")
        system_menu.addAction("Connect Bluetooth", self.connect_bluetooth)
        system_menu.addAction("Disconnect", self.disconnect_bluetooth)
        system_menu.addSeparator()
        system_menu.addAction("Query Vehicle", self.query_vehicle)
        system_menu.addAction("Query Faults", self.query_faults)
        system_menu.addAction("Clear Fault Codes", self.clear_fault_codes)
        system_menu.addSeparator()
        system_menu.addAction("Set Log Location", self.set_log_location)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Show Console", self.show_console)
        view_menu.addAction("Show Log", self.show_log)

    def _create_status_bar(self):
        """Create the status bar for Bluetooth connection status."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bluetooth: Not Connected")

    def _create_central_widget(self):
        """Create the main content area with buttons and displays."""
        # Create button bar
        button_layout = QHBoxLayout()
        self.query_vehicle_btn = QPushButton("Query Vehicle")
        self.query_faults_btn = QPushButton("Query Faults")
        self.clear_faults_btn = QPushButton("Clear Fault Codes")
        
        button_layout.addWidget(self.query_vehicle_btn)
        button_layout.addWidget(self.query_faults_btn)
        button_layout.addWidget(self.clear_faults_btn)
        
        # Create tab widget for data display
        self.tab_widget = QTabWidget()
        self.global_tab = QTableWidget()
        self.since_reset_tab = QTableWidget()
        self.canbus_tab = QTableWidget()
        self.general_tab = QTableWidget()
        
        self.tab_widget.addTab(self.global_tab, "Global")
        self.tab_widget.addTab(self.since_reset_tab, "Since Reset")
        self.tab_widget.addTab(self.canbus_tab, "CANBUS")
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Create fault display
        self.fault_display = QTextEdit()
        self.fault_display.setFixedHeight(100)
        self.fault_display.setReadOnly(True)
        
        # Add all components to main layout
        self.main_layout.addLayout(button_layout)
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.fault_display)
        
        # Connect button signals
        self.query_vehicle_btn.clicked.connect(self.query_vehicle)
        self.query_faults_btn.clicked.connect(self.query_faults)
        self.clear_faults_btn.clicked.connect(self.clear_fault_codes)
        
        # Disable buttons until connected
        self._update_button_states(False)
    
    def _setup_tables(self):
        """Setup the table widgets for data display."""
        # Setup all tables with the same structure
        for table in [self.global_tab, self.since_reset_tab, self.canbus_tab, self.general_tab]:
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setAlternatingRowColors(True)
    
    def _update_button_states(self, connected):
        """Update button states based on connection status."""
        self.query_vehicle_btn.setEnabled(connected)
        self.query_faults_btn.setEnabled(connected)
        self.clear_faults_btn.setEnabled(connected)
    
    def connect_bluetooth(self):
        """Open the Bluetooth connection dialog."""
        dialog = BluetoothDialog(self)
        dialog.connection_status_changed.connect(self._on_bluetooth_connection_changed)
        
        if dialog.exec():
            self.bluetooth_handler = dialog.get_bluetooth_handler()
            # Pass the Bluetooth handler to the OBD handler
            self.obd_handler.set_bluetooth_handler(self.bluetooth_handler)
            # Connect to the OBD adapter using the Bluetooth handler
            self.obd_handler.connect()
    
    def disconnect_bluetooth(self):
        """Disconnect from the Bluetooth device."""
        if self.bluetooth_handler:
            asyncio.create_task(self._async_disconnect())
    
    async def _async_disconnect(self):
        """Asynchronously disconnect from the Bluetooth device."""
        try:
            await self.bluetooth_handler.disconnect()
            self._on_bluetooth_connection_changed(False)
        except Exception as e:
            logger.error(f"Error disconnecting from Bluetooth device: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to disconnect: {str(e)}")
    
    def _on_bluetooth_connection_changed(self, connected):
        """Handle Bluetooth connection status changes."""
        if connected:
            self.status_bar.showMessage("Bluetooth: Connected")
            self._update_button_states(True)
        else:
            self.status_bar.showMessage("Bluetooth: Not Connected")
            self._update_button_states(False)
            self.bluetooth_handler = None

    def query_vehicle(self):
        """Handle vehicle query button click."""
        logger.info("Query vehicle button clicked")
        if not self.bluetooth_handler or not self.bluetooth_handler.get_connection_status():
            QMessageBox.warning(self, "Not Connected", "Please connect to an ELM327 adapter first.")
            return
        
        # Query data for each mode
        asyncio.create_task(self._async_query_vehicle_data(OBDMode.GLOBAL, self.global_tab))
        asyncio.create_task(self._async_query_vehicle_data(OBDMode.SINCE_RESET, self.since_reset_tab))
        asyncio.create_task(self._async_query_vehicle_data(OBDMode.CANBUS, self.canbus_tab))
        asyncio.create_task(self._async_query_vehicle_data(OBDMode.GENERAL, self.general_tab))

    async def _async_query_vehicle_data(self, mode, table):
        """Asynchronously query vehicle data for a specific mode."""
        try:
            # Clear the table
            table.setRowCount(0)
            
            # Query the data
            results = self.obd_handler.query_vehicle_data(mode)
            
            # Update the table
            for i, (name, response) in enumerate(results.items()):
                table.insertRow(i)
                
                # Parameter name
                name_item = QTableWidgetItem(name)
                table.setItem(i, 0, name_item)
                
                # Value
                value = str(response.value) if response.value is not None else "N/A"
                value_item = QTableWidgetItem(value)
                if not response.is_available:
                    value_item.setForeground(Qt.gray)
                table.setItem(i, 1, value_item)
                
                # Unit
                unit_item = QTableWidgetItem(response.unit)
                table.setItem(i, 2, unit_item)
            
            # Resize columns to content
            table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error querying vehicle data for mode {mode}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to query vehicle data: {str(e)}")

    def query_faults(self):
        """Handle fault query button click."""
        logger.info("Query faults button clicked")
        if not self.bluetooth_handler or not self.bluetooth_handler.get_connection_status():
            QMessageBox.warning(self, "Not Connected", "Please connect to an ELM327 adapter first.")
            return
        
        # Query fault codes
        asyncio.create_task(self._async_query_faults())

    async def _async_query_faults(self):
        """Asynchronously query fault codes."""
        try:
            # Query the fault codes
            fault_codes = self.obd_handler.query_fault_codes()
            
            # Update the fault display
            if fault_codes:
                self.fault_display.setText("\n".join(fault_codes))
            else:
                self.fault_display.setText("No fault codes found.")
            
        except Exception as e:
            logger.error(f"Error querying fault codes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to query fault codes: {str(e)}")

    def clear_fault_codes(self):
        """Handle clear fault codes button click."""
        logger.info("Clear fault codes button clicked")
        if not self.bluetooth_handler or not self.bluetooth_handler.get_connection_status():
            QMessageBox.warning(self, "Not Connected", "Please connect to an ELM327 adapter first.")
            return
        
        # Confirm with the user
        reply = QMessageBox.question(
            self, 
            "Clear Fault Codes", 
            "Are you sure you want to clear all fault codes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear fault codes
            asyncio.create_task(self._async_clear_fault_codes())

    async def _async_clear_fault_codes(self):
        """Asynchronously clear fault codes."""
        try:
            # Clear the fault codes
            success = self.obd_handler.clear_fault_codes()
            
            if success:
                # Wait 5 seconds and then query faults again
                await asyncio.sleep(5)
                await self._async_query_faults()
            else:
                QMessageBox.warning(self, "Error", "Failed to clear fault codes.")
            
        except Exception as e:
            logger.error(f"Error clearing fault codes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear fault codes: {str(e)}")

    def set_log_location(self):
        """Handle set log location menu action."""
        logger.info("Set log location menu item clicked")
        # Open a file dialog to select the log directory
        log_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Log Directory",
            MainWindow.log_directory
        )
        
        if log_dir:
            try:
                # Update the log directory
                MainWindow.log_directory = log_dir
                
                # Create the directory if it doesn't exist
                Path(log_dir).mkdir(parents=True, exist_ok=True)
                
                # Update the logging configuration
                self._update_logging_config()
                
                logger.info(f"Log directory set to: {log_dir}")
                QMessageBox.information(self, "Success", f"Log directory set to: {log_dir}")
            except Exception as e:
                logger.error(f"Error setting log directory: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to set log directory: {str(e)}")
    
    def _update_logging_config(self):
        """Update the logging configuration with the new log directory."""
        # Remove existing file handlers
        for handler in logger.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.root.removeHandler(handler)
        
        # Create new log file in the selected directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(MainWindow.log_directory) / f"obd_diagnostic_{timestamp}.log"
        
        # Add new file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.root.addHandler(file_handler)

    def show_console(self):
        """Handle show console menu action."""
        logger.info("Show console menu item clicked")
        # Create and show the console window
        console_window = ConsoleWindow(self)
        console_window.show()

    def show_log(self):
        """Handle show log menu action."""
        logger.info("Show log menu item clicked")
        # Create and show the log window
        log_window = LogWindow(self)
        log_window.show() 