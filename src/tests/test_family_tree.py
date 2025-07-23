"""
Unit tests for the family_tree module.
"""

import unittest

from ..family_tree import FamilyTree, LineageType, Relationship, RelationshipType
from ..person import Gender, Person


class TestLineageType(unittest.TestCase):
    """Tests for the LineageType enum."""

    def test_lineage_types(self):
        """Test that LineageType enum has the expected values."""
        self.assertEqual(LineageType.PATERNAL.value, "paternal")
        self.assertEqual(LineageType.MATERNAL.value, "maternal")
        self.assertEqual(LineageType.BOTH.value, "both")


class TestRelationshipType(unittest.TestCase):
    """Tests for the RelationshipType enum."""

    def test_relationship_types(self):
        """Test that RelationshipType enum has the expected values."""
        self.assertEqual(RelationshipType.FATHER.value, "father")
        self.assertEqual(RelationshipType.MOTHER.value, "mother")
        self.assertEqual(RelationshipType.GRANDFATHER.value, "grandfather")
        self.assertEqual(RelationshipType.GRANDMOTHER.value, "grandmother")


class TestRelationship(unittest.TestCase):
    """Tests for the Relationship class."""

    def test_relationship_initialization(self):
        """Test that a Relationship can be initialized with the expected values."""
        relationship = Relationship(
            Person("Deceased", Gender.MALE),
            RelationshipType.FATHER,
            [RelationshipType.FATHER],
            None,
        )
        self.assertEqual(relationship.relationship_type, RelationshipType.FATHER)
        self.assertEqual(relationship.lineage, [RelationshipType.FATHER])
        self.assertIsNone(relationship.lineage_type)
        self.assertEqual(relationship.degree, 1)

    def test_father_factory_method(self):
        """Test the father factory method."""
        relationship = Relationship.father(Person("Ali", Gender.MALE))
        self.assertEqual(relationship.relationship_type, RelationshipType.FATHER)
        self.assertEqual(relationship.lineage, [])
        self.assertIsNone(relationship.lineage_type)
        self.assertEqual(relationship.degree, 0)

    def test_mother_factory_method(self):
        """Test the mother factory method."""
        relationship = Relationship.mother(Person("Ali", Gender.FEMALE))
        self.assertEqual(relationship.relationship_type, RelationshipType.MOTHER)
        self.assertEqual(relationship.lineage, [])
        self.assertIsNone(relationship.lineage_type)
        self.assertEqual(relationship.degree, 0)

    def test_is_ancestor_property(self):
        """Test the is_ancestor property."""
        father = Relationship(
            Person("father", Gender.MALE),
            RelationshipType.FATHER,
            [RelationshipType.FATHER],
        )
        mother = Relationship(
            Person("mother", Gender.FEMALE),
            RelationshipType.MOTHER,
            [RelationshipType.MOTHER],
        )
        grandfather = Relationship(
            Person("father", Gender.MALE),
            RelationshipType.GRANDFATHER,
            [RelationshipType.FATHER, RelationshipType.FATHER],
        )
        grandmother = Relationship(
            Person("grandmother", Gender.FEMALE),
            RelationshipType.GRANDMOTHER,
            [RelationshipType.MOTHER, RelationshipType.MOTHER],
        )

        self.assertTrue(father.is_ancestor)
        self.assertTrue(mother.is_ancestor)
        self.assertTrue(grandfather.is_ancestor)
        self.assertTrue(grandmother.is_ancestor)


class TestFamilyTree(unittest.TestCase):
    """Tests for the FamilyTree class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a simple family tree for testing
        self.deceased = Person("Deceased", Gender.MALE)
        self.father = Person("Father", Gender.MALE)
        self.mother = Person("Mother", Gender.FEMALE)
        self.grandfather_paternal = Person("Paternal Grandfather", Gender.MALE)
        self.grandmother_paternal = Person("Paternal Grandmother", Gender.FEMALE)
        self.grandfather_maternal = Person("Maternal Grandfather", Gender.MALE)
        self.grandmother_maternal = Person("Maternal Grandmother", Gender.FEMALE)

        # Set up relationships
        self.deceased.add_father(self.father)
        self.deceased.add_mother(self.mother)
        self.father.add_father(self.grandfather_paternal)
        self.father.add_mother(self.grandmother_paternal)
        self.mother.add_father(self.grandfather_maternal)
        self.mother.add_mother(self.grandmother_maternal)

        # Create the family tree
        self.family_tree = FamilyTree(self.deceased)

    def test_initialization(self):
        """Test that a FamilyTree can be initialized with a deceased person."""
        self.assertEqual(self.family_tree.deceased, self.deceased)
        self.assertIsInstance(self.family_tree._relationships, dict)

    def test_process_ancestors(self):
        """Test that ancestors are correctly processed."""
        # Check that the father relationship is correctly established
        self.assertIn(RelationshipType.FATHER, self.family_tree._relationships)
        self.assertIn(
            self.father, self.family_tree.get_relatives(RelationshipType.FATHER)
        )

        # Check that the mother relationship is correctly established
        self.assertIn(RelationshipType.MOTHER, self.family_tree._relationships)
        self.assertIn(
            self.mother, self.family_tree.get_relatives(RelationshipType.MOTHER)
        )

        self.assertEqual(
            self.family_tree.get_relatives(RelationshipType.GRANDFATHER),
            {self.grandfather_maternal, self.grandfather_paternal},
        )
        self.assertEqual(
            self.family_tree.get_relatives(RelationshipType.GRANDMOTHER),
            {self.grandmother_paternal, self.grandmother_maternal},
        )

    def test_family_tree_with_no_ancestors(self):
        """Test a family tree with a deceased person who has no ancestors."""
        deceased_no_ancestors = Person("No Ancestors", Gender.MALE)
        family_tree = FamilyTree(deceased_no_ancestors)

        # Check that there are no relationships
        self.assertNotIn(RelationshipType.FATHER, family_tree._relationships)
        self.assertNotIn(RelationshipType.MOTHER, family_tree._relationships)

    def test_family_tree_with_partial_ancestors(self):
        """Test a family tree with a deceased person who has only one parent."""
        deceased_partial = Person("Partial Ancestors", Gender.MALE)
        father_only = Person("Father Only", Gender.MALE)
        deceased_partial.add_father(father_only)

        family_tree = FamilyTree(deceased_partial)

        # Check that only the father relationship is established
        self.assertIn(RelationshipType.FATHER, family_tree._relationships)
        self.assertNotIn(RelationshipType.MOTHER, family_tree._relationships)


if __name__ == "__main__":
    unittest.main()
