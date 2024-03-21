#!/bin/bash

# Define variables
PROJECT_DIR="/home/pi/house"
VENV_NAME="house_env"
DESKTOP_ENTRY="house.desktop"
DESKTOP_PATH="/home/pi/Desktop"

# Remove virtual environment
echo "Removing virtual environment..."
rm -rf "$PROJECT_DIR/$VENV_NAME"

# Remove launcher script
echo "Removing launcher script..."
rm -f "$PROJECT_DIR/launch_house.sh"

# Remove desktop entry
echo "Removing desktop entry..."
rm -f "$DESKTOP_PATH/$DESKTOP_ENTRY"

echo "Uninstallation complete."
