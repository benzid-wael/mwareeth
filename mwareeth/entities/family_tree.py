"""
This module provides a FamilyTree implementation to represent family relationships
and support Islamic inheritance calculations.
"""

import itertools
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set

# Import the translator if available, otherwise use a simple translation function
from .person import Gender, Person
from .relationship import Relationship, RelationshipType


class LineageType(Enum):
    """The type of lineage."""

    FULL = 1
    PARENTAL = 2
    MATERNAL = 3


class LineageOperation(Enum):
    """The operation to perform on the lineage."""

    PUSH_RELATIONSHIP = 1
    POP_THEN_PUSH_RELATIONSHIP = 2
    PUSH_PARENTAL_RELATIONSHIP = 3


@dataclass(frozen=True)
class RelationshipConfig:
    """The configuration for a relationship."""

    relationship_type: RelationshipType
    lineage_operation: LineageOperation


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

    @classmethod
    def change_focal_point(cls, person: Person) -> "FamilyTree":
        return cls(person)

    def get_relatives(self, relationship_type: RelationshipType) -> Set[Person]:
        """
        Get all relatives of a specific relationship type.

        Args:
            relationship_type: The type of relationship to retrieve (e.g., siblings, descendants, etc.)

        Returns:
            A set of people who have the specified relationship to the deceased.
        """
        return {rel.person for rel in self._relationships[relationship_type]}

    def get_siblings(self) -> Set[Person]:
        """
        Get all siblings of the deceased.
        """
        return {
            rel.person
            for relations in self._relationships.values()
            for rel in relations
            if rel.is_sibling
        }

    def get_uncles_and_aunts(self) -> Set[Person]:
        """
        Get all uncles of the deceased.
        """
        return {
            rel.person
            for relations in self._relationships.values()
            for rel in relations
            if rel.is_uncle_or_aunt
        }

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

    def get_all_deceased(self) -> Set[Person]:
        """
        Get all deceased family members.

        Returns:
            A set of all deceased people in the family tree.
        """
        return {person for person in self.get_all_members() if person.is_deceased}

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
                )
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
                    )
                )

    def _process_ancestors(self) -> None:
        """
        Process the ancestors of the deceased person and add them to the family tree.

        This method traverses the family tree upward from the deceased person,
        adding parents, grandparents, and their descendants (siblings, uncles, etc.).
        """
        # Start with the parents of the deceased
        stack = [Relationship(self.deceased, RelationshipType.SELF, [])]
        # Keep track of processed people to avoid cycles
        seen = set()

        # Process the stack
        while stack:
            relationship = stack.pop()

            # Skip if already processed
            if id(relationship.person) in seen:
                continue

            # Add current relationship to the family tree
            self._relationships[relationship.relationship_type].add(relationship)
            seen.add(id(relationship.person))

            is_ancestor_including_self = relationship.is_ancestor or (
                relationship.relationship_type == RelationshipType.SELF
            )
            if is_ancestor_including_self:
                # Process parents
                stack.extend(self._create_parent_relationships(relationship))
                # Process siblings
                stack.extend(
                    [
                        rel
                        for rel in self._collect_siblings(relationship)
                        if id(rel.person) not in seen
                    ]
                )
            elif relationship.is_sibling or relationship.is_nephew_or_niece:
                # Siblings: process descendants
                stack.extend(
                    [
                        Relationship(
                            person=child,
                            relationship_type=(
                                RelationshipType.NEPHEW
                                if child.gender == Gender.MALE
                                else RelationshipType.NIECE
                            ),
                            lineage=relationship.lineage
                            + [
                                (
                                    RelationshipType.SON
                                    if child.gender == Gender.MALE
                                    else RelationshipType.DAUGHTER
                                )
                            ],
                        )
                        for child in relationship.person.children
                    ]
                )
            elif relationship.is_uncle_or_aunt or relationship.is_cousin:
                stack.extend(
                    [
                        Relationship(
                            person=cousin,
                            relationship_type=RelationshipType.COUSIN,
                            lineage=relationship.lineage
                            + [
                                (
                                    RelationshipType.SON
                                    if cousin.gender == Gender.MALE
                                    else RelationshipType.DAUGHTER
                                )
                            ],
                        )
                        for cousin in relationship.person.children
                    ]
                )

    def _create_parent_relationships(
        self, relationship: Relationship
    ) -> List[Relationship]:
        result = []
        if relationship.person.father:
            relationship_type = (
                RelationshipType.GRANDFATHER
                if relationship.is_ancestor
                else RelationshipType.FATHER
            )
            result.append(
                Relationship(
                    person=relationship.person.father,
                    relationship_type=relationship_type,
                    lineage=relationship.lineage + [RelationshipType.FATHER],
                )
            )
        if relationship.person.mother:
            relationship_type = (
                RelationshipType.GRANDMOTHER
                if relationship.is_ancestor
                else RelationshipType.MOTHER
            )
            result.append(
                Relationship(
                    person=relationship.person.mother,
                    relationship_type=relationship_type,
                    lineage=relationship.lineage + [RelationshipType.MOTHER],
                )
            )
        return result

    def _collect_siblings(self, relationship: Relationship) -> List[Relationship]:
        """
        Process sibling of a person
        """
        child_relationships = []
        person = relationship.person
        parental_brothers = set()
        maternal_brothers = set()
        if person.father:
            parental_brothers = {
                sibling for sibling in person.father.children if sibling != person
            }
        if person.mother:
            maternal_brothers = {
                sibling for sibling in person.mother.children if sibling != person
            }

        full_brothers = parental_brothers.intersection(maternal_brothers)
        parental_brothers = parental_brothers.difference(full_brothers)
        maternal_brothers = maternal_brothers.difference(full_brothers)

        for child, lineage_type in itertools.chain(
            zip(full_brothers, [LineageType.FULL] * len(full_brothers)),
            zip(parental_brothers, [LineageType.PARENTAL] * len(parental_brothers)),
            zip(maternal_brothers, [LineageType.MATERNAL] * len(maternal_brothers)),
        ):
            config = ANCESTORS_SIBLINGS_RELATIONSHIPS[relationship.relationship_type][
                lineage_type
            ][child.gender]
            # copy the lineage to avoid modifying the original
            new_lineage = relationship.lineage[:]
            match config.lineage_operation:
                case LineageOperation.PUSH_RELATIONSHIP:
                    new_lineage.append(config.relationship_type)
                case LineageOperation.POP_THEN_PUSH_RELATIONSHIP:
                    new_lineage.pop()
                    new_lineage.append(config.relationship_type)
                case LineageOperation.PUSH_PARENTAL_RELATIONSHIP:
                    relationship_type = (
                        RelationshipType.SON
                        if child.gender == Gender.MALE
                        else RelationshipType.DAUGHTER
                    )
                    new_lineage.append(relationship_type)
                case _:
                    raise ValueError(
                        f"Unknown lineage operation: {config.lineage_operation.name}"
                    )

            child_relationships.append(
                Relationship(
                    person=child,
                    relationship_type=config.relationship_type,
                    lineage=new_lineage,
                )
            )

        return child_relationships


