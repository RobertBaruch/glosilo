"""Unit tests for dictionary.py"""

from typing import Any

import pytest

from glosilo import consts
from glosilo import dictionary


THE_DICTIONARY = dictionary.Dictionary(debug=True)


def _print_mismatch(what: str, word: str, expected: Any, got: Any) -> str:
    return f"{what} for {word}, expected: {expected}, got: {got}"


# @pytest.mark.parametrize("word", consts.COMMON_WORDS)
# def test_get_gloss(word: str) -> None:
#     gloss = THE_DICTIONARY.get_gloss(word)
#     assert (
#         gloss.orig_word == word
#     ), f"orig_word for {word} does not match: {gloss.orig_word} != {word}"
#     assert gloss.core == "", f"core for {word} does not match: {gloss.core} != ''"
#     assert (
#         gloss.prefixes == []
#     ), f"prefixes for {word} does not match: {gloss.prefixes} != []"
#     assert (
#         gloss.suffixes == []
#     ), f"suffixes for {word} does not match: {gloss.suffixes} != []"
#     assert (
#         gloss.preferred_definition == ""
#     ), f"preferred_definition for {word} does not match: {gloss.preferred_definition} != ''"


# @pytest.mark.parametrize("word", consts.COMMON_WORDS)
# def test_get_gloss_uppercase(word: str) -> None:
#     word = word[0].upper() + word[1:]
#     gloss = THE_DICTIONARY.get_gloss(word)
#     assert (
#         gloss.orig_word == word
#     ), f"orig_word {_print_mismatch(word, word, gloss.orig_word)}"
#     assert gloss.core == "", f"core {_print_mismatch(word, '', gloss.core)}"
#     assert (
#         gloss.prefixes == []
#     ), f"prefixes {_print_mismatch(word, [], gloss.prefixes)}"
#     assert (
#         gloss.suffixes == []
#     ), f"suffixes {_print_mismatch(word, [], gloss.suffixes)}"
#     assert (
#         gloss.preferred_definition == ""
#     ), f"preferred_definition {_print_mismatch(word, '', gloss.preferred_definition)}"
#     assert (
#         gloss.core_definition == ""
#     ), f"core_definition {_print_mismatch(word, '', gloss.core_definition)}"


# @pytest.mark.parametrize(
#     "word", ["iun", "iuj", "ion", "iojn", "faras", "diru", "postajn"]
# )
# def test_get_gloss_modified_common_words(word: str) -> None:
#     gloss = THE_DICTIONARY.get_gloss(word)
#     assert (
#         gloss.orig_word == word
#     ), f"orig_word for {word} does not match: {gloss.orig_word} != {word}"
#     assert gloss.core == "", f"core for {word} does not match: {gloss.core} != ''"
#     assert (
#         gloss.prefixes == []
#     ), f"prefixes for {word} does not match: {gloss.prefixes} != []"
#     assert (
#         gloss.suffixes == []
#     ), f"suffixes for {word} does not match: {gloss.suffixes} != []"
#     assert (
#         gloss.preferred_definition == ""
#     ), f"preferred_definition for {word} does not match: {gloss.preferred_definition} != ''"


@pytest.mark.parametrize("word", ["paroli", "parolu", "parolas"])
def test_get_gloss_paroli(word: str) -> None:
    gloss = THE_DICTIONARY.get_gloss(word)
    assert gloss.orig_word == word, _print_mismatch(
        "orig_word", word, word, gloss.orig_word
    )
    assert gloss.core == ["parol"], _print_mismatch("core", word, ["parol"], gloss.core)
    assert gloss.prefixes == [], _print_mismatch("prefixes", word, [], gloss.prefixes)
    assert gloss.suffixes == [], _print_mismatch("suffixes", word, [], gloss.suffixes)
    assert gloss.preferred_definition == "to-speak", _print_mismatch(
        "preferred_definition", word, "to-speak", gloss.preferred_definition
    )


@pytest.mark.parametrize(
    ["word", "suffixes", "definition", "ending", "core_definition"],
    [
        ("paroligi", ["ig"], "to-get-sb-to-talk", "i", "to-speak"),
        ("paroligas", ["ig"], "to-get-sb-to-talk", "i", "to-speak"),
        ("parolanto", ["ant"], "speaker", "i", "to-speak"),
        ("parolanta", ["ant"], "", "i", "to-speak"),
        ("parolo", [], "speech", "o", "speech"),
        ("parolaĉo", ["aĉ"], "", "o", "speech"),
    ],
)
def test_get_gloss_paroli_with_suffixes(
    word: str, suffixes: list[str], definition: str, ending: str, core_definition: str
) -> None:
    gloss = THE_DICTIONARY.get_gloss(word)
    assert gloss.orig_word == word, _print_mismatch(
        "orig_word", word, word, gloss.orig_word
    )
    assert gloss.core == ["parol"], _print_mismatch("core", word, ["parol"], gloss.core)
    assert gloss.prefixes == [], _print_mismatch("prefixes", word, [], gloss.prefixes)
    assert gloss.suffixes == suffixes, _print_mismatch(
        "suffixes", word, suffixes, gloss.suffixes
    )
    assert gloss.preferred_ending == ending, _print_mismatch(
        "preferred_ending", word, ending, gloss.preferred_ending
    )
    assert gloss.preferred_definition == definition, _print_mismatch(
        "preferred_definition", word, definition, gloss.preferred_definition
    )
    assert gloss.core_definition == core_definition, _print_mismatch(
        "core_definition", word, core_definition, gloss.core_definition
    )


