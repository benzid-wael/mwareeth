"""
This module provides visualizers for family trees.
"""

import importlib.util
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

from .entities.family_tree import FamilyTree, RelationshipType
from .entities.person import Gender
from .i18n import _, pgettext

GRAPHVIZ_AVAILABLE = importlib.util.find_spec("graphviz") is not None


class FamilyTreeVisualizer(ABC):
    """
    Abstract base class for family tree visualizers.

    This class defines the interface for visualizing family trees.
    Subclasses must implement the visualize method.
    """

    def __init__(self, family_tree: FamilyTree):
        """
        Initialize the visualizer with a family tree.

        Args:
            family_tree: The family tree to visualize
        """
        self.family_tree = family_tree

    @abstractmethod
    def visualize(self) -> str:
        """
        Visualize the family tree.

        Returns:
            A string representation of the visualization
        """
        pass


class FamilyTreeTextVisualizer(FamilyTreeVisualizer):
    """
    Visualizer that generates a text representation of a family tree.
    """

    def visualize(self) -> str:
        """
        Generate a text representation of the family tree.

        Returns:
            A string representation of the family tree, where each line represents a relationship.
        """
        lines = []

        # Add the deceased person as the root
        lines.append(
            f"{_('Deceased')}: {self.family_tree.deceased.name} ({self.family_tree.deceased.gender.value})"
        )
        lines.append("")

        # Add ancestors
        lines.append(f"=== {_('Ancestors')} ===")

        # Parents
        father = self.family_tree.get_relatives(RelationshipType.FATHER)
        if father:
            father_person = list(father)[0]
            lines.append(f"{_('father').capitalize()}: {father_person.name}")

        mother = self.family_tree.get_relatives(RelationshipType.MOTHER)
        if mother:
            mother_person = list(mother)[0]
            lines.append(f"{_('mother').capitalize()}: {mother_person.name}")

        # Grandparents
        grandfathers = self.family_tree.get_relatives(RelationshipType.GRANDFATHER)
        if grandfathers:
            lines.append(f"{_('Grandfathers')}:")
            for grandfather in grandfathers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandfather.name}")

        grandmothers = self.family_tree.get_relatives(RelationshipType.GRANDMOTHER)
        if grandmothers:
            lines.append(f"{_('Grandmothers')}:")
            for grandmother in grandmothers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandmother.name}")

        lines.append("")

        # Add siblings
        brothers = self.family_tree.get_relatives(RelationshipType.BROTHER)
        sisters = self.family_tree.get_relatives(RelationshipType.SISTER)
        if brothers or sisters:
            lines.append(f"=== {_('Siblings')} ===")

            if brothers:
                lines.append(f"{_('Brothers')}:")
                for brother in brothers:
                    lines.append(f"  - {brother.name}")

            if sisters:
                lines.append(f"{_('Sisters')}:")
                for sister in sisters:
                    lines.append(f"  - {sister.name}")

            lines.append("")

        # Add extended family
        uncles = self.family_tree.get_relatives(RelationshipType.UNCLE)
        aunts = self.family_tree.get_relatives(RelationshipType.AUNT)
        cousins = self.family_tree.get_relatives(RelationshipType.COUSIN)

        if uncles or aunts or cousins:
            lines.append(f"=== {_('Extended Family')} ===")

            if uncles:
                lines.append(f"{_('Uncles')}:")
                for uncle in uncles:
                    lines.append(f"  - {uncle.name}")

            if aunts:
                lines.append(f"{_('Aunts')}:")
                for aunt in aunts:
                    lines.append(f"  - {aunt.name}")

            if cousins:
                lines.append(f"{_('Cousins')}:")
                for cousin in cousins:
                    lines.append(f"  - {cousin.name} ({cousin.gender.value})")

            lines.append("")

        # Add descendants
        sons = self.family_tree.get_relatives(RelationshipType.SON)
        daughters = self.family_tree.get_relatives(RelationshipType.DAUGHTER)

        if sons or daughters:
            lines.append(f"=== {_('Descendants')} ===")

            if sons:
                lines.append(f"{_('Sons')}:")
                for son in sons:
                    lines.append(f"  - {son.name}")
                    # Add grandchildren
                    if son.children:
                        lines.append(f"    {_('Grandchildren')}:")
                        for grandchild in son.children:
                            gender = (
                                _("Son")
                                if grandchild.gender == Gender.MALE
                                else _("Daughter")
                            )
                            lines.append(f"      - {grandchild.name} ({gender})")

            if daughters:
                lines.append(f"{_('Daughters')}:")
                for daughter in daughters:
                    lines.append(f"  - {daughter.name}")
                    # Add grandchildren
                    if daughter.children:
                        lines.append(f"    {_('Grandchildren')}:")
                        for grandchild in daughter.children:
                            gender = (
                                _("Son")
                                if grandchild.gender == Gender.MALE
                                else _("Daughter")
                            )
                            lines.append(f"      - {grandchild.name} ({gender})")

        return "\n".join(lines)


