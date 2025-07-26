#!/usr/bin/env python3
"""
Example script demonstrating how to use the Mwareeth GUI.

This script shows how to launch the GUI version of the Mwareeth inheritance calculator.
"""

import sys
import os

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    # Try to import the GUI module
    from mwareeth.gui import MwareethGUI
except ImportError as e:
    print("Error: Could not import GUI dependencies.")
    print("Please install the GUI dependencies with:")
    print("  pip install -e .[gui]")
    print(f"\nOriginal error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Create and run the GUI application
    app = MwareethGUI(language="en")
    app.run()
