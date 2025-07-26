"""
This module provides a FamilyTree implementation to represent family relationships
and support Islamic inheritance calculations.
"""

import itertools
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Set

# Import the translator if available, otherwise use a simple translation function
from .person import Gender, Person

# ---- Enums ----


class LineageType(Enum):
    """Types of lineage for inheritance purposes."""

    BOTH = auto()  # Through both parents (full siblings)
    PATERNAL = auto()  # Through father's line
    MATERNAL = auto()  # Through mother's line


class RelationshipType(Enum):
    """Enumerates possible relationships between family members."""

    # Ancestors
    FATHER = "father"
    MOTHER = "mother"
    GRANDFATHER = "grandfather"
    GRANDMOTHER = "grandmother"

    # Siblings
    BROTHER = "brother"
    SISTER = "sister"

    # Extended family
    UNCLE = "uncle"  # e.g. Father's brother
    AUNT = "aunt"  # e.g. Father's sister

    # Cousins
    COUSIN = "cousin"  # e.g. Father's brother's child, mother's sister's child
    COUSIN_SON = "cousin son"  # e.g. Father's brother's son
    COUSIN_DAUGHTER = "cousin daughter"  # e.g. Father's brother's daughter

    # Nephews and nieces
    NEPHEW = "nephew"  # e.g. Brother's son
    NIECE = "niece"  # e.g. Sister's daughter

    # Children
    SON = "son"
    DAUGHTER = "daughter"
    GRANDSON = "grandson"
    GRANDDAUGHTER = "granddaughter"

    HUSBAND = "husband"
    WIFE = "wife"


# ---- Relationship Mappings ----

