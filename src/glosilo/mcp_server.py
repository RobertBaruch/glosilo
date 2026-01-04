"""MCP server for the glosilo lookup tool."""

from fastmcp import FastMCP
from glosilo import lookup

mcp = FastMCP("Glosilo MCP Server")


@mcp.tool
def eo_lookup(words: str) -> lookup.Results:
    """Look up Esperanto words with morphological analysis and definitions.

    Analyzes Esperanto words by breaking them down into morphological components
    (prefixes, core/root, suffixes, and grammatical endings) and retrieves their
    definitions from the ReVo (Reta Vortaro) Esperanto dictionary.

    The tool handles:
    - Simple words (e.g., "paroli" -> parol + i)
    - Derived words with affixes (e.g., "priparolado" -> pri + parol + ad + o)
    - Compound words (e.g., "bonfaranta" -> bon + far + ant + a)
    - Multiple words in a single query (space or punctuation separated)

    Lookup strategies (in order):
    1. Exact match - Direct dictionary lookup of the word as-is
    2. With ending - Reconstructs word from morphemes and tries different grammatical endings
    3. Suffix stripping - Progressively removes suffixes to find dictionary forms
    4. Core lookup - Looks up individual root morphemes separately

    Args:
        words: One or more Esperanto words to analyze. Can be:
               - A single word: "paroli"
               - Multiple words: "mi parolas Esperanton"
               - With punctuation: "Saluton! Kiel vi fartas?"
               Punctuation is automatically stripped from words.

    Returns:
        Results object containing a list of Result objects, one per word.
        Each Result includes:
        - word: The original word
        - prefixes: List of identified prefixes
        - core: List of root morphemes (multiple for compounds)
        - suffixes: List of identified suffixes
        - ending: The grammatical ending
        - lookup: LookupResult with:
          - found: Whether definitions were found
          - lookup_method: Strategy used ('exact', 'with_ending', 'suffix_stripped', 'core', or None)
          - lookup_word: Dictionary form that was found
          - article_id: ReVo article identifier
          - definitions: List of Definition objects with:
            - core_word: The root morpheme
            - lookup_word: The word form in the dictionary
            - senses: Dictionary mapping sense numbers to definition text

    Examples:
        >>> eo_lookup("paroli")
        # Returns analysis: parol (root) + i (infinitive ending)
        # With definition: "to speak"

        >>> eo_lookup("bonfaranto")
        # Returns analysis: bon (prefix) + far (root) + ant (suffix) + o (noun ending)
        # With definition: "benefactor, one who does good"

        >>> eo_lookup("mi parolas Esperanton")
        # Returns analysis for three words: "mi", "parolas", "Esperanton"
    """
    return lookup.convert_to_results(lookup.lookup_words(words))


if __name__ == "__main__":
    mcp.run()
