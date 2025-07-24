"""
Example script demonstrating how to visualize a family tree.
"""

import sys
import os

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.person import Person, Gender
from src.family_tree import FamilyTree


def create_sample_family():
    """Create a sample family tree for visualization."""
    # Create the deceased person
    deceased = Person("Ahmed", Gender.MALE)
    
    # Create parents
    father = Person("Mohammed", Gender.MALE)
    mother = Person("Fatima", Gender.FEMALE)
    
    # Create grandparents
    grandfather_paternal = Person("Ibrahim", Gender.MALE)
    grandmother_paternal = Person("Aisha", Gender.FEMALE)
    grandfather_maternal = Person("Yusuf", Gender.MALE)
    grandmother_maternal = Person("Khadija", Gender.FEMALE)
    
    # Create siblings
    brother = Person("Ali", Gender.MALE)
    sister = Person("Zaynab", Gender.FEMALE)
    
    # Create uncles and aunts
    uncle = Person("Omar", Gender.MALE)
    aunt = Person("Maryam", Gender.FEMALE)
    
    # Create children
    son = Person("Hamza", Gender.MALE)
    daughter = Person("Noor", Gender.FEMALE)
    
    # Create grandchildren
    grandson = Person("Zaid", Gender.MALE)
    granddaughter = Person("Layla", Gender.FEMALE)
    
    # Set up relationships
    
    # Connect deceased to parents
    deceased.add_father(father)
    deceased.add_mother(mother)
    
    # Connect parents to grandparents
    father.add_father(grandfather_paternal)
    father.add_mother(grandmother_paternal)
    mother.add_father(grandfather_maternal)
    mother.add_mother(grandmother_maternal)
    
    # Connect siblings
    brother.add_father(father)
    brother.add_mother(mother)
    sister.add_father(father)
    sister.add_mother(mother)
    
    # Connect uncles and aunts
    uncle.add_father(grandfather_paternal)
    uncle.add_mother(grandmother_paternal)
    aunt.add_father(grandfather_paternal)
    aunt.add_mother(grandmother_paternal)
    
    # Connect children
    deceased.add_child(son)
    deceased.add_child(daughter)
    
    # Connect grandchildren
    son.add_child(grandson)
    daughter.add_child(granddaughter)
    
    return deceased


def main():
    """Create and visualize a sample family tree."""
    # Create a sample family
    deceased = create_sample_family()
    
    # Create the family tree
    family_tree = FamilyTree(deceased)
    
    # Visualize the family tree
    visualization = family_tree.visualize()
    
    # Print the visualization
    print(visualization)


if __name__ == "__main__":
    main()
