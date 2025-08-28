# uNETWORK Server Utilities

Utility scripts for server maintenance, validation, and troubleshooting.

## Available Utilities

### 🔍 `validate-config.py`
**Configuration validation and environment checking**

Validates server configuration files and checks system requirements:

```bash
# Run full validation
./validate-config.py
```

**Checks performed:**
- ✅ JSON configuration file syntax
- ✅ Required configuration sections
- ✅ Server settings (host, port)
- ✅ Path validation
- ✅ Python dependency availability
- ✅ Python version compatibility
- ✅ uSCRIPT virtual environment
- ✅ Port availability

**Sample output:**
```
uNETWORK Server Configuration Validator
=============================================
Validating /path/to/config/server-config.example.json...
✅ Valid JSON structure
✅ All required sections present
✅ Server configuration valid (host: 127.0.0.1, port: 8080)
✅ Path valid: ui_path

Checking Python dependencies...
✅ flask
✅ flask_socketio
✅ eventlet
✅ requests

Checking environment...
✅ Python 3.9.6
✅ uSCRIPT virtual environment found
✅ Port 8080 is available

=============================================
✅ All checks passed - server should start successfully
```

## Usage Examples

### Pre-startup Validation
```bash
# Before starting the server, validate everything
cd /Users/agentdigital/uDOS/uNETWORK/server/utils
./validate-config.py

# If all checks pass, start the server
cd ..
./start-server.sh
```

### Troubleshooting Setup Issues
```bash
# Check what's wrong with server setup
./validate-config.py

# Common issues and solutions:
# - Missing Python packages: pip install flask flask-socketio eventlet requests
# - Port in use: Change port in config or stop conflicting service
# - Missing uSCRIPT venv: cd ../../../uSCRIPT && ./setup-environment.sh
```

### Integration with uSCRIPT
```bash
# Use uSCRIPT virtual environment for validation
cd ../../../uSCRIPT
source activate-venv.sh

cd ../uNETWORK/server/utils
./validate-config.py
```

## Development Notes

These utilities help ensure:
- **Configuration integrity** before server startup
- **Dependency verification** for all required packages
- **Environment validation** including Python version and virtual environments
- **Port availability** checking to prevent startup conflicts

Use these tools as part of your development workflow to catch configuration issues early.
