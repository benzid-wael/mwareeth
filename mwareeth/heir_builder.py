from typing import List

from statemachine import StateMachine
from statemachine.states import States

from .entities.heir import HeirType
from .entities.relationship import RelationshipType
from .utils.events import Events

FINAL_STATES = {HeirType.HUSBAND, HeirType.WIFE, HeirType.STRANGER}
NON_FINAL_STATES = set(HeirType.__members__.values()) - FINAL_STATES


class HeirStateMachine(StateMachine):
    _states = States.from_enum(HeirType, initial=HeirType.SELF, final=FINAL_STATES)
    _events = Events.from_enum(RelationshipType)

    # Initial State
    _states.SELF.to(_states.HUSBAND, event=_events.HUSBAND)
    _states.SELF.to(_states.WIFE, event=_events.WIFE)
    _states.SELF.to(_states.FATHER, event=_events.FATHER)
    _states.SELF.to(_states.MOTHER, event=_events.MOTHER)
    _states.SELF.to(_states.SON, event=_events.SON)
    _states.SELF.to(_states.DAUGHTER, event=_events.DAUGHTER)
    # siblings
    _states.SELF.to(_states.BROTHER_FULL, event=_events.BROTHER_FULL)
    _states.SELF.to(_states.BROTHER_PARENTAL, event=_events.BROTHER_PARENTAL)
    _states.SELF.to(_states.BROTHER_MATERNAL, event=_events.BROTHER_MATERNAL)
    _states.SELF.to(_states.SISTER_FULL, event=_events.SISTER_FULL)
    _states.SELF.to(_states.SISTER_PARENTAL, event=_events.SISTER_PARENTAL)
    _states.SELF.to(_states.SISTER_MATERNAL, event=_events.SISTER_MATERNAL)
    # auncles/aunts
    _states.SELF.to(_states.UNCLE_FULL, event=_events.PARENTAL_UNCLE_FULL)
    _states.SELF.to(_states.UNCLE_PARENTAL, event=_events.PARENTAL_UNCLE_PARENTAL)
    _states.SELF.to(_states.UTERINE, event=_events.PARENTAL_UNCLE_MATERNAL)
    _states.SELF.to(_states.UTERINE, event=_events.PARENTAL_AUNT_FULL)
    _states.SELF.to(_states.UTERINE, event=_events.PARENTAL_AUNT_PARENTAL)
    _states.SELF.to(_states.UTERINE, event=_events.PARENTAL_AUNT_MATERNAL)

    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_FULL)
    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_PARENTAL)
    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_MATERNAL)
    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_AUNT_FULL)
    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_AUNT_PARENTAL)
    _states.SELF.to(_states.UTERINE, event=_events.MATERNAL_AUNT_MATERNAL)

    # Descendants
    _states.SON.to(_states.SON, event=_events.SON)
    _states.SON.to(_states.DAUGHTER, event=_events.DAUGHTER)
    _states.DAUGHTER.to(_states.UTERINE, event=_events.SON)
    _states.DAUGHTER.to(_states.UTERINE, event=_events.DAUGHTER)

    # Ancestors
    _states.FATHER.to(_states.FATHER, event=_events.FATHER)
    _states.FATHER.to(_states.MOTHER, event=_events.MOTHER)
    _states.MOTHER.to(_states.MOTHER, event=_events.MOTHER)
    _states.MOTHER.to(_states.UTERINE, event=_events.FATHER)

    # Siblings
    _states.BROTHER_FULL.to(_states.NEPHEW_FULL, event=_events.SON)
    _states.BROTHER_FULL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.BROTHER_PARENTAL.to(_states.NEPHEW_PARENTAL, event=_events.SON)
    _states.BROTHER_PARENTAL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.BROTHER_MATERNAL.to(_states.UTERINE, event=_events.SON)
    _states.BROTHER_MATERNAL.to(_states.UTERINE, event=_events.DAUGHTER)

    _states.NEPHEW_PARENTAL.to(_states.NEPHEW_PARENTAL, event=_events.SON)
    _states.NEPHEW_PARENTAL.to(_states.UTERINE, event=_events.DAUGHTER)

    _states.SISTER_FULL.to(_states.UTERINE, event=_events.SON)
    _states.SISTER_PARENTAL.to(_states.UTERINE, event=_events.SON)
    _states.SISTER_MATERNAL.to(_states.UTERINE, event=_events.SON)
    _states.SISTER_FULL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.SISTER_PARENTAL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.SISTER_MATERNAL.to(_states.UTERINE, event=_events.DAUGHTER)

    # Uncles/Aunts
    _states.UNCLE_FULL.to(_states.SON_UNCLE_FULL, event=_events.SON)
    _states.UNCLE_PARENTAL.to(_states.SON_UNCLE_PARENTAL, event=_events.SON)
    _states.UNCLE_FULL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.UNCLE_PARENTAL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.SON_UNCLE_FULL.to(_states.SON_UNCLE_FULL, event=_events.SON)
    _states.SON_UNCLE_PARENTAL.to(_states.SON_UNCLE_PARENTAL, event=_events.SON)
    _states.SON_UNCLE_FULL.to(_states.UTERINE, event=_events.DAUGHTER)
    _states.SON_UNCLE_PARENTAL.to(_states.UTERINE, event=_events.DAUGHTER)

    _states.FATHER.to(_states.UNCLE_FULL, event=_events.PARENTAL_UNCLE_FULL)
    _states.FATHER.to(_states.UNCLE_PARENTAL, event=_events.PARENTAL_UNCLE_PARENTAL)
    # uterine uncles / aunts
    _states.FATHER.to(_states.UTERINE, event=_events.PARENTAL_UNCLE_MATERNAL)
    _states.FATHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_FULL)
    _states.FATHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_PARENTAL)
    _states.FATHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_MATERNAL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_FULL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_PARENTAL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_MATERNAL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_FULL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_PARENTAL)
    _states.FATHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_MATERNAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_UNCLE_FULL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_UNCLE_PARENTAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_UNCLE_MATERNAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_FULL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_PARENTAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.PARENTAL_AUNT_MATERNAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_FULL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_PARENTAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_UNCLE_MATERNAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_FULL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_PARENTAL)
    _states.MOTHER.to(_states.UTERINE, event=_events.MATERNAL_AUNT_MATERNAL)

    _states.UTERINE.to(_states.UTERINE, event=_events.FATHER)
    _states.UTERINE.to(_states.UTERINE, event=_events.MOTHER)
    _states.UTERINE.to(_states.UTERINE, event=_events.SON)
    _states.UTERINE.to(_states.UTERINE, event=_events.DAUGHTER)
    # This is an invalid event but was added to fix InvalidDefinition error
    _states.SELF.to(_states.STRANGER, event=_events.SELF)
    # These is an invalid event but was added to fix InstanceState error
    for heir_type in NON_FINAL_STATES:
        getattr(_states, heir_type.name).to(_states.STRANGER, event=_events.SELF)

    def transition(self, relationship_type: RelationshipType) -> None:
        self.send(relationship_type.name)

    @property
    def current_heir_type(self) -> HeirType:
        return HeirType.__members__[self.current_state.name.upper().replace(" ", "_")]


def deduce_heir_type(lineage: List[RelationshipType]) -> HeirType:
    state_machine = HeirStateMachine(allow_event_without_transition=False)
    for relationship in lineage:
        state_machine.transition(relationship)
    return state_machine.current_heir_type


if __name__ == "__main__":
    lineage = [
        RelationshipType.FATHER,
        RelationshipType.FATHER,
        RelationshipType.FATHER,
    ]
    print(f"""lineage: {lineage} --> {deduce_heir_type(lineage)}""")
    lineage = [
        RelationshipType.FATHER,
        RelationshipType.MOTHER,
        RelationshipType.FATHER,
    ]
    print(f"""lineage: {lineage} --> {deduce_heir_type(lineage)}""")
    lineage = [
        RelationshipType.PARENTAL_UNCLE_FULL,
        RelationshipType.SON,
        RelationshipType.SON,
    ]
    print(f"""lineage: {lineage} --> {deduce_heir_type(lineage)}""")
    lineage = [
        RelationshipType.PARENTAL_UNCLE_FULL,
        RelationshipType.SON,
        RelationshipType.DAUGHTER,
    ]
    print(f"""lineage: {lineage} --> {deduce_heir_type(lineage)}""")
