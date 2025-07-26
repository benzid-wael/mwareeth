"""
This module provides a comprehensive way to represent family relationships
that makes Islamic inheritance calculations easier and more accurate.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Set


class Religion(Enum):
    ISLAM = "Islam"
    CHRISTIANITY = "christianity"
    JEWISH = "jewish"
    OTHER = "other"


class Gender(Enum):
    UNKNOWN = "unknown"
    MALE = "male"
    FEMALE = "female"


@dataclass
class Person:
    """Represents a person in the family tree."""

    name: str
    gender: Gender
    religion: Religion = Religion.ISLAM
    birth_year: Optional[int] = None
    death_year: Optional[int] = None

    # Relationships
    father: Optional["Person"] = None
    mother: Optional["Person"] = None
    spouses: Set["Person"] = field(default_factory=set)
    children: Set["Person"] = field(default_factory=set)

    @property
    def is_alive(self) -> bool:
        return self.death_year is None

    @property
    def is_deceased(self) -> bool:
        return not self.is_alive

    @property
    def fullname(self) -> str:
        fullname = self.name.lower()
        father = self.father
        while father:
            fullname = f"{father.name.lower()}>{fullname}"
            father = father.father
        return fullname

    def add_father(self, father: "Person") -> "Person":
        if self.father and self.father != father:
            raise ValueError("Cannot replace father!")
        self.father = father
        father.children.add(self)
        return self

    def add_mother(self, mother: "Person") -> "Person":
        if self.mother and self.mother != mother:
            raise ValueError("Cannot replace mother!")
        self.mother = mother
        mother.children.add(self)
        return self

    def add_spouse(self, spouse: "Person") -> "Person":
        # TODO: for now, let's ignore unknow gender
        if self.gender == spouse.gender:
            raise ValueError("Invalid gender")
        self.spouses.add(spouse)

        if self.gender == Gender.FEMALE and len(self.spouses) > 1:
            raise ValueError("Too many husbands")
        return self

    def add_child(self, child: "Person") -> "Person":
        match self.gender:
            case Gender.MALE:
                child.add_father(self)
            case Gender.FEMALE:
                child.add_mother(self)
            case _:
                raise ValueError(
                    "Cannot determine relationship. Please add it using add_father() or add_mother() APIs!"
                )
        return self

    def __post_init__(self):
        """Validate person data."""
        if self.death_year and self.birth_year and self.death_year < self.birth_year:
            raise ValueError("Death year cannot be before birth year")

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{self.name} ({self.gender.name}, {self.religion.name})"
