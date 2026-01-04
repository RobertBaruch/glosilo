"""Allow glosilo to be run as a module."""
import sys

if __name__ == "__main__":
    # Default to lookup if no subcommand specified
    if len(sys.argv) > 1 and sys.argv[1] in ["stem", "lookup"]:
        subcommand = sys.argv.pop(1)
    else:
        subcommand = "lookup"

    if subcommand == "stem":
        from glosilo import stem
        stem.main()
    elif subcommand == "lookup":
        from glosilo import lookup
        lookup.main()
