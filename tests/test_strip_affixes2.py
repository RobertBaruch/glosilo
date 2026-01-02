"""Unit tests for _strip_affixes2 function."""
import pytest
from glosilo import eostem


class TestStripAffixes2:
    """Test cases for _strip_affixes2 function."""

    def test_simple_word_no_affixes(self):
        """Test word with no prefixes or suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes2("parol")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == []

    def test_word_with_prefix(self):
        """Test word with prefix."""
        core, prefixes, suffixes = eostem._strip_affixes2("malbon")
        assert prefixes == ["mal"]
        assert core == "bon"
        assert suffixes == []

    def test_word_with_suffix(self):
        """Test word with suffix."""
        core, prefixes, suffixes = eostem._strip_affixes2("parolant")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == ["ant"]

    def test_word_with_prefix_and_suffix(self):
        """Test word with both prefix and suffix."""
        core, prefixes, suffixes = eostem._strip_affixes2("nekomprenebl")
        assert prefixes == ["ne"]
        assert core == "kompren"
        assert suffixes == ["ebl"]

    def test_word_with_multiple_suffixes(self):
        """Test word with multiple suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes2("paroligit")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == ["ig", "it"]

    def test_word_with_multiple_prefixes(self):
        """Test word with multiple prefixes."""
        core, prefixes, suffixes = eostem._strip_affixes2("malnedir")
        assert prefixes == ["mal", "ne"]
        assert core == "dir"
        assert suffixes == []

    def test_ekvilibr_longest_match(self):
        """Test that ekvilibr is recognized as the longest match."""
        core, prefixes, suffixes = eostem._strip_affixes2("ekvilibrigit")
        assert prefixes == []
        assert core == "ekvilibr"
        assert suffixes == ["ig", "it"]

    def test_neigi_prefix_not_core(self):
        """Test that 'ne' is treated as core (not prefix) in 'neig' due to special case."""
        core, prefixes, suffixes = eostem._strip_affixes2("neig")
        assert prefixes == []
        assert core == "ne"
        assert suffixes == ["ig"]

    def test_neul_special_case(self):
        """Test that 'ne' is treated as core (not prefix) in 'neul' due to special case."""
        core, prefixes, suffixes = eostem._strip_affixes2("neul")
        assert prefixes == []
        assert core == "ne"
        assert suffixes == ["ul"]

    def test_neebla_core_is_ebl(self):
        """Test that 'ebl' is recognized as core in 'neebl'."""
        core, prefixes, suffixes = eostem._strip_affixes2("neebl")
        assert prefixes == ["ne"]
        assert core == "ebl"
        assert suffixes == []

    def test_neind_special_case(self):
        """Test that 'ind' is the core (not 'ne') in 'neind' - suffix is not ig/ul."""
        core, prefixes, suffixes = eostem._strip_affixes2("neind")
        assert prefixes == ["ne"]
        assert core == "ind"
        assert suffixes == []

    def test_studjar_compound_word(self):
        """Test that compound word 'studjar' is kept intact."""
        core, prefixes, suffixes = eostem._strip_affixes2("studjar")
        assert prefixes == []
        assert core == "studjar"
        assert suffixes == []

    def test_preposition_prefix_ensumig(self):
        """Test preposition used as prefix."""
        core, prefixes, suffixes = eostem._strip_affixes2("ensumig")
        # Should recognize 'en' as preposition prefix, 'sum' as core, 'ig' as suffix
        assert prefixes == ["en"]
        assert core == "sum"
        assert suffixes == ["ig"]

    def test_bonhumor_not_split(self):
        """Test that bonhumor is recognized as a unit."""
        core, prefixes, suffixes = eostem._strip_affixes2("bonhumor")
        # Should keep as single core since it's a compound
        assert core == "bonhumor"
        assert prefixes == []
        assert suffixes == []

    def test_maltrankvilig_with_prefix(self):
        """Test word with mal prefix and no suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes2("maltrankvil")
        assert prefixes == ["mal"]
        assert core == "trankvil"
        assert suffixes == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
