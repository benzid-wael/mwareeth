#!/usr/bin/env python3
"""
This example demonstrates how to use the gettext-based internationalization (i18n) 
support in the mwareeth project.
"""

import sys
import os

# Add the parent directory to the path so we can import the mwareeth package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mwareeth.i18n import _, set_language, get_available_languages
from mwareeth.family_tree_builder import FamilyTreeBuilder


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 50 + "\n")


def main():
    """
    Demonstrate the gettext-based internationalization support in the mwareeth project.
    """
    # Print available languages
    print("Available languages:")
    for lang in get_available_languages():
        print(f"- {lang}")
    
    print_separator()
    
    # Example 1: Using English translations
    print("Example 1: Using English translations")
    set_language("en")
    
    # Print some translated strings
    print(_("welcome"))
    print(_("deceased_intro"))
    print(_("name"), ":", "John")
    print(_("gender"), ":", "male")
    print(_("father"), ":", "Michael")
    print(_("mother"), ":", "Sarah")
    
    print_separator()
    
    # Example 2: Using Arabic translations
    print("Example 2: Using Arabic translations")
    set_language("ar")
    
    # Print the same strings in Arabic
    print(_("welcome"))
    print(_("deceased_intro"))
    print(_("name"), ":", "جون")
    print(_("gender"), ":", "ذكر")
    print(_("father"), ":", "مايكل")
    print(_("mother"), ":", "سارة")
    
    print_separator()
    
    # Example 3: Creating a family tree with translations
    print("Example 3: Creating a family tree with translations")
    
    # Switch back to English
    set_language("en")
    print("Creating a family tree in English:")
    
    # Create a family tree builder
    builder_en = FamilyTreeBuilder(language="en")
    
    # Add some people
    builder_en.add_person(
        name="John",
        gender="male",
        birth_year=1950,
        death_year=2020,
        is_deceased=True,
    )
    builder_en.add_person(
        name="Mary",
        gender="female",
        birth_year=1952,
    )
    builder_en.add_person(
        name="Bob",
        gender="male",
        birth_year=1975,
    )
    
    # Add relationships
    builder_en.add_relationship("Bob", "father", "John")
    builder_en.add_relationship("Bob", "mother", "Mary")
    
    # Build the family tree
    family_tree_en = builder_en.build()
    
    # Print the family tree visualization
    print(family_tree_en.visualize())
    
    print_separator()
    
    # Switch to Arabic
    set_language("ar")
    print("Creating a family tree in Arabic:")
    
    # Create a family tree builder
    builder_ar = FamilyTreeBuilder(language="ar")
    
    # Add some people
    builder_ar.add_person(
        name="جون",
        gender="male",
        birth_year=1950,
        death_year=2020,
        is_deceased=True,
    )
    builder_ar.add_person(
        name="ماري",
        gender="female",
        birth_year=1952,
    )
    builder_ar.add_person(
        name="بوب",
        gender="male",
        birth_year=1975,
    )
    
    # Add relationships
    builder_ar.add_relationship("بوب", _("father"), "جون")
    builder_ar.add_relationship("بوب", _("mother"), "ماري")
    
    # Build the family tree
    family_tree_ar = builder_ar.build()
    
    # Print the family tree visualization
    print(family_tree_ar.visualize())


if __name__ == "__main__":
    main()
