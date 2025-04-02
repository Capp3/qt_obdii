import asyncio
import logging
from typing import List, Optional, Callable
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

logger = logging.getLogger(__name__)

class BluetoothHandler:
    """Handles Bluetooth communication with ELM327 adapter."""
    
    # Common ELM327 service UUIDs
    ELM327_SERVICE_UUID = "0000FFE0-0000-1000-8000-00805F9B34FB"
    ELM327_CHARACTERISTIC_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"
    
    def __init__(self):
        self.client = None
        self.device = None
        self.is_connected = False
        self.connection_callback = None
        self.disconnection_callback = None
    
    def set_connection_callback(self, callback: Callable[[bool], None]):
        """Set a callback function to be called when connection status changes."""
        self.connection_callback = callback
    
    def set_disconnection_callback(self, callback: Callable[[], None]):
        """Set a callback function to be called when disconnected."""
        self.disconnection_callback = callback
    
    async def scan_for_devices(self) -> List[dict]:
        """Scan for available Bluetooth devices."""
        logger.info("Scanning for Bluetooth devices...")
        devices = []
        try:
            scanner = BleakScanner()
            discovered_devices = await scanner.discover()
            
            for device in discovered_devices:
                # Filter for devices that might be ELM327 adapters
                # ELM327 adapters often have "OBD" or "ELM" in their names
                if device.name and ("OBD" in device.name or "ELM" in device.name):
                    devices.append({
                        "name": device.name,
                        "address": device.address,
                        "rssi": device.rssi
                    })
                    logger.info(f"Found potential ELM327 device: {device.name} ({device.address})")
        except Exception as e:
            logger.error(f"Error scanning for Bluetooth devices: {str(e)}")
        
        return devices
    
    async def connect_to_device(self, address: str) -> bool:
        """Connect to an ELM327 adapter by its address."""
        if self.is_connected:
            logger.warning("Already connected to a device")
            return True
        
        try:
            logger.info(f"Connecting to device at {address}...")
            self.client = BleakClient(address)
            await self.client.connect()
            
            # Verify this is an ELM327 adapter
            services = await self.client.get_services()
            elm327_service = None
            
            for service in services:
                if service.uuid.lower() == self.ELM327_SERVICE_UUID.lower():
                    elm327_service = service
                    break
            
            if not elm327_service:
                logger.error("Connected device does not appear to be an ELM327 adapter")
                await self.disconnect()
                return False
            
            # Find the characteristic for sending commands
            characteristic = None
            for char in elm327_service.characteristics:
                if char.uuid.lower() == self.ELM327_CHARACTERISTIC_UUID.lower():
                    characteristic = char
                    break
            
            if not characteristic:
                logger.error("Could not find ELM327 characteristic")
                await self.disconnect()
                return False
            
            # Store the characteristic for later use
            self.characteristic = characteristic
            
            # Set up notification handler for responses
            await self.client.start_notify(
                characteristic.uuid, 
                self._notification_handler
            )
            
            # Test the connection with a simple command
            await self.send_command("ATZ")
            
            self.is_connected = True
            logger.info("Successfully connected to ELM327 adapter")
            
            if self.connection_callback:
                self.connection_callback(True)
            
            return True
            
        except BleakError as e:
            logger.error(f"Bluetooth error connecting to device: {str(e)}")
            if self.connection_callback:
                self.connection_callback(False)
            return False
        except Exception as e:
            logger.error(f"Error connecting to device: {str(e)}")
            if self.connection_callback:
                self.connection_callback(False)
            return False
    
    async def disconnect(self):
        """Disconnect from the ELM327 adapter."""
        if not self.is_connected or not self.client:
            return
        
        try:
            logger.info("Disconnecting from ELM327 adapter...")
            await self.client.disconnect()
            self.is_connected = False
            self.client = None
            self.characteristic = None
            
            if self.disconnection_callback:
                self.disconnection_callback()
                
            logger.info("Disconnected from ELM327 adapter")
        except Exception as e:
            logger.error(f"Error disconnecting from device: {str(e)}")
    
    async def send_command(self, command: str) -> Optional[str]:
        """Send a command to the ELM327 adapter and wait for a response."""
        if not self.is_connected or not self.client or not self.characteristic:
            logger.error("Not connected to ELM327 adapter")
            return None
        
        try:
            # Add carriage return to command
            command_with_cr = command + "\r"
            
            # Send the command
            await self.client.write_gatt_char(
                self.characteristic.uuid,
                command_with_cr.encode()
            )
            
            # Wait for response (implemented in notification handler)
            # This is a simplified version - in a real implementation,
            # you would need to match responses to commands
            await asyncio.sleep(0.1)  # Give some time for the response
            
            return "OK"  # Placeholder - actual response would come from notification handler
            
        except Exception as e:
            logger.error(f"Error sending command to ELM327: {str(e)}")
            return None
    
    def _notification_handler(self, sender, data):
        """Handle notifications from the ELM327 adapter."""
        try:
            # Decode the response
            response = data.decode('utf-8').strip()
            logger.debug(f"Received from ELM327: {response}")
            
            # In a real implementation, you would need to match this response
            # to the command that was sent
            
        except Exception as e:
            logger.error(f"Error handling notification from ELM327: {str(e)}")
    
    def get_connection_status(self) -> bool:
        """Get the current connection status."""
        return self.is_connected 