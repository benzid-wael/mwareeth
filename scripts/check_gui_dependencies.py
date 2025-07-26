#!/usr/bin/env python3
"""
Script to check if all the necessary dependencies for the Mwareeth GUI are installed.
"""

import sys
import importlib.util
import os


def check_module(module_name):
    """Check if a module is installed."""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {module_name} is NOT installed")
        return False
    else:
        print(f"✅ {module_name} is installed")
        return True


def main():
    """Check all the necessary dependencies for the Mwareeth GUI."""
    print("Checking dependencies for Mwareeth GUI...")

    # Check Python version
    print(f"\nPython version: {sys.version}")

    # Check core dependencies
    print("\nChecking core dependencies:")
    core_deps = ["tkinter", "json", "tempfile", "babel"]
    core_installed = all(check_module(dep) for dep in core_deps)

    # Check optional dependencies
    print("\nChecking optional dependencies:")
    optional_deps = ["graphviz", "PIL"]
    optional_installed = all(check_module(dep) for dep in optional_deps)

    # Check mwareeth modules
    print("\nChecking mwareeth modules:")
    try:
        import mwareeth

        print("✅ mwareeth is installed")

        # Check if the GUI module is available
        try:
            from mwareeth.gui import MwareethGUI

            print("✅ mwareeth.gui is available")
            gui_available = True
        except ImportError as e:
            print(f"❌ mwareeth.gui is NOT available: {e}")
            gui_available = False

        # Check if the entities module is available
        try:
            from mwareeth.entities.person import Gender, Religion
            from mwareeth.entities.family_tree import FamilyTree, RelationshipType

            print("✅ mwareeth.entities is available")
            entities_available = True
        except ImportError as e:
            print(f"❌ mwareeth.entities is NOT available: {e}")
            entities_available = False

        # Check if the i18n module is available
        try:
            from mwareeth.i18n import _, set_language

            print("✅ mwareeth.i18n is available")
            i18n_available = True
        except ImportError as e:
            print(f"❌ mwareeth.i18n is NOT available: {e}")
            i18n_available = False

        mwareeth_installed = gui_available and entities_available and i18n_available
    except ImportError as e:
        print(f"❌ mwareeth is NOT installed: {e}")
        mwareeth_installed = False

    # Print summary
    print("\nSummary:")
    if core_installed:
        print("✅ All core dependencies are installed")
    else:
        print("❌ Some core dependencies are missing")

    if optional_installed:
        print("✅ All optional dependencies are installed")
    else:
        print("⚠️ Some optional dependencies are missing (the GUI will still work, but with limited functionality)")

    if mwareeth_installed:
        print("✅ All mwareeth modules are available")
    else:
        print("❌ Some mwareeth modules are missing")

    # Print recommendations
    print("\nRecommendations:")
    if not core_installed or not mwareeth_installed:
        print("1. Install the mwareeth package with GUI dependencies:")
        print("   pip install -e .[gui]")
    elif not optional_installed:
        print("1. Install the optional dependencies for better functionality:")
        print("   pip install graphviz pillow")
    else:
        print("All dependencies are installed correctly!")
        print("If you're still having issues, please check the error message and report it to the developers.")


if __name__ == "__main__":
    main()
