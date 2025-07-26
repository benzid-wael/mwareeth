import unittest

from ..heir_builder import deduce_heir_type
from ..entities.relationship import RelationshipType
from ..entities.heir import HeirType


class TestHeirBuilder(unittest.TestCase):
    """Test cases for the heir_builder module."""

    def test_deduce_heir_type_spouses(self):
        """Test deducing heir types for spouses."""
        # Test husband
        lineage = [RelationshipType.HUSBAND]
        self.assertEqual(deduce_heir_type(lineage), HeirType.HUSBAND)

        # Test wife
        lineage = [RelationshipType.WIFE]
        self.assertEqual(deduce_heir_type(lineage), HeirType.WIFE)

    def test_deduce_heir_type_direct_ancestors(self):
        """Test deducing heir types for direct ancestors."""
        # Test father
        lineage = [RelationshipType.FATHER]
        self.assertEqual(deduce_heir_type(lineage), HeirType.FATHER)

        # Test mother
        lineage = [RelationshipType.MOTHER]
        self.assertEqual(deduce_heir_type(lineage), HeirType.MOTHER)

    def test_deduce_heir_type_direct_descendants(self):
        """Test deducing heir types for direct descendants."""
        # Test son
        lineage = [RelationshipType.SON]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SON)

        # Test daughter
        lineage = [RelationshipType.DAUGHTER]
        self.assertEqual(deduce_heir_type(lineage), HeirType.DAUGHTER)

    def test_deduce_heir_type_siblings(self):
        """Test deducing heir types for siblings."""
        # Test full brother
        lineage = [RelationshipType.BROTHER_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.BROTHER_FULL)

        # Test paternal brother
        lineage = [RelationshipType.BROTHER_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.BROTHER_PARENTAL)

        # Test maternal brother
        lineage = [RelationshipType.BROTHER_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.BROTHER_MATERNAL)

        # Test full sister
        lineage = [RelationshipType.SISTER_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SISTER_FULL)

        # Test paternal sister
        lineage = [RelationshipType.SISTER_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SISTER_PARENTAL)

        # Test maternal sister
        lineage = [RelationshipType.SISTER_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SISTER_MATERNAL)

    def test_deduce_heir_type_uncles(self):
        """Test deducing heir types for uncles."""
        # Test paternal uncle (full)
        lineage = [RelationshipType.PARENTAL_UNCLE_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UNCLE_FULL)

        # Test paternal uncle (paternal)
        lineage = [RelationshipType.PARENTAL_UNCLE_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UNCLE_PARENTAL)

        # Test paternal uncle (maternal) - should be uterine
        lineage = [RelationshipType.PARENTAL_UNCLE_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_aunts(self):
        """Test deducing heir types for aunts."""
        # All aunts should be uterine
        lineage = [RelationshipType.PARENTAL_AUNT_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.PARENTAL_AUNT_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.PARENTAL_AUNT_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.MATERNAL_AUNT_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.MATERNAL_AUNT_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.MATERNAL_AUNT_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_maternal_uncles(self):
        """Test deducing heir types for maternal uncles."""
        # All maternal uncles should be uterine
        lineage = [RelationshipType.MATERNAL_UNCLE_FULL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.MATERNAL_UNCLE_PARENTAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [RelationshipType.MATERNAL_UNCLE_MATERNAL]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_complex_lineages(self):
        """Test deducing heir types for complex lineages."""
        # Father's father's father
        lineage = [
            RelationshipType.FATHER,
            RelationshipType.FATHER,
            RelationshipType.FATHER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.FATHER)

        # Father's mother's father - should be uterine
        lineage = [
            RelationshipType.FATHER,
            RelationshipType.MOTHER,
            RelationshipType.FATHER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        # Son of paternal uncle (full)
        lineage = [
            RelationshipType.PARENTAL_UNCLE_FULL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SON_UNCLE_FULL)

        # Son of son of paternal uncle (full)
        lineage = [
            RelationshipType.PARENTAL_UNCLE_FULL,
            RelationshipType.SON,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SON_UNCLE_FULL)

        # Daughter of paternal uncle (full) - should be uterine
        lineage = [
            RelationshipType.PARENTAL_UNCLE_FULL,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_nephews(self):
        """Test deducing heir types for nephews."""
        # Son of full brother
        lineage = [
            RelationshipType.BROTHER_FULL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.NEPHEW_FULL)

        # Son of paternal brother
        lineage = [
            RelationshipType.BROTHER_PARENTAL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.NEPHEW_PARENTAL)

        # Son of maternal brother - should be uterine
        lineage = [
            RelationshipType.BROTHER_MATERNAL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_nieces(self):
        """Test deducing heir types for nieces."""
        # All nieces should be uterine
        lineage = [
            RelationshipType.BROTHER_FULL,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [
            RelationshipType.BROTHER_PARENTAL,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [
            RelationshipType.BROTHER_MATERNAL,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [
            RelationshipType.SISTER_FULL,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_sons_of_sisters(self):
        """Test deducing heir types for sons of sisters."""
        # All sons of sisters should be uterine
        lineage = [
            RelationshipType.SISTER_FULL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [
            RelationshipType.SISTER_PARENTAL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        lineage = [
            RelationshipType.SISTER_MATERNAL,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

    def test_deduce_heir_type_descendants_of_descendants(self):
        """Test deducing heir types for descendants of descendants."""
        # Son's son - should be son
        lineage = [
            RelationshipType.SON,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.SON)

        # Son's daughter - should be daughter
        lineage = [
            RelationshipType.SON,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.DAUGHTER)

        # Daughter's son - should be uterine
        lineage = [
            RelationshipType.DAUGHTER,
            RelationshipType.SON,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)

        # Daughter's daughter - should be uterine
        lineage = [
            RelationshipType.DAUGHTER,
            RelationshipType.DAUGHTER,
        ]
        self.assertEqual(deduce_heir_type(lineage), HeirType.UTERINE)


if __name__ == '__main__':
    unittest.main()
