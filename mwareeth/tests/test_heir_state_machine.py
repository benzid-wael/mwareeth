import unittest

from ..entities.heir import HeirType
from ..entities.relationship import RelationshipType
from ..heir_builder import HeirStateMachine


class TestHeirStateMachine(unittest.TestCase):
    """Test cases for the HeirStateMachine class."""

    def setUp(self):
        """Set up a new state machine for each test."""
        self.state_machine = HeirStateMachine(allow_event_without_transition=False)

    def test_initial_state(self):
        """Test that the initial state is SELF."""
        self.assertEqual(self.state_machine.current_heir_type, HeirType.SELF)

    def test_single_transitions(self):
        """Test single transitions from the initial state."""
        # Test transition to HUSBAND
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.HUSBAND)
        self.assertEqual(state_machine.current_heir_type, HeirType.HUSBAND)

        # Test transition to WIFE
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.WIFE)
        self.assertEqual(state_machine.current_heir_type, HeirType.WIFE)

        # Test transition to FATHER
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.FATHER)
        self.assertEqual(state_machine.current_heir_type, HeirType.FATHER)

        # Test transition to MOTHER
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.MOTHER)
        self.assertEqual(state_machine.current_heir_type, HeirType.MOTHER)

        # Test transition to SON
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.SON)

        # Test transition to DAUGHTER
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.DAUGHTER)
        self.assertEqual(state_machine.current_heir_type, HeirType.DAUGHTER)

    def test_sibling_transitions(self):
        """Test transitions to sibling states."""
        # Test transition to BROTHER_FULL
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.BROTHER_FULL)
        self.assertEqual(state_machine.current_heir_type, HeirType.BROTHER_FULL)

    def test_uncle_transitions(self):
        """Test transitions to uncle states."""
        # Test transition to UNCLE_FULL
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.BROTHER_FULL)
        self.assertEqual(state_machine.current_heir_type, HeirType.BROTHER_FULL)

        # Test transition to UNCLE_PARENTAL
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.PARENTAL_UNCLE_PARENTAL)
        self.assertEqual(state_machine.current_heir_type, HeirType.UNCLE_PARENTAL)

        # Test transition to UTERINE for maternal uncle
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.PARENTAL_UNCLE_MATERNAL)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_aunt_transitions(self):
        """Test transitions to aunt states (all should be UTERINE)."""
        # Test transition to UTERINE for paternal aunt (full)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.PARENTAL_AUNT_FULL)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_maternal_uncle_transitions(self):
        """Test transitions to maternal uncle states (all should be UTERINE)."""
        # Test transition to UTERINE for maternal uncle (full)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.MATERNAL_UNCLE_FULL)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_maternal_aunt_transitions(self):
        """Test transitions to maternal aunt states (all should be UTERINE)."""
        # Test transition to UTERINE for maternal aunt (full)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.MATERNAL_AUNT_FULL)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_multi_step_transitions(self):
        """Test multi-step transitions."""
        # Test father -> father -> father (should still be FATHER)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.FATHER)
        state_machine.transition(RelationshipType.FATHER)
        state_machine.transition(RelationshipType.FATHER)
        self.assertEqual(state_machine.current_heir_type, HeirType.FATHER)

        # Test father -> mother -> father (should be UTERINE)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.FATHER)
        state_machine.transition(RelationshipType.MOTHER)
        state_machine.transition(RelationshipType.MOTHER)
        state_machine.transition(RelationshipType.FATHER)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

        # Test son -> son (should be SON)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.SON)

        # Test son -> daughter (should be DAUGHTER)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.DAUGHTER)
        self.assertEqual(state_machine.current_heir_type, HeirType.DAUGHTER)

        # Test daughter -> son (should be UTERINE)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.DAUGHTER)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_nephew_transitions(self):
        """Test transitions to nephew states."""
        # Test brother (full) -> son (should be NEPHEW_FULL)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.BROTHER_FULL)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.NEPHEW_FULL)

        # Test brother (parental) -> son (should be NEPHEW_PARENTAL)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.BROTHER_PARENTAL)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.NEPHEW_PARENTAL)

        # Test brother (maternal) -> son (should be UTERINE)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.BROTHER_MATERNAL)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.UTERINE)

    def test_son_of_uncle_transitions(self):
        """Test transitions to son of uncle states."""
        # Test paternal uncle (full) -> son (should be SON_UNCLE_FULL)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.PARENTAL_UNCLE_FULL)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.SON_UNCLE_FULL)

        # Test paternal uncle (parental) -> son (should be SON_UNCLE_PARENTAL)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.PARENTAL_UNCLE_PARENTAL)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        state_machine.transition(RelationshipType.SON)
        self.assertEqual(state_machine.current_heir_type, HeirType.SON_UNCLE_PARENTAL)

    def test_invalid_transitions(self):
        """Test that invalid transitions raise exceptions."""
        # Test transition from HUSBAND (final state)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.HUSBAND)

        # HUSBAND is a final state, so any further transitions should raise an exception
        with self.assertRaises(Exception):
            state_machine.transition(RelationshipType.SON)

        # Test transition from WIFE (final state)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.WIFE)

        # WIFE is a final state, so any further transitions should raise an exception
        with self.assertRaises(Exception):
            state_machine.transition(RelationshipType.DAUGHTER)

        # Test transition from STRANGER (final state)
        state_machine = HeirStateMachine(allow_event_without_transition=False)
        state_machine.transition(RelationshipType.SELF)  # This transitions to STRANGER

        # STRANGER is a final state, so any further transitions should raise an exception
        with self.assertRaises(Exception):
            state_machine.transition(RelationshipType.FATHER)


if __name__ == "__main__":
    unittest.main()
