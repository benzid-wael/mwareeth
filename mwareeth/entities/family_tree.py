"""
This module provides a FamilyTree implementation to represent family relationships
and support Islamic inheritance calculations.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import auto, Enum
from typing import Dict, List, Optional, Set

# Import the translator if available, otherwise use a simple translation function
from ..i18n import _
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
    
    # Nephews and nieces
    NEPHEW = "nephew"  # e.g. Brother's son
    NIECE = "niece"  # e.g. Sister's daughter
    
    # Children
    SON = "son"
    DAUGHTER = "daughter"
    # FIXME(wbenzid): add grandson and granddaughter


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
        Gender.MALE: RelationshipType.COUSIN,
        Gender.FEMALE: RelationshipType.COUSIN,
    },
    
    # Children's children remain sons/daughters
    RelationshipType.SON: {
        Gender.MALE: RelationshipType.SON,
        Gender.FEMALE: RelationshipType.DAUGHTER,
    },
    RelationshipType.DAUGHTER: {
        Gender.MALE: RelationshipType.SON,
        Gender.FEMALE: RelationshipType.DAUGHTER,
    },
}

# Set of ancestor relationship types for quick lookup
ANCESTOR_RELATIONSHIPS = {
    RelationshipType.FATHER,
    RelationshipType.GRANDFATHER,
    RelationshipType.MOTHER,
    RelationshipType.GRANDMOTHER,
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
        self._relationships: Dict[RelationshipType, Set[Relationship]] = defaultdict(set)
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

        This method populates the `_relationships` dictionary with relationships to the deceased.
        The dictionary maps each relationship type to a set of people who have that relationship.
        """
        self._process_descendants()
        self._process_ancestors()

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
        relationship_type = CHILDREN_RELATIONSHIP_MAPPING[parent_relationship.relationship_type][child.gender]
        
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
            RelationshipType.SON if child.gender == Gender.MALE else RelationshipType.DAUGHTER
        )
        lineage = parent_relationship.lineage + [child_lineage_type]
        
        return Relationship(
            person=child,
            relationship_type=relationship_type,
            lineage=lineage,
            lineage_type=lineage_type
        )

    def _process_children(
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
        parent_lineage_type = RelationshipType.FATHER if is_father else RelationshipType.MOTHER
        lineage = child_relationship.lineage + [parent_lineage_type]
        
        return Relationship(
            person=parent,
            relationship_type=relationship_type,
            lineage=lineage,
            lineage_type=child_relationship.lineage_type
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
            child_relationships = self._process_children(relationship.person, relationship)
            stack.extend([rel for rel in child_relationships if id(rel.person) not in seen])

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
                RelationshipType.SON if child.gender == Gender.MALE 
                else RelationshipType.DAUGHTER
            )
            stack.append(
                Relationship(
                    person=child,
                    relationship_type=relationship_type,
                    lineage=[relationship_type],
                    lineage_type=None
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
                    RelationshipType.SON if grandchild.gender == Gender.MALE 
                    else RelationshipType.DAUGHTER
                )
                stack.append(
                    Relationship(
                        person=grandchild,
                        relationship_type=relationship_type,
                        lineage=[relationship_type],
                        lineage_type=None
                    )
                )

    def visualize(self) -> str:
        """
        Generate a visual representation of the family tree.

        Returns:
            A string representation of the family tree, where each line represents a relationship.
        """
        lines = []
        
        # Add the deceased person as the root
        lines.append(f"{_('Deceased')}: {self.deceased.name} ({self.deceased.gender.value})")
        lines.append("")
        
        # Add ancestors
        lines.append(f"=== {_('Ancestors')} ===")
        
        # Parents
        father = self.get_relatives(RelationshipType.FATHER)
        if father:
            father_person = list(father)[0]
            lines.append(f"{_('father').capitalize()}: {father_person.name}")
        
        mother = self.get_relatives(RelationshipType.MOTHER)
        if mother:
            mother_person = list(mother)[0]
            lines.append(f"{_('mother').capitalize()}: {mother_person.name}")
        
        # Grandparents
        grandfathers = self.get_relatives(RelationshipType.GRANDFATHER)
        if grandfathers:
            lines.append(f"{_('Grandfathers')}:")
            for grandfather in grandfathers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandfather.name}")
        
        grandmothers = self.get_relatives(RelationshipType.GRANDMOTHER)
        if grandmothers:
            lines.append(f"{_('Grandmothers')}:")
            for grandmother in grandmothers:
                # Determine if paternal or maternal
                lines.append(f"  - {grandmother.name}")
        
        lines.append("")
        
        # Add siblings
        brothers = self.get_relatives(RelationshipType.BROTHER)
        sisters = self.get_relatives(RelationshipType.SISTER)
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
        uncles = self.get_relatives(RelationshipType.UNCLE)
        aunts = self.get_relatives(RelationshipType.AUNT)
        cousins = self.get_relatives(RelationshipType.COUSIN)
        
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
        sons = self.get_relatives(RelationshipType.SON)
        daughters = self.get_relatives(RelationshipType.DAUGHTER)
        
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
                            gender = _("Son") if grandchild.gender == Gender.MALE else _("Daughter")
                            lines.append(f"      - {grandchild.name} ({gender})")
            
            if daughters:
                lines.append(f"{_('Daughters')}:")
                for daughter in daughters:
                    lines.append(f"  - {daughter.name}")
                    # Add grandchildren
                    if daughter.children:
                        lines.append(f"    {_('Grandchildren')}:")
                        for grandchild in daughter.children:
                            gender = _("Son") if grandchild.gender == Gender.MALE else _("Daughter")
                            lines.append(f"      - {grandchild.name} ({gender})")
        
        return "\n".join(lines)
