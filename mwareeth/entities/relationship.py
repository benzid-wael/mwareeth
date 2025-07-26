from dataclasses import dataclass
from enum import Enum
from typing import List

from .person import Person


class RelationshipType(Enum):
    """Enumerates possible relationships between family members."""

    SELF = "self"

    # Ancestors
    FATHER = "father"
    MOTHER = "mother"
    GRANDFATHER = "grandfather"
    GRANDMOTHER = "grandmother"

    # Siblings
    BROTHER_FULL = "brother_full"
    BROTHER_PARENTAL = "brother_parental"
    BROTHER_MATERNAL = "brother_maternal"
    SISTER_FULL = "sister_full"
    SISTER_PARENTAL = "sister_parental"
    SISTER_MATERNAL = "sister_maternal"

    # Extended family
    PARENTAL_UNCLE_FULL = "parental_uncle_full"
    PARENTAL_UNCLE_PARENTAL = "parental_uncle_parental"
    PARENTAL_UNCLE_MATERNAL = "parental_uncle_maternal"
    PARENTAL_AUNT_FULL = "parental_aunt_full"
    PARENTAL_AUNT_PARENTAL = "parental_aunt_parental"
    PARENTAL_AUNT_MATERNAL = "parental_aunt_maternal"
    MATERNAL_UNCLE_FULL = "maternal_uncle_full"
    MATERNAL_UNCLE_PARENTAL = "maternal_uncle_parental"
    MATERNAL_UNCLE_MATERNAL = "maternal_uncle_maternal"
    MATERNAL_AUNT_FULL = "maternal_aunt_full"
    MATERNAL_AUNT_PARENTAL = "maternal_aunt_parental"
    MATERNAL_AUNT_MATERNAL = "maternal_aunt_maternal"

    # Cousins
    COUSIN = "cousin"

    # Nephews and nieces
    NEPHEW = "nephew"
    NIECE = "niece"

    # Children
    SON = "son"
    DAUGHTER = "daughter"
    GRANDSON = "grandson"
    GRANDDAUGHTER = "granddaughter"

    HUSBAND = "husband"
    WIFE = "wife"

    def __repr__(self) -> str:
        return self.name


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
    Represents a relationship between two people in the family tree.

    This class is used for family tree navigation and relationship identification.
    It contains information about a person, their relationship to the deceased,
    and the lineage path that led to this relationship.

    While the Relationship class represents connections between people in the family tree,
    the Heir class specifically represents inheritance rights according to Islamic law.
    These two classes work together but serve different purposes:
    - Relationship: Used for family tree navigation and relationship identification
    - Heir: Used for inheritance calculations based on Islamic law

    To convert a Relationship to an Heir for inheritance calculations, use the
    Heir.from_relationship() method.

    Attributes:
        person: The person in the relationship
        relationship_type: The type of relationship (father, mother, etc.)
        lineage: The path of relationships that led to this relationship
    """

    person: Person
    relationship_type: RelationshipType
    lineage: List[RelationshipType]

    @classmethod
    def father(cls, father: Person) -> "Relationship":
        """Create a father relationship."""
        return cls(father, RelationshipType.FATHER, [RelationshipType.FATHER])

    @classmethod
    def mother(cls, mother: Person) -> "Relationship":
        """Create a mother relationship."""
        return cls(mother, RelationshipType.MOTHER, [RelationshipType.MOTHER])

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

    @property
    def is_sibling(self) -> bool:
        """Check if the relationship is a sibling (brother, sister, etc.)."""
        return self.relationship_type in {
            RelationshipType.BROTHER_FULL,
            RelationshipType.BROTHER_PARENTAL,
            RelationshipType.BROTHER_MATERNAL,
            RelationshipType.SISTER_FULL,
            RelationshipType.SISTER_PARENTAL,
            RelationshipType.SISTER_MATERNAL,
        }

    @property
    def is_uncle_or_aunt(self) -> bool:
        """Check if the relationship is an uncle or aunt."""
        return self.relationship_type in {
            RelationshipType.PARENTAL_UNCLE_FULL,
            RelationshipType.PARENTAL_UNCLE_PARENTAL,
            RelationshipType.PARENTAL_UNCLE_MATERNAL,
            RelationshipType.PARENTAL_AUNT_FULL,
            RelationshipType.PARENTAL_AUNT_PARENTAL,
            RelationshipType.PARENTAL_AUNT_MATERNAL,
            RelationshipType.MATERNAL_UNCLE_FULL,
            RelationshipType.MATERNAL_UNCLE_PARENTAL,
            RelationshipType.MATERNAL_UNCLE_MATERNAL,
            RelationshipType.MATERNAL_AUNT_FULL,
            RelationshipType.MATERNAL_AUNT_PARENTAL,
            RelationshipType.MATERNAL_AUNT_MATERNAL,
        }

    @property
    def is_cousin(self) -> bool:
        """Check if the relationship is a cousin."""
        return self.relationship_type is RelationshipType.COUSIN

    @property
    def is_nephew_or_niece(self) -> bool:
        """Check if the relationship is a nephew or niece."""
        return self.relationship_type in {
            RelationshipType.NEPHEW,
            RelationshipType.NIECE,
        }

    def __hash__(self) -> int:
        """Generate a hash based on the lineage path."""
        return "-".join(rel.name for rel in self.lineage).__hash__()

    def __repr__(self) -> str:
        return f"<Relationship: person:{self.person.name}, relation:{self.relationship_type.name}>"
