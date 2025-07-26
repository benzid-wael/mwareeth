"""
This module provides a component for visualizing family trees in the GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tempfile
import platform
import os
import shutil

from ..family_tree_builder import FamilyTreeBuilder
from ..i18n import _

# Try to import Graphviz, but don't fail if it's not installed
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


class FamilyTreeView(ttk.Frame):
    """
    A component for visualizing family trees in the GUI.
    
    This class provides a graphical representation of a family tree,
    using Graphviz if available, or a text-based representation otherwise.
    """
    
    def __init__(self, parent):
        """
        Initialize the family tree view.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Set up styles for the widgets
        self.setup_styles()
        
        # Create a notebook (tabbed interface) directly in the main frame
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs for text and graphical views
        self.create_text_view_tab()
        self.create_graphical_view_tab()
        
        # Initialize zoom level
        self.zoom_level = 1.0
        
        # Check if Graphviz is available
        if not GRAPHVIZ_AVAILABLE:
            self.show_graphviz_not_installed()
    
    def setup_styles(self):
        """Set up custom styles for the widgets."""
        style = ttk.Style()
        style.configure("Control.TButton", padding=3)
        # Make refresh buttons more prominent
        style.configure("Refresh.TButton", padding=(10, 5), font=('', 10, 'bold'))
    
    def create_text_view_tab(self):
        """Create the text view tab."""
        # Create Text View tab
        self.text_view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_view_tab, text=_("Text View"))
        
        # Create a frame for controls with a prominent refresh button
        control_frame = ttk.Frame(self.text_view_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add a prominent refresh button
        refresh_button = ttk.Button(
            control_frame, 
            text=_("Refresh View"), 
            command=self.refresh_visualization,
            padding=(10, 5),
            style="Control.TButton"
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Create a text widget for displaying the family tree as text
        text_container = ttk.Frame(self.text_view_tab)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.text = tk.Text(text_container, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side=tk.LEFT)
        
        # Add vertical scrollbar to text widget
        text_scrollbar_y = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.text.yview)
        text_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=text_scrollbar_y.set)
    
    def create_graphical_view_tab(self):
        """Create the graphical view tab."""
        # Create Graphical View tab
        self.graph_view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_view_tab, text=_("Graphical View"))
        
        # Create a frame for controls with better organization
        control_frame = ttk.Frame(self.graph_view_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a sub-frame for zoom controls to group them together
        zoom_frame = ttk.LabelFrame(control_frame, text=_("Zoom Controls"))
        zoom_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Create zoom buttons in the zoom frame
        zoom_in_btn = ttk.Button(
            zoom_frame, 
            text="+", 
            width=2,
            command=self.zoom_in,
            style="Control.TButton"
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        zoom_out_btn = ttk.Button(
            zoom_frame, 
            text="-", 
            width=2,
            command=self.zoom_out,
            style="Control.TButton"
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        reset_zoom_btn = ttk.Button(
            zoom_frame, 
            text=_("Reset"),
            command=self.reset_zoom,
            style="Control.TButton"
        )
        reset_zoom_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Create a sub-frame for image actions
        image_frame = ttk.LabelFrame(control_frame, text=_("Image Actions"))
        image_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Button to open in new window
        open_window_btn = ttk.Button(
            image_frame, 
            text=_("Open in Window"),
            command=self.open_in_new_window,
            style="Control.TButton"
        )
        open_window_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Button to save the image
        self.save_image_btn = ttk.Button(
            image_frame, 
            text=_("Save Image"),
            command=self.save_image,
            style="Control.TButton",
            state=tk.DISABLED  # Initially disabled until an image is available
        )
        self.save_image_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Add a prominent refresh button
        refresh_button = ttk.Button(
            control_frame, 
            text=_("Refresh View"), 
            command=self.refresh_visualization,
            padding=(10, 5),
            style="Control.TButton"
        )
        refresh_button.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Create a canvas for displaying the image
        graph_container = ttk.Frame(self.graph_view_tab)
        graph_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(graph_container, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbars to canvas
        graph_scrollbar_y = ttk.Scrollbar(graph_container, orient=tk.VERTICAL, command=self.canvas.yview)
        graph_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        graph_scrollbar_x = ttk.Scrollbar(graph_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        graph_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=graph_scrollbar_y.set, xscrollcommand=graph_scrollbar_x.set)
        
        # Create a frame for the image to enable zooming
        self.image_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, anchor=tk.NW, window=self.image_frame)
        
        # Create a label for displaying the image
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()
        self.image = None
        
        # Bind mouse wheel for zooming
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows and macOS
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
    
    def refresh_visualization(self):
        """Refresh the visualization with the current family tree."""
        # This method will be called by the parent widget
        pass
    
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
                if hasattr(self, 'current_image_path') and self.current_image_path:
                    # Load the original image and resize it
                    self.image = tk.PhotoImage(file=self.current_image_path)
                    self.image = self.image.subsample(int(1/self.zoom_level) if self.zoom_level < 1 else 1)
                    self.image = self.image.zoom(int(self.zoom_level) if self.zoom_level > 1 else 1)
                    
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
        if hasattr(self, 'current_image_path') and self.current_image_path:
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
                scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
                scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                scrollbar_x = ttk.Scrollbar(new_window, orient=tk.HORIZONTAL, command=canvas.xview)
                scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
                canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
                
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
                    command=lambda: self.zoom_image(canvas, image_label, image, 1.2)
                )
                zoom_in_btn.pack(side=tk.LEFT, padx=2)
                
                zoom_out_btn = ttk.Button(
                    control_frame, 
                    text="-", 
                    width=2,
                    command=lambda: self.zoom_image(canvas, image_label, image, 0.8)
                )
                zoom_out_btn.pack(side=tk.LEFT, padx=2)
                
                reset_zoom_btn = ttk.Button(
                    control_frame, 
                    text=_("Reset Zoom"),
                    command=lambda: self.reset_image_zoom(canvas, image_label, image)
                )
                reset_zoom_btn.pack(side=tk.LEFT, padx=2)
                
                # Add save button to the new window
                save_btn = ttk.Button(
                    control_frame, 
                    text=_("Save Image"),
                    command=lambda: self.save_image_from_path(self.current_image_path)
                )
                save_btn.pack(side=tk.LEFT, padx=2)
                
                # Store zoom level for this window
                new_window.zoom_level = 1.0
                
                # Set window size
                width = min(image.width() + 30, 1200)
                height = min(image.height() + 100, 800)
                new_window.geometry(f"{width}x{height}")
                
            except Exception as e:
                messagebox.showerror(_("Error"), _("Failed to open image in new window: {error}", error=str(e)))
        else:
            messagebox.showinfo(_("Info"), _("No image to display. Please generate a family tree visualization first."))
    
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
                zoomed_image = original_image.subsample(int(1/window.zoom_level))
            
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
        canvas.config(scrollregion=(0, 0, original_image.width(), original_image.height()))
    
    def show_graphviz_not_installed(self):
        """Show a message that Graphviz is not installed and provide installation instructions."""
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, _("Graphviz is not installed. Please install it to visualize the family tree graphically."))
        self.text.insert(tk.END, "\n\n")
        
        # Add platform-specific installation instructions
        if platform.system() == "Windows":
            self.text.insert(tk.END, _("To install Graphviz on Windows:"))
            self.text.insert(tk.END, "\n1. ")
            self.text.insert(tk.END, _("Download and install Graphviz from https://graphviz.org/download/"))
            self.text.insert(tk.END, "\n2. ")
            self.text.insert(tk.END, _("Add the Graphviz bin directory to your PATH"))
            self.text.insert(tk.END, "\n3. ")
            self.text.insert(tk.END, _("Install the Python package: pip install graphviz"))
        elif platform.system() == "Darwin":  # macOS
            self.text.insert(tk.END, _("To install Graphviz on macOS:"))
            self.text.insert(tk.END, "\n1. ")
            self.text.insert(tk.END, _("Using Homebrew: brew install graphviz"))
            self.text.insert(tk.END, "\n2. ")
            self.text.insert(tk.END, _("Install the Python package: pip install graphviz"))
        else:  # Linux
            self.text.insert(tk.END, _("To install Graphviz on Linux:"))
            self.text.insert(tk.END, "\n1. ")
            self.text.insert(tk.END, _("Using apt: sudo apt-get install graphviz"))
            self.text.insert(tk.END, "\n2. ")
            self.text.insert(tk.END, _("Install the Python package: pip install graphviz"))
    
    def display_tree(self, builder: FamilyTreeBuilder) -> None:
        """
        Display a family tree.
        
        Args:
            tree: The family tree to display
        """
        # Clear the text widget
        self.text.delete(1.0, tk.END)
        
        # Display the text representation of the tree
        tree = builder.build()
        self.text.insert(tk.END, tree.visualize())
        
        # Reset the image label
        self.image_label.configure(image="")
        
        # If Graphviz is available, also display a graphical representation
        if GRAPHVIZ_AVAILABLE:
            try:
                # Create a temporary file for the image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Add nodes for each person in the family tree
                # Start with the deceased person
                deceased = tree.deceased
                if deceased:
                    builder.generate_family_tree_graphviz(temp_path)
                    
                    # Display the image
                    try:
                        # Store the path to the current image for zoom and new window functionality
                        self.current_image_path = temp_path + '.png'
                        
                        # Load the image
                        self.image = tk.PhotoImage(file=self.current_image_path)
                        self.image_label.configure(image=self.image)
                        
                        # Update the canvas scrollregion to match the image size
                        self.image_label.update_idletasks()  # Make sure the label has been updated
                        self.canvas.config(scrollregion=(0, 0, self.image.width(), self.image.height()))
                        
                        # Reset zoom level
                        self.zoom_level = 1.0
                        
                        # Enable the save image button
                        self.save_image_btn.configure(state=tk.NORMAL)
                        
                        # Don't remove the temporary file yet, as we need it for zoom and new window
                        # It will be removed when a new visualization is generated or the application closes
                    except Exception as img_error:
                        self.text.insert(tk.END, "\n\n")
                        self.text.insert(tk.END, _("Error displaying image: {error}", error=str(img_error)))
                else:
                    self.text.insert(tk.END, "\n\n")
                    self.text.insert(tk.END, _("No deceased person set. Please set a deceased person to visualize the family tree."))
                
            except Exception as e:
                self.text.insert(tk.END, "\n\n")
                self.text.insert(tk.END, _("Error generating graphical representation: {error}", error=str(e)))
                
                # Check if the error is related to the Graphviz executable not being found
                if "executable" in str(e).lower() and "not found" in str(e).lower():
                    self.text.insert(tk.END, "\n\n")
                    self.text.insert(tk.END, _("It seems the Graphviz executable is not installed or not in your PATH."))
                    self.text.insert(tk.END, "\n")
                    self.text.insert(tk.END, _("Please install the Graphviz system package and make sure it's in your PATH."))
    
    def save_image(self):
        """Save the current family tree image to a file."""
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            messagebox.showinfo(_("Info"), _("No image to save. Please generate a family tree visualization first!"))
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
            filetypes=[
                (_("PNG Image"), "*.png"),
                (_("All Files"), "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Copy the image file to the user-selected location
            shutil.copy2(image_path, file_path)
            messagebox.showinfo(_("Success"), _("Image saved successfully to {path}", path=file_path))
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to save image: {error}", error=str(e)))
    
    def update_language(self) -> None:
        """Update the widget with the current language translations."""
        # Update tab titles
        if hasattr(self, "notebook"):
            self.notebook.tab(0, text=_("Text View"))
            self.notebook.tab(1, text=_("Graphical View"))
        
        # Update button text
        if hasattr(self, "save_image_btn"):
            self.save_image_btn.configure(text=_("Save Image"))
        
        # Update all frames and buttons in the text view tab
        if hasattr(self, "text_view_tab"):
            for widget in self.text_view_tab.winfo_children():
                if isinstance(widget, ttk.Frame):  # Control frame
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button) and "Refresh" in child.cget("text"):
                            child.configure(text=_("Refresh View"))
        
        # Update all frames and buttons in the graphical view tab
        if hasattr(self, "graph_view_tab"):
            for widget in self.graph_view_tab.winfo_children():
                if isinstance(widget, ttk.Frame):  # Control frame
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            if "Refresh" in child.cget("text"):
                                child.configure(text=_("Refresh View"))
                        elif isinstance(child, ttk.LabelFrame):
                            if "Zoom" in child.cget("text"):
                                child.configure(text=_("Zoom Controls"))
                            elif "Image" in child.cget("text"):
                                child.configure(text=_("Image Actions"))
                            
                            # Update buttons inside label frames
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Button):
                                    if grandchild.cget("text") == "Reset":
                                        grandchild.configure(text=_("Reset"))
                                    elif grandchild.cget("text") == "Open in Window":
                                        grandchild.configure(text=_("Open in Window"))
                                    elif grandchild.cget("text") == "Save Image":
                                        grandchild.configure(text=_("Save Image"))
