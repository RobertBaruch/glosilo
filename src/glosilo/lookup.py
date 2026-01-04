"""Command-line tool for looking up Esperanto words with definitions.

Combines glosilo.stem with retavortaro sense definitions to provide
comprehensive word analysis including definitions.

Usage:
    python -m glosilo.lookup <word> [<word> ...]
    python -m glosilo.lookup "sentence with multiple words"
"""

import sys
import io
import json
import pathlib
import string
from typing import Any

import gensenses
from glosilo import eostem
from glosilo.structs import CoredWord

KAP_DICTIONARY_FILE = "kap_dictionary.json"
DEFAULT_REVO_FONTO_DIR = "F:/revo-fonto/revo/"


def load_kap_dictionary() -> dict[str, str]:
    """Load the kap_dictionary.json from retavortaropy.

    Returns:
        Dictionary mapping kap text to article identifiers
    """
    kap_dict_path = pathlib.Path(KAP_DICTIONARY_FILE)
    if not kap_dict_path.exists():
        return {}

    with open(kap_dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_senses_from_xml(article_id: str) -> dict[str, dict[str, str]]:
    """Load sense definitions by calling gensenses.py via subprocess.

    Args:
        article_id: The article identifier (e.g., "parol", "kompren")

    Returns:
        Dictionary mapping kap text to sense dictionaries
    """
    xml_path = pathlib.Path(DEFAULT_REVO_FONTO_DIR).joinpath(f"{article_id}.xml")
    if not xml_path.exists():
        return {}

    try:
        return gensenses.json_lookup(xml_path)
    except Exception:
        # Return empty dict on error
        return {}


def try_lookup_with_endings(
    base_word: str, kap_dict: dict[str, str]
) -> tuple[str | None, str | None]:
    """Try to find a word in kap_dict by trying different endings.

    Args:
        base_word: The base word to look up
        kap_dict: The kap dictionary

    Returns:
        Tuple of (lookup_word, article_id) if found, (None, None) otherwise
    """
    # List of common Esperanto endings to try
    endings = ["", "i", "o", "a", "e", "as", "is", "os", "us", "u", "n", "j", "jn"]

    # First try exact match
    if base_word in kap_dict:
        return base_word, kap_dict[base_word]

    # Try with different endings
    for ending in endings:
        lookup = base_word + ending
        if lookup in kap_dict:
            return lookup, kap_dict[lookup]

    return None, None


def lookup_word_definitions(
    word: str, cored: CoredWord, kap_dict: dict[str, str], rad_dict: dict[str, str]
) -> dict[str, Any]:
    """Look up definitions for a word using multiple strategies.

    Strategy:
    1. Try exact word match in kap_dict
    2. Try word with different endings
    3. Try looking up each core separately

    Args:
        word: The original word
        cored: The stemmed word analysis
        kap_dict: The kap dictionary
        rad_dict: The rad dictionary

    Returns:
        Dictionary with lookup results and definitions
    """
    result: dict[str, Any] = {
        "found": False,
        "lookup_method": None,
        "lookup_word": None,
        "article_id": None,
        "definitions": {},
    }

    article_id: str | None = None

    # Strategy 1: Try exact word match
    if word in kap_dict:
        article_id = kap_dict[word]
        senses = load_senses_from_xml(article_id)
        if word in senses:
            result["found"] = True
            result["lookup_method"] = "exact"
            result["lookup_word"] = word
            result["article_id"] = article_id
            # Use consistent structure: core -> {lookup_word -> definitions}
            # For non-compound words, core is single element
            core_word = cored.core[0] if len(cored.core) == 1 else word
            result["definitions"] = {core_word: {word: senses[word]}}
            return result

    # Strategy 2: Try reconstructed word with different endings
    # Reconstruct: prefixes + core + suffixes (without ending)
    base_word = "".join(cored.prefixes) + "".join(cored.core) + "".join(cored.suffixes)
    lookup_word, article_id = try_lookup_with_endings(base_word, kap_dict)
    if lookup_word and article_id:
        senses = load_senses_from_xml(article_id)
        if lookup_word in senses:
            result["found"] = True
            result["lookup_method"] = "with_ending"
            result["lookup_word"] = lookup_word
            result["article_id"] = article_id
            # Use consistent structure: core -> {lookup_word -> definitions}
            core_word = "|".join(cored.core)
            result["definitions"] = {core_word: {lookup_word: senses[lookup_word]}}
            return result

    # Strategy 2.5: Try progressively stripping suffixes
    # For words like "ĉirkaŭparolado" (ĉirkaŭ+parol+ad+o), try:
    # - ĉirkaŭparolad + endings (fails)
    # - ĉirkaŭparol + endings (should find "ĉirkaŭparoli")
    if cored.suffixes:
        # Try removing suffixes one at a time from the end
        for i in range(len(cored.suffixes) - 1, -1, -1):
            # Reconstruct with fewer suffixes
            partial_suffixes = cored.suffixes[:i]
            partial_base = (
                "".join(cored.prefixes)
                + "".join(cored.core)
                + "".join(partial_suffixes)
            )

            lookup_word, article_id = try_lookup_with_endings(partial_base, kap_dict)
            if lookup_word and article_id:
                senses = load_senses_from_xml(article_id)
                if lookup_word in senses:
                    result["found"] = True
                    result["lookup_method"] = "suffix_stripped"
                    result["lookup_word"] = lookup_word
                    result["article_id"] = article_id
                    # Use consistent structure: core -> {lookup_word -> definitions}
                    core_word = "|".join(cored.core)
                    result["definitions"] = {
                        core_word: {lookup_word: senses[lookup_word]}
                    }
                    return result

    # Strategy 3: Try looking up cores
    # For compound words, we have multiple cores
    core_definitions: dict[str, dict[str, dict[str, str]]] = {}

    for core_part in cored.core:
        # Skip single-letter linking vowels
        if len(core_part) == 1 and core_part in "aeio":
            continue

        # Check if core is in rad_dict
        if core_part in rad_dict:
            # First, try with the preferred ending from the original word
            core_with_ending = core_part + cored.preferred_ending
            if core_with_ending in kap_dict:
                article_id = kap_dict[core_with_ending]
                senses = load_senses_from_xml(article_id)
                if core_with_ending in senses:
                    # Structure: core -> {lookup_word -> {sense_num -> definition}}
                    core_definitions[core_part] = {
                        core_with_ending: senses[core_with_ending]
                    }
                    continue

            # If not found with preferred ending, try other endings
            core_lookup, core_article_id = try_lookup_with_endings(core_part, kap_dict)
            if core_lookup and core_article_id:
                senses = load_senses_from_xml(core_article_id)
                if core_lookup in senses:
                    # Structure: core -> {lookup_word -> {sense_num -> definition}}
                    core_definitions[core_part] = {core_lookup: senses[core_lookup]}

    if core_definitions:
        result["found"] = True
        result["lookup_method"] = "core"
        result["lookup_word"] = "|".join(cored.core)
        result["definitions"] = core_definitions
        return result

    return result


def lookup_word_to_dict(
    stemmer: eostem.Stemmer,
    word: str,
    kap_dict: dict[str, str],
    rad_dict: dict[str, str],
) -> dict[str, Any]:
    """Look up a word and return complete analysis with definitions.

    Args:
        stemmer: The Stemmer instance
        word: The word to look up
        kap_dict: The kap dictionary
        rad_dict: The rad dictionary

    Returns:
        Dictionary with complete word analysis and definitions
    """
    # Stem the word
    cored = stemmer.core_word(word, debug=False)

    # Get stem analysis
    result: dict[str, Any] = {
        "word": cored.orig_word,
        "prefixes": cored.prefixes,
        "core": cored.core,
        "suffixes": cored.suffixes,
        "ending": cored.preferred_ending,
    }

    # Look up definitions
    lookup_result = lookup_word_definitions(word, cored, kap_dict, rad_dict)
    result["lookup"] = lookup_result

    return result


def main() -> None:
    """Main entry point for the lookup command."""
    # Ensure UTF-8 encoding for output on Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    if len(sys.argv) < 2:
        print(
            "Usage: python -m glosilo.lookup <word> [<word> ...]",
            file=sys.stderr,
        )
        print("\nExamples:", file=sys.stderr)
        print("  python -m glosilo.lookup parolanto", file=sys.stderr)
        print('  python -m glosilo.lookup "unu du bonfaras, kie?"', file=sys.stderr)
        sys.exit(1)

    words: list[str] = []

    # Parse arguments
    for arg in sys.argv[1:]:
        # Split the argument into words and strip punctuation
        # This allows quoted strings like "unu du tri, kvar?"
        for token in arg.split():
            # Remove punctuation from the token
            word = token.strip(string.punctuation)
            if word:  # Only add non-empty words
                words.append(word)

    if not words:
        print("Error: No word provided", file=sys.stderr)
        sys.exit(1)

    # Initialize stemmer
    stemmer = eostem.Stemmer()

    # Load dictionaries
    kap_dict = load_kap_dictionary()
    rad_dict = stemmer.get_rad_dictionary()

    # Look up each word
    results: list[dict[str, Any]] = []
    for word in words:
        word_result = lookup_word_to_dict(stemmer, word, kap_dict, rad_dict)
        results.append(word_result)

    # Output JSON
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
