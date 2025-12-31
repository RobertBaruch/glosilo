"""Command-line tool for stemming Esperanto words.

Usage:
    python -m glosilo.stem <word>
    python -m glosilo.stem --debug <word>
"""

import sys
from glosilo import eostem
from glosilo.structs import CoredWord


def format_cored_word(cored: CoredWord) -> str:
    """Format a CoredWord for display."""
    parts = []

    # Build the word breakdown
    prefixes_str = "+".join(cored.prefixes) if cored.prefixes else ""
    suffixes_str = "+".join(cored.suffixes) if cored.suffixes else ""

    word_parts = []
    if prefixes_str:
        word_parts.append(prefixes_str)
    if cored.core:
        word_parts.append(cored.core)
    if suffixes_str:
        word_parts.append(suffixes_str)
    if cored.preferred_ending:
        word_parts.append(cored.preferred_ending)

    breakdown = "+".join(word_parts)

    # Format output
    parts.append(f"Word: {cored.orig_word}")
    parts.append(f"Breakdown: {breakdown}")
    parts.append(f"Core: {cored.core}")

    if cored.prefixes:
        parts.append(f"Prefixes: {', '.join(cored.prefixes)}")
    if cored.suffixes:
        parts.append(f"Suffixes: {', '.join(cored.suffixes)}")
    if cored.preferred_ending:
        parts.append(f"Ending: {cored.preferred_ending}")

    return "\n".join(parts)


def main() -> None:
    """Main entry point for the stem command."""
    if len(sys.argv) < 2:
        print("Usage: python -m glosilo.stem [--debug] <word>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python -m glosilo.stem parolanto", file=sys.stderr)
        print("  python -m glosilo.stem --debug nekompreneble", file=sys.stderr)
        sys.exit(1)

    debug: bool = False
    word: str | None = None

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "--debug":
            debug = True
        elif not word:
            word = arg
        else:
            print(f"Error: Unexpected argument '{arg}'", file=sys.stderr)
            sys.exit(1)

    if not word:
        print("Error: No word provided", file=sys.stderr)
        sys.exit(1)

    # Stem the word
    cored = eostem.core_word(word, debug=debug)

    # Print results
    if not debug:
        print(format_cored_word(cored))
    else:
        # Debug mode already prints detailed info during processing
        print("\n" + "=" * 50)
        print(format_cored_word(cored))


if __name__ == "__main__":
    main()
