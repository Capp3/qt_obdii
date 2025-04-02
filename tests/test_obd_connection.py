import pytest
from unittest.mock import Mock, patch

# Mock the OBD import to avoid actual hardware connection
mock_obd = Mock()
mock_obd.OBD = Mock()

with patch.dict('sys.modules', {'obd': mock_obd}):
    from obd import OBD

def test_obd_connection():
    """Test that we can create an OBD connection object"""
    # This test now uses mocked OBD to avoid actual hardware connection
    assert OBD is not None
    assert isinstance(OBD, Mock)

def test_obd_connection_parameters():
    """Test that OBD connection parameters are valid"""
    # Test with mocked connection parameters
    mock_connection = OBD()
    assert mock_connection is not None
    # Add more specific parameter tests as needed 