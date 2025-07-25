import argparse
import sys
import os
import platform
import subprocess
import importlib.util
from mwareeth.family_tree_builder import FamilyTreeBuilder

def check_and_install_package(package_name, extras=None):
    """
    Check if a package is installed and install it if it's not.
    
    Args:
        package_name (str): The name of the package to check and install.
        extras (str, optional): Any extras to install with the package.
    
    Returns:
        bool: True if the package is installed or was successfully installed, False otherwise.
    """
    try:
        # Try to import the package
        importlib.import_module(package_name)
        return True
    except ImportError:
        # If the package is not installed, try to install it
        try:
            print(f"Installing {package_name}...")
            if extras:
                cmd = [sys.executable, "-m", "pip", "install", f"{package_name}[{extras}]"]
            else:
                cmd = [sys.executable, "-m", "pip", "install", package_name]
            
            subprocess.run(cmd, check=True)
            return True
        except subprocess.SubprocessError:
            print(f"Error: Could not install {package_name}.")
            return False

def setup_macos_tkinter():
    """
    Set up the environment variables for Tkinter on macOS.
    
    This function checks if the system is macOS and if Homebrew and Tcl/Tk are available.
    If they are, it sets up the environment variables needed for Tkinter to work.
    If Homebrew or Tcl/Tk are not installed, it attempts to install them.
    
    Returns:
        bool: True if the setup was successful, False otherwise.
    """
    # Check if the system is macOS
    if platform.system() != "Darwin":
        return True
    
    print("Setting up Tkinter for macOS...")
    
    # Check if Homebrew is installed
    try:
        subprocess.run(["brew", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("Homebrew is installed.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Homebrew is not installed. Attempting to install...")
        try:
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            print(f"Running: {install_cmd}")
            print("This may take a while and might require your password.")
            print("If this fails, please install Homebrew manually and try again.")
            print("Visit https://brew.sh for installation instructions.")
            
            # We can't directly install Homebrew here as it requires user interaction
            # Just provide instructions
            print("\nPlease install Homebrew manually and run this script again.")
            print("After installing Homebrew, you may need to run:")
            print("  brew install tcl-tk")
            return False
        except Exception as e:
            print(f"Error attempting to install Homebrew: {e}")
            return False
    
    # Check if Tcl/Tk is installed
    try:
        result = subprocess.run(["brew", "list", "tcl-tk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("Tcl/Tk is not installed with Homebrew. Attempting to install...")
            try:
                subprocess.run(["brew", "install", "tcl-tk"], check=True)
                print("Successfully installed Tcl/Tk.")
            except subprocess.SubprocessError as e:
                print(f"Error installing Tcl/Tk: {e}")
                print("Please install Tcl/Tk manually with:")
                print("  brew install tcl-tk")
                return False
        else:
            print("Tcl/Tk is installed.")
    except subprocess.SubprocessError:
        print("Could not check if Tcl/Tk is installed.")
        return False
    
    # Get the Tcl/Tk installation path
    try:
        result = subprocess.run(["brew", "--prefix", "tcl-tk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        tcl_tk_path = result.stdout.decode('utf-8').strip()
        print(f"Found Tcl/Tk at: {tcl_tk_path}")
    except subprocess.SubprocessError:
        print("Could not get Tcl/Tk installation path.")
        return False
    
    # Set up environment variables
    os.environ["PATH"] = f"{tcl_tk_path}/bin:{os.environ.get('PATH', '')}"
    os.environ["LDFLAGS"] = f"-L{tcl_tk_path}/lib"
    os.environ["CPPFLAGS"] = f"-I{tcl_tk_path}/include"
    os.environ["PKG_CONFIG_PATH"] = f"{tcl_tk_path}/lib/pkgconfig"
    os.environ["PYTHON_CONFIGURE_OPTS"] = f"--with-tcltk-includes='-I{tcl_tk_path}/include' --with-tcltk-libs='-L{tcl_tk_path}/lib -ltcl8.6 -ltk8.6'"
    
    print("Environment variables set up for Tcl/Tk.")
    return True


def run_gui_example():
    """
    Run the GUI example script as a fallback.
    
    Returns:
        bool: True if the example script ran successfully, False otherwise.
    """
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "gui_example.py")
    if os.path.exists(example_path):
        try:
            print("Trying to run the GUI example script...")
            subprocess.run([sys.executable, example_path], check=True)
            return True
        except subprocess.SubprocessError:
            print("Failed to run the GUI example script.")
            return False
    else:
        print(f"Could not find the GUI example script at {example_path}")
        return False

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
        # Check and install GUI dependencies if needed
        if not check_and_install_package("mwareeth", "gui"):
            print("Failed to install GUI dependencies.")
            print("Please install them manually with:")
            print("  pip install mwareeth[gui]")
            sys.exit(1)
        
        # Set up Tkinter environment variables on macOS
        if not setup_macos_tkinter():
            print("Failed to set up Tkinter environment for macOS.")
            print("You can try running the GUI with the run_gui.sh script:")
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "run_gui.sh")
            if os.path.exists(script_path):
                print(f"  {script_path}")
            else:
                print("  scripts/run_gui.sh")
            sys.exit(1)
        
        try:
            # Import the GUI module
            from mwareeth.gui import MwareethGUI
            
            # Launch the GUI
            print("Starting Mwareeth GUI...")
            app = MwareethGUI(language=args.language)
            app.run()
        except ImportError as e:
            print(f"Error: Could not import GUI dependencies: {e}")
            print("Please install the GUI dependencies with:")
            print("  pip install mwareeth[gui]")
            
            # Try running the example script as a fallback
            if not run_gui_example():
                sys.exit(1)
        except Exception as e:
            print(f"Error starting GUI: {e}")
            
            if platform.system() == "Darwin" and "tcl" in str(e).lower():
                print("Tkinter could not initialize properly on macOS.")
                print("You can try running the GUI with the run_gui.sh script:")
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "run_gui.sh")
                if os.path.exists(script_path):
                    print(f"  {script_path}")
                else:
                    print("  scripts/run_gui.sh")
            
            # Try running the example script as a fallback
            if not run_gui_example():
                sys.exit(1)
    else:
        # Launch the CLI version
        builder = FamilyTreeBuilder(language=args.language)
        tree = builder.interactive_build()
        print(tree.visualize())


if __name__ == "__main__":
    main()
