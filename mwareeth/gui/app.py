"""
Main GUI application for the mwareeth inheritance calculator.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
from typing import Dict, List, Optional, Tuple, Any

from ..family_tree_builder import FamilyTreeBuilder
from ..entities.person import Gender, Religion
from ..i18n import _, set_language

from .family_tree_view import FamilyTreeView
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
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_menu(self):
        """Set up the application menu."""
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
        language_menu.add_command(label=_("English"), command=lambda: self.change_language("en"))
        language_menu.add_command(label=_("Arabic"), command=lambda: self.change_language("ar"))
        menubar.add_cascade(label=_("Language"), menu=language_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_("About"), command=self.show_about)
        menubar.add_cascade(label=_("Help"), menu=help_menu)
        
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
        
        self.person_form = PersonForm(person_form_frame, self.add_person)
        
        # Right frame: Add relationship form
        relationship_form_frame = ttk.LabelFrame(right_frame, text=_("Add Relationship"))
        relationship_form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.relationship_form = RelationshipForm(relationship_form_frame, self.add_relationship)
        
        # People list
        people_frame = ttk.LabelFrame(left_frame, text=_("People"))
        people_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a treeview for the people list
        self.people_tree = ttk.Treeview(people_frame, columns=("name", "gender", "deceased"), show="headings")
        self.people_tree.heading("name", text=_("Name"))
        self.people_tree.heading("gender", text=_("Gender"))
        self.people_tree.heading("deceased", text=_("Deceased"))
        self.people_tree.column("name", width=150)
        self.people_tree.column("gender", width=100)
        self.people_tree.column("deceased", width=100)
        self.people_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(people_frame, orient=tk.VERTICAL, command=self.people_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.people_tree.configure(yscrollcommand=scrollbar.set)
        
        # Set as deceased button
        set_deceased_button = ttk.Button(people_frame, text=_("Set as Deceased"), command=self.set_as_deceased)
        set_deceased_button.pack(pady=5)
    
    def setup_visualization_tab(self):
        """Set up the visualization tab for displaying the family tree."""
        visualization_tab = ttk.Frame(self.notebook)
        self.notebook.add(visualization_tab, text=_("Visualization"))
        
        # Create the family tree view
        self.family_tree_view = FamilyTreeView(visualization_tab)
        self.family_tree_view.pack(fill=tk.BOTH, expand=True)
        
        # Add a button to refresh the visualization
        refresh_button = ttk.Button(visualization_tab, text=_("Refresh"), command=self.refresh_visualization)
        refresh_button.pack(pady=5)
    
    def setup_inheritance_tab(self):
        """Set up the inheritance tab for displaying inheritance calculations."""
        inheritance_tab = ttk.Frame(self.notebook)
        self.notebook.add(inheritance_tab, text=_("Inheritance"))
        
        # Create a text widget to display the inheritance calculation
        self.inheritance_text = tk.Text(inheritance_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.inheritance_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(inheritance_tab, orient=tk.VERTICAL, command=self.inheritance_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inheritance_text.configure(yscrollcommand=scrollbar.set)
        
        # Add a button to calculate inheritance
        calculate_button = ttk.Button(inheritance_tab, text=_("Calculate Inheritance"), command=self.calculate_inheritance)
        calculate_button.pack(pady=5)
    
    def add_person(self, name: str, gender: str, religion: str, birth_year: Optional[int], death_year: Optional[int], is_deceased: bool) -> None:
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
    
    def add_relationship(self, person_name: str, relation_type: str, relative_name: str) -> None:
        """
        Add a relationship between two people.
        
        Args:
            person_name: The name of the first person
            relation_type: The type of relationship ("father", "mother", "child", "spouse")
            relative_name: The name of the relative
        """
        try:
            self.builder.add_relationship(person_name, relation_type, relative_name)
            self.status_var.set(_("Added {relation} relationship between {person1} and {person2}", 
                                relation=relation_type, person1=person_name, person2=relative_name))
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
            self.people_tree.insert("", tk.END, values=(name, person.gender.value, is_deceased))
        
        # Update the relationship form with the current people
        if hasattr(self, "relationship_form"):
            self.relationship_form.update_people_list(list(self.builder.people.keys()))
    
    def refresh_visualization(self) -> None:
        """Refresh the family tree visualization."""
        try:
            tree = self.builder.build()
            self.family_tree_view.display_tree(tree)
            self.status_var.set(_("Family tree visualization refreshed"))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))
    
    def calculate_inheritance(self) -> None:
        """Calculate and display the inheritance shares."""
        try:
            tree = self.builder.build()
            
            # Enable the text widget for editing
            self.inheritance_text.config(state=tk.NORMAL)
            
            # Clear the text widget
            self.inheritance_text.delete(1.0, tk.END)
            
            # Add a placeholder for inheritance calculation
            # In a real implementation, this would call the inheritance calculation logic
            self.inheritance_text.insert(tk.END, _("Inheritance calculation not yet implemented"))
            
            # Disable the text widget again
            self.inheritance_text.config(state=tk.DISABLED)
            
            self.status_var.set(_("Inheritance calculation completed"))
        except ValueError as e:
            messagebox.showerror(_("Error"), str(e))
    
    def new_family_tree(self) -> None:
        """Create a new family tree."""
        if messagebox.askyesno(_("Confirm"), _("Are you sure you want to create a new family tree? Any unsaved changes will be lost.")):
            self.builder = FamilyTreeBuilder()
            self.current_file = None
            self.update_people_list()
            self.status_var.set(_("Created new family tree"))
    
    def open_file(self) -> None:
        """Open a family tree from a file."""
        file_path = filedialog.askopenfilename(
            title=_("Open Family Tree"),
            filetypes=[(_("JSON Files"), "*.json"), (_("All Files"), "*.*")]
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
            
            self.status_var.set(_("Saved family tree to {file}", file=self.current_file))
        except Exception as e:
            messagebox.showerror(_("Error"), str(e))
    
    def save_as(self) -> None:
        """Save the family tree to a new file."""
        file_path = filedialog.asksaveasfilename(
            title=_("Save Family Tree"),
            defaultextension=".json",
            filetypes=[(_("JSON Files"), "*.json"), (_("All Files"), "*.*")]
        )
        
        if not file_path:
            return
        
        self.current_file = file_path
        self.save_file()
    
    def change_language(self, language: str) -> None:
        """
        Change the application language.
        
        Args:
            language: The language code to use for translations
        """
        try:
            set_language(language)
            messagebox.showinfo(_("Info"), _("Language changed. Please restart the application for the changes to take effect."))
        except ValueError:
            messagebox.showerror(_("Error"), _("Failed to change language"))
    
    def show_about(self) -> None:
        """Show the about dialog."""
        messagebox.showinfo(
            _("About"),
            _("Mwareeth - Islamic Inheritance Calculator\n\nA tool to calculate inheritance according to Islamic law.")
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
            