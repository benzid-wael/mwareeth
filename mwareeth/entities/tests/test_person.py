"""
Unit tests for the person module.
"""

import unittest

from ..person import Gender, Person, Religion


class TestReligion(unittest.TestCase):
    """Tests for the Religion enum."""

    def test_religion_values(self):
        """Test that Religion enum has the expected values."""
        self.assertEqual(Religion.ISLAM.value, "Islam")
        self.assertEqual(Religion.CHRISTIANITY.value, "christianity")
        self.assertEqual(Religion.JEWISH.value, "jewish")
        self.assertEqual(Religion.OTHER.value, "other")


class TestGender(unittest.TestCase):
    """Tests for the Gender enum."""

    def test_gender_values(self):
        """Test that Gender enum has the expected values."""
        self.assertEqual(Gender.UNKNOWN.value, "unknown")
        self.assertEqual(Gender.MALE.value, "male")
        self.assertEqual(Gender.FEMALE.value, "female")


class TestPerson(unittest.TestCase):
    """Tests for the Person class."""

    def setUp(self):
        """Set up test fixtures."""
        self.person = Person("Test Person", Gender.MALE)
        self.father = Person("Father", Gender.MALE)
        self.mother = Person("Mother", Gender.FEMALE)
        self.spouse = Person("Spouse", Gender.FEMALE)
        self.child = Person("Child", Gender.MALE)

    def test_initialization(self):
        """Test that a Person can be initialized with the expected values."""
        # Test with minimal required parameters
        person = Person("Test Person", Gender.MALE)
        self.assertEqual(person.name, "Test Person")
        self.assertEqual(person.gender, Gender.MALE)
        self.assertEqual(person.religion, Religion.ISLAM)  # Default value
        self.assertIsNone(person.birth_year)
        self.assertIsNone(person.death_year)
        self.assertIsNone(person.father)
        self.assertIsNone(person.mother)
        self.assertEqual(person.spouses, set())
        self.assertEqual(person.children, set())

        # Test with all parameters
        person = Person(
            name="Full Test",
            gender=Gender.FEMALE,
            religion=Religion.CHRISTIANITY,
            birth_year=1980,
            death_year=2020,
        )
        self.assertEqual(person.name, "Full Test")
        self.assertEqual(person.gender, Gender.FEMALE)
        self.assertEqual(person.religion, Religion.CHRISTIANITY)
        self.assertEqual(person.birth_year, 1980)
        self.assertEqual(person.death_year, 2020)

    def test_is_alive_property(self):
        """Test the is_alive property."""
        # Person with no death_year should be alive
        alive_person = Person("Alive", Gender.MALE)
        self.assertTrue(alive_person.is_alive)

        # Person with death_year should not be alive
        dead_person = Person("Dead", Gender.MALE, death_year=2020)
        self.assertFalse(dead_person.is_alive)

    def test_add_father(self):
        """Test the add_father method."""
        # Test adding a father
        self.person.add_father(self.father)
        self.assertEqual(self.person.father, self.father)
        self.assertIn(self.person, self.father.children)

        # Test method chaining
        result = self.person.add_father(self.father)
        self.assertEqual(result, self.person)

        # Test adding a different father (should raise ValueError)
        different_father = Person("Different Father", Gender.MALE)
        with self.assertRaises(ValueError):
            self.person.add_father(different_father)

    def test_add_mother(self):
        """Test the add_mother method."""
        # Test adding a mother
        self.person.add_mother(self.mother)
        self.assertEqual(self.person.mother, self.mother)
        self.assertIn(self.person, self.mother.children)

        # Test method chaining
        result = self.person.add_mother(self.mother)
        self.assertEqual(result, self.person)

        # Test adding a different mother (should raise ValueError)
        different_mother = Person("Different Mother", Gender.FEMALE)
        with self.assertRaises(ValueError):
            self.person.add_mother(different_mother)

    def test_add_spouse(self):
        """Test the add_spouse method."""
        # Test adding a spouse
        self.person.add_spouse(self.spouse)
        self.assertIn(self.spouse, self.person.spouses)

        # Test method chaining
        result = self.person.add_spouse(self.spouse)
        self.assertEqual(result, self.person)

        # Test adding a spouse with same gender (should raise ValueError)
        same_gender_spouse = Person("Same Gender", Gender.MALE)
        with self.assertRaises(ValueError):
            self.person.add_spouse(same_gender_spouse)

        # Test adding multiple husbands to a female (should raise ValueError)
        female = Person("Female", Gender.FEMALE)
        husband1 = Person("Husband1", Gender.MALE)
        husband2 = Person("Husband2", Gender.MALE)

        female.add_spouse(husband1)
        with self.assertRaises(ValueError):
            female.add_spouse(husband2)

        # Test adding multiple wives to a male (should be allowed)
        male = Person("Male", Gender.MALE)
        wife1 = Person("Wife1", Gender.FEMALE)
        wife2 = Person("Wife2", Gender.FEMALE)

        male.add_spouse(wife1)
        male.add_spouse(wife2)
        self.assertEqual(len(male.spouses), 2)

    def test_add_child(self):
        """Test the add_child method."""
        # Test male adding a child
        self.father.add_child(self.child)
        self.assertEqual(self.child.father, self.father)
        self.assertIn(self.child, self.father.children)

        # Test female adding a child
        self.mother.add_child(self.child)
        self.assertEqual(self.child.mother, self.mother)
        self.assertIn(self.child, self.mother.children)

        # Test method chaining
        result = self.father.add_child(self.child)
        self.assertEqual(result, self.father)

        # Test unknown gender adding a child (should raise ValueError)
        unknown_gender = Person("Unknown", Gender.UNKNOWN)
        with self.assertRaises(ValueError):
            unknown_gender.add_child(Person("Child", Gender.MALE))

    def test_post_init_validation(self):
        """Test the __post_init__ validation."""
        # Test valid birth and death years
        valid_person = Person("Valid", Gender.MALE, birth_year=1980, death_year=2020)
        self.assertEqual(valid_person.birth_year, 1980)
        self.assertEqual(valid_person.death_year, 2020)

        # Test invalid birth and death years (death before birth)
        with self.assertRaises(ValueError):
            Person("Invalid", Gender.MALE, birth_year=2000, death_year=1990)

    def test_hash(self):
        """Test the __hash__ method."""
        # Test that hash returns the id of the object
        person = Person("Hash Test", Gender.MALE)
        self.assertEqual(hash(person), id(person))

        # Test that two different Person objects have different hashes
        person1 = Person("Person1", Gender.MALE)
        person2 = Person("Person2", Gender.MALE)
        self.assertNotEqual(hash(person1), hash(person2))


if __name__ == "__main__":
    unittest.main()