# Maps parent relationship types to their children's relationship types based on gender
CHILDREN_RELATIONSHIP_MAPPING = {
    # Parent's children become siblings
    RelationshipType.FATHER: {
        Gender.MALE: RelationshipType.BROTHER,
        Gender.FEMALE: RelationshipType.SISTER,
    },
    RelationshipType.MOTHER: {
        Gender.MALE: RelationshipType.BROTHER,
        Gender.FEMALE: RelationshipType.SISTER,
    },
    # Grandparent's children become uncles/aunts
    RelationshipType.GRANDFATHER: {
        Gender.MALE: RelationshipType.UNCLE,
        Gender.FEMALE: RelationshipType.AUNT,
    },
    RelationshipType.GRANDMOTHER: {
        Gender.MALE: RelationshipType.UNCLE,
        Gender.FEMALE: RelationshipType.AUNT,
    },
    # Sibling's children become nephews/nieces
    RelationshipType.BROTHER: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.SISTER: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    # Uncle/Aunt's children become cousins
    RelationshipType.UNCLE: {
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    RelationshipType.AUNT: {
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    # Nephew/Niece's children remain nephews/nieces
    RelationshipType.NEPHEW: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.NIECE: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    # Cousin's children remain cousins
    RelationshipType.COUSIN: {
        Gender.MALE: RelationshipType.COUSIN_SON,
        Gender.FEMALE: RelationshipType.COUSIN_DAUGHTER,
    },
    # Children's children remain sons/daughters
    RelationshipType.SON: {
        Gender.MALE: RelationshipType.GRANDSON,
        Gender.FEMALE: RelationshipType.GRANDDAUGHTER,
    },
    RelationshipType.DAUGHTER: {
        Gender.MALE: RelationshipType.GRANDSON,
        Gender.FEMALE: RelationshipType.GRANDDAUGHTER,
    },
}

# Set of ancestor relationship types for quick lookup
ANCESTOR_RELATIONSHIPS = {
    RelationshipType.FATHER,
    RelationshipType.GRANDFATHER,
    RelationshipType.MOTHER,
    RelationshipType.GRANDMOTHER,
}

DESCENDANT_RELATIONSHIPS = {
    RelationshipType.SON,
    RelationshipType.DAUGHTER,
    RelationshipType.GRANDSON,
    RelationshipType.GRANDDAUGHTER,
}


@dataclass(frozen=True)
class Relationship:
    """
    Represents a relationship between two people.

    Attributes:
        person: The person in the relationship
        relationship_type: The type of relationship (father, mother, etc.)
        lineage: The path of relationships that led to this relationship
        lineage_type: Whether the relationship is through paternal or maternal line
    """

    person: Person
    relationship_type: RelationshipType
    lineage: List[RelationshipType]
    lineage_type: Optional[LineageType] = None

    @classmethod
    def father(cls, father: Person) -> "Relationship":
        """Create a father relationship."""
        return cls(father, RelationshipType.FATHER, [RelationshipType.FATHER], None)

    @classmethod
    def mother(cls, mother: Person) -> "Relationship":
        """Create a mother relationship."""
        return cls(mother, RelationshipType.MOTHER, [RelationshipType.MOTHER], None)

    @property
    def degree(self) -> int:
        """Get the degree of the relationship (number of steps in the lineage)."""
        return len(self.lineage)

    @property
    def is_ancestor(self) -> bool:
        """Check if the relationship is an ancestor (father, mother, grandfather, grandmother)."""
        return self.relationship_type in ANCESTOR_RELATIONSHIPS

    @property
    def is_descendant(self) -> bool:
        """Check if the relationship is a descendant (son, daughter, etc.)."""
        return self.relationship_type in DESCENDANT_RELATIONSHIPS

    def __hash__(self) -> int:
        """Generate a hash based on the lineage path."""
        return "-".join(rel.name for rel in self.lineage).__hash__()


class FamilyTree:
    """
    Represents a family tree structure optimized for Islamic inheritance calculations.

    This class provides methods to:
    1. Add and manage family members
    2. Navigate relationships (siblings, descendants, ancestors, etc.)
    3. Identify heirs according to Islamic inheritance rules
    4. Support the calculation of inheritance shares
    """

    def __init__(self, deceased: Person):
        """
        Initialize a family tree, with a deceased person as the focal point.

        Args:
            deceased: The deceased person whose inheritance is being calculated
        """
        self.deceased = deceased
        self._relationships: Dict[RelationshipType, Set[Relationship]] = defaultdict(
            set
        )
        self._generate_relationships()

    def get_relatives(self, relationship_type: RelationshipType) -> Set[Person]:
        """
        Get all relatives of a specific relationship type.

        Args:
            relationship_type: The type of relationship to retrieve (e.g., siblings, descendants, etc.)

        Returns:
            A set of people who have the specified relationship to the deceased.
        """
        return {rel.person for rel in self._relationships[relationship_type]}

    def get_all_members(self) -> Set[Person]:
        """
        Get all members of the family tree.

        Returns:
            A list of all people in the family tree.
        """
        members = {self.deceased}
        queue = [self.deceased]
        while queue:
            person = queue.pop()
            for relative in itertools.chain(
                person.children, person.spouses, [person.father, person.mother]
            ):
                if relative and relative not in members:
                    members.add(relative)
                    queue.append(relative)
        return members

    def _generate_relationships(self) -> None:
        """
        Generate relationships between family members.

        This method populates the `_relationships` dictionary with relationships to the deceased.
        The dictionary maps each relationship type to a set of people who have that relationship.
        """
        self._process_descendants()
        self._process_ancestors()
        # process spouses
        relationship_type = (
            RelationshipType.HUSBAND
            if self.deceased.gender == Gender.FEMALE
            else RelationshipType.WIFE
        )
        for spouse in self.deceased.spouses:
            self._relationships[relationship_type].add(
                Relationship(
                    person=spouse,
                    relationship_type=relationship_type,
                    lineage=[relationship_type],
                    lineage_type=None,
                )
            )

    def _create_child_relationship(
        self, child: Person, parent_relationship: Relationship
    ) -> Relationship:
        """
        Create a relationship for a child based on the parent's relationship.

        Args:
            child: The child person
            parent_relationship: The relationship of the parent

        Returns:
            A new relationship object for the child
        """
        # Determine the relationship type based on the parent's relationship and child's gender
        relationship_type = CHILDREN_RELATIONSHIP_MAPPING[
            parent_relationship.relationship_type
        ][child.gender]

        # Determine the lineage type (which side of the family)
        lineage_type = parent_relationship.lineage_type

        # For direct children of the deceased, determine the lineage type
        if not lineage_type and parent_relationship.is_ancestor:
            lineage_type = (
                LineageType.PATERNAL
                if parent_relationship.relationship_type == RelationshipType.FATHER
                else LineageType.MATERNAL
            )

        # Create the child's lineage by extending the parent's lineage
        child_lineage_type = (
            RelationshipType.SON
            if child.gender == Gender.MALE
            else RelationshipType.DAUGHTER
        )
        lineage = parent_relationship.lineage + [child_lineage_type]

        return Relationship(
            person=child,
            relationship_type=relationship_type,
            lineage=lineage,
            lineage_type=lineage_type,
        )

    def _process_non_descendant_children(
        self, person: Person, relationship: Relationship
    ) -> List[Relationship]:
        """
        Process the children of a person and create relationships for them.

        Args:
            person: The person whose children to process
            relationship: The relationship of the person to the deceased

        Returns:
            A list of relationships for the children
        """
        child_relationships = []

        for child in person.children:
            child_relationship = self._create_child_relationship(child, relationship)
            child_relationships.append(child_relationship)

        return child_relationships

    def _create_parent_relationship(
        self, parent: Person, child_relationship: Relationship, is_father: bool
    ) -> Relationship:
        """
        Create a relationship for a parent based on the child's relationship.

        Args:
            parent: The parent person
            child_relationship: The relationship of the child
            is_father: Whether the parent is a father (True) or mother (False)

        Returns:
            A new relationship object for the parent
        """
        # Determine the relationship type (grandfather or grandmother)
        relationship_type = (
            RelationshipType.GRANDFATHER if is_father else RelationshipType.GRANDMOTHER
        )

        # Create the parent's lineage by extending the child's lineage
        parent_lineage_type = (
            RelationshipType.FATHER if is_father else RelationshipType.MOTHER
        )
        lineage = child_relationship.lineage + [parent_lineage_type]

        return Relationship(
            person=parent,
            relationship_type=relationship_type,
            lineage=lineage,
            lineage_type=child_relationship.lineage_type,
        )

    def _process_ancestors(self) -> None:
        """
        Process the ancestors of the deceased person and add them to the family tree.

        This method traverses the family tree upward from the deceased person,
        adding parents, grandparents, and their descendants (siblings, uncles, etc.).
        """
        # Start with the parents of the deceased
        stack = []
        if self.deceased.father:
            stack.append(Relationship.father(self.deceased.father))
        if self.deceased.mother:
            stack.append(Relationship.mother(self.deceased.mother))

        # Keep track of processed people to avoid cycles
        seen = {id(self.deceased)}

        # Process the stack
        while stack:
            relationship = stack.pop()

            # Skip if already processed
            if id(relationship.person) in seen:
                continue

            # Add current relationship to the family tree
            self._relationships[relationship.relationship_type].add(relationship)
            seen.add(id(relationship.person))

            # Process the person's parents (if they're an ancestor)
            if relationship.is_ancestor:
                # Add father if available
                if relationship.person.father:
                    father_relationship = self._create_parent_relationship(
                        relationship.person.father, relationship, True
                    )
                    stack.append(father_relationship)

                # Add mother if available
                if relationship.person.mother:
                    mother_relationship = self._create_parent_relationship(
                        relationship.person.mother, relationship, False
                    )
                    stack.append(mother_relationship)

            # Process the person's children (siblings, cousins, etc.)
            child_relationships = self._process_non_descendant_children(
                relationship.person, relationship
            )
            stack.extend(
                [rel for rel in child_relationships if id(rel.person) not in seen]
            )

    def _process_descendants(self) -> None:
        """
        Process the descendants of the deceased person and add them to the family tree.

        This method traverses the family tree downward from the deceased person,
        adding children, grandchildren, etc.
        """
        # Start with the children of the deceased
        stack = []
        for child in self.deceased.children:
            relationship_type = (
                RelationshipType.SON
                if child.gender == Gender.MALE
                else RelationshipType.DAUGHTER
            )
            stack.append(
                Relationship(
                    person=child,
                    relationship_type=relationship_type,
                    lineage=[relationship_type],
                    lineage_type=None,
                )
            )

        # Keep track of processed people to avoid cycles
        seen = set()

        # Process the stack
        while stack:
            relationship = stack.pop()
            # Check for circular references
            if id(relationship.person) in seen:
                raise ValueError("Circular reference detected in family tree")

            # Add current relationship to the family tree
            self._relationships[relationship.relationship_type].add(relationship)
            seen.add(id(relationship.person))

            # Process the person's children
            for grandchild in relationship.person.children:
                relationship_type = (
                    RelationshipType.GRANDSON
                    if grandchild.gender == Gender.MALE
                    else RelationshipType.GRANDDAUGHTER
                )
                lineage = relationship.lineage + [
                    (
                        RelationshipType.SON
                        if relationship.person.gender == Gender.MALE
                        else RelationshipType.DAUGHTER
                    )
                ]
                stack.append(
                    Relationship(
                        person=grandchild,
                        relationship_type=relationship_type,
                        lineage=lineage,
                        lineage_type=None,
                    )
                )

    def visualize(self) -> str:
        """
        Generate a visual representation of the family tree.

        Returns:
            A string representation of the family tree, where each line represents a relationship.
        """
        # Import here to avoid circular imports
        from ..visualizers import FamilyTreeTextVisualizer

        # Create a text visualizer and return its output
        visualizer = FamilyTreeTextVisualizer(self)
        return visualizer.visualize()
