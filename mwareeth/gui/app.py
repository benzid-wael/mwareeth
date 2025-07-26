"""
Main GUI application for the mwareeth inheritance calculator.
"""

import json
import os
import platform
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from ..family_tree_builder import FamilyTreeBuilder
from ..i18n import _, set_language
from .forms import PersonForm, RelationshipForm


class MwareethGUI:
    """
    Main GUI application for the mwareeth inheritance calculator.

    This class provides a graphical user interface for building and visualizing
    family trees and calculating inheritance according to Islamic law.
    """

    def __init__(self, language: str = "en"):
        """
        Initialize the GUI application.

        Args:
            language: The language code to use for translations (default: "en")
        """
        self.builder = FamilyTreeBuilder(language=language)
        self.current_file = None

        # Create the main window
        self.root = tk.Tk()
        self.root.title(_("Mwareeth - Islamic Inheritance Calculator"))
        self.root.geometry("1000x700")

        # Load icons
        self.load_icons()

        # Set application icon
        if hasattr(self, "app_icon"):
            self.root.iconphoto(True, self.app_icon)

        # Set up the main menu
        self.setup_menu()

        # Set up the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.setup_family_tab()
        self.setup_visualization_tab()
        self.setup_inheritance_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(_("Ready"))
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_icons(self):
        """Load icons for the application."""
        # Get the path to the icons directory
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = current_dir / "assets" / "icons"

        # Check if the icons directory exists
        if not icons_dir.exists():
            print("Icons directory not found. Icons will not be loaded.")
            return

        try:
            # Load main application icon
            app_icon_path = icons_dir / "app_icon_64.png"
            if app_icon_path.exists():
                self.app_icon = tk.PhotoImage(file=str(app_icon_path))

            # Load function-specific icons
            icon_files = {
                "add_person": "add_person.png",
                "add_relationship": "add_relationship.png",
                "calculate_inheritance": "calculate_inheritance.png",
                "visualize_tree": "visualize_tree.png",
                "save_load": "save_load.png",
                "male": "male.png",
                "female": "female.png",
                "deceased": "deceased.png",
            }

            self.icons = {}
            for icon_name, file_name in icon_files.items():
                icon_path = icons_dir / file_name
                if icon_path.exists():
                    self.icons[icon_name] = tk.PhotoImage(file=str(icon_path))
        except Exception as e:
            print(f"Error loading icons: {e}")

    def setup_menu(self):
        """Set up the application menu."""
        # Create a new menubar
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_("New Family Tree"), command=self.new_family_tree)
        file_menu.add_command(label=_("Open..."), command=self.open_file)
        file_menu.add_command(label=_("Save"), command=self.save_file)
        file_menu.add_command(label=_("Save As..."), command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label=_("Exit"), command=self.root.quit)
        menubar.add_cascade(label=_("File"), menu=file_menu)

        # Language menu
        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_command(
            label=_("English"), command=lambda: self.change_language("en")
        )
        language_menu.add_command(
            label=_("Arabic"), command=lambda: self.change_language("ar")
        )
        menubar.add_cascade(label=_("Language"), menu=language_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_("About"), command=self.show_about)
        menubar.add_cascade(label=_("Help"), menu=help_menu)

        # Apply the menubar to the root window
        self.root.config(menu=menubar)

    def setup_family_tab(self):
        """Set up the family tab for adding people and relationships."""
        family_tab = ttk.Frame(self.notebook)
        self.notebook.add(family_tab, text=_("Family"))

        # Split the tab into two frames
        left_frame = ttk.Frame(family_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(family_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame: Add person form
        person_form_frame = ttk.LabelFrame(left_frame, text=_("Add Person"))
        person_form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.person_form = PersonForm(
            person_form_frame,
            self.add_person,
            self.icons if hasattr(self, "icons") else None,
        )

        # Right frame: Add relationship form
        relationship_form_frame = ttk.LabelFrame(
            right_frame, text=_("Add Relationship")
        )
        relationship_form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.relationship_form = RelationshipForm(
            relationship_form_frame,
            self.add_relationship,
            self.icons if hasattr(self, "icons") else None,
        )

        # People list
        people_frame = ttk.LabelFrame(left_frame, text=_("People"))
        people_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a frame to hold the treeview and scrollbar
        tree_frame = ttk.Frame(people_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar first
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a treeview for the people list
        self.people_tree = ttk.Treeview(
            tree_frame,
            columns=("name", "gender", "deceased"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        self.people_tree.heading("name", text=_("Name"))
        self.people_tree.heading("gender", text=_("Gender"))
        self.people_tree.heading("deceased", text=_("Deceased"))
        self.people_tree.column("name", width=150)
        self.people_tree.column("gender", width=100)
        self.people_tree.column("deceased", width=100)
        self.people_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar to work with the treeview
        scrollbar.config(command=self.people_tree.yview)

        # Set as deceased button
        set_deceased_button = ttk.Button(
            people_frame,
            text=_("Set as Deceased"),
            command=self.set_as_deceased,
            image=(
                self.icons.get("deceased")
                if hasattr(self, "icons") and "deceased" in self.icons
                else None
            ),
            compound=tk.LEFT,
            padding=(5, 2),
        )
        set_deceased_button.pack(pady=5)

    def setup_visualization_tab(self):
        """Set up the visualization tabs for displaying the family tree."""
        # Create Text View tab
        self.text_view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_view_tab, text=_("Text View"))

        # Create a frame to contain the text widget and scrollbars
        text_frame = ttk.Frame(self.text_view_tab)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a text widget for displaying the family tree as text
        self.text_view = tk.Text(text_frame, wrap=tk.WORD)
        self.text_view.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add vertical scrollbar to text widget
        text_scrollbar_y = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.text_view.yview
        )
        text_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_view.configure(yscrollcommand=text_scrollbar_y.set)

        # Create Graphical View tab
        self.graph_view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_view_tab, text=_("Graphical View"))

        # Create a frame for the graphical view
        graph_container = ttk.Frame(self.graph_view_tab)
        graph_container.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for displaying the image
        self.canvas = tk.Canvas(graph_container, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbars to canvas
        graph_scrollbar_y = ttk.Scrollbar(
            graph_container, orient=tk.VERTICAL, command=self.canvas.yview
        )
        graph_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        graph_scrollbar_x = ttk.Scrollbar(
            graph_container, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        graph_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(
            yscrollcommand=graph_scrollbar_y.set, xscrollcommand=graph_scrollbar_x.set
        )

        # Create a frame for the image to enable zooming
        self.image_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            0, 0, anchor=tk.NW, window=self.image_frame
        )

        # Create a label for displaying the image
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()
        self.image = None

        # Initialize zoom level
        self.zoom_level = 1.0

        # Bind mouse wheel for zooming
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows and macOS
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down

        # Create control buttons for the graphical view
        control_frame = ttk.Frame(self.graph_view_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create zoom buttons
        zoom_in_btn = ttk.Button(
            control_frame,
            text="+",
            width=2,
            command=self.zoom_in,
            style="Control.TButton",
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2)

        zoom_out_btn = ttk.Button(
            control_frame,
            text="-",
            width=2,
            command=self.zoom_out,
            style="Control.TButton",
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2)

        reset_zoom_btn = ttk.Button(
            control_frame,
            text=_("Reset Zoom"),
            command=self.reset_zoom,
            style="Control.TButton",
        )
        reset_zoom_btn.pack(side=tk.LEFT, padx=2)

        # Button to open in new window
        open_window_btn = ttk.Button(
            control_frame,
            text=_("Open in Window"),
            command=self.open_in_new_window,
            style="Control.TButton",
        )
        open_window_btn.pack(side=tk.LEFT, padx=2)

        # Button to save the image
        self.save_image_btn = ttk.Button(
            control_frame,
            text=_("Save Image"),
            command=self.save_image,
            style="Control.TButton",
            state=tk.DISABLED,  # Initially disabled until an image is available
        )
        self.save_image_btn.pack(side=tk.LEFT, padx=2)

        # Add a button to refresh both visualizations
        refresh_button = ttk.Button(
            control_frame,
            text=_("Refresh"),
            command=self.refresh_visualization,
            image=(
                self.icons.get("visualize_tree")
                if hasattr(self, "icons") and "visualize_tree" in self.icons
                else None
            ),
            compound=tk.LEFT,
            padding=(5, 2),
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

    def setup_inheritance_tab(self):
        """Set up the inheritance tab for displaying inheritance calculations."""
        inheritance_tab = ttk.Frame(self.notebook)
        self.notebook.add(inheritance_tab, text=_("Inheritance"))

        # Create a text widget to display the inheritance calculation
        self.inheritance_text = tk.Text(
            inheritance_tab, wrap=tk.WORD, state=tk.DISABLED
        )
        self.inheritance_text.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            inheritance_tab, orient=tk.VERTICAL, command=self.inheritance_text.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inheritance_text.configure(yscrollcommand=scrollbar.set)

        # Add a button to calculate inheritance
        calculate_button = ttk.Button(
            inheritance_tab,
            text=_("Calculate Inheritance"),
            command=self.calculate_inheritance,
            image=(
                self.icons.get("calculate_inheritance")
                if hasattr(self, "icons") and "calculate_inheritance" in self.icons
                else None
            ),
            compound=tk.LEFT,
            padding=(5, 2),
        )
        calculate_button.pack(pady=5)

    def add_person(
        self,
        name: str,
        gender: str,
        religion: str,
        birth_year: Optional[int],
        death_year: Optional[int],
        is_deceased: bool,
    ) -> None:
        """
        Add a person to the family tree.

        Args:
            name: The name of the person
            gender: The gender of the person ("male" or "female")
            religion: The religion of the person
            birth_year: The birth year of the person (optional)
            death_year: The death year of the person (optional)
            is_deceased: Whether this person is the deceased (focal point of the tree)
        """
        try:
            self.builder.add_person(
                name=name,
                gender=gender,
                religion=religion,
                birth_year=birth_year,
                death_year=death_year,
                is_deceased=is_deceased,
            )
            self.update_people_list()
            self.status_var.set(_("Added {name} to the family tree", name=name))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))

    def add_relationship(
        self, person_name: str, relation_type: str, relative_name: str
    ) -> None:
        """
        Add a relationship between two people.

        Args:
            person_name: The name of the first person
            relation_type: The type of relationship ("father", "mother", "child", "spouse")
            relative_name: The name of the relative
        """
        try:
            self.builder.add_relationship(person_name, relation_type, relative_name)
            self.status_var.set(
                _(
                    "Added {relation} relationship between {person1} and {person2}",
                    relation=relation_type,
                    person1=person_name,
                    person2=relative_name,
                )
            )
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))

    def set_as_deceased(self) -> None:
        """Set the selected person as the deceased (focal point of the tree)."""
        selection = self.people_tree.selection()
        if not selection:
            messagebox.showinfo(_("Info"), _("Please select a person first"))
            return

        item = self.people_tree.item(selection[0])
        name = item["values"][0]

        try:
            self.builder.set_deceased(name)
            self.update_people_list()
            self.status_var.set(_("Set {name} as the deceased", name=name))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))

    def update_people_list(self) -> None:
        """Update the people list in the treeview."""
        # Clear the treeview
        for item in self.people_tree.get_children():
            self.people_tree.delete(item)

        # Add people to the treeview
        for name, person in self.builder.people.items():
            is_deceased = _("Yes") if person == self.builder.deceased else _("No")
            self.people_tree.insert(
                "", tk.END, values=(name, person.gender.value, is_deceased)
            )

        # Update the relationship form with the current people
        if hasattr(self, "relationship_form"):
            self.relationship_form.update_people_list(list(self.builder.people.keys()))

    def refresh_visualization(self) -> None:
        """Refresh the family tree visualization in both tabs."""
        try:
            # Import visualizers here to avoid circular imports
            from ..visualizers import (
                FamilyTreeTextVisualizer,
            )

            # Build the family tree
            tree = self.builder.build()

            # Update text view using the text visualizer
            self.text_view.delete(1.0, tk.END)
            text_visualizer = FamilyTreeTextVisualizer(tree)
            self.text_view.insert(tk.END, text_visualizer.visualize())

            # Update graphical view
            self.update_graphical_view(tree)

            self.status_var.set(_("Family tree visualization refreshed"))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))

    def update_graphical_view(self, tree) -> None:
        """Update the graphical view with the given tree."""
        # Import visualizers here to avoid circular imports
        from ..visualizers import GRAPHVIZ_AVAILABLE, FamilyTreeGraphvizVisualizer

        # Reset the image label
        self.image_label.configure(image="")

        # Check if Graphviz is available
        if not GRAPHVIZ_AVAILABLE:
            self.show_graphviz_not_installed()
            return

        try:
            # Create a temporary file for the image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name

            # Generate the family tree visualization using the graphical visualizer
            deceased = tree.deceased
            if deceased:
                graphical_visualizer = FamilyTreeGraphvizVisualizer(tree)
                output_path = graphical_visualizer.render(temp_path, view=False)

                # Display the image
                try:
                    # Store the path to the current image for zoom and new window functionality
                    self.current_image_path = output_path

                    # Load the image
                    self.image = tk.PhotoImage(file=self.current_image_path)
                    self.image_label.configure(image=self.image)

                    # Update the canvas scrollregion to match the image size
                    self.image_label.update_idletasks()  # Make sure the label has been updated
                    self.canvas.config(
                        scrollregion=(0, 0, self.image.width(), self.image.height())
                    )

                    # Reset zoom level
                    self.zoom_level = 1.0

                    # Enable the save image button
                    self.save_image_btn.configure(state=tk.NORMAL)
                except Exception as img_error:
                    self.text_view.insert(tk.END, "\n\n")
                    self.text_view.insert(
                        tk.END,
                        _("Error displaying image: {error}", error=str(img_error)),
                    )
            else:
                self.text_view.insert(tk.END, "\n\n")
                self.text_view.insert(
                    tk.END,
                    _(
                        "No deceased person set. Please set a deceased person to visualize the family tree."
                    ),
                )
        except Exception as e:
            self.text_view.insert(tk.END, "\n\n")
            self.text_view.insert(
                tk.END,
                _("Error generating graphical representation: {error}", error=str(e)),
            )

    def show_graphviz_not_installed(self):
        """Show a message that Graphviz is not installed and provide installation instructions."""
        self.text_view.insert(
            tk.END,
            _(
                "Graphviz is not installed. Please install it to visualize the family tree graphically."
            ),
        )
        self.text_view.insert(tk.END, "\n\n")

        # Add platform-specific installation instructions
        if platform.system() == "Windows":
            self.text_view.insert(tk.END, _("To install Graphviz on Windows:"))
            self.text_view.insert(tk.END, "\n1. ")
            self.text_view.insert(
                tk.END,
                _("Download and install Graphviz from https://graphviz.org/download/"),
            )
            self.text_view.insert(tk.END, "\n2. ")
            self.text_view.insert(
                tk.END, _("Add the Graphviz bin directory to your PATH")
            )
            self.text_view.insert(tk.END, "\n3. ")
            self.text_view.insert(
                tk.END, _("Install the Python package: pip install graphviz")
            )
        elif platform.system() == "Darwin":  # macOS
            self.text_view.insert(tk.END, _("To install Graphviz on macOS:"))
            self.text_view.insert(tk.END, "\n1. ")
            self.text_view.insert(tk.END, _("Using Homebrew: brew install graphviz"))
            self.text_view.insert(tk.END, "\n2. ")
            self.text_view.insert(
                tk.END, _("Install the Python package: pip install graphviz")
            )
        else:  # Linux
            self.text_view.insert(tk.END, _("To install Graphviz on Linux:"))
            self.text_view.insert(tk.END, "\n1. ")
            self.text_view.insert(tk.END, _("Using apt: sudo apt-get install graphviz"))
            self.text_view.insert(tk.END, "\n2. ")
            self.text_view.insert(
                tk.END, _("Install the Python package: pip install graphviz")
            )

    def zoom_in(self):
        """Zoom in on the graph."""
        self.zoom_level *= 1.2
        self.apply_zoom()

    def zoom_out(self):
        """Zoom out on the graph."""
        self.zoom_level *= 0.8
        self.apply_zoom()

    def reset_zoom(self):
        """Reset zoom to original size."""
        self.zoom_level = 1.0
        self.apply_zoom()

    def apply_zoom(self):
        """Apply the current zoom level to the image."""
        if self.image:
            # Calculate new dimensions
            new_width = int(self.image.width() * self.zoom_level)
            new_height = int(self.image.height() * self.zoom_level)

            # Create a resized image
            try:
                # Get the original image path
                if hasattr(self, "current_image_path") and self.current_image_path:
                    # Load the original image and resize it
                    self.image = tk.PhotoImage(file=self.current_image_path)
                    self.image = self.image.subsample(
                        int(1 / self.zoom_level) if self.zoom_level < 1 else 1
                    )
                    self.image = self.image.zoom(
                        int(self.zoom_level) if self.zoom_level > 1 else 1
                    )

                    # Update the image in the label
                    self.image_label.configure(image=self.image)

                    # Update the canvas scrollregion
                    self.canvas.config(scrollregion=(0, 0, new_width, new_height))
            except Exception as e:
                print(f"Error applying zoom: {e}")

    def on_mousewheel(self, event):
        """Handle mousewheel events for zooming."""
        # Determine the direction of the scroll
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.zoom_in()
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.zoom_out()

    def open_in_new_window(self):
        """Open the current graph in a new window."""
        if hasattr(self, "current_image_path") and self.current_image_path:
            try:
                # Create a new top-level window
                new_window = tk.Toplevel()
                new_window.title(_("Family Tree Visualization"))

                # Create a frame for the image
                frame = ttk.Frame(new_window)
                frame.pack(fill=tk.BOTH, expand=True)

                # Create a canvas with scrollbars
                canvas = tk.Canvas(frame, bg="white")
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Add scrollbars
                scrollbar_y = ttk.Scrollbar(
                    frame, orient=tk.VERTICAL, command=canvas.yview
                )
                scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                scrollbar_x = ttk.Scrollbar(
                    new_window, orient=tk.HORIZONTAL, command=canvas.xview
                )
                scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
                canvas.configure(
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set
                )

                # Load the image
                image = tk.PhotoImage(file=self.current_image_path)

                # Create a label to display the image
                image_label = ttk.Label(canvas, image=image)
                canvas.create_window(0, 0, anchor=tk.NW, window=image_label)

                # Set the scrollregion to the size of the image
                canvas.config(scrollregion=(0, 0, image.width(), image.height()))

                # Keep a reference to the image to prevent garbage collection
                new_window.image = image

                # Add zoom controls
                control_frame = ttk.Frame(new_window)
                control_frame.pack(fill=tk.X, padx=5, pady=5)

                zoom_in_btn = ttk.Button(
                    control_frame,
                    text="+",
                    width=2,
                    command=lambda: self.zoom_image(canvas, image_label, image, 1.2),
                )
                zoom_in_btn.pack(side=tk.LEFT, padx=2)

                zoom_out_btn = ttk.Button(
                    control_frame,
                    text="-",
                    width=2,
                    command=lambda: self.zoom_image(canvas, image_label, image, 0.8),
                )
                zoom_out_btn.pack(side=tk.LEFT, padx=2)

                reset_zoom_btn = ttk.Button(
                    control_frame,
                    text=_("Reset Zoom"),
                    command=lambda: self.reset_image_zoom(canvas, image_label, image),
                )
                reset_zoom_btn.pack(side=tk.LEFT, padx=2)

                # Add save button to the new window
                save_btn = ttk.Button(
                    control_frame,
                    text=_("Save Image"),
                    command=lambda: self.save_image_from_path(self.current_image_path),
                )
                save_btn.pack(side=tk.LEFT, padx=2)

                # Store zoom level for this window
                new_window.zoom_level = 1.0

                # Set window size
                width = min(image.width() + 30, 1200)
                height = min(image.height() + 100, 800)
                new_window.geometry(f"{width}x{height}")

            except Exception as e:
                messagebox.showerror(
                    _("Error"),
                    _("Failed to open image in new window: {error}", error=str(e)),
                )
        else:
            messagebox.showinfo(
                _("Info"),
                _(
                    "No image to display. Please generate a family tree visualization first."
                ),
            )

    def zoom_image(self, canvas, label, original_image, factor):
        """Zoom the image in the new window."""
        # Get the parent window
        window = canvas.winfo_toplevel()

        # Update zoom level
        window.zoom_level *= factor

        # Apply zoom
        try:
            # Create a resized image
            new_width = int(original_image.width() * window.zoom_level)
            new_height = int(original_image.height() * window.zoom_level)

            # Use subsample and zoom for better quality
            if window.zoom_level >= 1:
                zoomed_image = original_image.zoom(int(window.zoom_level))
            else:
                zoomed_image = original_image.subsample(int(1 / window.zoom_level))

            # Update the image in the label
            label.configure(image=zoomed_image)

            # Keep a reference to prevent garbage collection
            window.zoomed_image = zoomed_image

            # Update the canvas scrollregion
            canvas.config(scrollregion=(0, 0, new_width, new_height))
        except Exception as e:
            print(f"Error applying zoom in new window: {e}")

    def reset_image_zoom(self, canvas, label, original_image):
        """Reset zoom in the new window."""
        # Get the parent window
        window = canvas.winfo_toplevel()

        # Reset zoom level
        window.zoom_level = 1.0

        # Update the image in the label
        label.configure(image=original_image)

        # Update the canvas scrollregion
        canvas.config(
            scrollregion=(0, 0, original_image.width(), original_image.height())
        )

    def save_image(self):
        """Save the current family tree image to a file."""
        if not hasattr(self, "current_image_path") or not self.current_image_path:
            messagebox.showinfo(
                _("Info"),
                _(
                    "No image to save. Please generate a family tree visualization first."
                ),
            )
            return

        self.save_image_from_path(self.current_image_path)

    def save_image_from_path(self, image_path):
        """
        Save an image from the given path to a user-selected location.

        Args:
            image_path: The path to the image to save
        """
        if not image_path or not os.path.exists(image_path):
            messagebox.showinfo(_("Info"), _("No image to save."))
            return

        # Ask the user for a file location
        file_path = filedialog.asksaveasfilename(
            title=_("Save Family Tree Image"),
            defaultextension=".png",
            filetypes=[(_("PNG Image"), "*.png"), (_("All Files"), "*.*")],
        )

        if not file_path:
            return  # User cancelled

        try:
            # Copy the image file to the user-selected location
            import shutil

            shutil.copy2(image_path, file_path)
            messagebox.showinfo(
                _("Success"), _("Image saved successfully to {path}", path=file_path)
            )
        except Exception as e:
            messagebox.showerror(
                _("Error"), _("Failed to save image: {error}", error=str(e))
            )

    def calculate_inheritance(self) -> None:
        """Calculate and display the inheritance shares."""
        try:
            # build tree if needed

            # Enable the text widget for editing
            self.inheritance_text.config(state=tk.NORMAL)

            # Clear the text widget
            self.inheritance_text.delete(1.0, tk.END)

            # Add a placeholder for inheritance calculation
            # In a real implementation, this would call the inheritance calculation logic
            self.inheritance_text.insert(
                tk.END, _("Inheritance calculation not yet implemented")
            )

            # Disable the text widget again
            self.inheritance_text.config(state=tk.DISABLED)

            self.status_var.set(_("Inheritance calculation completed"))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))

    def new_family_tree(self) -> None:
        """Create a new family tree."""
        if messagebox.askyesno(
            _("Confirm"),
            _(
                "Are you sure you want to create a new family tree? Any unsaved changes will be lost."
            ),
        ):
            self.builder = FamilyTreeBuilder()
            self.current_file = None
            self.update_people_list()
            self.status_var.set(_("Created new family tree"))

    def open_file(self) -> None:
        """Open a family tree from a file."""
        file_path = filedialog.askopenfilename(
            title=_("Open Family Tree"),
            filetypes=[(_("JSON Files"), "*.json"), (_("All Files"), "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            self.builder = FamilyTreeBuilder()
            self.builder.from_dict(data)
            self.current_file = file_path
            self.update_people_list()
            self.status_var.set(_("Opened family tree from {file}", file=file_path))
        except Exception as e:
            messagebox.showerror(_("Error"), str(e))

    def save_file(self) -> None:
        """Save the family tree to the current file."""
        if not self.current_file:
            self.save_as()
            return

        try:
            with open(self.current_file, "w") as f:
                json.dump(self.builder.to_dict(), f, indent=2)

            self.status_var.set(
                _("Saved family tree to {file}", file=self.current_file)
            )
        except Exception as e:
            messagebox.showerror(_("Error"), str(e))

    def save_as(self) -> None:
        """Save the family tree to a new file."""
        file_path = filedialog.asksaveasfilename(
            title=_("Save Family Tree"),
            defaultextension=".json",
            filetypes=[(_("JSON Files"), "*.json"), (_("All Files"), "*.*")],
        )

        if not file_path:
            return

        self.current_file = file_path
        self.save_file()

    def change_language(self, language: str) -> None:
        """
        Change the application language, update all UI elements, and set text direction.

        Args:
            language: The language code to use for translations
        """
        try:
            # Change the language
            set_language(language)

            # Update the builder's language
            self.builder.language = language

            # Set text direction based on language
            text_direction = "rtl" if language == "ar" else "ltr"
            self.set_text_direction(text_direction)

            # Update all UI elements with the new translations
            self.update_ui_language()

            # Show success message
            messagebox.showinfo(_("Info"), _("Language changed successfully."))
        except ValueError as e:
            messagebox.showerror(
                _("Error"), _("Failed to change language: {error}", error=str(e))
            )

    def set_text_direction(self, direction: str) -> None:
        """
        Set the text direction for the entire UI.

        Args:
            direction: The text direction ("rtl" for right-to-left, "ltr" for left-to-right)
        """
        # Store the current direction
        self.text_direction = direction

        # Apply direction to the root window
        self.root.tk.call("tk", "scaling", 1.0)  # Reset scaling to avoid issues

        if direction == "rtl":
            # Set RTL for the entire application
            self.root.tk.call(
                "source", os.path.join(os.path.dirname(__file__), "assets", "rtl.tcl")
            )

            # Update the layout of frames
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Frame, tk.Frame)):
                    self.update_frame_direction(widget, "rtl")
        else:
            # Set LTR for the entire application
            self.root.tk.call(
                "source", os.path.join(os.path.dirname(__file__), "assets", "ltr.tcl")
            )

            # Update the layout of frames
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Frame, tk.Frame)):
                    self.update_frame_direction(widget, "ltr")

    def update_frame_direction(self, frame, direction: str) -> None:
        """
        Update the direction of a frame and its children.

        Args:
            frame: The frame to update
            direction: The text direction ("rtl" or "ltr")
        """
        # Update pack direction for children
        for child in frame.winfo_children():
            if hasattr(child, "pack_info"):
                try:
                    pack_info = child.pack_info()
                    if "side" in pack_info:
                        # Swap LEFT and RIGHT for RTL
                        if direction == "rtl" and pack_info["side"] == tk.LEFT:
                            child.pack_forget()
                            child.pack(
                                side=tk.RIGHT,
                                **{k: v for k, v in pack_info.items() if k != "side"},
                            )
                        elif direction == "rtl" and pack_info["side"] == tk.RIGHT:
                            child.pack_forget()
                            child.pack(
                                side=tk.LEFT,
                                **{k: v for k, v in pack_info.items() if k != "side"},
                            )
                        elif direction == "ltr" and pack_info["side"] == tk.LEFT:
                            child.pack_forget()
                            child.pack(
                                side=tk.LEFT,
                                **{k: v for k, v in pack_info.items() if k != "side"},
                            )
                        elif direction == "ltr" and pack_info["side"] == tk.RIGHT:
                            child.pack_forget()
                            child.pack(
                                side=tk.RIGHT,
                                **{k: v for k, v in pack_info.items() if k != "side"},
                            )
                except Exception:
                    # Skip if pack_info fails
                    pass

            # Recursively update child frames
            if isinstance(child, (ttk.Frame, tk.Frame)):
                self.update_frame_direction(child, direction)

    def update_ui_language(self) -> None:
        """Update all UI elements with the current language translations."""
        # Update window title
        self.root.title(_("Mwareeth - Islamic Inheritance Calculator"))

        # Update status bar
        self.status_var.set(_("Ready"))

        # Recreate the menu (this is more reliable than trying to update it)
        self.setup_menu()

        # Update notebook tabs
        self.notebook.tab(0, text=_("Family"))
        self.notebook.tab(1, text=_("Text View"))
        self.notebook.tab(2, text=_("Graphical View"))
        self.notebook.tab(3, text=_("Inheritance"))

        # Update people tree headings
        self.people_tree.heading("name", text=_("Name"))
        self.people_tree.heading("gender", text=_("Gender"))
        self.people_tree.heading("deceased", text=_("Deceased"))

        # Update inheritance text placeholder if it exists
        if hasattr(self, "inheritance_text"):
            self.inheritance_text.config(state=tk.NORMAL)
            self.inheritance_text.delete(1.0, tk.END)
            self.inheritance_text.insert(
                tk.END, _("Inheritance calculation not yet implemented")
            )
            self.inheritance_text.config(state=tk.DISABLED)

        # Update forms with text direction
        if hasattr(self, "person_form"):
            self.person_form.update_language(self.text_direction)

        if hasattr(self, "relationship_form"):
            self.relationship_form.update_language(self.text_direction)

        # Update family tree view
        if hasattr(self, "family_tree_view") and hasattr(
            self.family_tree_view, "update_language"
        ):
            self.family_tree_view.update_language()

        # Update all widgets starting from the root window
        # This ensures we catch all widgets, even those not directly in the main frame
        self.update_widget_text(self.root)

        # Refresh the people list to update "Yes"/"No" translations
        self.update_people_list()

        # Force a geometry update to ensure all widgets are properly laid out
        self.root.update_idletasks()

    def update_widget_text(self, widget) -> None:
        """
        Recursively update the text of all widgets.

        Args:
            widget: The widget to update
        """
        try:
            # Skip if widget is destroyed or not properly initialized
            if not widget.winfo_exists():
                return

            # Update button text (both ttk and tk)
            if isinstance(widget, (ttk.Button, tk.Button)) and hasattr(
                widget, "configure"
            ):
                text = widget.cget("text")
                if text:
                    widget.configure(text=_(text))

            # Update label text (both ttk and tk)
            elif isinstance(widget, (ttk.Label, tk.Label)) and hasattr(
                widget, "configure"
            ):
                text = widget.cget("text")
                if text and not isinstance(text, tk.StringVar):
                    widget.configure(text=_(text))

            # Update LabelFrame text and anchor (both ttk and tk)
            elif isinstance(widget, (ttk.LabelFrame, tk.LabelFrame)) and hasattr(
                widget, "configure"
            ):
                text = widget.cget("text")
                if text:
                    # Update text with translation
                    widget.configure(text=_(text))

                    # Update label anchor based on text direction
                    if hasattr(self, "text_direction"):
                        if self.text_direction == "rtl":
                            widget.configure(
                                labelanchor="ne"
                            )  # Northeast anchor for RTL
                        else:
                            widget.configure(
                                labelanchor="nw"
                            )  # Northwest anchor for LTR

            # Update Radiobutton text (both ttk and tk)
            elif isinstance(widget, (ttk.Radiobutton, tk.Radiobutton)) and hasattr(
                widget, "configure"
            ):
                text = widget.cget("text")
                if text:
                    widget.configure(text=_(text))

            # Update Checkbutton text (both ttk and tk)
            elif isinstance(widget, (ttk.Checkbutton, tk.Checkbutton)) and hasattr(
                widget, "configure"
            ):
                text = widget.cget("text")
                if text:
                    widget.configure(text=_(text))

            # Update Menu items
            elif isinstance(widget, tk.Menu):
                # Menu items can't be easily updated, so we recreate the menu in setup_menu()
                pass

            # Recursively update children
            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    self.update_widget_text(child)

        except tk.TclError:
            # Skip any widgets that cause Tcl errors (might be in the process of being destroyed)
            pass

    def show_about(self) -> None:
        """Show the about dialog."""
        messagebox.showinfo(
            _("About"),
            _(
                "Mwareeth - Islamic Inheritance Calculator\n\nA tool to calculate inheritance according to Islamic law."
            ),
        )

    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()


def main() -> None:
    """Run the GUI application."""
    app = MwareethGUI()
    app.run()


if __name__ == "__main__":
    main()
