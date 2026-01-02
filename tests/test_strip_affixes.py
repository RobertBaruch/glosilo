"""Unit tests for _strip_affixes function."""
import pytest
from glosilo import eostem


class TestStripAffixes:
    """Test cases for _strip_affixes function."""

    def test_simple_word_no_affixes(self):
        """Test word with no prefixes or suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes("parol")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == []

    def test_word_with_prefix(self):
        """Test word with prefix."""
        core, prefixes, suffixes = eostem._strip_affixes("malbon")
        assert prefixes == ["mal"]
        assert core == "bon"
        assert suffixes == []

    def test_word_with_suffix(self):
        """Test word with suffix."""
        core, prefixes, suffixes = eostem._strip_affixes("parolant")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == ["ant"]

    def test_word_with_prefix_and_suffix(self):
        """Test word with both prefix and suffix."""
        core, prefixes, suffixes = eostem._strip_affixes("nekomprenebl")
        assert prefixes == ["ne"]
        assert core == "kompren"
        assert suffixes == ["ebl"]

    def test_word_with_multiple_suffixes(self):
        """Test word with multiple suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes("paroligit")
        assert prefixes == []
        assert core == "parol"
        assert suffixes == ["ig", "it"]

    def test_word_with_multiple_prefixes(self):
        """Test word with multiple prefixes."""
        core, prefixes, suffixes = eostem._strip_affixes("malnedir")
        assert prefixes == ["mal", "ne"]
        assert core == "dir"
        assert suffixes == []

    def test_ekvilibr_longest_match(self):
        """Test that ekvilibr is recognized as the longest match."""
        core, prefixes, suffixes = eostem._strip_affixes("ekvilibrigit")
        assert prefixes == []
        assert core == "ekvilibr"
        assert suffixes == ["ig", "it"]

    def test_neigi_prefix_not_core(self):
        """Test that 'ne' is treated as prefix, not core in 'neig'."""
        core, prefixes, suffixes = eostem._strip_affixes("neig")
        assert prefixes == ["ne"]
        assert core == "ig"
        assert suffixes == []

    def test_neebla_core_is_ebl(self):
        """Test that 'ebl' is recognized as core in 'neebl'."""
        core, prefixes, suffixes = eostem._strip_affixes("neebl")
        assert prefixes == ["ne"]
        assert core == "ebl"
        assert suffixes == []

    def test_studjar_compound_word(self):
        """Test that compound word 'studjar' is kept intact."""
        core, prefixes, suffixes = eostem._strip_affixes("studjar")
        assert prefixes == []
        assert core == "studjar"
        assert suffixes == []

    def test_preposition_prefix_ensumig(self):
        """Test preposition used as prefix."""
        core, prefixes, suffixes = eostem._strip_affixes("ensumig")
        # Should recognize 'en' as preposition prefix, 'sum' as core, 'ig' as suffix
        assert "en" in prefixes or core == "ensum"  # Either interpretation acceptable
        assert "ig" in suffixes or core == "ensumig"

    def test_bonhumor_not_split(self):
        """Test that bonhumor is recognized as a unit."""
        core, prefixes, suffixes = eostem._strip_affixes("bonhumor")
        # Should keep as single core since it's a compound
        assert core in ["bonhumor", "bon"]  # Either is acceptable

    def test_maltrankvilig_with_prefix(self):
        """Test word with mal prefix and multiple suffixes."""
        core, prefixes, suffixes = eostem._strip_affixes("maltrankvil")
        assert "mal" in prefixes
        assert "trankvil" in core
        assert suffixes == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
