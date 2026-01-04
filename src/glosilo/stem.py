"""Command-line tool for stemming Esperanto words.

Usage:
    python -m glosilo.stem <word>
    python -m glosilo.stem --debug <word>
    python -m glosilo.stem --verify <word>
    python -m glosilo.stem --verify "sentence with multiple words"
    python -m glosilo.stem --json <word> [<word> ...]
"""

import sys
import io
import json
import string
from glosilo import eostem
from glosilo.structs import CoredWord


def verify_stem(
    stemmer: eostem.Stemmer,
    cored: CoredWord,
    dictionary: dict[str, str],
    rad_dictionary: dict[str, str] | None = None,
) -> tuple[bool, str]:
    """Verify that the stem exists in the dictionary.

    The stem is formed by combining the core with the ending, and optionally
    with suffixes if needed. First tries core+ending (e.g., "paroli"), then
    tries core+suffixes+ending (e.g., "subigi") if the first lookup fails.
    Also checks if the core itself exists in rad_dictionary.

    Checks both lowercase and capitalized versions of the lookup word.

    Args:
        cored: The cored word to verify
        dictionary: Dictionary mapping words to file paths
        rad_dictionary: Optional rad dictionary mapping roots to definitions

    Returns:
        Tuple of (found, lookup_word) where found is True if the word exists
        in the dictionary, and lookup_word is the word that was looked up.
    """
    # First try: core + ending (without suffixes)
    # This handles most normal words like "paroli", "kompreni"
    core_str = stemmer.core_to_str(cored.core)
    lookup_word = (
        core_str + cored.preferred_ending if cored.preferred_ending else core_str
    )
    found = lookup_word in dictionary

    if not found:
        capitalized = lookup_word.capitalize()
        found = capitalized in dictionary

    # Second try: core + suffixes + ending
    # This handles words where the core is a preposition used as a root,
    # like "subigi" (sub+ig+i) or "forigi" (for+ig+i)
    if not found and cored.suffixes:
        lookup_word_with_suffixes = stemmer.core_to_str(cored.core) + "".join(
            cored.suffixes
        )
        if cored.preferred_ending:
            lookup_word_with_suffixes += cored.preferred_ending

        found = lookup_word_with_suffixes in dictionary
        if not found:
            capitalized = lookup_word_with_suffixes.capitalize()
            found = capitalized in dictionary

        # If found with suffixes, use that as the lookup word
        if found:
            lookup_word = lookup_word_with_suffixes

    # Third try: check if the core itself is in rad_dictionary
    # This handles cases where the root exists even if the full word doesn't
    if not found and rad_dictionary is not None:
        # Check if single root in rad_dictionary, or if compound with all parts valid
        if len(cored.core) == 1 and cored.core[0] in rad_dictionary:
            found = True
            # Keep the original lookup_word for display
        elif len(cored.core) > 1 and all(
            part in rad_dictionary for part in cored.core if len(part) > 1
        ):
            found = True
            # Keep the original lookup_word for display

    return found, lookup_word


def cored_word_to_dict(
    stemmer: eostem.Stemmer,
    cored: CoredWord,
    verify: bool = False,
    dictionary: dict[str, str] | None = None,
    rad_dictionary: dict[str, str] | None = None,
) -> dict[str, str | list[str] | dict[str, str | bool]]:
    """Convert a CoredWord to a dictionary for JSON serialization.

    Args:
        stemmer: The Stemmer instance
        cored: The cored word to convert
        verify: Whether to include verification information
        dictionary: Dictionary for verification
        rad_dictionary: Rad dictionary for verification

    Returns:
        Dictionary with word analysis
    """
    result: dict[str, str | list[str] | dict[str, str | bool]] = {
        "word": cored.orig_word,
        "prefixes": cored.prefixes,
        "core": cored.core,
        "suffixes": cored.suffixes,
        "ending": cored.preferred_ending,
    }

    # Add verification result if requested
    if verify and dictionary is not None:
        found, lookup_word = verify_stem(stemmer, cored, dictionary, rad_dictionary)
        result["verification"] = {
            "found": found,
            "lookup_word": lookup_word,
        }

    return result


