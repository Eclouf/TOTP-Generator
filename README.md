# TOTP Generator GUI

A modern graphical user interface for generating TOTP (Time-based One-Time Password) codes according to RFC 6238.

## Features

- TOTP code generation with multiple hash algorithms
- Support for standard TOTP URIs (otpauth://)
- Modern and intuitive user interface using Toga
- Automatic code updates
- Progress bar to visualize remaining time
- Quick clipboard copy
- Cross-platform support (Windows, Linux, macOS)

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installing Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

```bash
python -m src.app
```

### Input Formats

The application accepts two types of inputs:

1. Base32 Secret Key (e.g., JBSWY3DPEHPK3PXP)
2. Complete TOTP URI:
```
otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example&algorithm=SHA1&digits=6&period=30
```

### Configurable Parameters

- **Secret**: Base32 secret key
- **Period**: Refresh interval (in seconds, default: 30)
- **Digits**: Code length (6-8 digits)
- **Algorithm**: Multiple supported hash algorithms including:
  - SHA1 (default)
  - SHA256
  - SHA512
  - And more...

### Using the Interface

1. **Enter Secret**:
   - Type or paste your Base32 secret key
   - Or paste a complete TOTP URI

2. **Configure Parameters**:
   - Adjust the period if needed (default: 30 seconds)
   - Select number of digits (6-8)
   - Choose hash algorithm

3. **Generate Code**:
   - Click "Generate" button
   - Code will auto-update based on period
   - Progress bar shows time until next update

4. **Copy Code**:
   - Click "Copy" button to copy code to clipboard
   - A confirmation message will appear briefly

## Project Structure

```
totp-gui/
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── totp.py
│   └── views/
│       ├── __init__.py
│       └── main_window.py
├── resources/
│   └── TOTP.png
├── requirements.txt
└── README.md
```

## Dependencies

- **toga**: Cross-platform GUI framework
- **pyperclip**: Clipboard management
- **cryptography**: Cryptographic functions

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies
3. Create a branch for your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Security Considerations

- Minimum 6 digits recommended for TOTP codes
- Store secret keys securely
- Use secure hash algorithms (SHA1 minimum)