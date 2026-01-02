"""The main glosser."""

import copy
import io
import pathlib
import re
from typing import Iterable
import unicodedata

from absl import app  # type: ignore

from glosilo import consts
from glosilo import structs
from glosilo.dictionary import Dictionary


DEBUG = False
WORDPILE = ""
# DEBUG = True
# WORDPILE = "Ĉapman-domo"
DEBUGWORD = "Ĉapman-domo" if DEBUG else ""

WORDFILE = "text1.txt"
OUTFILE = "gloss1.tex"


class Glosser:
    """Glosses a wordpile."""
    dictionary: Dictionary
    difficult: dict[str, str]
    names: dict[str, str]
    name_used: dict[str, bool]

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary
        self.difficult = {}
        path = pathlib.Path(__file__).parent / consts.DIFFICULT_WORDLIST_FILE
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                key, value = line.split(":", 1)
                self.difficult[key.strip()] = value.strip()

        path = pathlib.Path(__file__).parent / consts.NAMELIST_FILE
        self.names = {}
        self.name_used = {}
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                key, value = line.split(":", 1)
                self.names[key.strip()] = value.strip()
                self.name_used[key.strip()] = False

    def handle_name(self, g: structs.CoredWord) -> None:
        if g.orig_word in self.names:
            print(f"{g.orig_word} is a name")
            if self.name_used[g.orig_word]:
                g.core_definition = ""
                g.preferred_definition = ""
                g.parts = []
            else:
                self.name_used[g.orig_word] = True
                g.core_definition = self.names[g.orig_word]
                g.preferred_definition = self.names[g.orig_word]
                g.parts = []

    def gloss(self, wordpile: str, fout: io.TextIOWrapper) -> None:
        """Glosses a wordpile."""
        if DEBUG:
            print("==============================")

        # Make a copy of the gloss from the dictionary because we will be modifying them
        # for punctuation.
        glosses: list[structs.CoredWord] = []
        for word in words_to_gloss(wordpile):
            g = get_dictionary_gloss(self.dictionary, word)
            g = adjust_gloss(self, g)
            glosses.append(g)
            self.handle_name(g)
            for part in g.parts:
                self.handle_name(part)
        glosses = merge_punctuation(glosses)

        print("\\section{}\n\\begingl%", file=fout)

        for g in glosses:
            line = hyphenated_gloss(self, g) if g.parts else single_part_gloss(self, g)
            print(line, file=fout)

        print("\\endgl%\n", file=fout)

def words_to_gloss(words: str) -> Iterable[str]:
    """Yields individual words to gloss."""
    for word in words.split():
        for part in re.split(consts.PUNCTUATION_REGEX, word):
            if not part:
                continue
            yield part


def suffix_list_to_tags(suffixes: list[str]) -> str:
    """Converts a list of suffixes to tags."""
    if not suffixes:
        return ""
    return "-".join(
        consts.SUFFIXES[suffix].lower()
        for suffix in suffixes
        if suffix in consts.SUFFIXES
    )


def merge_punctuation(glosses: list[structs.CoredWord]) -> list[structs.CoredWord]:
    """Merges glosses with punctuation."""
    punctuated_glosses: list[structs.CoredWord] = []

    for g in glosses:
        # If the last character in the previous word was in [(“] then prepend the
        # previous word to the current word and add the current word.
        if punctuated_glosses and punctuated_glosses[-1].orig_word[-1] in "(“":
            orig_word = punctuated_glosses[-1].orig_word
            punctuated_glosses[-1] = copy.copy(g)
            punctuated_glosses[-1].orig_word = orig_word + g.orig_word
            continue

        if g.orig_word not in ".,:;)”—!?":
            punctuated_glosses.append(g)
            continue

        punctuated_glosses[-1].orig_word += g.orig_word

    return punctuated_glosses


def get_dictionary_gloss(dictionary: Dictionary, word: str) -> structs.CoredWord:
    """Gets the gloss from the dictionary."""
    from glosilo.eostem import core_to_str

    analysis = dictionary.get_gloss(word)
    if (
        core_to_str(analysis.core) + analysis.preferred_ending in consts.COMMON_WORDS
        and not analysis.prefixes
        and not analysis.suffixes
    ):
        return structs.CoredWord(word, [], [""], [], "", [], "", "")
    return copy.copy(analysis)