def format_cored_word(
    stemmer: eostem.Stemmer,
    cored: CoredWord,
    verify: bool = False,
    dictionary: dict[str, str] | None = None,
    rad_dictionary: dict[str, str] | None = None,
) -> str:
    """Format a CoredWord for display as a one-line output.

    Format: word = prefix+core+suffix+ending [lookup: word | FOUND/NOT FOUND]

    Examples:
        parolanto = parol+ant+i
        nekompreneble = ne+kompren+ebl+i [lookup: kompreni | FOUND]
        maltrankviliga = mal+trankvil+ig+i [lookup: trankvili | NOT FOUND]
    """
    # Build the word breakdown
    word_parts: list[str] = []
    if cored.prefixes:
        word_parts.append("+".join(cored.prefixes))
    if cored.core:
        word_parts.append(stemmer.core_display(cored.core))
    if cored.suffixes:
        word_parts.append("+".join(cored.suffixes))
    if cored.preferred_ending:
        word_parts.append(cored.preferred_ending)

    breakdown = "+".join(word_parts)
    result = f"{cored.orig_word} = {breakdown}"

    # Add verification result if requested
    if verify and dictionary is not None:
        found, lookup_word = verify_stem(stemmer, cored, dictionary, rad_dictionary)
        status = "FOUND" if found else "NOT FOUND"
        result += f" [lookup: {lookup_word} | {status}]"

    return result


def main() -> None:
    """Main entry point for the stem command."""
    # Ensure UTF-8 encoding for output on Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    if len(sys.argv) < 2:
        print(
            "Usage: python -m glosilo.stem [--debug] [--verify] [--json] <word> [<word> ...]",
            file=sys.stderr,
        )
        print("\nOptions:", file=sys.stderr)
        print("  --debug   Show detailed stemming process", file=sys.stderr)
        print("  --verify  Verify stem exists in dictionary", file=sys.stderr)
        print("  --json    Output results as JSON", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python -m glosilo.stem parolanto", file=sys.stderr)
        print(
            "  python -m glosilo.stem parolanto nekompreneble ekdiri", file=sys.stderr
        )
        print("  python -m glosilo.stem --debug nekompreneble", file=sys.stderr)
        print(
            "  python -m glosilo.stem --verify maltrankviliga kato lernejo",
            file=sys.stderr,
        )
        print("  python -m glosilo.stem --debug --verify ekdiri", file=sys.stderr)
        print(
            '  python -m glosilo.stem --verify "unu du bonfaras, kie?"',
            file=sys.stderr,
        )
        print(
            '  python -m glosilo.stem --json "parolanto nekompreneble"',
            file=sys.stderr,
        )
        sys.exit(1)

    debug: bool = False
    verify: bool = False
    json_output: bool = False
    words: list[str] = []

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "--debug":
            debug = True
        elif arg == "--verify":
            verify = True
        elif arg == "--json":
            json_output = True
        else:
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

    stemmer = eostem.Stemmer()

    # Load dictionaries if verification requested
    dictionary: dict[str, str] | None = None
    rad_dictionary: dict[str, str] | None = None
    if verify:
        dictionary = stemmer.get_kap_dictionary()
        rad_dictionary = stemmer.get_rad_dictionary()

    # Stem each word
    if json_output:
        # JSON output mode: collect all results and output as array
        results: list[dict[str, str | list[str] | dict[str, str | bool]]] = []
        for word in words:
            cored = stemmer.core_word(word, debug=False)  # No debug in JSON mode

            # When verifying, only include words that are NOT FOUND
            if verify:
                assert dictionary is not None
                found, _ = verify_stem(stemmer, cored, dictionary, rad_dictionary)
                if found:
                    continue  # Skip words that are found

            results.append(
                cored_word_to_dict(
                    stemmer,
                    cored,
                    verify=verify,
                    dictionary=dictionary,
                    rad_dictionary=rad_dictionary,
                )
            )

        # Output JSON with no other text
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # Normal text output mode
        for word in words:
            cored = stemmer.core_word(word, debug=debug)

            # When verifying, only show words that are NOT FOUND
            if verify:
                assert dictionary is not None
                found, _ = verify_stem(stemmer, cored, dictionary, rad_dictionary)
                if found:
                    continue  # Skip words that are found

            # Print results
            if debug:
                print("\n" + "=" * 50)
            print(
                format_cored_word(
                    stemmer,
                    cored,
                    verify=verify,
                    dictionary=dictionary,
                    rad_dictionary=rad_dictionary,
                )
            )


if __name__ == "__main__":
    main()
