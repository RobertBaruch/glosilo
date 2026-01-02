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
KAP_DICTIONARY_PATH = Path("F:/retavortaropy/kap_dictionary.json")
_rad_dictionary_cache: dict[str, str] | None = None
_kap_dictionary_cache: dict[str, str] | None = None


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


def _get_kap_dictionary() -> dict[str, str]:
    """Get the kap dictionary, loading it once and caching it."""
    global _kap_dictionary_cache
    if _kap_dictionary_cache is None:
        if KAP_DICTIONARY_PATH.exists():
            try:
                with open(KAP_DICTIONARY_PATH, "r", encoding="utf-8") as f:
                    _kap_dictionary_cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If loading fails, use empty dict
                _kap_dictionary_cache = {}
        else:
            _kap_dictionary_cache = {}
    # _kap_dictionary_cache is guaranteed to be dict[str, str] here, not None
    assert _kap_dictionary_cache is not None
    return _kap_dictionary_cache


def lookup_kap(word_without_ending: str) -> bool:
    """Check if word (without ending) exists in kap_dictionary with any ending.

    Args:
        word_without_ending: The word core/root without its grammatical ending

    Returns:
        True if word+ending exists in kap_dict for any ending in ["a", "e", "i", "o"]
    """
    kap_dict = _get_kap_dictionary()
    return any(word_without_ending + ending in kap_dict
               for ending in ["a", "e", "i", "o"])


def core_to_str(core: str | list[str]) -> str:
    """Convert core to string for dictionary lookup (joins with no separator).

    Args:
        core: Either a string (legacy) or list of strings (compound)

    Returns:
        String with parts joined by empty string (for dictionary lookup)
    """
    if isinstance(core, list):
        return "".join(core)
    return core


def core_display(core: str | list[str]) -> str:
    """Convert core to display representation with | separator.

    Args:
        core: Either a string or list of strings

    Returns:
        String with parts joined by | for compound words
    """
    if isinstance(core, list):
        return "|".join(core)
    return core


def make_core(parts: str | list[str]) -> list[str]:
    """Normalize core to list[str] format.

    Args:
        parts: Either a single string or list of strings

    Returns:
        List of core parts (single element for non-compounds)
    """
    if isinstance(parts, list):
        return parts
    return [parts]


def _try_split_compound(word: str, rad_dict: dict[str, str]) -> list[str] | None:
    """Try to split a word into compound parts.

    Algorithm:
    1. Try all possible split points
    2. For each split, check if both parts exist in rad_dictionary
    3. Handle optional linking vowels (a, e, i, o) between parts
    4. Support recursive splitting for 3+ part compounds
    5. Prefer longest valid roots

    Args:
        word: The word to attempt to split
        rad_dict: Root dictionary for validation

    Returns:
        List of core parts if valid compound found, None otherwise

    Examples:
        bluokul -> ['blu', 'okul'] (no linking vowel, okul starts with o)
        vaporŝip -> ['vapor', 'ŝip'] (no linking vowel)
        multehom -> ['mult', 'e', 'hom'] (linking e)
        dikfingr -> ['dik', 'fingr'] (no linking vowel)
    """
    # Don't split words shorter than 4 characters
    if len(word) < 4:
        return None

    # Get all affixes to exclude them from compound parts
    # A compound must consist of ROOTS, not affixes
    all_affixes = set(consts.PREFIXES) | set(consts.SUFFIXES) | set(consts.PREPOSITIONS)

    best_split = None
    best_score = 0  # Score based on root lengths

    # Try all split points from position 2 to len-2
    for i in range(2, len(word) - 1):
        left_part = word[:i]
        right_part = word[i:]

        # Try without linking vowel
        # Both parts must be in rad_dict AND not be affixes
        if (left_part in rad_dict and right_part in rad_dict and
            left_part not in all_affixes and right_part not in all_affixes):
            score = len(left_part) + len(right_part)
            if score > best_score:
                best_score = score
                best_split = [left_part, right_part]

        # Try with linking vowel (check if left ends with a/e/i/o)
        if left_part and left_part[-1] in 'aeio':
            left_root = left_part[:-1]
            linking_vowel = left_part[-1]
            # Both parts must be in rad_dict AND not be affixes
            if (left_root in rad_dict and right_part in rad_dict and
                left_root not in all_affixes and right_part not in all_affixes):
                score = len(left_root) + len(right_part)
                if score > best_score:
                    best_score = score
                    best_split = [left_root, linking_vowel, right_part]

    # If we found a 2-part split, try recursive splitting on the right part
    # Only use the recursive split if it provides more total root length
    if best_split and len(best_split) == 2:
        right_part_original_len = len(best_split[1])
        right_subsplit = _try_split_compound(best_split[1], rad_dict)
        if right_subsplit:
            # Only use recursive split if total root length is greater
            right_subsplit_len = sum(len(p) for p in right_subsplit if len(p) > 1)
            if right_subsplit_len > right_part_original_len:
                best_split = [best_split[0]] + right_subsplit
    elif best_split and len(best_split) == 3:
        # Has linking vowel - try recursive split on right part
        right_part_original_len = len(best_split[2])
        right_subsplit = _try_split_compound(best_split[2], rad_dict)
        if right_subsplit:
            # Only use recursive split if total root length is greater
            right_subsplit_len = sum(len(p) for p in right_subsplit if len(p) > 1)
            if right_subsplit_len > right_part_original_len:
                best_split = [best_split[0], best_split[1]] + right_subsplit

    return best_split