@pytest.mark.parametrize(
    ["word", "prefixes", "core", "suffixes", "ending", "definition", "core_definition"],
    [
        ("ĉiel", [], ["ĉiel"], [], "", "every-manner", "every-manner"),
        ("ĉielo", [], ["ĉiel"], [], "o", "heaven", "heaven"),
        ("mi", [], ["mi"], [], "", "I", "I"),
        ("mia", [], ["mi"], [], "a", "mine", "I"),
        ("venonta", [], ["ven"], ["ont"], "i", "coming", "to-come"),
        ("ĉioma", [], ["ĉiom"], [], "a", "???", "all"),
        ("lernejo", [], ["lern"], ["ej"], "o", "school", "to-learn"),
        ("studjaro", [], ["stud", "jar"], [], "o", "academic-year", "academic-year"),
        ("neebla", ["ne"], ["ebl"], [], "i", "", "to-be-possible"),
        ("iomete", [], ["iom"], ["et"], "e", "a-little", "some"),
        ("bruligis", [], ["brul"], ["ig"], "i", "to-burn", "to-burn"),
        ("bonhumore", [], ["bon", "humor"], [], "e", "cheerfully", "cheerfully"),
        ("malbonhumore", ["mal"], ["bon", "humor"], [], "e", "", "cheerfully"),
        ("supozeble", [], ["supoz"], ["ebl"], "i", "presumably", "to-suppose"),
        ("malantaŭ", ["mal"], ["antaŭ"], [], "", "", "before"),
    ],
)
def test_get_gloss_fakeouts(
    word: str,
    prefixes: list[str],
    core: list[str],
    suffixes: list[str],
    ending: str,
    definition: str,
    core_definition: str,
) -> None:
    gloss = THE_DICTIONARY.get_gloss(word)
    assert gloss.orig_word == word, _print_mismatch(
        "orig_word", word, word, gloss.orig_word
    )
    assert gloss.prefixes == prefixes, _print_mismatch(
        "prefixes", word, prefixes, gloss.prefixes
    )
    assert gloss.core == core, _print_mismatch("core", word, core, gloss.core)
    assert gloss.prefixes == prefixes, _print_mismatch(
        "prefixes", word, prefixes, gloss.prefixes
    )
    assert gloss.suffixes == suffixes, _print_mismatch(
        "suffixes", word, suffixes, gloss.suffixes
    )
    assert gloss.preferred_ending == ending, _print_mismatch(
        "preferred_ending", word, ending, gloss.preferred_ending
    )
    assert gloss.preferred_definition == definition, _print_mismatch(
        "preferred_definition", word, definition, gloss.preferred_definition
    )
    assert gloss.core_definition == core_definition, _print_mismatch


@pytest.mark.parametrize(
    ["word", "part0orig", "part1orig"],
    [
        ("alkohol-brulilo", "alkoholo", "brulilo"),
        ("artileri-pafado", "artilerio", "pafado"),
        ("artilerio-pafado", "artilerio", "pafado"),
        ("revolver-pafoj", "revolvero", "pafo"),
        ("revolvero-pafoj", "revolvero", "pafo"),
        ("pli-malpli", "pli", "malpli"),
        ("nigra-blanka", "nigra", "blanka"),
        ("antaŭ-brako", "antaŭ", "brako"),
        ("neniam-mortantaj", "neniam", "mortanta"),
    ]
)
def test_get_hyphenated_gloss(word: str, part0orig: str, part1orig: str) -> None:
    gloss = THE_DICTIONARY.get_gloss(word)
    assert gloss.orig_word == word, _print_mismatch(
        "orig_word", word, word, gloss.orig_word
    )
    assert (
        len(gloss.parts) == 2
    ), f"{_print_mismatch('parts', word, 2, len(gloss.parts))}: {gloss.parts}"
    part0 = gloss.parts[0]
    part1 = gloss.parts[1]

    assert part0.orig_word == part0orig, _print_mismatch(
        "part0 orig_word", word, part0orig, part0.orig_word
    )
    assert part1.orig_word == part1orig, _print_mismatch(
        "part1 orig_word", word, part1orig, part1.orig_word
    )
    # assert part1.core == "brul", _print_mismatch("core", word, "brul", part1.core)
    # assert part1.suffixes == ["il"], _print_mismatch(
    #     "suffixes", word, ["il"], part1.suffixes
    # )
