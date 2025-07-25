"""
This module provides form components for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional, Dict, Any

from ..entities.person import Gender, Religion
from ..i18n import _


class PersonForm(ttk.Frame):
    """
    A form for adding people to the family tree.
    """
    
    def __init__(self, parent, callback: Callable, icons: Dict[str, Any] = None):
        """
        Initialize the person form.
        
        Args:
            parent: The parent widget
            callback: The function to call when the form is submitted
            icons: Dictionary of icons to use for the form
        """
        super().__init__(parent)
        self.callback = callback
        self.icons = icons or {}
        
        # Create form fields
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
    
    def create_widgets(self):
        """Create the form widgets."""
        # Name field
        ttk.Label(self, text=_("Name:")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Gender field
        ttk.Label(self, text=_("Gender:")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar(value="male")
        ttk.Radiobutton(self, text=_("Male"), variable=self.gender_var, value="male").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text=_("Female"), variable=self.gender_var, value="female").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Religion field
        ttk.Label(self, text=_("Religion:")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.religion_var = tk.StringVar(value="Islam")
        religion_combo = ttk.Combobox(self, textvariable=self.religion_var)
        religion_combo['values'] = [r.value for r in Religion]
        religion_combo.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Birth year field
        ttk.Label(self, text=_("Birth Year:")).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.birth_year_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.birth_year_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Death year field
        ttk.Label(self, text=_("Death Year:")).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.death_year_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.death_year_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Is deceased checkbox
        self.is_deceased_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text=_("Is Deceased"), variable=self.is_deceased_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Submit button
        add_person_button = ttk.Button(
            self, 
            text=_("Add Person"), 
            command=self.submit,
            image=self.icons.get("add_person") if "add_person" in self.icons else None,
            compound=tk.LEFT,
            padding=(5, 2)
        )
        add_person_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid
        self.columnconfigure(1, weight=1)
    
    def submit(self):
        """Submit the form."""
        # Get form values
        name = self.name_var.get()
        gender = self.gender_var.get()
        religion = self.religion_var.get()
        
        # Parse birth and death years
        birth_year = None
        if self.birth_year_var.get():
            try:
                birth_year = int(self.birth_year_var.get())
            except ValueError:
                pass
        
        death_year = None
        if self.death_year_var.get():
            try:
                death_year = int(self.death_year_var.get())
            except ValueError:
                pass
        
        is_deceased = self.is_deceased_var.get()
        
        # Call the callback function
        self.callback(name, gender, religion, birth_year, death_year, is_deceased)
        
        # Clear the form
        self.name_var.set("")
        self.gender_var.set("male")
        self.religion_var.set("Islam")
        self.birth_year_var.set("")
        self.death_year_var.set("")
        self.is_deceased_var.set(False)


class RelationshipForm(ttk.Frame):
    """
    A form for adding relationships between people.
    """
    
    def __init__(self, parent, callback: Callable, icons: Dict[str, Any] = None):
        """
        Initialize the relationship form.
        
        Args:
            parent: The parent widget
            callback: The function to call when the form is submitted
            icons: Dictionary of icons to use for the form
        """
        super().__init__(parent)
        self.callback = callback
        self.icons = icons or {}
        self.people = []
        
        # Create form fields
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
    
    def create_widgets(self):
        """Create the form widgets."""
        # Person field
        ttk.Label(self, text=_("Person:")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.person_var = tk.StringVar()
        self.person_combo = ttk.Combobox(self, textvariable=self.person_var)
        self.person_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Relationship type field
        ttk.Label(self, text=_("Relationship:")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.relation_var = tk.StringVar()
        relation_combo = ttk.Combobox(self, textvariable=self.relation_var)
        relation_combo['values'] = [_("father"), _("mother"), _("child"), _("spouse")]
        relation_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Relative field
        ttk.Label(self, text=_("Relative:")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.relative_var = tk.StringVar()
        self.relative_combo = ttk.Combobox(self, textvariable=self.relative_var)
        self.relative_combo.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Submit button
        add_relationship_button = ttk.Button(
            self, 
            text=_("Add Relationship"), 
            command=self.submit,
            image=self.icons.get("add_relationship") if "add_relationship" in self.icons else None,
            compound=tk.LEFT,
            padding=(5, 2)
        )
        add_relationship_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure grid
        self.columnconfigure(1, weight=1)
    
    def update_people_list(self, people: List[str]):
        """
        Update the list of people in the comboboxes.
        
        Args:
            people: The list of people names
        """
        self.people = people
        self.person_combo['values'] = people
        self.relative_combo['values'] = people
    
    def submit(self):
        """Submit the form."""
        # Get form values
        person_name = self.person_var.get()
        relation_type = self.relation_var.get()
        relative_name = self.relative_var.get()
        
        # Call the callback function
        self.callback(person_name, relation_type, relative_name)
        
        # Clear the form
        self.person_var.set("")
        self.relation_var.set("")
        self.relative_var.set("")
