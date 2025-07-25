#!/bin/bash
# Script to run the Mwareeth GUI on macOS with proper Tcl/Tk configuration

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Please install it first:"
    echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Check if tcl-tk is installed
if ! brew list tcl-tk &> /dev/null; then
    echo "Installing tcl-tk with Homebrew..."
    brew install tcl-tk
fi

# Get the tcl-tk installation path
TCL_TK_PATH=$(brew --prefix tcl-tk)
echo "Found Tcl/Tk at: $TCL_TK_PATH"

# Set up environment variables
export PATH="$TCL_TK_PATH/bin:$PATH"
export LDFLAGS="-L$TCL_TK_PATH/lib"
export CPPFLAGS="-I$TCL_TK_PATH/include"
export PKG_CONFIG_PATH="$TCL_TK_PATH/lib/pkgconfig"
export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$TCL_TK_PATH/include' --with-tcltk-libs='-L$TCL_TK_PATH/lib -ltcl8.6 -ltk8.6'"

# Check if the mwareeth package is installed with GUI dependencies
echo "Checking if mwareeth is installed with GUI dependencies..."
python3 -c "import mwareeth.gui" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing mwareeth with GUI dependencies..."
    pip install -e .[gui]
fi

# Run the GUI
echo "Starting Mwareeth GUI..."
python3 main.py --gui

# If there's an error, try running the example script
if [ $? -ne 0 ]; then
    echo "Failed to start GUI with main.py. Trying the example script..."
    python3 examples/gui_example.py
fi