class FamilyTreeGraphvizVisualizer(FamilyTreeVisualizer):
    """
    Visualizer that generates a graphical representation of a family tree using Graphviz.
    """

    def __init__(self, family_tree: FamilyTree):
        """
        Initialize the visualizer with a family tree.

        Args:
            family_tree: The family tree to visualize
            builder: The FamilyTreeBuilder instance that contains all people (not just those in the tree)
        """
        super().__init__(family_tree)

    def visualize(self) -> str:
        """
        Generate a graphical representation of the family tree.

        Returns:
            A string representation of the Graphviz DOT source
        """
        if not GRAPHVIZ_AVAILABLE:
            return "Graphviz is not installed. Please install it to visualize the family tree graphically."

        Digraph = importlib.import_module("graphviz").Digraph

        # Create a new directed graph
        dot = Digraph(comment=_("Family Tree"), strict=False)
        dot.attr(rankdir="TB", size="8,8")

        # Collect people from the family tree
        people = {person.name: person for person in self.family_tree.get_all_members()}

        # Add nodes for each person
        for name, person in people.items():
            # Set node attributes based on gender
            shape = "box" if person.gender == Gender.MALE else "ellipse"

            # Set color based on whether the person is deceased
            color = "red" if person == self.family_tree.deceased else "black"

            # Create label with person's details
            label = f"{name}"
            if person.birth_year:
                prefix = (
                    pgettext("male", "Born")
                    if person.gender == Gender.MALE
                    else pgettext("female", "Born")
                )
                label += f"\n{prefix}: {person.birth_year}"
            if person.death_year:
                prefix = (
                    pgettext("male", "Died")
                    if person.gender == Gender.MALE
                    else pgettext("female", "Died")
                )
                label += f"\n{prefix}: {person.death_year}"

            # Add the node
            dot.node(
                name,
                label=label,
                shape=shape,
                color=color,
                style="filled" if person == self.family_tree.deceased else "",
                fillcolor="lightgray" if person == self.family_tree.deceased else "",
            )

        # Add edges for parent-child relationships
        for name, person in people.items():
            # Add edge to father
            if person.father and person.father.name in people:
                dot.edge(person.father.name, name, color="blue", label=_("father"))

            # Add edge to mother
            if person.mother and person.mother.name in people:
                dot.edge(person.mother.name, name, color="green", label=_("mother"))

        # Add edges for spousal relationships
        for name, person in people.items():
            for spouse in person.spouses:
                if spouse.name in people and name < spouse.name:  # Only add once
                    label = (
                        pgettext("male", "spouse")
                        if person.gender == Gender.MALE
                        else pgettext("female", "spouse")
                    )
                    dot.edge(
                        name,
                        spouse.name,
                        color="red",
                        style="dashed",
                        dir="none",
                        label=label,
                    )

        return dot.source

    def render(self, path: Optional[str] = None, view: bool = False) -> str:
        """
        Render the family tree visualization to a file.

        Args:
            path: The path to save the rendered file (without extension)
            view: Whether to open the rendered file

        Returns:
            The path to the rendered file
        """
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError(
                "Graphviz is not installed. Please install it to visualize the family tree graphically."
            )

        # Create a temporary file if no path is provided
        if not path:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                path = temp_file.name

        Digraph = importlib.import_module("graphviz").Digraph

        # Create a new directed graph
        dot = Digraph(comment=_("Family Tree"), strict=False)
        dot.attr(rankdir="TB", size="8,8")

        # Collect people from the family tree
        people = {person.name: person for person in self.family_tree.get_all_members()}

        # Add nodes for each person
        for name, person in people.items():
            # Set node attributes based on gender
            shape = "box" if person.gender == Gender.MALE else "ellipse"

            # Set color based on whether the person is deceased
            color = "red" if person == self.family_tree.deceased else "black"

            # Create label with person's details
            label = f"{name}"
            if person.birth_year:
                prefix = (
                    pgettext("male", "Born")
                    if person.gender == Gender.MALE
                    else pgettext("female", "Born")
                )
                label += f"\n{prefix}: {person.birth_year}"
            if person.death_year:
                prefix = (
                    pgettext("male", "Died")
                    if person.gender == Gender.MALE
                    else pgettext("female", "Died")
                )
                label += f"\n{prefix}: {person.death_year}"

            # Add the node
            dot.node(
                name,
                label=label,
                shape=shape,
                color=color,
                style="filled" if person == self.family_tree.deceased else "",
                fillcolor="lightgray" if person == self.family_tree.deceased else "",
            )

        # Add edges for parent-child relationships
        for name, person in people.items():
            # Add edge to father
            if person.father and person.father.name in people:
                dot.edge(person.father.name, name, color="blue", label=_("father"))

            # Add edge to mother
            if person.mother and person.mother.name in people:
                dot.edge(person.mother.name, name, color="green", label=_("mother"))

        # Add edges for spousal relationships
        for name, person in people.items():
            for spouse in person.spouses:
                if spouse.name in people and name < spouse.name:  # Only add once
                    label = (
                        pgettext("male", "spouse")
                        if person.gender == Gender.MALE
                        else pgettext("female", "spouse")
                    )
                    dot.edge(
                        name,
                        spouse.name,
                        color="red",
                        style="dashed",
                        dir="none",
                        label=label,
                    )

        # Render the graph
        try:
            # Try to render and display the graph
            output_path = dot.render(path, format="png", view=view, cleanup=True)
            return output_path
        except Exception as e:
            # If rendering fails, just return the DOT source
            raise RuntimeError(f"Could not render the graph: {e}")
