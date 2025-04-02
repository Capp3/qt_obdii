import obd
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class OBDMode(Enum):
    """OBD-II modes as per the specification."""
    GLOBAL = 1
    SINCE_RESET = 2
    FAULT_CODES = 3
    CLEAR_FAULTS = 4
    CANBUS = 6
    GENERAL = 9

@dataclass
class OBDResponse:
    """Container for OBD response data."""
    mode: OBDMode
    command: str
    value: Optional[float]
    unit: str
    is_available: bool

class OBDHandler:
    def __init__(self, bluetooth_handler=None):
        self.connection = None
        self.is_connected = False
        self.bluetooth_handler = bluetooth_handler
        self._setup_commands()

    def _setup_commands(self):
        """Initialize OBD commands for different modes."""
        self.commands = {
            OBDMode.GLOBAL: obd.commands[1],
            OBDMode.SINCE_RESET: obd.commands[2],
            OBDMode.CANBUS: obd.commands[6],
            OBDMode.GENERAL: obd.commands[9]
        }

    def set_bluetooth_handler(self, bluetooth_handler):
        """Set the Bluetooth handler for OBD communication."""
        self.bluetooth_handler = bluetooth_handler
        logger.info("Bluetooth handler set for OBD communication")

    def connect(self, port: str = None) -> bool:
        """Connect to the OBD adapter."""
        try:
            if self.bluetooth_handler and self.bluetooth_handler.get_connection_status():
                # Use the Bluetooth handler for communication
                logger.info("Using Bluetooth handler for OBD communication")
                self.is_connected = True
                return True
            
            # Fall back to direct connection if no Bluetooth handler
            if port:
                self.connection = obd.OBD(port)
            else:
                self.connection = obd.OBD()
            
            self.is_connected = self.connection.is_connected()
            if self.is_connected:
                logger.info("Successfully connected to OBD adapter")
            else:
                logger.error("Failed to connect to OBD adapter")
            
            return self.is_connected
        except Exception as e:
            logger.error(f"Error connecting to OBD adapter: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the OBD adapter."""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from OBD adapter")

    async def send_command(self, command: str) -> Optional[str]:
        """Send a command to the OBD adapter and wait for a response."""
        if not self.is_connected:
            logger.error("Not connected to OBD adapter")
            return None
        
        try:
            if self.bluetooth_handler and self.bluetooth_handler.get_connection_status():
                # Use the Bluetooth handler for communication
                return await self.bluetooth_handler.send_command(command)
            elif self.connection:
                # Use the direct connection
                response = self.connection.query(obd.commands[command])
                if response.is_null():
                    return None
                return str(response.value)
            else:
                logger.error("No connection available")
                return None
        except Exception as e:
            logger.error(f"Error sending command to OBD adapter: {str(e)}")
            return None

    def query_vehicle_data(self, mode: OBDMode) -> Dict[str, OBDResponse]:
        """Query vehicle data for a specific mode."""
        if not self.is_connected:
            logger.error("Not connected to OBD adapter")
            return {}

        results = {}
        try:
            for cmd in self.commands[mode]:
                if self.bluetooth_handler and self.bluetooth_handler.get_connection_status():
                    # Use the Bluetooth handler for communication
                    # This is a simplified version - in a real implementation,
                    # you would need to send the command and parse the response
                    results[cmd.name] = OBDResponse(
                        mode=mode,
                        command=cmd.name,
                        value=None,  # Placeholder
                        unit="",     # Placeholder
                        is_available=True
                    )
                elif self.connection:
                    # Use the direct connection
                    response = self.connection.query(cmd)
                    results[cmd.name] = OBDResponse(
                        mode=mode,
                        command=cmd.name,
                        value=response.value.magnitude if response.is_null() is False else None,
                        unit=str(response.unit),
                        is_available=not response.is_null()
                    )
        except Exception as e:
            logger.error(f"Error querying vehicle data: {str(e)}")

        return results

    def query_fault_codes(self) -> List[str]:
        """Query fault codes from the vehicle."""
        if not self.is_connected:
            logger.error("Not connected to OBD adapter")
            return []

        try:
            if self.bluetooth_handler and self.bluetooth_handler.get_connection_status():
                # Use the Bluetooth handler for communication
                # This is a simplified version - in a real implementation,
                # you would need to send the command and parse the response
                return ["P0000", "P0001"]  # Placeholder
            elif self.connection:
                # Use the direct connection
                response = self.connection.query(obd.commands[3])
                if response.is_null():
                    return []
                return response.value
        except Exception as e:
            logger.error(f"Error querying fault codes: {str(e)}")
            return []

    def clear_fault_codes(self) -> bool:
        """Clear fault codes from the vehicle."""
        if not self.is_connected:
            logger.error("Not connected to OBD adapter")
            return False

        try:
            if self.bluetooth_handler and self.bluetooth_handler.get_connection_status():
                # Use the Bluetooth handler for communication
                # This is a simplified version - in a real implementation,
                # you would need to send the command and parse the response
                return True  # Placeholder
            elif self.connection:
                # Use the direct connection
                response = self.connection.query(obd.commands[4])
                success = not response.is_null()
                if success:
                    logger.info("Successfully cleared fault codes")
                else:
                    logger.error("Failed to clear fault codes")
                return success
        except Exception as e:
            logger.error(f"Error clearing fault codes: {str(e)}")
            return False 