def _strip_affixes2(word_without_ending: str) -> tuple[list[str], list[str], list[str]]:
    """Alternative algorithm for stripping affixes using iterative reconstruction.

    This algorithm:
    0.5. Try compound word splitting on the original word FIRST
    1. Strips one preposition from the beginning (if possible)
    2. Strips all prefixes from the remainder
    3. Strips all suffixes from what's left
    3.5. Try compound word splitting on the remainder
    4. Iterates through all combinations of "unstripping" prefixes and suffixes
    5. For each combination, reconstructs the root and checks if it exists in rad_dict
    6. Returns the configuration with the longest validated root

    Args:
        word_without_ending: The word with its ending already removed

    Returns:
        Tuple of (core, prefixes, suffixes) where:
        - core is a list[str] (single element for simple words, multiple for compounds)
        - prefixes may include a preposition
    """
    rad_dict = _get_rad_dictionary()

    # Step 1: Try to strip one preposition from the beginning
    preposition: str | None = None
    remainder = word_without_ending

    for prep in sorted(consts.PREPOSITIONS, key=len, reverse=True):
        if word_without_ending.startswith(prep):
            preposition = prep
            remainder = word_without_ending[len(prep):]
            break

    # Step 2: Strip all prefixes from the remainder
    temp_prefixes: list[str] = []
    while True:
        found_prefix = False
        for prefix in consts.PREFIXES:
            if remainder.startswith(prefix):
                temp_prefixes.append(prefix)
                remainder = remainder[len(prefix):]
                found_prefix = True
                break
        if not found_prefix:
            break

    # Step 3: Strip all suffixes from what's left
    temp_suffixes: list[str] = []
    while True:
        found_suffix = False
        for suffix in consts.SUFFIXES:
            if remainder.endswith(suffix):
                temp_suffixes.insert(0, suffix)
                remainder = remainder[:-len(suffix)]
                found_suffix = True
                break
        if not found_suffix:
            break

    # Now remainder is the core after maximum stripping
    # temp_prefixes contains all stripped prefixes
    # temp_suffixes contains all stripped suffixes

    # Step 4 & 5: Iterate through all combinations, reconstruct roots, and validate
    # We'll also consider compound splits as one of the possibilities
    deconstructions: list[tuple[list[str], list[str], list[str], int, int]] = []

    # Try all combinations of how many prefixes/suffixes to "unstri" (add back to core)
    for num_prefixes_to_keep_in_core in range(len(temp_prefixes) + 1):
        for num_suffixes_to_keep_in_core in range(len(temp_suffixes) + 1):
            # Reconstruct the root
            # Prefixes that go back into core: last num_prefixes_to_keep_in_core
            # Suffixes that go back into core: first num_suffixes_to_keep_in_core
            reconstructed_root_parts: list[str] = []

            if num_prefixes_to_keep_in_core > 0:
                reconstructed_root_parts.extend(temp_prefixes[-num_prefixes_to_keep_in_core:])

            reconstructed_root_parts.append(remainder)

            if num_suffixes_to_keep_in_core > 0:
                reconstructed_root_parts.extend(temp_suffixes[:num_suffixes_to_keep_in_core])

            reconstructed_root = "".join(reconstructed_root_parts)

            # Check if this root is valid
            if reconstructed_root in rad_dict:
                # This is a valid configuration
                # Prefixes that were stripped: first (len - num_to_keep) prefixes
                stripped_prefixes = temp_prefixes[:len(temp_prefixes) - num_prefixes_to_keep_in_core]
                # Suffixes that were stripped: last (len - num_to_keep) suffixes
                stripped_suffixes = temp_suffixes[num_suffixes_to_keep_in_core:]

                # Add preposition to front of prefixes if it exists
                if preposition:
                    stripped_prefixes = [preposition] + stripped_prefixes

                # Special case for "ne": prefer it as a root only if there are no suffixes,
                # or the only suffix is "ig" or "ul"
                # This makes "neig" and "neul" have "ne" as core, but "neebl" and "neind"
                # have "ebl" and "ind" as core
                score_penalty = 0
                if reconstructed_root == "ne" and stripped_suffixes:
                    # If "ne" is the core and there are suffixes, check if they're ig/ul only
                    if len(stripped_suffixes) == 1 and stripped_suffixes[0] in ["ig", "ul"]:
                        # Boost this configuration (negative penalty = higher priority)
                        score_penalty = -1000
                    else:
                        # Penalize this configuration to prefer other decompositions
                        score_penalty = 1000

                # Also penalize "ig" or "ul" as cores when "ne" is a prefix
                if reconstructed_root in ["ig", "ul"] and "ne" in stripped_prefixes:
                    score_penalty = 1000

                deconstructions.append((
                    stripped_prefixes,
                    make_core(reconstructed_root),  # Convert to list[str] format
                    stripped_suffixes,
                    len(reconstructed_root),
                    score_penalty
                ))

    # Step 5.5: Also try compound word splitting on various reconstructed forms
    # Try compound on the remainder (after max stripping)
    compound_parts = _try_split_compound(remainder, rad_dict)
    if compound_parts:
        all_prefixes = ([preposition] if preposition else []) + temp_prefixes
        # Calculate score for compound: sum of root lengths (excluding linking vowels)
        compound_score = sum(len(p) for p in compound_parts if len(p) > 1)
        # Small penalty for compounds to prefer simpler affixed forms when scores are close
        # (prefer "parol+ant" over "par+o+lant" when both are valid)
        compound_penalty = 10
        deconstructions.append((
            all_prefixes,
            compound_parts,
            temp_suffixes,
            compound_score,
            compound_penalty
        ))

    # Also try compound on the original word (before any stripping)
    compound_parts_original = _try_split_compound(word_without_ending, rad_dict)
    if compound_parts_original:
        compound_score_original = sum(len(p) for p in compound_parts_original if len(p) > 1)
        # Smaller penalty for compounds without affixes (these are more likely to be true compounds)
        compound_penalty_original = 5
        deconstructions.append((
            [],
            compound_parts_original,
            [],
            compound_score_original,
            compound_penalty_original
        ))

    # Step 6: Choose the element with the longest reconstructed root
    if deconstructions:
        # Sort by penalty (ascending), then root length (descending), then affixes stripped (descending)
        deconstructions.sort(key=lambda x: (-x[4], x[3], len(x[0]) + len(x[2])), reverse=True)
        best = deconstructions[0]
        return best[1], best[0], best[2]  # core (already list[str]), prefixes, suffixes

    # Fallback: return with maximum stripping
    all_prefixes = ([preposition] if preposition else []) + temp_prefixes
    return make_core(remainder), all_prefixes, temp_suffixes


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

    # Check if word is a core-immune word or vortetoj that shouldn't be split
    if word.startswith(tuple(consts.CORE_IMMUNE_CORES | consts.VORTETOJ)):
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

