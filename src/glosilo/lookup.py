"""Command-line tool for looking up Esperanto words with definitions.

Combines glosilo.stem with retavortaro sense definitions to provide
comprehensive word analysis including definitions.

Usage:
    python -m glosilo.lookup <word> [<word> ...]
    python -m glosilo.lookup "sentence with multiple words"
"""

from dataclasses import dataclass
from importlib.resources import files
import io
import json
import string
import sys
from typing import Any
import zipfile

from glosilo import eostem
from glosilo.structs import CoredWord

JSONDATA_ZIP_FILE = "jsondata.zip"


@dataclass
class Definition:
    """Definition data for a single word or core morpheme.

    Attributes:
        core_word: The core morpheme (e.g., 'parol')
        lookup_word: The word form found in dictionary (e.g., 'paroli')
        senses: Dictionary mapping sense numbers to definition text
                Example: {'1': 'to speak', '2': 'to talk'}
    """

    core_word: str
    lookup_word: str
    senses: dict[str, str]


@dataclass
class LookupResult:
    """Result of looking up word definitions.

    Corresponds to the output of lookup_word_definitions().

    Attributes:
        found: Whether definitions were found
        lookup_method: Method used to find definitions ('exact', 'with_ending', 'suffix_stripped', 'core', or None)
        lookup_word: The word form that was found in the dictionary (or compound core representation)
        article_id: The ReVo article identifier (e.g., 'parol', 'kompren')
        definitions: List of definitions (one per core morpheme for compound words)
    """

    found: bool
    lookup_method: str | None
    lookup_word: str | None
    article_id: str | None
    definitions: list[Definition]


@dataclass
class Result:
    """Complete word analysis result with definitions.

    Corresponds to the output of lookup_words() for each word.

    Attributes:
        word: The original word being analyzed
        prefixes: List of identified prefixes
        core: List of core morphemes (multiple for compound words)
        suffixes: List of identified suffixes
        ending: The grammatical ending
        lookup: The lookup result containing definitions
    """

    word: str
    prefixes: list[str]
    core: list[str]
    suffixes: list[str]
    ending: str
    lookup: LookupResult


@dataclass
class Results:
    """Collection of word analysis results.

    Wrapper for multiple Result objects from analyzing multiple words.

    Attributes:
        results: List of Result objects, one per analyzed word
    """

    results: list[Result]


def load_senses(article_id: str) -> dict[str, dict[str, str]]:
    """Load sense definitions from JSON file in jsondata.zip.

    Args:
        article_id: The article identifier (e.g., "parol", "kompren")

    Returns:
        Dictionary mapping kap text to sense dictionaries
    """
    json_filename = f"jsondata/{article_id}.json"
    zip_path = files("glosilo.data").joinpath(JSONDATA_ZIP_FILE)
    with zip_path.open("rb") as f:
        with zipfile.ZipFile(f) as zip_file:
            # Check if the JSON file exists in the zip
            if json_filename not in zip_file.namelist():
                print(f"Did not find {json_filename}")
                return {}

            # Read and parse the JSON file
            with zip_file.open(json_filename) as json_file:
                return json.load(json_file)


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
        senses = load_senses(article_id)
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
        senses = load_senses(article_id)
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
                senses = load_senses(article_id)
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
                senses = load_senses(article_id)
                if core_with_ending in senses:
                    # Structure: core -> {lookup_word -> {sense_num -> definition}}
                    core_definitions[core_part] = {
                        core_with_ending: senses[core_with_ending]
                    }
                    continue

            # If not found with preferred ending, try other endings
            core_lookup, core_article_id = try_lookup_with_endings(core_part, kap_dict)
            if core_lookup and core_article_id:
                senses = load_senses(core_article_id)
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


def lookup_words(words: str) -> list[dict[str, Any]]:
    _words: list[str] = []

    # Split the argument into words and strip punctuation
    # This allows quoted strings like "unu du tri, kvar?"
    for token in words.split():
        # Remove punctuation from the token
        word = token.strip(string.punctuation)
        if word:  # Only add non-empty words
            _words.append(word)

    if not _words:
        return []

    # Initialize stemmer
    stemmer = eostem.Stemmer()

    # Load dictionaries
    kap_dict = stemmer.get_kap_dictionary()
    rad_dict = stemmer.get_rad_dictionary()

    # Look up each word
    results: list[dict[str, Any]] = []
    for word in _words:
        word_result = lookup_word_to_dict(stemmer, word, kap_dict, rad_dict)
        results.append(word_result)

    return results


def convert_to_results(lookup_data: list[dict[str, Any]]) -> Results:
    """Convert lookup_words output to a Results dataclass.

    Args:
        lookup_data: Output from lookup_words() function

    Returns:
        Results dataclass instance containing list of Result objects
    """
    result_list: list[Result] = []

    for item in lookup_data:
        # Extract lookup data
        lookup_dict = item["lookup"]

        # Convert definitions from nested dict to list of Definition objects
        definitions: list[Definition] = []
        defs_dict = lookup_dict["definitions"]

        # Iterate through the nested structure: core -> lookup_word -> senses
        for core_word, lookup_words_dict in defs_dict.items():
            for lookup_word, senses in lookup_words_dict.items():
                definitions.append(
                    Definition(
                        core_word=core_word, lookup_word=lookup_word, senses=senses
                    )
                )

        # Create LookupResult
        lookup_result = LookupResult(
            found=lookup_dict["found"],
            lookup_method=lookup_dict["lookup_method"],
            lookup_word=lookup_dict["lookup_word"],
            article_id=lookup_dict["article_id"],
            definitions=definitions,
        )

        # Create Result
        result = Result(
            word=item["word"],
            prefixes=item["prefixes"],
            core=item["core"],
            suffixes=item["suffixes"],
            ending=item["ending"],
            lookup=lookup_result,
        )

        result_list.append(result)

    return Results(results=result_list)


def main() -> None:
    """Main entry point for the lookup command."""
    # Ensure UTF-8 encoding for output on Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    if len(sys.argv) != 2:
        print(
            "Usage: python -m glosilo.lookup <words>",
            file=sys.stderr,
        )
        print("\nExamples:", file=sys.stderr)
        print("  python -m glosilo.lookup parolanto", file=sys.stderr)
        print('  python -m glosilo.lookup "unu du bonfaras, kie?"', file=sys.stderr)
        sys.exit(1)

    print(json.dumps(lookup_words(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