ANCESTORS_SIBLINGS_RELATIONSHIPS = {
    RelationshipType.SELF: {
        # [] + FULL --> [BROTHER_FULL]
        LineageType.FULL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.BROTHER_FULL, LineageOperation.PUSH_RELATIONSHIP
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.SISTER_FULL, LineageOperation.PUSH_RELATIONSHIP
            ),
        },
        LineageType.PARENTAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.BROTHER_PARENTAL, LineageOperation.PUSH_RELATIONSHIP
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.SISTER_PARENTAL, LineageOperation.PUSH_RELATIONSHIP
            ),
        },
        LineageType.MATERNAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.BROTHER_MATERNAL, LineageOperation.PUSH_RELATIONSHIP
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.SISTER_MATERNAL, LineageOperation.PUSH_RELATIONSHIP
            ),
        },
    },
    RelationshipType.FATHER: {
        # [FATHER] + FULL --> [PARENTAL_UNCLE_FULL]
        LineageType.FULL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.PARENTAL_AUNT_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        # [FATHER] + PARENTAL --> [PARENTAL_UNCLE_PARENTAL]
        LineageType.PARENTAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.PARENTAL_AUNT_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.MATERNAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.PARENTAL_AUNT_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
    },
    RelationshipType.MOTHER: {
        # [MOTHER] + FULL --> [MATERNAL_UNCLE_FULL]
        LineageType.FULL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.PARENTAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.MATERNAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
    },
    RelationshipType.GRANDFATHER: {
        # [FATHER, FATHER] + FULL --> [FATHER, PARENTAL_UNCLE_FULL]
        LineageType.FULL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.PARENTAL_AUNT_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        # [FATHER, FATHER] + PARENTAL --> [FATHER, PARENTAL_UNCLE_PARENTAL]
        LineageType.PARENTAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.MATERNAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.PARENTAL_UNCLE_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
    },
    RelationshipType.GRANDMOTHER: {
        # [MOTHER, MOTHER] + FULL --> [MATERNAL_UNCLE_FULL]
        LineageType.FULL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_FULL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.PARENTAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_PARENTAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
        LineageType.MATERNAL: {
            Gender.MALE: RelationshipConfig(
                RelationshipType.MATERNAL_UNCLE_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
            Gender.FEMALE: RelationshipConfig(
                RelationshipType.MATERNAL_AUNT_MATERNAL,
                LineageOperation.POP_THEN_PUSH_RELATIONSHIP,
            ),
        },
    },
}
