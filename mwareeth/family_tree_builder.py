"""
This module provides a FamilyTreeBuilder class to help users build a family tree
from their inputs in an interactive and user-friendly way.
"""

from enum import IntEnum, auto
from typing import Dict, List, Optional, Set, Tuple
import importlib.util


from .i18n import _, set_language, force_language, get_available_languages
from .entities.person import Gender, Person, Religion
from .entities.family_tree import FamilyTree


GRAPHVIZ_AVAILABLE = importlib.util.find_spec("graphviz") is not None


class InteractiveBuildCommand(IntEnum):
    ADD_PERSON = auto()
    ADD_RELATIONSHIP = auto()
    VISUALIZE = auto()
    BUILD_FAMILY_TREE = auto()


class FamilyTreeBuilder:
    """
    A builder class to help construct a family tree from user inputs.

    This class provides methods to:
    1. Add people to the family tree
    2. Establish relationships between people
    3. Validate the family tree structure
    4. Generate a FamilyTree instance
    """

    def __init__(self, language: str = "en"):
        """
        Initialize an empty family tree builder.

        Args:
            language: The language code to use for translations (default: "en")
        """
        self.people: Dict[str, Person] = {}
        self.deceased: Optional[Person] = None
        self._set_language(language)

    def _set_language(self, language: str) -> None:
        """
        Set the language for the family tree builder.

        Args:
            language: The language code to use for translations
        """
        try:
            set_language(language)
        except ValueError:
            # If the language is not supported, use English as fallback
            set_language("en")

    def add_person(
        self,
        name: str,
        gender: str,
        religion: str = "Islam",
        birth_year: Optional[int] = None,
        death_year: Optional[int] = None,
        is_deceased: bool = False,
    ) -> Person:
        """
        Add a person to the family tree.

        Args:
            name: The name of the person
            gender: The gender of the person ("male" or "female")
            religion: The religion of the person (default: "Islam")
            birth_year: The birth year of the person (optional)
            death_year: The death year of the person (optional)
            is_deceased: Whether this person is the deceased (focal point of the tree)

        Returns:
            The created Person object

        Raises:
            ValueError: If a person with the same name already exists or if invalid data is provided
        """
        if name in self.people:
            raise ValueError(
                _("A person with the name '{name}' already exists", name=name)
            )

        # Convert gender string to Gender enum
        try:
            gender_enum = Gender[gender.upper()]
        except KeyError:
            raise ValueError(
                _("Invalid gender: {gender}. Must be 'male' or 'female'", gender=gender)
            )

        # Convert religion string to Religion enum
        try:
            religion_enum = Religion[religion.upper()]
        except KeyError:
            religion_enum = Religion.OTHER

        # Create the person
        person = Person(
            name=name,
            gender=gender_enum,
            religion=religion_enum,
            birth_year=birth_year,
            death_year=death_year,
        )

        # Add the person to the dictionary
        self.people[name] = person

        # Set as deceased if specified
        if is_deceased:
            if self.deceased:
                raise ValueError(_("A deceased person is already set"))
            self.deceased = person

        return person

    def set_deceased(self, name: str) -> Person:
        """
        Set a person as the deceased (focal point of the tree).

        Args:
            name: The name of the person to set as deceased

        Returns:
            The Person object set as deceased

        Raises:
            ValueError: If the person does not exist
        """
        if name not in self.people:
            raise ValueError(_("Person '{name}' does not exist", name=name))

        self.deceased = self.people[name]
        return self.deceased

    def add_relationship(
        self, person_name: str, relation_type: str, relative_name: str
    ) -> Tuple[Person, Person]:
        """
        Add a relationship between two people.

        Args:
            person_name: The name of the first person
            relation_type: The type of relationship ("father", "mother", "child", "spouse")
            relative_name: The name of the relative

        Returns:
            A tuple of (person, relative) Person objects

        Raises:
            ValueError: If either person does not exist or if the relationship is invalid
        """
        # Check if both people exist
        if person_name not in self.people:
            raise ValueError(_("Person '{name}' does not exist", name=person_name))
        if relative_name not in self.people:
            raise ValueError(_("Person '{name}' does not exist", name=relative_name))

        person = self.people[person_name]
        relative = self.people[relative_name]

        # Add the relationship based on the type
        if relation_type.lower() == _("father"):
            person.add_father(relative)
        elif relation_type.lower() == _("mother"):
            person.add_mother(relative)
        elif relation_type.lower() == _("child"):
            person.add_child(relative)
        elif relation_type.lower() == _("spouse"):
            person.add_spouse(relative)
            relative.add_spouse(person)
        else:
            raise ValueError(
                _("Invalid relationship type: {relation}", relation=relation_type)
            )

        return person, relative

    def add_father(self, child_name: str, father_name: str) -> Tuple[Person, Person]:
        """
        Add a father-child relationship.

        Args:
            child_name: The name of the child
            father_name: The name of the father

        Returns:
            A tuple of (child, father) Person objects
        """
        return self.add_relationship(child_name, "father", father_name)

    def add_mother(self, child_name: str, mother_name: str) -> Tuple[Person, Person]:
        """
        Add a mother-child relationship.

        Args:
            child_name: The name of the child
            mother_name: The name of the mother

        Returns:
            A tuple of (child, mother) Person objects
        """
        return self.add_relationship(child_name, "mother", mother_name)

    def add_child(self, parent_name: str, child_name: str) -> Tuple[Person, Person]:
        """
        Add a parent-child relationship.

        Args:
            parent_name: The name of the parent
            child_name: The name of the child

        Returns:
            A tuple of (parent, child) Person objects
        """
        return self.add_relationship(parent_name, "child", child_name)

    def add_spouse(self, person_name: str, spouse_name: str) -> Tuple[Person, Person]:
        """
        Add a spousal relationship.

        Args:
            person_name: The name of the first person
            spouse_name: The name of the spouse

        Returns:
            A tuple of (person, spouse) Person objects
        """
        return self.add_relationship(person_name, "spouse", spouse_name)

    def validate(self) -> List[str]:
        """
        Validate the family tree structure.

        Returns:
            A list of validation errors, or an empty list if the tree is valid
        """
        errors = []

        # Check if a deceased person is set
        if not self.deceased:
            errors.append(_("No deceased person is set"))

        # Check for circular references
        visited = set()
        for person in self.people.values():
            path = set()
            if self._has_circular_reference(person, visited, path):
                errors.append(
                    _("Circular reference detected involving {name}", name=person.name)
                )
                errors.append(f"  - Visited: {', '.join(p.name for p in visited)}")
                errors.append(f"  - Path: {', '.join(p.name for p in path)}")

        # Check for inconsistent relationships
        for name, person in self.people.items():
            # Check father-child consistency
            if person.father and person not in person.father.children:
                errors.append(
                    _("Inconsistent father-child relationship for {name}", name=name)
                )

            # Check mother-child consistency
            if person.mother and person not in person.mother.children:
                errors.append(
                    _("Inconsistent mother-child relationship for {name}", name=name)
                )

            # Check spouse consistency
            for spouse in person.spouses:
                if person not in spouse.spouses:
                    errors.append(
                        _(
                            "Inconsistent spousal relationship between {name1} and {name2}",
                            name1=name,
                            name2=spouse.name,
                        )
                    )

        return errors

    def _has_circular_reference(
        self, person: Person, visited: Set[Person], path: Set[Person]
    ) -> bool:
        """
        Check if there's a circular reference in the family tree.

        Args:
            person: The person to check
            visited: Set of already visited person IDs
            path: Set of person IDs in the current path

        Returns:
            True if a circular reference is detected, False otherwise
        """
        person_id = person

        # If we've seen this person in the current path, there's a cycle
        if person_id in path:
            return True

        # If we've already checked this person and found no cycles, skip
        if person_id in visited:
            return False

        # # Check parents
        # if person.father and self._has_circular_reference(person.father, visited, path):
        #     return True
        # if person.mother and self._has_circular_reference(person.mother, visited, path):
        #     return True

        # Add the person to the current path
        path.add(person_id)

        # Check children
        for child in person.children:
            if self._has_circular_reference(child, visited, path):
                return True

        # No cycles found, remove from path and mark as visited
        path.remove(person_id)
        visited.add(person_id)
        return False

    def build(self) -> FamilyTree:
        """
        Build and return a FamilyTree instance.

        Returns:
            A FamilyTree instance

        Raises:
            ValueError: If the family tree is invalid
        """
        # Validate the tree first
        errors = self.validate()
        if errors:
            raise ValueError(
                _("Invalid family tree: {errors}", errors=", ".join(errors))
            )

        # Check if deceased is set
        if not self.deceased:
            raise ValueError(_("No deceased person is set"))

        # Create and return the family tree
        return FamilyTree(self.deceased)

    def from_dict(self, data: Dict) -> "FamilyTreeBuilder":
        """
        Build a family tree from a dictionary representation.

        Args:
            data: A dictionary containing the family tree data

        Returns:
            The FamilyTreeBuilder instance

        Example:
            data = {
                "deceased": "John",
                "people": [
                    {"name": "John", "gender": "male", "birth_year": 1950, "death_year": 2020},
                    {"name": "Mary", "gender": "female", "birth_year": 1952},
                    {"name": "Bob", "gender": "male", "birth_year": 1975},
                ],
                "relationships": [
                    {"person": "Bob", "relation": "father", "relative": "John"},
                    {"person": "Bob", "relation": "mother", "relative": "Mary"},
                ]
            }
        """
        # Add people
        for person_data in data.get("people", []):
            self.add_person(
                name=person_data["name"],
                gender=person_data["gender"],
                religion=person_data.get("religion", "Islam"),
                birth_year=person_data.get("birth_year"),
                death_year=person_data.get("death_year"),
                is_deceased=person_data["name"] == data.get("deceased"),
            )

        # Add relationships
        for rel_data in data.get("relationships", []):
            self.add_relationship(
                person_name=rel_data["person"],
                relation_type=rel_data["relation"],
                relative_name=rel_data["relative"],
            )

        return self

    def to_dict(self) -> Dict:
        """
        Convert the family tree to a dictionary representation.

        Returns:
            A dictionary containing the family tree data
        """
        result = {
            "deceased": self.deceased.name if self.deceased else None,
            "people": [],
            "relationships": [],
        }

        # Add people
        for name, person in self.people.items():
            person_data = {
                "name": name,
                "gender": person.gender.value,
                "religion": person.religion.value,
            }
            if person.birth_year:
                person_data["birth_year"] = str(person.birth_year)
            if person.death_year:
                person_data["death_year"] = str(person.death_year)

            result["people"].append(person_data)

        # Add relationships
        for name, person in self.people.items():
            # Add father relationship
            if person.father:
                result["relationships"].append(
                    {
                        "person": name,
                        "relation": "father",
                        "relative": person.father.name,
                    }
                )

            # Add mother relationship
            if person.mother:
                result["relationships"].append(
                    {
                        "person": name,
                        "relation": "mother",
                        "relative": person.mother.name,
                    }
                )

            # Add spouse relationships
            for spouse in person.spouses:
                # Only add the relationship once (from the person with the lexicographically smaller name)
                if name < spouse.name:
                    result["relationships"].append(
                        {
                            "person": name,
                            "relation": "spouse",
                            "relative": spouse.name,
                        }
                    )

        return result

    def interactive_build(self) -> FamilyTree:
        """
        Build a family tree interactively by prompting the user for inputs.

        Returns:
            A FamilyTree instance
        """
        print(_("Welcome to the Family Tree Builder!"))
        print(
            _(
                "Let's start by adding the deceased person (the focal point of the tree)."
            )
        )

        # Add the deceased person
        name = input(f"{_('Name')}: ")
        gender = input(f"{_('Gender')} (male/female): ")
        birth_year_str = input(f"{_('Birth year (optional, press Enter to skip)')}: ")
        birth_year = int(birth_year_str) if birth_year_str else None
        death_year_str = input(f"{_('Death year (optional, press Enter to skip)')}: ")
        death_year = int(death_year_str) if death_year_str else None

        self.add_person(
            name=name,
            gender=gender,
            birth_year=birth_year,
            death_year=death_year,
            is_deceased=True,
        )

        # Add more people and relationships
        commands = sorted(
            [
                (InteractiveBuildCommand.ADD_PERSON, _("Add a person")),
                (InteractiveBuildCommand.ADD_RELATIONSHIP, _("Add a relationship")),
                (InteractiveBuildCommand.VISUALIZE, _("Visualize the family tree")),
                (
                    InteractiveBuildCommand.BUILD_FAMILY_TREE,
                    _("Finish and build the family tree"),
                ),
            ]
        )
        while True:
            print(f"\n{_('What would you like to do?')}")
            print(
                "\n".join(f"{command}. {help_text}" for command, help_text in commands)
            )
            choice = input(f"{_('Enter your choice')} (1-{len(commands)}): ")

            try:
                choice = int(choice)
                choice = InteractiveBuildCommand(choice)
            except ValueError:
                print(_("Invalid choice. Please try again."))
                continue

            match choice:
                case InteractiveBuildCommand.ADD_PERSON:
                    self._interactive_add_person()
                case InteractiveBuildCommand.ADD_RELATIONSHIP:
                    self._interactive_add_relationship()
                case InteractiveBuildCommand.VISUALIZE:
                    self._visualize_family_tree()
                case InteractiveBuildCommand.BUILD_FAMILY_TREE:
                    break

        # Validate and build the tree
        errors = self.validate()
        if errors:
            print(_("Invalid family tree: {errors}", errors=""))
            for error in errors:
                print(f"- {error}")
            print(_("Please fix these errors and try again."))
            return self.interactive_build()

        return self.build()

    def _interactive_add_person(self) -> None:
        """Interactively add a person to the family tree."""
        print(f"\n{_('Adding a new person')}:")
        name = input(f"{_('Name')}: ")
        gender = input(f"{_('Gender')} (male/female): ")
        birth_year_str = input(f"{_('Birth year (optional, press Enter to skip)')}: ")
        birth_year = int(birth_year_str) if birth_year_str else None
        death_year_str = input(f"{_('Death year (optional, press Enter to skip)')}: ")
        death_year = int(death_year_str) if death_year_str else None

        try:
            self.add_person(
                name=name,
                gender=gender,
                birth_year=birth_year,
                death_year=death_year,
            )
            print(_("Added {name} to the family tree.", name=name))
        except ValueError as e:
            print(f"Error: {e}")

    def _interactive_add_relationship(self) -> None:
        """Interactively add a relationship to the family tree."""
        print(f"\n{_('Adding a new relationship')}:")
        print(f"{_('Available people')}:")
        for i, name in enumerate(sorted(self.people.keys()), 1):
            print(f"{i}. {name}")

        person_name = input(f"{_('Enter the name of the first person')}: ")
        if person_name not in self.people:
            print(_("Person '{name}' does not exist", name=person_name))
            return

        print(f"{_('Relationship types')}:")
        rel_types = [_("father"), _("mother"), _("child"), _("spouse")]
        for i, rel_type in enumerate(rel_types, 1):
            print(f"{i}. {rel_type.capitalize()}")

        rel_choice = input(f"{_('Enter your choice')} (1-4): ")
        try:
            rel_type = rel_types[int(rel_choice) - 1]
        except (ValueError, IndexError):
            print(_("Invalid relationship type: {relation}", relation=rel_choice))
            return

        relative_name = input(
            f"{_('Enter the name of the {relation}', relation=rel_type)}: "
        )
        if relative_name not in self.people:
            print(_("Person '{name}' does not exist", name=relative_name))
            return

        try:
            self.add_relationship(person_name, rel_type, relative_name)
            print(
                _(
                    "Added {relation} relationship between {person1} and {person2}.",
                    relation=rel_type,
                    person1=person_name,
                    person2=relative_name,
                )
            )
        except ValueError as e:
            print(f"Error: {e}")

    def _visualize_family_tree(self) -> None:
        """Visualize the family tree using Graphviz."""
        try:
            tree = self.build()
        except Exception as e:
            print(f"{_('Invalid family tree: {errors}', errors=str(e))}")
            print(_("Please fix these errors and try again."))
            return

        if not GRAPHVIZ_AVAILABLE:
            print(
                f"\n{_('Graphviz is not installed. Please install it to visualize the family tree.')}"
            )
            print(_("You can install it with: pip install graphviz"))
            print(_("You may also need to install the Graphviz system package."))

            tree.visualize()
            return

        lang = None
        while not lang:
            try:
                print(_("Pick language:"))
                supported_languages = get_available_languages()
                for i, lang in enumerate(supported_languages, 1):
                    print(f"{i}. {lang}")
                lang = input(
                    f"{_('Enter your choice')} (1-{len(supported_languages)}): "
                )
                lang = supported_languages[int(lang) - 1]
            except (ValueError, IndexError):
                print(_("Invalid choice. Please try again."))
                lang = None
                continue

        print(f"\n{_('Visualizing the family tree:')}")
        with force_language(lang):
            self.generate_family_tree_graphviz("family_tree", view=True)

    def generate_family_tree_graphviz(self, path: str, view: bool = True):
        """
        Generate a graphical representation of the family tree using Graphviz.

        Args:
            path: The path to save the rendered file (without extension)
            view: Whether to open the rendered file

        Returns:
            The path to the rendered file
        """
        # Import here to avoid circular imports
        from .visualizers import FamilyTreeGraphvizVisualizer

        # Build the family tree
        tree = self.build()

        # Create a graphical visualizer and render the output
        visualizer = FamilyTreeGraphvizVisualizer(tree, self)
        return visualizer.render(path, view)
