"""
This module provides a FamilyTreeBuilder class to help users build a family tree
from their inputs in an interactive and user-friendly way.
"""

from enum import IntEnum, auto
from typing import Dict, List, Optional, Set, Tuple

# Try to import Graphviz, but don't fail if it's not installed
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    # Define a dummy Digraph class to avoid "possibly unbound" errors
    class Digraph:
        """Dummy Digraph class when graphviz is not available."""
        def __init__(self, comment='', strict=False):
            self.comment = comment
            self.strict = strict
            self.source = "Graphviz not available"
        
        def attr(self, *args, **kwargs):
            """Dummy attr method."""
            pass
        
        def node(self, *args, **kwargs):
            """Dummy node method."""
            pass
        
        def edge(self, *args, **kwargs):
            """Dummy edge method."""
            pass
        
        def render(self, *args, **kwargs):
            """Dummy render method."""
            raise ImportError("Graphviz is not installed")

from .entities.person import Gender, Person, Religion
from .entities.family_tree import FamilyTree



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

    def __init__(self):
        """Initialize an empty family tree builder."""
        self.people: Dict[str, Person] = {}
        self.deceased: Optional[Person] = None

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
            raise ValueError(f"A person with the name '{name}' already exists")
        
        # Convert gender string to Gender enum
        try:
            gender_enum = Gender[gender.upper()]
        except KeyError:
            raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")
        
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
                raise ValueError("A deceased person is already set")
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
            raise ValueError(f"Person '{name}' does not exist")
        
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
            raise ValueError(f"Person '{person_name}' does not exist")
        if relative_name not in self.people:
            raise ValueError(f"Person '{relative_name}' does not exist")
        
        person = self.people[person_name]
        relative = self.people[relative_name]
        
        # Add the relationship based on the type
        if relation_type.lower() == "father":
            person.add_father(relative)
        elif relation_type.lower() == "mother":
            person.add_mother(relative)
        elif relation_type.lower() == "child":
            person.add_child(relative)
        elif relation_type.lower() == "spouse":
            person.add_spouse(relative)
            relative.add_spouse(person)
        else:
            raise ValueError(f"Invalid relationship type: {relation_type}")
        
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
            errors.append("No deceased person is set")
        
        # Check for circular references
        visited = set()
        for person in self.people.values():
            path = set()
            if self._has_circular_reference(person, visited, path):
                errors.append(f"Circular reference detected involving {person.name}")
                errors.append(f"  - Visited: {', '.join(p.name for p in visited)}")
                errors.append(f"  - Path: {', '.join(p.name for p in path)}")
        
        # Check for inconsistent relationships
        for name, person in self.people.items():
            # Check father-child consistency
            if person.father and person not in person.father.children:
                errors.append(f"Inconsistent father-child relationship for {name}")
            
            # Check mother-child consistency
            if person.mother and person not in person.mother.children:
                errors.append(f"Inconsistent mother-child relationship for {name}")
            
            # Check spouse consistency
            for spouse in person.spouses:
                if person not in spouse.spouses:
                    errors.append(f"Inconsistent spousal relationship between {name} and {spouse.name}")
        
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
            raise ValueError(f"Invalid family tree: {', '.join(errors)}")
        
        # Check if deceased is set
        if not self.deceased:
            raise ValueError("No deceased person is set")
        
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
                result["relationships"].append({
                    "person": name,
                    "relation": "father",
                    "relative": person.father.name,
                })
            
            # Add mother relationship
            if person.mother:
                result["relationships"].append({
                    "person": name,
                    "relation": "mother",
                    "relative": person.mother.name,
                })
            
            # Add spouse relationships
            for spouse in person.spouses:
                # Only add the relationship once (from the person with the lexicographically smaller name)
                if name < spouse.name:
                    result["relationships"].append({
                        "person": name,
                        "relation": "spouse",
                        "relative": spouse.name,
                    })
        
        return result

    def interactive_build(self) -> FamilyTree:
        """
        Build a family tree interactively by prompting the user for inputs.
        
        Returns:
            A FamilyTree instance
        """
        print("Welcome to the Family Tree Builder!")
        print("Let's start by adding the deceased person (the focal point of the tree).")
        
        # Add the deceased person
        name = input("Name: ")
        gender = input("Gender (male/female): ")
        birth_year_str = input("Birth year (optional, press Enter to skip): ")
        birth_year = int(birth_year_str) if birth_year_str else None
        death_year_str = input("Death year (optional, press Enter to skip): ")
        death_year = int(death_year_str) if death_year_str else None
        
        self.add_person(
            name=name,
            gender=gender,
            birth_year=birth_year,
            death_year=death_year,
            is_deceased=True,
        )
        
        # Add more people and relationships
        commands = sorted([
            (InteractiveBuildCommand.ADD_PERSON, "Add a person"),
            (InteractiveBuildCommand.ADD_RELATIONSHIP, "Add a relationship"),
            (InteractiveBuildCommand.VISUALIZE, "Visualize the family tree"),
            (InteractiveBuildCommand.BUILD_FAMILY_TREE, "Finish and build the family tree"),
        ])
        while True:
            print("\nWhat would you like to do?")
            print("\n".join(f"{command}. {help_text}" for command, help_text in commands))
            choice = input(f"Enter your choice (1-{len(commands)}): ")
            
            try:
                choice = int(choice)
                choice = InteractiveBuildCommand(choice)
            except ValueError:
                print("Invalid choice. Please try again.")
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
            print("The family tree has the following errors:")
            for error in errors:
                print(f"- {error}")
            print("Please fix these errors and try again.")
            return self.interactive_build()
        
        return self.build()

    def _interactive_add_person(self) -> None:
        """Interactively add a person to the family tree."""
        print("\nAdding a new person:")
        name = input("Name: ")
        gender = input("Gender (male/female): ")
        birth_year_str = input("Birth year (optional, press Enter to skip): ")
        birth_year = int(birth_year_str) if birth_year_str else None
        death_year_str = input("Death year (optional, press Enter to skip): ")
        death_year = int(death_year_str) if death_year_str else None
        
        try:
            self.add_person(
                name=name,
                gender=gender,
                birth_year=birth_year,
                death_year=death_year,
            )
            print(f"Added {name} to the family tree.")
        except ValueError as e:
            print(f"Error: {e}")

    def _interactive_add_relationship(self) -> None:
        """Interactively add a relationship to the family tree."""
        print("\nAdding a new relationship:")
        print("Available people:")
        for i, name in enumerate(sorted(self.people.keys()), 1):
            print(f"{i}. {name}")
        
        person_name = input("Enter the name of the first person: ")
        if person_name not in self.people:
            print(f"Error: Person '{person_name}' does not exist.")
            return
        
        print("Relationship types:")
        print("1. Father")
        print("2. Mother")
        print("3. Child")
        print("4. Spouse")
        
        rel_choice = input("Enter the relationship type (1-4): ")
        rel_types = ["father", "mother", "child", "spouse"]
        try:
            rel_type = rel_types[int(rel_choice) - 1]
        except (ValueError, IndexError):
            print("Error: Invalid relationship type.")
            return
        
        relative_name = input(f"Enter the name of the {rel_type}: ")
        if relative_name not in self.people:
            print(f"Error: Person '{relative_name}' does not exist.")
            return
        
        try:
            self.add_relationship(person_name, rel_type, relative_name)
            print(f"Added {rel_type} relationship between {person_name} and {relative_name}.")
        except ValueError as e:
            print(f"Error: {e}")

    def _visualize_family_tree(self) -> None:
        """Visualize the family tree using Graphviz."""
        try:
            tree = self.build()
        except Exception as e:
            print(f"Invalid family tree: {e}")
            print("Please fix the errors before visualizing.")
            return

        if not GRAPHVIZ_AVAILABLE:
            print("\nGraphviz is not installed. Please install it to visualize the family tree.")
            print("You can install it with: pip install graphviz")
            print("You may also need to install the Graphviz system package.")

            tree.visualize()
            return

        print("\nVisualizing the family tree:")
        # Create a new directed graph
        dot = Digraph(comment='Family Tree', strict=False)
        dot.attr(rankdir='TB', size='8,8')
        
        # Add nodes for each person
        for name, person in self.people.items():
            # Set node attributes based on gender
            shape = 'box' if person.gender == Gender.MALE else 'ellipse'
            
            # Set color based on whether the person is deceased
            color = 'red' if person == self.deceased else 'black'
            
            # Create label with person's details
            label = f"{name}"
            if person.birth_year:
                label += f"\nBorn: {person.birth_year}"
            if person.death_year:
                label += f"\nDied: {person.death_year}"
            
            # Add the node
            dot.node(name, label=label, shape=shape, color=color, 
                        style='filled' if person == self.deceased else '', 
                        fillcolor='lightgray' if person == self.deceased else '')
        
        # Add edges for parent-child relationships
        for name, person in self.people.items():
            # Add edge to father
            if person.father and person.father.name in self.people:
                dot.edge(person.father.name, name, color='blue', label='father')
            
            # Add edge to mother
            if person.mother and person.mother.name in self.people:
                dot.edge(person.mother.name, name, color='green', label='mother')
        
        # Add edges for spousal relationships
        for name, person in self.people.items():
            for spouse in person.spouses:
                if spouse.name in self.people and name < spouse.name:  # Only add once
                    dot.edge(name, spouse.name, color='red', style='dashed', dir='none', label='spouse')
        
        # Render the graph
        try:
            # Try to render and display the graph
            dot.render('family_tree.dot', format='png', view=True, cleanup=True)
            print("Family tree visualization has been generated and should open automatically.")
        except Exception as e:
            # If rendering fails, just print the DOT source
            print("Could not render the graph. Here's the DOT source:")
            print(dot.source)
            print(f"Error: {e}")
