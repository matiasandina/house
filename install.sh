#!/bin/bash

# Define variables
PROJECT_DIR="/home/pi/house"
SCRIPT_NAME="house.py"
VENV_NAME="house_env"
DESKTOP_ENTRY="house.desktop"
DESKTOP_PATH="/home/pi/Desktop"
REQUIREMENTS_FILE="$PROJECT_DIR/house_requirements.txt"

# Ensure python3-venv and python3-pip are installed
echo "Checking for python3-venv and python3-pip..."
if ! dpkg -l | grep -qw python3-venv; then
    echo "python3-venv not found. Installing..."
    sudo apt-get update && sudo apt-get install -y python3-venv
fi

if ! dpkg -l | grep -qw python3-pip; then
    echo "python3-pip not found. Installing..."
    sudo apt-get install -y python3-pip
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv "$PROJECT_DIR/$VENV_NAME"
source "$PROJECT_DIR/$VENV_NAME/bin/activate"

# Ensure wheel is installed before other dependencies
echo "Ensuring wheel is installed..."
pip3 install wheel

# Install dependencies within the virtual environment from requirements file
echo "Installing dependencies from $REQUIREMENTS_FILE..."
pip3 install -r "$REQUIREMENTS_FILE"

# Create launcher script
echo "Creating launcher script..."
cat <<EOF > "$PROJECT_DIR/launch_house.sh"
#!/bin/bash

# Define the project directory
PROJECT_DIR="$PROJECT_DIR"

# Change to the project directory
cd "\$PROJECT_DIR" || exit

# Activate virtual environment
source "\$PROJECT_DIR/$VENV_NAME/bin/activate" || exit

# Run the Python script with an identifier and elevated privileges
exec -a House sudo python3 "\$PROJECT_DIR/$SCRIPT_NAME"
EOF

# Run the Python script with an identifier and elevated privileges
exec -a House sudo python3 '\$PROJECT_DIR/$SCRIPT_NAME'
" > "$PROJECT_DIR/launch_house.sh"

chmod +x "$PROJECT_DIR/launch_house.sh"


# Copy the desktop entry to the desktop
echo "Setting up desktop entry..."
cp "$PROJECT_DIR/$DESKTOP_ENTRY" "$DESKTOP_PATH/$DESKTOP_ENTRY"

# Make sure the Exec line in the desktop entry points to the launcher script
#sed -i "s|Exec=.*|Exec=$PROJECT_DIR/launch_house.sh|" "$DESKTOP_PATH/$DESKTOP_ENTRY"

echo "Installation complete. You can run the application from the desktop icon or by executing ./launch_house.sh in the terminal."

# Deactivate the virtual environment
deactivate

