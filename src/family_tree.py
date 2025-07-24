"""
This module provides a FamilyTree implementation to represent family relationships
and support Islamic inheritance calculations.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import auto, Enum
from typing import Dict, List, Optional, Set

from .person import Gender, Person


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
    # Nephews and nieces
    NEPHEW = "nephew"  # e.g. Father's brother's son, grnadfather's brother son, etc.
    NIECE = "niece"  # e.g. Mother's sister's daughter
    # children
    SON = "son"
    DAUGHTER = "daughter"


CHILDREN_RELATIONSHIP_TYPE_MAPPING = {
    RelationshipType.FATHER: {
        Gender.MALE: RelationshipType.BROTHER,
        Gender.FEMALE: RelationshipType.SISTER,
    },
    RelationshipType.GRANDFATHER: {
        Gender.MALE: RelationshipType.UNCLE,
        Gender.FEMALE: RelationshipType.AUNT,
    },
    RelationshipType.MOTHER: {
        Gender.MALE: RelationshipType.BROTHER,
        Gender.FEMALE: RelationshipType.SISTER,
    },
    RelationshipType.GRANDMOTHER: {
        Gender.MALE: RelationshipType.UNCLE,
        Gender.FEMALE: RelationshipType.AUNT,
    },
    RelationshipType.BROTHER: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.SISTER: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.UNCLE: {
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    RelationshipType.AUNT: {
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    RelationshipType.NEPHEW: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.NIECE: {
        Gender.MALE: RelationshipType.NEPHEW,
        Gender.FEMALE: RelationshipType.NIECE,
    },
    RelationshipType.COUSIN: {
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    RelationshipType.SON: {
        Gender.MALE: RelationshipType.SON,
        Gender.FEMALE: RelationshipType.DAUGHTER,
    },
    RelationshipType.DAUGHTER: {
        Gender.MALE: RelationshipType.SON,
        Gender.FEMALE: RelationshipType.DAUGHTER,
    },
}


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
        return cls(father, RelationshipType.FATHER, [RelationshipType.FATHER], None)

    @classmethod
    def mother(cls, mother: Person) -> "Relationship":
        """Create a father relationship."""
        return cls(mother, RelationshipType.MOTHER, [RelationshipType.MOTHER], None)

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
        self._process_descendants()
        self._process_ancestors()

    def _process_children(
        self, person: Person, relationship: Relationship
    ) -> List[Relationship]:
        stack = []
        for child in person.children:
            lineage = (
                RelationshipType.SON
                if child.gender == Gender.MALE
                else RelationshipType.DAUGHTER
            )
            stack.append(
                Relationship(
                    child,
                    CHILDREN_RELATIONSHIP_TYPE_MAPPING[relationship.relationship_type][
                        child.gender
                    ],
                    relationship.lineage + [lineage],
                    relationship.lineage_type,
                )
            )
        return stack

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
            if id(relationship.person) in seen:
                continue

            # add current relationship to the family tree
            self._relationships[relationship.relationship_type].add(relationship)
            seen.add(id(relationship.person))

            # explore relatives of the current person
            lineage_type = relationship.lineage_type
            if not lineage_type:
                lineage_type = (
                    LineageType.PATERNAL
                    if relationship.relationship_type == RelationshipType.FATHER
                    else LineageType.MATERNAL
                )
            if relationship.is_ancestor and relationship.person.father:
                stack.append(
                    Relationship(
                        relationship.person.father,
                        RelationshipType.GRANDFATHER,
                        relationship.lineage + [RelationshipType.FATHER],
                        lineage_type,
                    )
                )
            if relationship.is_ancestor and relationship.person.mother:
                stack.append(
                    Relationship(
                        relationship.person.mother,
                        RelationshipType.GRANDMOTHER,
                        relationship.lineage + [RelationshipType.MOTHER],
                        lineage_type,
                    )
                )
            stack.extend(
                [
                    rel
                    for rel in self._process_children(relationship.person, relationship)
                    if rel.person not in seen
                ]
            )

    def _process_descendants(self) -> None:
        """
        Process the descendants of a person and add them to the family tree.
        """
        stack = [
            Relationship(
                child,
                (
                    RelationshipType.SON
                    if child.gender == Gender.MALE
                    else RelationshipType.DAUGHTER
                ),
                [RelationshipType.SON],
                None,
            )
            for child in self.deceased.children
        ]
        seen = set()
        while stack:
            relationship = stack.pop()
            if id(relationship.person) in seen:
                raise ValueError("Circular reference detected")

            # add current relationship to the family tree
            self._relationships[relationship.relationship_type].add(relationship)
            seen.add(id(relationship.person))

            # explore descendants of the current person
            stack.extend(
                [
                    Relationship(
                        grandchild,
                        (
                            RelationshipType.SON
                            if grandchild.gender == Gender.MALE
                            else RelationshipType.DAUGHTER
                        ),
                        [RelationshipType.SON],
                        None,
                    )
                    for grandchild in relationship.person.children
                ]
            )

    def visualize(self) -> str:
        """
        Generate a visual representation of the family tree.

        Returns:
            A string representation of the family tree, where each line represents a relationship.
        """
        lines = []
        
        # Add the deceased person as the root
        lines.append(f"Deceased: {self.deceased.name} ({self.deceased.gender.value})")
        lines.append("")
        
        # Add ancestors
        lines.append("=== Ancestors ===")
        
        # Parents
        father = self.get_relatives(RelationshipType.FATHER)
        if father:
            father_person = list(father)[0]
            lines.append(f"Father: {father_person.name}")
        
        mother = self.get_relatives(RelationshipType.MOTHER)
        if mother:
            mother_person = list(mother)[0]
            lines.append(f"Mother: {mother_person.name}")
        
        # Grandparents
        grandfathers = self.get_relatives(RelationshipType.GRANDFATHER)
        if grandfathers:
            lines.append("Grandfathers:")
            for grandfather in grandfathers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandfather.name}")
        
        grandmothers = self.get_relatives(RelationshipType.GRANDMOTHER)
        if grandmothers:
            lines.append("Grandmothers:")
            for grandmother in grandmothers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandmother.name}")
        
        lines.append("")
        
        # Add siblings
        brothers = self.get_relatives(RelationshipType.BROTHER)
        sisters = self.get_relatives(RelationshipType.SISTER)
        if brothers or sisters:
            lines.append("=== Siblings ===")
            
            if brothers:
                lines.append("Brothers:")
                for brother in brothers:
                    lines.append(f"  - {brother.name}")
            
            if sisters:
                lines.append("Sisters:")
                for sister in sisters:
                    lines.append(f"  - {sister.name}")
            
            lines.append("")
        
        # Add extended family
        uncles = self.get_relatives(RelationshipType.UNCLE)
        aunts = self.get_relatives(RelationshipType.AUNT)
        cousins = self.get_relatives(RelationshipType.COUSIN)
        
        if uncles or aunts or cousins:
            lines.append("=== Extended Family ===")
            
            if uncles:
                lines.append("Uncles:")
                for uncle in uncles:
                    lines.append(f"  - {uncle.name}")
            
            if aunts:
                lines.append("Aunts:")
                for aunt in aunts:
                    lines.append(f"  - {aunt.name}")
            
            if cousins:
                lines.append("Cousins:")
                for cousin in cousins:
                    lines.append(f"  - {cousin.name} ({cousin.gender.value})")
            
            lines.append("")
        
        # Add descendants
        sons = self.get_relatives(RelationshipType.SON)
        daughters = self.get_relatives(RelationshipType.DAUGHTER)
        
        if sons or daughters:
            lines.append("=== Descendants ===")
            
            if sons:
                lines.append("Sons:")
                for son in sons:
                    lines.append(f"  - {son.name}")
                    # Add grandchildren
                    if son.children:
                        lines.append("    Grandchildren:")
                        for grandchild in son.children:
                            gender = "Son" if grandchild.gender == Gender.MALE else "Daughter"
                            lines.append(f"      - {grandchild.name} ({gender})")
            
            if daughters:
                lines.append("Daughters:")
                for daughter in daughters:
                    lines.append(f"  - {daughter.name}")
                    # Add grandchildren
                    if daughter.children:
                        lines.append("    Grandchildren:")
                        for grandchild in daughter.children:
                            gender = "Son" if grandchild.gender == Gender.MALE else "Daughter"
                            lines.append(f"      - {grandchild.name} ({gender})")
        
        return "\n".join(lines)
