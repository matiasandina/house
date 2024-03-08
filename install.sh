#!/bin/bash

PROJECT_DIR="/home/pi/house"
SCRIPT_NAME="house.py"
VENV_NAME="house_env"
DESKTOP_ENTRY="house.desktop"

# Create and activate virtual environment
python3 -m venv "$PROJECT_DIR/$VENV_NAME"
source "$PROJECT_DIR/$VENV_NAME/bin/activate"

# Install dependencies within the virtual environment
pip install adafruit-circuitpython-bh1750==1.1.0 adafruit-circuitpython-busdevice==5.1.8 adafruit-circuitpython-HTU21D==0.11.4 adafruit-circuitpython-register==1.9.8 adafruit-circuitpython-typing==1.7.0 RPi.GPIO==0.7.0

# Create launcher script that activates venv, and runs the app
echo "#!/bin/bash
# Activate virtual environment
source '$PROJECT_DIR/$VENV_NAME/bin/activate'

# Run the Python script with elevated privileges
sudo python '$PROJECT_DIR/$SCRIPT_NAME'

# No need to deactivate virtual environment here; script execution ends" > "$PROJECT_DIR/launch_house.sh"

chmod +x "$PROJECT_DIR/launch_house.sh"

# Copy the desktop entry to the desktop
DESKTOP_PATH="/home/pi/Desktop"
cp "$PROJECT_DIR/$DESKTOP_ENTRY" "$DESKTOP_PATH/$DESKTOP_ENTRY"

# Make sure the Exec line in the desktop entry points to the launcher script
sed -i "s|Exec=.*|Exec=$PROJECT_DIR/launch_house.sh|" "$DESKTOP_PATH/$DESKTOP_ENTRY"

# Optionally, update the Icon line if your path is different
# sed -i "s|Icon=.*|Icon=$PROJECT_DIR/img/house_logo.png|" "$DESKTOP_PATH/$DESKTOP_ENTRY"

# Inform the user that the installation is complete
echo "Installation complete. You can run the application from the desktop icon or executing ./launch_house.sh in the terminal."

# Deactivate the virtual environment
deactivate
