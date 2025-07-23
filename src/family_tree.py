"""
This module provides a FamilyTree implementation to represent family relationships
and support Islamic inheritance calculations.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

from .person import Person


class LineageType(Enum):
    """Types of lineage for inheritance purposes."""

    PATERNAL = "paternal"  # Through father's line
    MATERNAL = "maternal"  # Through mother's line
    BOTH = "both"  # Through both parents (full siblings)


class RelationshipType(Enum):
    """Enumerates possible relationships between family members."""

    # Ancestors
    FATHER = "father"
    MOTHER = "mother"
    GRANDFATHER = "grandfather"
    GRANDMOTHER = "grandmother"


@dataclass(frozen=True)
class Relationship:
    """Represents a relationship between two people."""

    person: Person
    relationship_type: RelationshipType
    lineage: List[RelationshipType]
    lineage_type: Optional[LineageType] = None

    @classmethod
    def father(cls, father: Person) -> "Relationship":
        """Create a father relationship."""
        return cls(father, RelationshipType.FATHER, [], None)

    @classmethod
    def mother(cls, mother: Person) -> "Relationship":
        """Create a father relationship."""
        return cls(mother, RelationshipType.MOTHER, [], None)

    @property
    def degree(self) -> int:
        """Get the degree of the relationship."""
        return len(self.lineage)

    @property
    def is_ancestor(self) -> bool:
        """Check if the relationship is an ancestor."""
        return self.relationship_type in {
            RelationshipType.FATHER,
            RelationshipType.GRANDFATHER,
            RelationshipType.MOTHER,
            RelationshipType.GRANDMOTHER,
        }

    def __hash__(self) -> int:
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

    def _generate_relationships(self) -> None:
        """
        Generate relationships between family members.

        This method populates the `kinship` dictionary with relationships to the deceased.
        The dictionary maps each relationship to a set of people who have that relationship.
        """
        self._process_ancestors()

    def _process_ancestors(self) -> None:
        """
        Process the ancestors of a person and add them to the family tree.
        """
        stack = [
            Relationship.father(self.deceased.father) if self.deceased.father else None,
            Relationship.mother(self.deceased.mother) if self.deceased.mother else None,
        ]
        stack = [rel for rel in stack if rel is not None]
        seen = {id(self.deceased)}
        while stack:
            relationship = stack.pop()
            if id(relationship.person) not in seen:
                seen.add(id(relationship.person))
                self._relationships[relationship.relationship_type].add(relationship)
                lineage_type = relationship.lineage_type
                if not lineage_type:
                    lineage_type = (
                        LineageType.PATERNAL
                        if relationship.relationship_type == RelationshipType.FATHER
                        else LineageType.MATERNAL
                    )
                if relationship.person.father and relationship.is_ancestor:
                    stack.append(
                        Relationship(
                            relationship.person.father,
                            RelationshipType.GRANDFATHER,
                            relationship.lineage + [RelationshipType.FATHER],
                            lineage_type,
                        )
                    )
                if relationship.person.mother and relationship.is_ancestor:
                    stack.append(
                        Relationship(
                            relationship.person.mother,
                            RelationshipType.GRANDMOTHER,
                            relationship.lineage + [RelationshipType.MOTHER],
                            lineage_type,
                        )
                    )
