#!/usr/bin/env python3
"""
Script to check if all the necessary dependencies for the Mwareeth GUI are installed.
"""

import sys
import importlib.util


def check_module(module_name, fail_if_missing=False):
    """Check if a module is installed."""
    spec = importlib.util.find_spec(module_name)

    if not spec and fail_if_missing:
        raise ImportError(f"Module {module_name} is not installed")

    if spec:
        print(f"✅ {module_name} is installed")
        return True
    print(f"❌ {module_name} is NOT installed")
    return False


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
        check_module("mwareeth", fail_if_missing=True)
        check_module("mwareeth.gui", fail_if_missing=True)
        check_module("mwareeth.gui", fail_if_missing=True)
        check_module("mwareeth.entities.person", fail_if_missing=True)
        check_module("mwareeth.entities.family_tree", fail_if_missing=True)
        check_module("mwareeth.i18n", fail_if_missing=True)

        mwareeth_installed = True
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
        print(
            "⚠️ Some optional dependencies are missing (the GUI will still work, but with limited functionality)"
        )

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
        print(
            "If you're still having issues, please check the error message and report it to the developers."
        )


if __name__ == "__main__":
    main()
