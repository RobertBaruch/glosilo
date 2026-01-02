"""Unit tests for compound word splitting."""
import pytest
from glosilo import eostem


class TestCompoundWords:
    """Test cases for compound word splitting."""

    def test_vaporŝip_compound(self):
        """vaporŝip -> vapor + ŝip"""
        cored = eostem.core_word("vaporŝip")
        assert cored.core == ["vapor", "ŝip"]

    def test_puŝoŝip_compound(self):
        """puŝoŝip -> puŝ + o + ŝip (with linking o)"""
        cored = eostem.core_word("puŝoŝip")
        assert cored.core == ["puŝ", "o", "ŝip"]

    def test_lastatemp_compound(self):
        """lastatemp -> last + a + temp (with linking a)"""
        cored = eostem.core_word("lastatemp")
        assert cored.core == ["last", "a", "temp"]

    def test_dikfingr_compound(self):
        """dikfingr -> dik + fingr"""
        cored = eostem.core_word("dikfingr")
        assert cored.core == ["dik", "fingr"]

    def test_ruĝfarb_compound(self):
        """ruĝfarb -> ruĝ + farb"""
        cored = eostem.core_word("ruĝfarb")
        assert cored.core == ["ruĝ", "farb"]

    def test_bluokul_compound(self):
        """bluokul -> blu + okul"""
        cored = eostem.core_word("bluokul")
        assert cored.core == ["blu", "okul"]

    def test_laŭtleg_compound(self):
        """laŭtleg -> laŭt + leg"""
        cored = eostem.core_word("laŭtleg")
        assert cored.core == ["laŭt", "leg"]

    def test_pagipov_compound(self):
        """pagipov -> pag + pov (with linking i)"""
        cored = eostem.core_word("pagipov")
        assert cored.core == ["pag", "i", "pov"]

    def test_pagopov_compound(self):
        """pagopov -> pag + pov (with linking o)"""
        cored = eostem.core_word("pagopov")
        assert cored.core == ["pag", "o", "pov"]

    def test_multehom_linking_vowel(self):
        """multehom -> mult + hom (with linking e)"""
        cored = eostem.core_word("multehom")
        assert cored.core == ["mult", "e", "hom"]

    def test_multekost_linking_vowel(self):
        """multekost -> mult + kost (with linking e)"""
        cored = eostem.core_word("multekost")
        assert cored.core == ["mult", "e", "kost"]

    def test_simple_word_single_element(self):
        """Simple words should remain single-element lists."""
        cored = eostem.core_word("parol")
        assert cored.core == ["parol"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