def adjust_gloss(glosser: Glosser, g: structs.CoredWord) -> structs.CoredWord:
    """Adjusts the gloss for things we want the reader to figure out."""
    from glosilo import eostem

    word = g.orig_word
    word = eostem.maybe_strip_plural_acc_ending(word)
    word = eostem.replace_verb_ending(word)
    if word in glosser.difficult:
        g.preferred_definition = glosser.difficult[word]
        return g

    last_suffix = 1
    first_prefix = 0

    # Do not translate particles, let the reader figure them out.
    if len(g.suffixes) >= last_suffix and g.suffixes[-last_suffix] in [
        "at",
        "it",
        "ot",
        "ant",
        "int",
        "ont",
    ]:
        suf = g.suffixes[-last_suffix]
        rip = len(suf) + 1
        word = word[:-rip] + "i"
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        last_suffix += 1

    # Do not translate ig/iĝ, let the reader figure it out.
    if len(g.suffixes) >= last_suffix and g.suffixes[-last_suffix] in ["ig", "iĝ"]:
        suf = g.suffixes[-last_suffix]
        rip = len(suf) + 1
        word = word[:-rip] + "i"
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        last_suffix += 1

    # Do not translate aĵ, let the reader figure it out.
    if len(g.suffixes) >= last_suffix and g.suffixes[-last_suffix] == "aĵ":
        suf = g.suffixes[-last_suffix]
        rip = len(suf) + 1
        word = word[:-rip] + word[-1]
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        last_suffix += 1

    # Do not translate ad, let the reader figure it out.
    if len(g.suffixes) >= last_suffix and g.suffixes[-last_suffix] == "ad":
        suf = g.suffixes[-last_suffix]
        rip = len(suf) + 1
        word = word[:-rip] + "i"
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        last_suffix += 1

    # Do not translate ebl, let the reader figure it out.
    if len(g.suffixes) >= last_suffix and g.suffixes[-last_suffix] == "ebl":
        suf = g.suffixes[-last_suffix]
        rip = len(suf) + 1
        word = word[:-rip] + "i"
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        last_suffix += 1

    # Do not translate mal, let the reader figure it out.
    if len(g.prefixes) > first_prefix and g.prefixes[first_prefix] == "mal":
        pref = g.prefixes[first_prefix]
        rip = len(pref)
        word = word[rip:]
        analysis = get_dictionary_gloss(glosser.dictionary, word)
        g.preferred_definition = ""
        first_prefix += 1

    return g

def hyphenated_gloss(glosser: Glosser, g: structs.CoredWord) -> str:
    """Returns a formatted gloss for a hyphenated word."""
    if DEBUG:
        print(g)

    definition = "-".join(core_gloss(glosser, part) for part in g.parts)
    if "???" in definition:
        print(g)

    if not g.preferred_definition or (
        g.core_definition == g.preferred_definition
    ):
        return f"{g.orig_word}[{definition}]"
    preferred_definition = g.preferred_definition.replace("-", " ")
    return f"{g.orig_word}[{definition}/{preferred_definition}]"

def core_gloss(glosser: Glosser, g: structs.CoredWord) -> str:
    """Returns a formatted core."""
    if g.preferred_definition == "???":
        return "???"

    definition = g.core_definition
    suffix_list = suffix_list_to_tags(g.suffixes)
    if definition and suffix_list:
        definition = f"{definition}+{{\\sc {suffix_list}}}"
    if definition and g.prefixes:
        prefix_list = "-".join(
            consts.PREFIXES[prefix].lower() for prefix in g.prefixes
        )
        definition = f"{{\\sc {prefix_list}}}+{definition}"
    return definition

def single_part_gloss(glosser: Glosser, g: structs.CoredWord) -> str:
    """Returns a formatted gloss for a single part."""
    if DEBUG:
        print(g)

    if g.preferred_definition == "???" or g.core_definition == "???":
        print(g)

    definition = core_gloss(glosser, g)
    # if g.preferred_definition == "???":
    #     return f"{g.orig_word}[???]"

    if not g.preferred_definition or (
        g.core_definition == g.preferred_definition
    ):
        return f"{g.orig_word}[{definition}]"
    preferred_definition = g.preferred_definition.replace("-", " ")
    return f"{g.orig_word}[{definition}/{preferred_definition}]"


def run() -> None:
    """Runs the glosser."""
    dictionary = Dictionary(debug=DEBUG, debug_word=DEBUGWORD)
    glosser = Glosser(dictionary)
    words = WORDPILE
    if not words:
        with open(WORDFILE, "r", encoding="utf-8") as infile:
            words = infile.read()
    words = unicodedata.normalize('NFC', words)
    words = words.replace("\\-", "")
    paragraphs = words.split("\n\n")
    with open(OUTFILE, "w", encoding="utf-8") as outfile:
        for paragraph in paragraphs:
            glosser.gloss(paragraph, outfile)


def main(argv: list[str]) -> None:
    """Main function."""
    del argv  # Unused.
    run()


if __name__ == "__main__":
    app.run(main)
