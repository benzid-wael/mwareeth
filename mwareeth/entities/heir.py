from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from .madhhab import Madhhab
from .person import Person
from .relationship import RelationshipType


class HeirType(Enum):
    """The type of heirship."""

    # Spouses
    HUSBAND = auto()
    WIFE = auto()

    # Descendants
    SON = auto()
    DAUGHTER = auto()

    # Ancestors
    FATHER = auto()
    MOTHER = auto()

    # Siblings
    BROTHER_FULL = auto()
    BROTHER_PARENTAL = auto()
    BROTHER_MATERNAL = auto()
    SISTER_FULL = auto()
    SISTER_PARENTAL = auto()
    SISTER_MATERNAL = auto()
    # nephews
    NEPHEW_FULL = auto()
    NEPHEW_PARENTAL = auto()

    # Uncles
    UNCLE_FULL = auto()
    UNCLE_PARENTAL = auto()
    SON_UNCLE_FULL = auto()
    SON_UNCLE_PARENTAL = auto()

    UTERINE = auto()
    STRANGER = auto()
    SELF = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Heir:
    """
    Represents a potential heir in Islamic inheritance calculations.

    This class is used to represent a person who may inherit from the deceased
    according to Islamic inheritance rules. It contains information about the
    type of heir, the lineage path that led to this heir status, and the
    school of Islamic jurisprudence (madhhab) to use for calculations.

    While the Relationship class represents connections between people in the family tree,
    the Heir class specifically represents inheritance rights according to Islamic law.
    These two classes work together but serve different purposes:
    - Relationship: Used for family tree navigation and relationship identification
    - Heir: Used for inheritance calculations based on Islamic law

    Attributes:
        heir_type: The type of heir (e.g., son, daughter, father, etc.)
        lineage: The path of relationships that led to this heir status
        madhhab: The school of Islamic jurisprudence to use for calculations
    """

    person: Person
    heir_type: HeirType
    lineage: List[RelationshipType]
    madhhab: Madhhab | None = None

    @property
    def is_stranger(self) -> bool:
        return self.heir_type == HeirType.STRANGER

    @property
    def is_uterine(self) -> bool:
        return self.heir_type == HeirType.UTERINE

    @property
    def is_fardh(self) -> bool:
        return self.heir_type in (
            HeirType.HUSBAND,
            HeirType.WIFE,
            HeirType.FATHER,
            HeirType.MOTHER,
            HeirType.DAUGHTER,
            HeirType.SISTER_FULL,
            HeirType.SISTER_PARENTAL,
            HeirType.SISTER_MATERNAL,
            HeirType.BROTHER_MATERNAL,
        )

    @property
    def is_taasib(self) -> bool:
        return self.heir_type in (
            HeirType.FATHER,
            HeirType.SON,
            HeirType.BROTHER_FULL,
            HeirType.BROTHER_PARENTAL,
            HeirType.UNCLE_FULL,
            HeirType.UNCLE_PARENTAL,
        )
