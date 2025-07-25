import argparse
import sys
import os
import platform
import subprocess
from mwareeth.family_tree_builder import FamilyTreeBuilder

def setup_macos_tkinter():
    """
    Set up the environment variables for Tkinter on macOS.
    
    This function checks if the system is macOS and if Homebrew and Tcl/Tk are available.
    If they are, it sets up the environment variables needed for Tkinter to work.
    
    Returns:
        bool: True if the setup was successful, False otherwise.
    """
    # Check if the system is macOS
    if platform.system() != "Darwin":
        return True
    
    # Check if Homebrew is installed
    try:
        subprocess.run(["brew", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: Homebrew is not installed. Tkinter might not work correctly.")
        print("If you encounter Tkinter errors, install Homebrew and run the run_gui.sh script.")
        return False
    
    # Check if Tcl/Tk is installed
    try:
        result = subprocess.run(["brew", "list", "tcl-tk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("Warning: Tcl/Tk is not installed with Homebrew.")
            print("If you encounter Tkinter errors, run the run_gui.sh script.")
            return False
    except subprocess.SubprocessError:
        print("Warning: Could not check if Tcl/Tk is installed.")
        print("If you encounter Tkinter errors, run the run_gui.sh script.")
        return False
    
    # Get the Tcl/Tk installation path
    try:
        result = subprocess.run(["brew", "--prefix", "tcl-tk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        tcl_tk_path = result.stdout.decode('utf-8').strip()
    except subprocess.SubprocessError:
        print("Warning: Could not get Tcl/Tk installation path.")
        print("If you encounter Tkinter errors, run the run_gui.sh script.")
        return False
    
    # Set up environment variables
    os.environ["PATH"] = f"{tcl_tk_path}/bin:{os.environ.get('PATH', '')}"
    os.environ["LDFLAGS"] = f"-L{tcl_tk_path}/lib"
    os.environ["CPPFLAGS"] = f"-I{tcl_tk_path}/include"
    os.environ["PKG_CONFIG_PATH"] = f"{tcl_tk_path}/lib/pkgconfig"
    os.environ["PYTHON_CONFIGURE_OPTS"] = f"--with-tcltk-includes='-I{tcl_tk_path}/include' --with-tcltk-libs='-L{tcl_tk_path}/lib -ltcl8.6 -ltk8.6'"
    
    return True


def main():
    """
    Main entry point for the mwareeth application.
    
    This function parses command-line arguments and launches either the CLI or GUI version
    of the application, depending on the arguments provided.
    """
    parser = argparse.ArgumentParser(description="Mwareeth - Islamic Inheritance Calculator")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI version")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    args = parser.parse_args()
    
    if args.gui:
        # Set up Tkinter environment variables on macOS
        setup_macos_tkinter()
        
        try:
            # Import the GUI module
            from mwareeth.gui import MwareethGUI
            
            # Launch the GUI
            app = MwareethGUI(language=args.language)
            app.run()
        except ImportError as e:
            print("Error: Could not import GUI dependencies.")
            print("Please install the GUI dependencies with:")
            print("  pip install mwareeth[gui]")
            print(f"\nOriginal error: {e}")
            sys.exit(1)
        except Exception as e:
            if platform.system() == "Darwin" and "tcl" in str(e).lower():
                print("Error: Tkinter could not initialize properly on macOS.")
                print("Please try running the GUI with the run_gui.sh script:")
                print("  ./run_gui.sh")
                print(f"\nOriginal error: {e}")
            else:
                print(f"Error: {e}")
            sys.exit(1)
    else:
        # Launch the CLI version
        builder = FamilyTreeBuilder(language=args.language)
        tree = builder.interactive_build()
        print(tree.visualize())


if __name__ == "__main__":
    main()
