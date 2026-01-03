"""Unit tests for _strip_affixes2 function."""
import pytest
from glosilo import eostem


@pytest.fixture
def stemmer() -> eostem.Stemmer:
    return eostem.Stemmer()

def test_simple_word_no_affixes(stemmer: eostem.Stemmer):
    """Test word with no prefixes or suffixes."""
    core, prefixes, suffixes = stemmer._strip_affixes2("parol")
    assert prefixes == []
    assert core == ["parol"]
    assert suffixes == []

def test_word_with_prefix(stemmer: eostem.Stemmer):
    """Test word with prefix."""
    core, prefixes, suffixes = stemmer._strip_affixes2("malbon")
    assert prefixes == ["mal"]
    assert core == ["bon"]
    assert suffixes == []

def test_word_with_suffix(stemmer: eostem.Stemmer):
    """Test word with suffix."""
    core, prefixes, suffixes = stemmer._strip_affixes2("parolant")
    assert prefixes == []
    assert core == ["parol"]
    assert suffixes == ["ant"]

def test_word_with_prefix_and_suffix(stemmer: eostem.Stemmer):
    """Test word with both prefix and suffix."""
    core, prefixes, suffixes = stemmer._strip_affixes2("nekomprenebl")
    assert prefixes == ["ne"]
    assert core == ["kompren"]
    assert suffixes == ["ebl"]

def test_word_with_multiple_suffixes(stemmer: eostem.Stemmer):
    """Test word with multiple suffixes."""
    core, prefixes, suffixes = stemmer._strip_affixes2("paroligit")
    assert prefixes == []
    assert core == ["parol"]
    assert suffixes == ["ig", "it"]

def test_word_with_multiple_prefixes(stemmer: eostem.Stemmer):
    """Test word with multiple prefixes."""
    core, prefixes, suffixes = stemmer._strip_affixes2("malnedir")
    assert prefixes == ["mal", "ne"]
    assert core == ["dir"]
    assert suffixes == []

def test_ekvilibr_longest_match(stemmer: eostem.Stemmer):
    """Test that ekvilibr is recognized as the longest match."""
    core, prefixes, suffixes = stemmer._strip_affixes2("ekvilibrigit")
    assert prefixes == []
    assert core == ["ekvilibr"]
    assert suffixes == ["ig", "it"]

def test_neigi_prefix_not_core(stemmer: eostem.Stemmer):
    """Test that 'ne' is treated as core (not prefix) in 'neig' due to special case."""
    core, prefixes, suffixes = stemmer._strip_affixes2("neig")
    assert prefixes == []
    assert core == ["ne"]
    assert suffixes == ["ig"]

def test_neul_special_case(stemmer: eostem.Stemmer):
    """Test that 'ne' is treated as core (not prefix) in 'neul' due to special case."""
    core, prefixes, suffixes = stemmer._strip_affixes2("neul")
    assert prefixes == []
    assert core == ["ne"]
    assert suffixes == ["ul"]

def test_neebla_core_is_ebl(stemmer: eostem.Stemmer):
    """Test that 'ebl' is recognized as core in 'neebl'."""
    core, prefixes, suffixes = stemmer._strip_affixes2("neebl")
    assert prefixes == ["ne"]
    assert core == ["ebl"]
    assert suffixes == []

def test_neind_special_case(stemmer: eostem.Stemmer):
    """Test that 'ind' is the core (not 'ne') in 'neind' - suffix is not ig/ul."""
    core, prefixes, suffixes = stemmer._strip_affixes2("neind")
    assert prefixes == ["ne"]
    assert core == ["ind"]
    assert suffixes == []

def test_preposition_prefix_ensumig(stemmer: eostem.Stemmer):
    """Test preposition used as prefix."""
    core, prefixes, suffixes = stemmer._strip_affixes2("ensumig")
    # Should recognize 'en' as preposition prefix, 'sum' as core, 'ig' as suffix
    assert prefixes == ["en"]
    assert core == ["sum"]
    assert suffixes == ["ig"]

def test_bonhumor_compound(stemmer: eostem.Stemmer):
    """Test that bonhumor is split as a compound."""
    core, prefixes, suffixes = stemmer._strip_affixes2("bonhumor")
    # Should split into bon + humor compound
    assert core == ["bon", "humor"]
    assert prefixes == []
    assert suffixes == []

def test_maltrankvilig_with_prefix(stemmer: eostem.Stemmer):
    """Test word with mal prefix and no suffixes."""
    core, prefixes, suffixes = stemmer._strip_affixes2("maltrankvil")
    assert prefixes == ["mal"]
    assert core == ["trankvil"]
    assert suffixes == []

def test_dezert_not_split_as_preposition(stemmer: eostem.Stemmer):
    """Test that 'dezert' is not incorrectly split as 'de+zert'."""
    core, prefixes, suffixes = stemmer._strip_affixes2("dezert")
    # 'dezert' is a valid root in rad_dictionary
    # 'zert' is NOT a valid root
    # Should NOT treat 'de' as a preposition prefix
    assert prefixes == []
    assert core == ["dezert"]
    assert suffixes == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
