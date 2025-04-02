from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
import asyncio
import logging
from processes.bluetooth_handler import BluetoothHandler

logger = logging.getLogger(__name__)

class BluetoothDialog(QDialog):
    """Dialog for selecting and connecting to Bluetooth devices."""
    
    connection_status_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to ELM327 Adapter")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        self.bluetooth_handler = BluetoothHandler()
        self.devices = []
        
        self._setup_ui()
        self._connect_signals()
        
        # Start scanning for devices
        self.scan_button.click()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Scanning for ELM327 adapters...")
        layout.addWidget(self.status_label)
        
        # Device list
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.device_list)
        
        # Progress bar for scanning
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.scan_button = QPushButton("Scan")
        self.connect_button = QPushButton("Connect")
        self.cancel_button = QPushButton("Cancel")
        
        self.connect_button.setEnabled(False)
        
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.scan_button.clicked.connect(self._scan_for_devices)
        self.connect_button.clicked.connect(self._connect_to_device)
        self.cancel_button.clicked.connect(self.reject)
        self.device_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Set callbacks for the Bluetooth handler
        self.bluetooth_handler.set_connection_callback(self._on_connection_status_changed)
    
    def _on_selection_changed(self):
        """Handle device selection change."""
        self.connect_button.setEnabled(self.device_list.currentItem() is not None)
    
    def _scan_for_devices(self):
        """Scan for Bluetooth devices."""
        self.device_list.clear()
        self.devices = []
        self.status_label.setText("Scanning for ELM327 adapters...")
        self.progress_bar.show()
        self.scan_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        
        # Run the scan in a separate thread
        asyncio.create_task(self._async_scan())
    
    async def _async_scan(self):
        """Asynchronously scan for Bluetooth devices."""
        try:
            # Scan for devices
            self.devices = await self.bluetooth_handler.scan_for_devices()
            
            # Update the UI with the results
            if self.devices:
                for device in self.devices:
                    item = QListWidgetItem(f"{device['name']} ({device['address']}) - Signal: {device['rssi']} dBm")
                    item.setData(Qt.UserRole, device['address'])
                    self.device_list.addItem(item)
                
                self.status_label.setText(f"Found {len(self.devices)} potential ELM327 adapters")
            else:
                self.status_label.setText("No ELM327 adapters found")
            
        except Exception as e:
            logger.error(f"Error scanning for devices: {str(e)}")
            self.status_label.setText(f"Error scanning for devices: {str(e)}")
        
        finally:
            # Update UI state
            self.progress_bar.hide()
            self.scan_button.setEnabled(True)
            self._on_selection_changed()
    
    def _connect_to_device(self):
        """Connect to the selected device."""
        selected_item = self.device_list.currentItem()
        if not selected_item:
            return
        
        device_address = selected_item.data(Qt.UserRole)
        
        self.status_label.setText(f"Connecting to {selected_item.text()}...")
        self.progress_bar.show()
        self.scan_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        
        # Run the connection in a separate thread
        asyncio.create_task(self._async_connect(device_address))
    
    async def _async_connect(self, address):
        """Asynchronously connect to a Bluetooth device."""
        try:
            # Connect to the device
            success = await self.bluetooth_handler.connect_to_device(address)
            
            if success:
                self.status_label.setText("Connected successfully")
                self.connection_status_changed.emit(True)
                self.accept()
            else:
                self.status_label.setText("Failed to connect to device")
                self.connection_status_changed.emit(False)
        
        except Exception as e:
            logger.error(f"Error connecting to device: {str(e)}")
            self.status_label.setText(f"Error connecting to device: {str(e)}")
            self.connection_status_changed.emit(False)
        
        finally:
            # Update UI state
            self.progress_bar.hide()
            self.scan_button.setEnabled(True)
            self._on_selection_changed()
    
    def _on_connection_status_changed(self, connected):
        """Handle connection status changes."""
        self.connection_status_changed.emit(connected)
    
    def get_bluetooth_handler(self):
        """Get the Bluetooth handler instance."""
        return self.bluetooth_handler 