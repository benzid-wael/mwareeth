"""
This module provides a component for visualizing family trees in the GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
from typing import Optional

from ..entities.family_tree import FamilyTree, RelationshipType
from ..entities.person import Gender
from ..i18n import _

# Try to import Graphviz, but don't fail if it's not installed
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    # Define a dummy Digraph class to avoid "possibly unbound" errors
    class Digraph:
        """Dummy Digraph class when graphviz is not available."""
        def __init__(self, comment='', strict=False):
            self.comment = comment
            self.strict = strict
            self.source = "Graphviz not available"
        
        def attr(self, *args, **kwargs):
            """Dummy attr method."""
            pass
        
        def node(self, *args, **kwargs):
            """Dummy node method."""
            pass
        
        def edge(self, *args, **kwargs):
            """Dummy edge method."""
            pass
        
        def render(self, *args, **kwargs):
            """Dummy render method."""
            raise ImportError("Graphviz is not installed")


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
        
        # Create a frame for the visualization
        self.visualization_frame = ttk.Frame(self)
        self.visualization_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a text widget for displaying the family tree
        self.text = tk.Text(self.visualization_frame, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(self.visualization_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(self.visualization_frame, orient=tk.HORIZONTAL, command=self.text.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Create a label for displaying the image
        self.image_label = ttk.Label(self.visualization_frame)
        self.image = None
        
        # Check if Graphviz is available
        if not GRAPHVIZ_AVAILABLE:
            self.text.insert(tk.END, _("Graphviz is not installed. Please install it to visualize the family tree graphically."))
            self.text.insert(tk.END, "\n\n")
            self.text.insert(tk.END, _("You can install it with: pip install graphviz"))
            self.text.insert(tk.END, "\n")
            self.text.insert(tk.END, _("You may also need to install the Graphviz system package."))
    
    def display_tree(self, tree: FamilyTree) -> None:
        """
        Display a family tree.
        
        Args:
            tree: The family tree to display
        """
        # Clear the text widget
        self.text.delete(1.0, tk.END)
        
        # Display the text representation of the tree
        self.text.insert(tk.END, tree.visualize())
        
        # If Graphviz is available, also display a graphical representation
        if GRAPHVIZ_AVAILABLE:
            try:
                # Create a temporary file for the image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Create a new directed graph
                dot = Digraph(comment='Family Tree', strict=False)
                dot.attr(rankdir='TB', size='8,8')
                
                # Add nodes for each person in the family tree
                # Start with the deceased person
                deceased = tree.deceased
                dot.node(deceased.name, label=deceased.name, shape='box' if deceased.gender == Gender.MALE else 'ellipse',
                         color='red', style='filled', fillcolor='lightgray')
                
                # Add all relatives
                
                # Add fathers
                for father in tree.get_relatives(RelationshipType.FATHER):
                    dot.node(father.name, label=father.name, shape='box', color='blue')
                    dot.edge(father.name, deceased.name, color='blue', label=_('father'))
                
                # Add mothers
                for mother in tree.get_relatives(RelationshipType.MOTHER):
                    dot.node(mother.name, label=mother.name, shape='ellipse', color='green')
                    dot.edge(mother.name, deceased.name, color='green', label=_('mother'))
                
                # Add brothers
                for brother in tree.get_relatives(RelationshipType.BROTHER):
                    dot.node(brother.name, label=brother.name, shape='box', color='black')
                    # Connect to parents if available
                    if deceased.father and brother.father and deceased.father.name == brother.father.name:
                        dot.edge(deceased.father.name, brother.name, color='blue', label=_('father'))
                    if deceased.mother and brother.mother and deceased.mother.name == brother.mother.name:
                        dot.edge(deceased.mother.name, brother.name, color='green', label=_('mother'))
                
                # Add sisters
                for sister in tree.get_relatives(RelationshipType.SISTER):
                    dot.node(sister.name, label=sister.name, shape='ellipse', color='black')
                    # Connect to parents if available
                    if deceased.father and sister.father and deceased.father.name == sister.father.name:
                        dot.edge(deceased.father.name, sister.name, color='blue', label=_('father'))
                    if deceased.mother and sister.mother and deceased.mother.name == sister.mother.name:
                        dot.edge(deceased.mother.name, sister.name, color='green', label=_('mother'))
                
                # Add sons
                for son in tree.get_relatives(RelationshipType.SON):
                    dot.node(son.name, label=son.name, shape='box', color='black')
                    dot.edge(deceased.name, son.name, color='black', label=_('son'))
                
                # Add daughters
                for daughter in tree.get_relatives(RelationshipType.DAUGHTER):
                    dot.node(daughter.name, label=daughter.name, shape='ellipse', color='black')
                    dot.edge(deceased.name, daughter.name, color='black', label=_('daughter'))
                
                # Add spouses
                for spouse in deceased.spouses:
                    dot.node(spouse.name, label=spouse.name, 
                             shape='box' if spouse.gender == Gender.MALE else 'ellipse', 
                             color='red')
                    dot.edge(deceased.name, spouse.name, color='red', style='dashed', 
                             dir='none', label=_('spouse'))
                
                # Render the graph
                dot.render(temp_path, format='png', cleanup=True)
                
                # Display the image
                self.image = tk.PhotoImage(file=temp_path + '.png')
                self.image_label.configure(image=self.image)
                self.image_label.pack(fill=tk.BOTH, expand=True)
                
                # Remove the temporary file
                os.unlink(temp_path + '.png')
                
            except Exception as e:
                self.text.insert(tk.END, "\n\n")
                self.text.insert(tk.END, _("Error generating graphical representation: {error}", error=str(e)))
