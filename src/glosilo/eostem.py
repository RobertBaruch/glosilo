"""Esperanto stemming utilities.

This module contains functions for stemming Esperanto words by stripping
prefixes, suffixes, and endings to find the core/root of a word.
"""

import json
from pathlib import Path
from glosilo import consts
from glosilo import structs


DEBUGWORD = ""
RAD_DICTIONARY_PATH = Path("F:/retavortaropy/rad_dictionary.json")
_rad_dictionary_cache: dict[str, str] | None = None


def _get_rad_dictionary() -> dict[str, str]:
    """Get the rad dictionary, loading it once and caching it."""
    global _rad_dictionary_cache
    if _rad_dictionary_cache is None:
        if RAD_DICTIONARY_PATH.exists():
            try:
                with open(RAD_DICTIONARY_PATH, "r", encoding="utf-8") as f:
                    _rad_dictionary_cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If loading fails, use empty dict
                _rad_dictionary_cache = {}
        else:
            _rad_dictionary_cache = {}
    # _rad_dictionary_cache is guaranteed to be dict[str, str] here, not None
    assert _rad_dictionary_cache is not None
    return _rad_dictionary_cache


def maybe_strip_plural_acc_ending(word: str) -> str:
    """Strips obvious plural and accusative endings."""
    if word in consts.STRIP_PLURAL_ACC_IMMUNE_WORDS:
        return word
    if word.endswith("jn"):
        return word[:-2]
    if word.endswith(("n", "j")):
        return word[:-1]
    return word


def _strip_prefixes(
    word: str, curr_prefixes: list[str] | None = None
) -> tuple[str, list[str]]:
    """Strips a prefix from a word."""
    prefixes: list[str] = curr_prefixes or []

    # Probably not the best.
    if word.startswith(tuple(consts.CORE_IMMUNE_CORES)): # | consts.VORTETOJ)):
        return word, prefixes

    for prefix in consts.PREFIXES:
        if word.startswith(prefix):
            prefixes.append(prefix)
            word = word[len(prefix) :]
            return _strip_prefixes(word, prefixes)

    return word, prefixes


def _strip_suffixes(
    word: str, curr_suffixes: list[str] | None = None
) -> tuple[str, list[str]]:
    """Strips all suffixes from a word."""
    suffixes: list[str] = curr_suffixes or []

    if word in consts.CORE_IMMUNE_CORES | consts.VORTETOJ:
        return word, suffixes

    for suffix in consts.SUFFIXES:
        if word.endswith(suffix):
            suffixes.insert(0, suffix)
            word = word[: -len(suffix)]
            return _strip_suffixes(word, suffixes)

    return word, suffixes

def _strip_affixes(word: str) -> tuple[str, list[str], list[str]]:
    """Strips all prefixes and suffixes from a word."""
    prefixes: list[str] = []
    suffixes: list[str] = []
    preposition_prefixes: list[str] = []

    # First strip standard prefixes (mal, ne, ek, dis)
    while any((word.startswith(prefix) for prefix in consts.PREFIXES)):
        for prefix in consts.PREFIXES:
            if word.startswith(prefix):
                prefixes.append(prefix)
                word = word[len(prefix) :]
                break

    # Try stripping prepositions as prefixes
    # Only strip if the remainder is a valid root in rad_dictionary or CORE_IMMUNE_CORES
    # This prevents "forto" → "for+to" (incorrect, "to" is not a root)
    # but allows "alprem" → "al+prem" (correct, "prem" is a root)
    rad_dict = _get_rad_dictionary()
    for preposition in sorted(consts.PREPOSITIONS, key=len, reverse=True):
        if word.startswith(preposition):
            remainder = word[len(preposition):]
            # Only strip preposition if remainder is a valid root
            if remainder in consts.CORE_IMMUNE_CORES or remainder in rad_dict:
                preposition_prefixes.append(preposition)
                word = remainder
                break

    # Strip suffixes
    while any((word.endswith(suffix) for suffix in consts.SUFFIXES)):
        for suffix in consts.SUFFIXES:
            if word.endswith(suffix):
                suffixes.insert(0, suffix)
                word = word[: -len(suffix)]
                break

    # Combine all prefixes (standard prefixes first, then prepositions)
    all_prefixes = prefixes + preposition_prefixes

    # Check all combinations of prefixes and suffixes for core-immune words or vortetoj.
    # If we hit a core-immune word, then use only those prefixes and suffixes.
    for num_suffixes in range(len(suffixes), -1, -1):
        for num_prefixes in range(len(all_prefixes), -1, -1):
            core = word
            if num_prefixes:
                core = "".join(all_prefixes[-num_prefixes:]) + core
            if num_suffixes:
                core = core + "".join(suffixes[:num_suffixes])
            if core in consts.CORE_IMMUNE_CORES or core in consts.VORTETOJ:
                if num_prefixes:
                    all_prefixes = all_prefixes[:-num_prefixes]
                suffixes = suffixes[num_suffixes:]
                return core, all_prefixes, suffixes

    return word, all_prefixes, suffixes

def replace_verb_ending(word: str) -> str:
    """Replace the verb ending from a word."""
    if word in consts.CORE_IMMUNE_WORDS:
        return word
    if word.endswith(("as", "is", "os", "us")):
        return word[:-2] + "i"
    if word.endswith("u"):
        return word[:-1] + "i"
    return word


def _split_ending(word: str, debug: bool = False) -> tuple[str, str]:
    orig_ending = ""
    if (
        len(word) >= 2
        and word[-1] in ["a", "e", "i", "o", "u"]
        and word not in consts.VORTETOJ
    ):
        orig_ending = word[-1]
        word = word[:-1]

    if debug:
        print(f"Split ending: {word}+{orig_ending}")

    return word, orig_ending


def core_word(word: str, debug: bool = False) -> structs.CoredWord:
    """Cores a word by removing all possible prefixes and suffixes."""
    if debug:
        print(f"Coring {word}")
    orig_word = word
    word = word.lower()

    # Strip any ending.
    word = maybe_strip_plural_acc_ending(word)
    word = replace_verb_ending(word)
    word, orig_ending = _split_ending(word, debug)
    # word, prefixes = _strip_prefixes(word)
    # word, suffixes = _strip_suffixes(word)

    word, prefixes, suffixes = _strip_affixes(word)

    core = word

    if orig_word == DEBUGWORD:
        print(f"  Stripped: {prefixes}+{word}+{suffixes}+{orig_ending}")
    # If the last suffix is one that converts a verb to another type of word, then
    # change the ending to "i".
    if suffixes and suffixes[-1] in consts.VERB_SUFFIXES:
        if orig_word == DEBUGWORD:
            print(f"  Verb suffix: {suffixes[-1]}; orig_ending changed to 'i'")
        orig_ending = "i"

    # If there's no core, try to get one from the prefixes or suffixes.
    if not core and suffixes:
        core = suffixes.pop(0)
        if orig_word == DEBUGWORD:
            print(f"  No core, trying to use suffix {core}")
    if not core and prefixes:
        core = prefixes.pop()
        if orig_word == DEBUGWORD:
            print(f"  No core, trying to use prefix {core}")

    analysis = structs.CoredWord(
        orig_word, prefixes, core, suffixes, orig_ending, [], "", ""
    )
    if debug:
        print(f"  Cored: {analysis}")

    return analysis
