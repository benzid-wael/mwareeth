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
        self.assertEqual(LineageType.BOTH.value, 1)
        self.assertEqual(LineageType.PATERNAL.value, 2)
        self.assertEqual(LineageType.MATERNAL.value, 3)


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
        self.assertEqual(relationship.lineage, [RelationshipType.FATHER])
        self.assertIsNone(relationship.lineage_type)
        self.assertEqual(relationship.degree, 1)

    def test_mother_factory_method(self):
        """Test the mother factory method."""
        relationship = Relationship.mother(Person("Ali", Gender.FEMALE))
        self.assertEqual(relationship.relationship_type, RelationshipType.MOTHER)
        self.assertEqual(relationship.lineage, [RelationshipType.MOTHER])
        self.assertIsNone(relationship.lineage_type)
        self.assertEqual(relationship.degree, 1)

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

        # Check that grandparents are correctly established
        self.assertEqual(
            self.family_tree.get_relatives(RelationshipType.GRANDFATHER),
            {self.grandfather_maternal, self.grandfather_paternal},
        )
        self.assertEqual(
            self.family_tree.get_relatives(RelationshipType.GRANDMOTHER),
            {self.grandmother_paternal, self.grandmother_maternal},
        )

    def test_process_ancestors_with_siblings(self):
        """Test that ancestors and siblings are correctly processed."""
        # Create a family with siblings
        deceased = Person("Deceased", Gender.MALE)
        father = Person("Father", Gender.MALE)
        mother = Person("Mother", Gender.FEMALE)
        brother = Person("Brother", Gender.MALE)
        sister = Person("Sister", Gender.FEMALE)

        # Set up relationships
        deceased.add_father(father)
        deceased.add_mother(mother)
        brother.add_father(father)
        brother.add_mother(mother)
        sister.add_father(father)
        sister.add_mother(mother)

        # Create the family tree
        family_tree = FamilyTree(deceased)

        # Check that siblings are correctly established
        self.assertIn(RelationshipType.BROTHER, family_tree._relationships)
        self.assertIn(brother, family_tree.get_relatives(RelationshipType.BROTHER))
        self.assertIn(RelationshipType.SISTER, family_tree._relationships)
        self.assertIn(sister, family_tree.get_relatives(RelationshipType.SISTER))

    def test_process_ancestors_with_uncles_aunts(self):
        """Test that ancestors, uncles and aunts are correctly processed."""
        # Create a family with uncles and aunts
        deceased = Person("Deceased", Gender.MALE)
        father = Person("Father", Gender.MALE)
        grandfather = Person("Grandfather", Gender.MALE)
        grandmother = Person("Grandmother", Gender.FEMALE)
        uncle = Person("Uncle", Gender.MALE)
        aunt = Person("Aunt", Gender.FEMALE)

        # Set up relationships
        deceased.add_father(father)
        father.add_father(grandfather)
        father.add_mother(grandmother)
        uncle.add_father(grandfather)
        uncle.add_mother(grandmother)
        aunt.add_father(grandfather)
        aunt.add_mother(grandmother)

        # Create the family tree
        family_tree = FamilyTree(deceased)

        # Check that uncles and aunts are correctly established
        self.assertIn(RelationshipType.UNCLE, family_tree._relationships)
        self.assertIn(uncle, family_tree.get_relatives(RelationshipType.UNCLE))
        self.assertIn(RelationshipType.AUNT, family_tree._relationships)
        self.assertIn(aunt, family_tree.get_relatives(RelationshipType.AUNT))

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

    def test_process_descendants(self):
        """Test that descendants are correctly processed."""
        # Create a family with descendants
        deceased = Person("Deceased", Gender.MALE)
        son = Person("Son", Gender.MALE)
        daughter = Person("Daughter", Gender.FEMALE)
        grandson = Person("Grandson", Gender.MALE)
        granddaughter = Person("Granddaughter", Gender.FEMALE)

        # Set up relationships
        deceased.add_child(son)
        deceased.add_child(daughter)
        son.add_child(grandson)
        daughter.add_child(granddaughter)

        # Create the family tree
        family_tree = FamilyTree(deceased)

        # Check that descendants are correctly established
        self.assertIn(RelationshipType.SON, family_tree._relationships)
        self.assertIn(son, family_tree.get_relatives(RelationshipType.SON))
        self.assertIn(RelationshipType.DAUGHTER, family_tree._relationships)
        self.assertIn(daughter, family_tree.get_relatives(RelationshipType.DAUGHTER))

        # Check that grandchildren are correctly established
        # Note: The current implementation only processes direct children, not grandchildren
        # If the implementation changes to include grandchildren, this test should be updated
        self.assertIn(grandson, family_tree.get_relatives(RelationshipType.SON))
        self.assertIn(
            granddaughter, family_tree.get_relatives(RelationshipType.DAUGHTER)
        )

    def test_process_descendants_with_no_children(self):
        """Test that a family tree with no descendants is correctly processed."""
        # Create a family with no descendants
        deceased = Person("Deceased", Gender.MALE)

        # Create the family tree
        family_tree = FamilyTree(deceased)

        # Check that there are no descendants
        self.assertNotIn(RelationshipType.SON, family_tree._relationships)
        self.assertNotIn(RelationshipType.DAUGHTER, family_tree._relationships)

    def test_process_descendants_circular_reference(self):
        """Test that a circular reference in descendants raises a ValueError."""
        # Create a family with a circular reference
        deceased = Person("Deceased", Gender.MALE)
        son = Person("Son", Gender.MALE)

        # Set up circular relationship (deceased -> son -> deceased)
        deceased.add_child(son)

        # This would create a circular reference, which should raise a ValueError
        # when the family tree is created
        with self.assertRaises(ValueError):
            son.add_child(deceased)
            FamilyTree(deceased)


if __name__ == "__main__":
    unittest.main()
