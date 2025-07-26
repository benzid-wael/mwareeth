import os
import sys

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mwareeth.family_tree_builder import FamilyTreeBuilder

if __name__ == "__main__":
    # Create a new family tree builder
    builder = FamilyTreeBuilder(language="en")

    # Build the family tree interactively
    tree = builder.interactive_build()

    # Print the family tree
    print(tree.visualize())

    import json

    # Save the family tree to a JSON file
    with open("family_tree.json", "w") as f:
        json.dump(builder.to_dict(), f, indent=2)
