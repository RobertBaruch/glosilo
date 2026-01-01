"""Command-line tool for stemming Esperanto words.

Usage:
    python -m glosilo.stem <word>
    python -m glosilo.stem --debug <word>
    python -m glosilo.stem --verify <word>
"""

import json
import sys
from pathlib import Path
from glosilo import eostem
from glosilo.structs import CoredWord

DICTIONARY_PATH = Path("F:/retavortaropy/kap_dictionary.json")


def load_dictionary() -> dict[str, str] | None:
    """Load the dictionary from the JSON file.

    Returns:
        Dictionary mapping words to file paths, or None if file not found.
    """
    if not DICTIONARY_PATH.exists():
        return None

    try:
        with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load dictionary: {e}", file=sys.stderr)
        return None


def verify_stem(cored: CoredWord, dictionary: dict[str, str]) -> tuple[bool, str]:
    """Verify that the stem exists in the dictionary.

    The stem is formed by combining the core with the ending.
    For example, "nekompreneble" -> core="kompren" + ending="i" -> "kompreni"

    Args:
        cored: The cored word to verify
        dictionary: Dictionary mapping words to file paths

    Returns:
        Tuple of (found, lookup_word) where found is True if the word exists
        in the dictionary, and lookup_word is the word that was looked up.
    """
    # Form the lookup word: core + ending
    lookup_word = cored.core + cored.preferred_ending if cored.preferred_ending else cored.core
    found = lookup_word in dictionary
    return found, lookup_word


def format_cored_word(cored: CoredWord, verify: bool = False, dictionary: dict[str, str] | None = None) -> str:
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
        word_parts.append(cored.core)
    if cored.suffixes:
        word_parts.append("+".join(cored.suffixes))
    if cored.preferred_ending:
        word_parts.append(cored.preferred_ending)

    breakdown = "+".join(word_parts)
    result = f"{cored.orig_word} = {breakdown}"

    # Add verification result if requested
    if verify and dictionary is not None:
        found, lookup_word = verify_stem(cored, dictionary)
        status = "FOUND" if found else "NOT FOUND"
        result += f" [lookup: {lookup_word} | {status}]"

    return result


def main() -> None:
    """Main entry point for the stem command."""
    if len(sys.argv) < 2:
        print("Usage: python -m glosilo.stem [--debug] [--verify] <word>", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  --debug   Show detailed stemming process", file=sys.stderr)
        print("  --verify  Verify stem exists in dictionary", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python -m glosilo.stem parolanto", file=sys.stderr)
        print("  python -m glosilo.stem --debug nekompreneble", file=sys.stderr)
        print("  python -m glosilo.stem --verify maltrankviliga", file=sys.stderr)
        print("  python -m glosilo.stem --debug --verify ekdiri", file=sys.stderr)
        sys.exit(1)

    debug: bool = False
    verify: bool = False
    word: str | None = None

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "--debug":
            debug = True
        elif arg == "--verify":
            verify = True
        elif not word:
            word = arg
        else:
            print(f"Error: Unexpected argument '{arg}'", file=sys.stderr)
            sys.exit(1)

    if not word:
        print("Error: No word provided", file=sys.stderr)
        sys.exit(1)

    # Load dictionary if verification requested
    dictionary: dict[str, str] | None = None
    if verify:
        dictionary = load_dictionary()
        if dictionary is None:
            print(f"Warning: Dictionary not found at {DICTIONARY_PATH}", file=sys.stderr)
            print("Continuing without verification...\n", file=sys.stderr)
            verify = False

    # Stem the word
    cored = eostem.core_word(word, debug=debug)

    # Print results
    if not debug:
        print(format_cored_word(cored, verify=verify, dictionary=dictionary))
    else:
        # Debug mode already prints detailed info during processing
        print("\n" + "=" * 50)
        print(format_cored_word(cored, verify=verify, dictionary=dictionary))


if __name__ == "__main__":
    main()
