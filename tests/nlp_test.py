"""Unit tests for nlp.py."""

import pytest

from glosilo import nlp
from glosilo import consts


@pytest.mark.parametrize("word", consts.VORTETOJ)
def test_maybe_strip_plural_acc_ending_ignores_immune_words(word: str) -> None:
    assert nlp.maybe_strip_plural_acc_ending(word) == word


@pytest.mark.parametrize("word", ["kato", "katoj", "katojn", "katon"])
def test_maybe_strip_plural_acc_ending_strips_plural_accusative_ending(
    word: str,
) -> None:
    assert nlp.maybe_strip_plural_acc_ending(word) == "kato"


@pytest.mark.parametrize(
    ["word", "prefixes", "core", "suffixes", "ending"],
    [
        ("mia", [], "mi", [], "a"),
        ("nuna", [], "nun", [], "a"),
        ("ĉiom", [], "ĉiom", [], ""),
        ("la", [], "la", [], ""),
        ("estas", [], "est", [], "i"),
        ("plej", [], "plej", [], ""),
        ("unua", [], "unu", [], "a"),
        ("ajna", [], "ajn", [], "a"),
        ("diras", [], "dir", [], "i"),
        ("diro", [], "dir", [], "o"),
        ("dira", [], "dir", [], "a"),
        ("diru", [], "dir", [], "i"),
        ("dirigemita", [], "dir", ["ig", "em", "it"], "i"),
        ("direbligita", [], "dir", ["ebl", "ig", "it"], "i"),
        ("diraĉema", [], "dir", ["aĉ", "em"], "i"),
        ("pugnema", [], "pugn", ["em"], "i"),
        ("ekdiri", ["ek"], "dir", [], "i"),
        ("ekdiru", ["ek"], "dir", [], "i"),
        ("malnediro", ["mal", "ne"], "dir", [], "o"),
        ("nei", [], "ne", [], "i"),
        ("nea", [], "ne", [], "a"),
        ("neigi", ["ne"], "ig", [], "i"),
        ("neebla", ["ne"], "ebl", [], "i"),
        ("igi", [], "ig", [], "i"),
        ("nego", [], "neg", [], "o"),
        ("aĉeti", [], "aĉet", [], "i"),
        ("aŭtoritato", [], "aŭtoritat", [], "o"),
        ("geja", [], "gej", [], "a"),
        ("hejme", [], "hejm", [], "e"),
        ("disciplini", [], "disciplin", [], "i"),
        ("parolanto", [], "parol", ["ant"], "i"),
        ("jaro", [], "jar", [], "o"),
        ("lernejo", [], "lern", ["ej"], "o"),
        ("nekompreneble", ["ne"], "kompren", ["ebl"], "i"),
        ("malantaŭ", ["mal"], "antaŭ", [], ""),
        ("neebligos", ["ne"], "ebl", ["ig"], "i"),
        ("maltrankviliga", ["mal"], "trankvil", ["ig"], "i"),
        ("nebulo", [], "nebul", [], "o"),
        ("mem", [], "mem", [], ""),
    ],
)
def test_core_word_produces_core(
    word: str, prefixes: list[str], core: str, suffixes: list[str], ending: str
) -> None:
    cored = nlp.core_word(word, True)

    assert (
        cored.prefixes == prefixes
    ), f"Prefixes do not match, got {cored.prefixes}, expected {prefixes}"
    assert cored.core == core, f"Core does not match, got {cored.core}, expected {core}"
    assert (
        cored.suffixes == suffixes
    ), f"Suffixes do not match, got {cored.suffixes}, expected {suffixes}"
    assert (
        cored.preferred_ending == ending
    ), f"Ending does not match, got {cored.preferred_ending}, expected {ending}"
