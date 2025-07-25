# Mwareeth

Mwareeth is a knowledge-based system to calculate and divide estate according to Islamic inheritance law (Fiqh al-Mawarith).

## Features

- Build and visualize family trees
- Calculate inheritance shares according to Islamic law
- Support for both command-line interface (CLI) and graphical user interface (GUI)
- Internationalization support (currently English and Arabic)

## Installation

### Basic Installation (CLI only)

```bash
pip install mwareeth
```

### Full Installation (with GUI support)

```bash
pip install mwareeth[gui]
```

## Usage

### Command-Line Interface

```bash
# Launch the interactive CLI
mwareeth

# Specify a language
mwareeth --language ar
```

### Graphical User Interface

```bash
# Launch the GUI
mwareeth --gui

# Specify a language
mwareeth --gui --language ar
```

#### macOS Users

If you encounter Tkinter errors on macOS (e.g., `Can't find a usable init.tcl`), use the provided script:

```bash
# Make the script executable (if needed)
chmod +x ./scripts/run_gui.sh

# Run the GUI with proper Tcl/Tk configuration
./scripts/run_gui.sh
```

This script will:
1. Install Tcl/Tk using Homebrew if needed
2. Configure the environment variables correctly
3. Launch the GUI application

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/mwareeth.git
cd mwareeth

# Install in development mode with GUI dependencies
pip install -e .[gui]
```

### Running Examples

```bash
# Run the CLI example
python examples/build_tree.py

# Run the GUI example
python examples/gui_example.py
```

## Dependencies

- **Core Dependencies**:
  - Python 3.12+
  - Babel (for internationalization)
  - Graphviz (for visualization)

- **GUI Dependencies** (optional):
  - Tkinter (included in standard Python library)
  - Pillow (for advanced image handling)
