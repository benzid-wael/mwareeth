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
        
        # Store widget references for language updates
        self.widgets = {}
        
        # Create form fields
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
    
    def create_widgets(self):
        """Create the form widgets."""
        # Name field
        self.widgets["name_label"] = ttk.Label(self, text=_("Name:"))
        self.widgets["name_label"].grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Gender field
        self.widgets["gender_label"] = ttk.Label(self, text=_("Gender:"))
        self.widgets["gender_label"].grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar(value="male")
        self.widgets["male_radio"] = ttk.Radiobutton(self, text=_("Male"), variable=self.gender_var, value="male")
        self.widgets["male_radio"].grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.widgets["female_radio"] = ttk.Radiobutton(self, text=_("Female"), variable=self.gender_var, value="female")
        self.widgets["female_radio"].grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Religion field
        self.widgets["religion_label"] = ttk.Label(self, text=_("Religion:"))
        self.widgets["religion_label"].grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.religion_var = tk.StringVar(value="Islam")
        self.widgets["religion_combo"] = ttk.Combobox(self, textvariable=self.religion_var)
        self.widgets["religion_combo"]['values'] = [r.value for r in Religion]
        self.widgets["religion_combo"].grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Birth year field
        self.widgets["birth_year_label"] = ttk.Label(self, text=_("Birth Year:"))
        self.widgets["birth_year_label"].grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.birth_year_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.birth_year_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Death year field
        self.widgets["death_year_label"] = ttk.Label(self, text=_("Death Year:"))
        self.widgets["death_year_label"].grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.death_year_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.death_year_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Is deceased checkbox
        self.is_deceased_var = tk.BooleanVar(value=False)
        self.widgets["is_deceased_check"] = ttk.Checkbutton(self, text=_("Is Deceased"), variable=self.is_deceased_var)
        self.widgets["is_deceased_check"].grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Submit button
        self.widgets["add_person_button"] = ttk.Button(
            self, 
            text=_("Add Person"), 
            command=self.submit,
            image=self.icons.get("add_person") if "add_person" in self.icons else None,
            compound=tk.LEFT,
            padding=(5, 2)
        )
        self.widgets["add_person_button"].grid(row=6, column=0, columnspan=2, pady=10)
        
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


    def update_language(self, direction="ltr"):
        """
        Update the form widgets with the current language translations and adjust layout for text direction.
        
        Args:
            direction: The text direction ("rtl" for right-to-left, "ltr" for left-to-right)
        """
        # Update labels
        self.widgets["name_label"].configure(text=_("Name:"))
        self.widgets["gender_label"].configure(text=_("Gender:"))
        self.widgets["religion_label"].configure(text=_("Religion:"))
        self.widgets["birth_year_label"].configure(text=_("Birth Year:"))
        self.widgets["death_year_label"].configure(text=_("Death Year:"))
        
        # Update radio buttons
        self.widgets["male_radio"].configure(text=_("Male"))
        self.widgets["female_radio"].configure(text=_("Female"))
        
        # Update checkbox
        self.widgets["is_deceased_check"].configure(text=_("Is Deceased"))
        
        # Update button
        self.widgets["add_person_button"].configure(text=_("Add Person"))
        
        # Update layout based on text direction
        self.update_layout(direction)
    
    def update_layout(self, direction="ltr"):
        """
        Update the form layout based on text direction.
        
        Args:
            direction: The text direction ("rtl" for right-to-left, "ltr" for left-to-right)
        """
        # Get all grid slaves
        slaves = self.grid_slaves()
        
        # Store current grid info for each widget
        grid_info = {}
        for widget in slaves:
            grid_info[widget] = widget.grid_info()
        
        # Remove all widgets from grid
        for widget in slaves:
            widget.grid_forget()
        
        # Reconfigure grid
        if direction == "rtl":
            # RTL layout: labels on right, fields on left
            self.columnconfigure(0, weight=1)  # Fields column gets weight
            self.columnconfigure(1, weight=0)  # Labels column has fixed width
            
            # Rearrange widgets
            for widget, info in grid_info.items():
                row = info["row"]
                col = info["column"]
                sticky = info["sticky"]
                padx = info["padx"]
                pady = info["pady"]
                columnspan = info["columnspan"]
                
                # Swap columns (0->1, 1->0) except for widgets that span multiple columns
                if columnspan == 1:
                    new_col = 1 if col == 0 else 0
                    # Adjust sticky direction
                    if "w" in sticky.lower():
                        sticky = sticky.lower().replace("w", "e").upper()
                    elif "e" in sticky.lower():
                        sticky = sticky.lower().replace("e", "w").upper()
                else:
                    new_col = col
                
                widget.grid(row=row, column=new_col, sticky=sticky, padx=padx, pady=pady, columnspan=columnspan)
        else:
            # LTR layout: labels on left, fields on right
            self.columnconfigure(0, weight=0)  # Labels column has fixed width
            self.columnconfigure(1, weight=1)  # Fields column gets weight
            
            # Restore original layout
            for widget, info in grid_info.items():
                widget.grid(**info)


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
        
        # Store widget references for language updates
        self.widgets = {}
        
        # Create form fields
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
    
    def create_widgets(self):
        """Create the form widgets."""
        # Person field
        self.widgets["person_label"] = ttk.Label(self, text=_("Person:"))
        self.widgets["person_label"].grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.person_var = tk.StringVar()
        self.person_combo = ttk.Combobox(self, textvariable=self.person_var)
        self.person_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Relationship type field
        self.widgets["relationship_label"] = ttk.Label(self, text=_("Relationship:"))
        self.widgets["relationship_label"].grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.relation_var = tk.StringVar()
        self.widgets["relation_combo"] = ttk.Combobox(self, textvariable=self.relation_var)
        self.widgets["relation_combo"]['values'] = [_("father"), _("mother"), _("child"), _("spouse")]
        self.widgets["relation_combo"].grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Relative field
        self.widgets["relative_label"] = ttk.Label(self, text=_("Relative:"))
        self.widgets["relative_label"].grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.relative_var = tk.StringVar()
        self.relative_combo = ttk.Combobox(self, textvariable=self.relative_var)
        self.relative_combo.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Submit button
        self.widgets["add_relationship_button"] = ttk.Button(
            self, 
            text=_("Add Relationship"), 
            command=self.submit,
            image=self.icons.get("add_relationship") if "add_relationship" in self.icons else None,
            compound=tk.LEFT,
            padding=(5, 2)
        )
        self.widgets["add_relationship_button"].grid(row=3, column=0, columnspan=2, pady=10)
        
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
    
    def update_language(self, direction="ltr"):
        """
        Update the form widgets with the current language translations and adjust layout for text direction.
        
        Args:
            direction: The text direction ("rtl" for right-to-left, "ltr" for left-to-right)
        """
        # Update labels
        self.widgets["person_label"].configure(text=_("Person:"))
        self.widgets["relationship_label"].configure(text=_("Relationship:"))
        self.widgets["relative_label"].configure(text=_("Relative:"))
        
        # Update relationship values
        self.widgets["relation_combo"]['values'] = [_("father"), _("mother"), _("child"), _("spouse")]
        
        # Update button
        self.widgets["add_relationship_button"].configure(text=_("Add Relationship"))
        
        # Update layout based on text direction
        self.update_layout(direction)
    
    def update_layout(self, direction="ltr"):
        """
        Update the form layout based on text direction.
        
        Args:
            direction: The text direction ("rtl" for right-to-left, "ltr" for left-to-right)
        """
        # Get all grid slaves
        slaves = self.grid_slaves()
        
        # Store current grid info for each widget
        grid_info = {}
        for widget in slaves:
            grid_info[widget] = widget.grid_info()
        
        # Remove all widgets from grid
        for widget in slaves:
            widget.grid_forget()
        
        # Reconfigure grid
        if direction == "rtl":
            # RTL layout: labels on right, fields on left
            self.columnconfigure(0, weight=1)  # Fields column gets weight
            self.columnconfigure(1, weight=0)  # Labels column has fixed width
            
            # Rearrange widgets
            for widget, info in grid_info.items():
                row = info["row"]
                col = info["column"]
                sticky = info["sticky"]
                padx = info["padx"]
                pady = info["pady"]
                columnspan = info["columnspan"]
                
                # Swap columns (0->1, 1->0) except for widgets that span multiple columns
                if columnspan == 1:
                    new_col = 1 if col == 0 else 0
                    # Adjust sticky direction
                    if "w" in sticky.lower():
                        sticky = sticky.lower().replace("w", "e").upper()
                    elif "e" in sticky.lower():
                        sticky = sticky.lower().replace("e", "w").upper()
                else:
                    new_col = col
                
                widget.grid(row=row, column=new_col, sticky=sticky, padx=padx, pady=pady, columnspan=columnspan)
        else:
            # LTR layout: labels on left, fields on right
            self.columnconfigure(0, weight=0)  # Labels column has fixed width
            self.columnconfigure(1, weight=1)  # Fields column gets weight
            
            # Restore original layout
            for widget, info in grid_info.items():
                widget.grid(**info)
    
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
