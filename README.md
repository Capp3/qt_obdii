# Qt OBDII Interface

[![Tests](https://github.com/capp3/qt_obdii/actions/workflows/tests.yml/badge.svg)](https://github.com/capp3/qt_obdii/actions/workflows/tests.yml)

A modern OBD2 (On-Board Diagnostics) interface application built with Qt and Python, providing a user-friendly way to interact with your vehicle's diagnostic system. This project is based on the [python-OBD](https://github.com/brendan-w/python-OBD) package and enhanced with a Qt-based graphical user interface.

## Features

- Modern Qt-based graphical user interface
- Bluetooth OBD2 adapter support
- Real-time vehicle data monitoring
- Support for standard OBD2 PIDs
- Cross-platform compatibility (Windows, Linux, macOS)

## Prerequisites

- Python 3.8 - 3.11 (Python 3.13 is not currently supported due to dependency issues)
- OBD2 Bluetooth adapter or USB adapter
- Bluetooth capabilities (if using Bluetooth adapter)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/qt_obdii.git
cd qt_obdii
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Bluetooth Setup (Linux)

If you're using a Bluetooth adapter on Linux, install the following requirements:

```bash
sudo apt-get install bluetooth bluez-utils blueman
```

### Using the Run Script

For Unix-based systems (Linux, macOS), you can use the provided `run.sh` script to automatically set up and run the application:

```bash
chmod +x run.sh  # Make the script executable (first time only)
./run.sh
```

The run script will:

- Check for Python 3 installation
- Create a virtual environment if it doesn't exist
- Install all required dependencies
- Activate the virtual environment
- Launch the application

This is the recommended way to run the application as it handles all the setup automatically.

## Usage

1. Connect your OBD2 adapter to your vehicle's OBD2 port
2. If using Bluetooth, pair your adapter with your computer
3. Run the application:

```bash
python src/main.py
```

## Development

For development purposes, install additional development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Project Structure

```
qt_obdii/
├── src/
│   ├── main.py          # Application entry point
│   ├── gui/             # GUI-related modules
│   └── processes/       # Background processes and OBD communication
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── README.md           # This file
```

## Troubleshooting

### Python Version Issues

If you encounter errors related to dataclasses or pint package, ensure you're using Python 3.8 - 3.11. Python 3.13 is not currently supported due to compatibility issues with some dependencies.

To check your Python version:

```bash
python --version
```

If you need to install a different Python version:

- On macOS with Homebrew: `brew install python@3.11`
- On Linux: Use your distribution's package manager
- On Windows: Download from python.org

### Installation Issues

#### Network Timeout Issues

If you encounter timeout errors while installing dependencies, try one of these solutions:

1. Increase the timeout period:

```bash
pip install --default-timeout=100 -r requirements.txt
```

2. Install packages individually:

```bash
pip install pyside6
pip install python-dotenv
pip install obd
pip install bleak>=0.21.0
pip install asyncio>=3.4.3
pip install qasync>=0.24.0
```

3. Use an alternative PyPI mirror:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Common Issues

1. **QApplication Singleton Error**
   - If you see the error "Please destroy the QApplication singleton before creating a new QApplication instance"
   - This typically happens when the application is restarted without properly cleaning up
   - Solution: Close all instances of the application and try again
   - If the issue persists, try running the application with a clean Python environment

2. **Bluetooth Connection Issues**
   - Ensure your Bluetooth adapter is properly paired
   - Check if the adapter is in range
   - Verify Bluetooth services are running

3. **OBD Connection Issues**
   - Ensure the adapter is properly connected to the OBD2 port
   - Check if the vehicle's ignition is on
   - Verify the adapter's power LED is lit

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

## Acknowledgments

- Based on the [python-OBD](https://github.com/brendan-w/python-OBD) package
- Thanks to all contributors who have helped shape this project