def _strip_affixes(word_without_ending: str) -> tuple[str, list[str], list[str]]:
    """Strips all prefixes and suffixes from a word without an ending."""
    prefixes: list[str] = []
    suffixes: list[str] = []
    preposition_prefixes: list[str] = []

    # Load rad_dictionary for validation
    rad_dict = _get_rad_dictionary()

    # Find longest root match in rad_dictionary or CORE_IMMUNE_CORES by trying
    # combinations of prefix/suffix stripping. E.g. for "ekvilibrigit", we find
    # "ekvilibr" (no prefixes, suffixes=["ig","it"]) is longest match.
    # CORE_IMMUNE_CORES handles compound words like "studjar" that aren't in rad_dict.
    #
    # Scoring: prefer cores that are NOT prefixes. If core is a prefix,
    # score is reduced. This ensures "neigi" → "ne+ig+i" not "ne+igi".
    best_score = -1
    best_config = None  # (prefixes, core, suffixes)

    # Try all combinations of prefix stripping
    for num_prefixes in range(10):  # Reasonable upper limit
        temp_word = word_without_ending
        temp_prefixes = []

        # Strip num_prefixes prefixes
        for _ in range(num_prefixes):
            found = False
            for prefix in consts.PREFIXES:
                if temp_word.startswith(prefix):
                    temp_prefixes.append(prefix)
                    temp_word = temp_word[len(prefix):]
                    found = True
                    break
            if not found:
                break

        # Try all combinations of suffix stripping
        for num_suffixes in range(10):  # Reasonable upper limit
            test_word = temp_word
            test_suffixes = []

            # Strip num_suffixes suffixes
            for _ in range(num_suffixes):
                found = False
                for suffix in consts.SUFFIXES:
                    if test_word.endswith(suffix):
                        test_suffixes.insert(0, suffix)
                        test_word = test_word[:-len(suffix)]
                        found = True
                        break
                if not found:
                    break

            # Check if test_word is valid root in rad_dict or CORE_IMMUNE_CORES
            if test_word and (test_word in rad_dict or test_word in consts.CORE_IMMUNE_CORES):
                # Score: length of root, but penalize if core is a known prefix
                # This makes "ne+ig" preferred over "ne+igi" for "neigi"
                score = len(test_word) * 10
                if test_word in consts.PREFIXES:
                    score -= 100  # Heavy penalty for prefix as core

                if score > best_score:
                    best_score = score
                    best_config = (
                        temp_prefixes[:],
                        test_word,
                        test_suffixes[:]
                    )

    # Use best config if found, otherwise use normal stripping
    if best_config:
        prefixes, word_without_ending, suffixes = best_config
    else:
        # Fall back: strip all standard prefixes then suffixes normally
        while any((word_without_ending.startswith(prefix) for prefix in consts.PREFIXES)):
            for prefix in consts.PREFIXES:
                if word_without_ending.startswith(prefix):
                    prefixes.append(prefix)
                    word_without_ending = word_without_ending[len(prefix):]
                    break

        # Try stripping prepositions (only if no best_config)
        for prep in sorted(consts.PREPOSITIONS, key=len, reverse=True):
            if word_without_ending.startswith(prep):
                remainder = word_without_ending[len(prep):]
                # Check if remainder is valid
                if remainder in consts.CORE_IMMUNE_CORES or remainder in rad_dict:
                    preposition_prefixes.append(prep)
                    word_without_ending = remainder
                    break
                # Check after stripping suffixes
                test_rem = remainder
                for suffix in consts.SUFFIXES:
                    if test_rem.endswith(suffix):
                        pot_root = test_rem[:-len(suffix)]
                        if pot_root and (pot_root in consts.CORE_IMMUNE_CORES or
                                       pot_root in rad_dict):
                            preposition_prefixes.append(prep)
                            word_without_ending = remainder
                            break
                if preposition_prefixes:
                    break

        # Strip suffixes
        while any((word_without_ending.endswith(suffix) for suffix in consts.SUFFIXES)):
            for suffix in consts.SUFFIXES:
                if word_without_ending.endswith(suffix):
                    suffixes.insert(0, suffix)
                    word_without_ending = word_without_ending[:-len(suffix)]
                    break

    # Combine all prefixes (standard prefixes first, then prepositions)
    all_prefixes = prefixes + preposition_prefixes

    # Check all combinations of prefixes and suffixes for core-immune words or vortetoj.
    # If we hit a core-immune word, then use only those prefixes and suffixes.
    for num_suffixes in range(len(suffixes), -1, -1):
        for num_prefixes in range(len(all_prefixes), -1, -1):
            core = word_without_ending
            if num_prefixes:
                core = "".join(all_prefixes[-num_prefixes:]) + core
            if num_suffixes:
                core = core + "".join(suffixes[:num_suffixes])
            if core in consts.CORE_IMMUNE_CORES or core in consts.VORTETOJ:
                if num_prefixes:
                    all_prefixes = all_prefixes[:-num_prefixes]
                suffixes = suffixes[num_suffixes:]
                return core, all_prefixes, suffixes

    return word_without_ending, all_prefixes, suffixes

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

    core, prefixes, suffixes = _strip_affixes2(word)

    if orig_word == DEBUGWORD:
        print(f"  Stripped: {prefixes}+{core_display(core)}+{suffixes}+{orig_ending}")
    # If the last suffix is one that converts a verb to another type of word, then
    # change the ending to "i".
    if suffixes and suffixes[-1] in consts.VERB_SUFFIXES:
        if orig_word == DEBUGWORD:
            print(f"  Verb suffix: {suffixes[-1]}; orig_ending changed to 'i'")
        orig_ending = "i"
    # Also change ending to "i" if the core itself is a verb suffix
    # (e.g., "neebla" → "ne+ebl+i" where "ebl" is the core)
    if len(core) == 1 and core[0] in consts.VERB_SUFFIXES:
        if orig_word == DEBUGWORD:
            print(f"  Core is verb suffix: {core[0]}; orig_ending changed to 'i'")
        orig_ending = "i"

    # If there's no core, try to get one from the prefixes or suffixes.
    if not core or (len(core) == 1 and not core[0]):
        if suffixes:
            core = [suffixes.pop(0)]
            if orig_word == DEBUGWORD:
                print(f"  No core, trying to use suffix {core[0]}")
        elif prefixes:
            core = [prefixes.pop()]
            if orig_word == DEBUGWORD:
                print(f"  No core, trying to use prefix {core[0]}")

    analysis = structs.CoredWord(
        orig_word, prefixes, core, suffixes, orig_ending, [], "", ""
    )
    if debug:
        print(f"  Cored: {analysis}")

    return analysis
