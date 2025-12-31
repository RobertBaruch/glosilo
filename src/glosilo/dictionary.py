"""The dictionary."""

import copy
import pathlib
import re

from glosilo import consts
from glosilo import eostem
from glosilo import structs


class Dictionary:
    """The dictionary class."""

    debug: bool
    debug_word: str
    words: dict[str, structs.CoredWord]

    def __init__(self, debug: bool = False, debug_word: str = ""):
        self.debug = debug
        self.debug_word = debug_word
        self.words = {}
        self._read_word_files()

    def _parse_word_file_line(self, line: str) -> None:
        line = line.strip()
        if not line or line.startswith("#"):
            return

        try:
            key, value = line.split(": ")
        except ValueError as e:
            raise ValueError(f"Error in line: {line}") from e

        key = key.strip()
        value = value.strip()

        analysis = eostem.core_word(key, key == self.debug_word)
        value = value.replace("(", "").replace(")", "")
        defs = [part.strip() for part in re.split("[;,]", value)]
        pref_def = self._choose_preferred_translation(key, value)
        analysis.definitions = defs
        analysis.preferred_definition = pref_def

        # We don't particularly care about definitions that *should* be obvious.
        if analysis.prefixes and analysis.prefixes[0] in ["ne", "mal"]:
            return

        if key == self.debug_word:
            print(f"Dictionary initial load of {key}: {analysis}")
        self.words[key] = analysis

    def _load_word_file(self, path: pathlib.Path) -> None:
        with path.open(mode="r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self._parse_word_file_line(line)

    def _add_core_definitions(self) -> None:
        for word, analysis in self.words.items():
            if word == self.debug_word:
                print(f"Adding core definition for {word}; initial analysis {analysis}")
            # if word in consts.COMMON_WORDS:
            #     continue
            if analysis.preferred_ending not in consts.ENDING_ALTERNATIVES:
                analysis.core_definition = analysis.preferred_definition
                if word == self.debug_word:
                    print(f"  No ending alternatives for {word}; new analysis {analysis}")
                continue

            # For cores that are vortetoj, we just use the preferred
            # definition as the core definition. Except for ĉiel, which is easily
            # confused with ĉielo.
            if (
                analysis.core in (consts.VORTETOJ - {"ĉiel"})
                and analysis.core in self.words
            ):
                analysis.core_definition = self.words[
                    analysis.core
                ].preferred_definition
                if word == self.debug_word:
                    print(f"  Vorteto core {analysis.core} for {word}; new analysis {analysis}")
                continue

            for ending in [analysis.preferred_ending] + consts.ENDING_ALTERNATIVES[
                analysis.preferred_ending
            ]:
                root = analysis.core + ending
                if word == self.debug_word:
                    print(f"  Trying root {root}")
                if root in self.words:
                    analysis.core_definition = self.words[root].preferred_definition
                    if word == self.debug_word:
                        print(f"  Found core definition for {word}; new analysis {analysis}")
                    break

            if root not in self.words:
                if word == self.debug_word:
                    print(f"  No core definition found for {word}; new analysis {analysis}")
                analysis.core_definition = "???"

    def _read_word_files(self) -> None:
        """Reads the word file."""
        for name in [consts.WORDFILE, consts.WORDFILE_ADDITIONS]:
            path = pathlib.Path(__file__).parent / name
            self._load_word_file(path)
        self._add_core_definitions()

    def _choose_preferred_translation(self, key: str, value: str) -> str:
        """Chooses the preferred translation for a word.

        Splits value on commas and semicolons, and returns the part that is the closest
        match alphabetically to the key. If the first part begins with "to ", then
        prepends "to-" to the chosen part.

        Args:
            key: The key, the Esperanto word.
            value: The value, a comma or semicolon-separated list of translations.

        Returns:
            The chosen translation.
        """
        parts = re.split("[,;] ", value)
        if len(parts) == 1:
            return parts[0].replace(" ", "-")

        include_to = parts[0].startswith("to ")

        for i, part in enumerate(parts):
            if part.startswith("to "):
                parts[i] = part[3:]

        scores: list[int] = []
        for part in parts:
            # The score is the number of first characters that match.
            score = 0
            for i in range(min(len(part), len(key))):
                if part[i] == (
                    key[i]
                    .replace("ŭ", "u")
                    .replace("ĉ", "ch")
                    .replace("ĝ", "j")
                    .replace("ŝ", "sh")
                    .replace("j", "y")
                ):
                    score += 1
                else:
                    break
            scores.append(score)

        # Choose the index with the highest score.
        chosen_index = scores.index(max(scores))
        chosen_part = parts[chosen_index]
        if include_to and not chosen_part.startswith("to "):
            chosen_part = f"to-{chosen_part}"
        return chosen_part.replace(" ", "-")

    def lookup_cored_word(
        self, cored_word: structs.CoredWord, num_prefixes: int, num_suffixes: int
    ) -> structs.CoredWord:
        """Looks up a cored word with a certain number of prefixes and suffixes.

        We always use the LAST num_prefixes prefixes and the FIRST num_suffixes
        suffixes.
        """
        if self.debug:
            print(f" Trying {num_prefixes} prefixes and {num_suffixes} suffixes")
        prefix = ""
        suffix = ""
        # If one of the suffixes is for a participle, then prefer the "i" ending.
        preferred_ending = cored_word.preferred_ending
        if num_prefixes:
            prefix = "".join(cored_word.prefixes[-num_prefixes:])
        if num_suffixes:
            suffix = "".join(cored_word.suffixes[:num_suffixes])
        root = prefix + cored_word.core + suffix
        endings = [preferred_ending]
        if preferred_ending in consts.ENDING_ALTERNATIVES:
            endings += consts.ENDING_ALTERNATIVES[preferred_ending]
        for ending in endings:
            if self.debug:
                print(f"  Trying {root}+{ending}")
            analysis = self._get_saved_gloss(root + ending)
            if analysis.preferred_definition != "???":
                return analysis

        return structs.CoredWord(cored_word.orig_word, [], "", [], "", [], "???", "???")

    def _get_saved_gloss(self, word: str) -> structs.CoredWord:
        analysis = self.words.get(
            word,
            structs.CoredWord(word, [], "", [], "", [], "???", "???"),
        )
        if self.debug:
            print(f"Retrieving saved gloss: {analysis}")
        return analysis

    def _reanalyze(self, word: str) -> structs.CoredWord:
        analysis = eostem.core_word(word, debug=self.debug)
        if self.debug:
            print(f"  Initial reanalysis: {analysis}")
        # Start with all prefixes and suffixes, and strip prefixes first.
        for num_suffixes in range(len(analysis.suffixes), -1, -1):
            for num_prefixes in range(len(analysis.prefixes), -1, -1):
                new_analysis = self.lookup_cored_word(
                    analysis, num_prefixes, num_suffixes
                )
                if new_analysis.preferred_definition != "???":
                    analysis = copy.copy(analysis)
                    # analysis.preferred_definition = new_analysis.preferred_definition
                    analysis.core_definition = new_analysis.core_definition
                    if self.debug:
                        print(f"  Reanalyzed as {analysis}")
                    return analysis

        # If the core is a vorteto, then use that in the core definition.
        if analysis.core in consts.VORTETOJ and analysis.core in self.words:
            analysis = copy.copy(analysis)
            analysis.core_definition = self.words[analysis.core].preferred_definition
            analysis.preferred_definition = "???"
            return analysis

        return structs.CoredWord(word, [], "", [], "", [], "???", "???")

    def get_hyphenated_gloss(self, word: str) -> structs.CoredWord:
        """Analyzes a hyphenated word."""
        orig_word = word
        word = word.lower()
        word = eostem.maybe_strip_plural_acc_ending(word)
        word = eostem.replace_verb_ending(word)
        full_analysis = self._get_saved_gloss(word)
        if full_analysis.preferred_definition == "???":
            if self.debug:
                print(f"  No definition found for {word}; reanalyzing")
            # If the word doesn't end in a standard Esperanto ending (u has already
            # been converted to i), then don't reanalyze.
            if word[-1] in ["a", "e", "i", "o"]:
                full_analysis = self._reanalyze(word)

        # For hyphenated (compound) words, we analyze each part separately. We assume
        # that each part other than the last has no ending. So firstly, this helps
        # us when we have a word like "aerŝipo", which becomes hypenated as "aer-ŝipo".
        # We also assume that all parts other than the end have an "o" ending. This is,
        # unfortunately, not always true: nigra-blanka and not nigr-blanka. So we'll
        # first try with an ending, then without.
        parts = word.split("-")
        orig_parts = orig_word.split("-")
        analyses = []
        for i, part in enumerate(parts):
            if i == len(parts) - 1 or part in consts.VORTETOJ:
                g = self.get_gloss(part)
                g.orig_word = orig_parts[i]
                analyses.append(g)
                continue
            part += "o"
            g = self.get_gloss(part)
            if g.core_definition == "???":
                g = self.get_gloss(part[:-1])
            g.orig_word = orig_parts[i]
            analyses.append(g)
        return structs.CoredWord(
            orig_word,
            analyses[0].prefixes,
            full_analysis.core,
            analyses[-1].suffixes,
            full_analysis.preferred_ending,
            [],
            full_analysis.preferred_definition,
            "???",
            parts=analyses,
        )

    def get_gloss(self, word: str) -> structs.CoredWord:
        """Analyzes a word."""
        if self.debug:
            print(f"Getting gloss for {word}")
        if not word[0].isalpha():
            return structs.CoredWord(word, [], "", [], "", [], "", "")
        if "-" in word:
            parts = word.split("-")
            # To get around words like d-ro and s-ro.
            if len(parts[0]) > 1:
                return self.get_hyphenated_gloss(word)

        orig_word = word
        word = word.lower()
        word = eostem.maybe_strip_plural_acc_ending(word)
        word = eostem.replace_verb_ending(word)
        analysis = self._get_saved_gloss(word)
        if analysis.preferred_definition == "???":
            if self.debug:
                print(
                    f"  No definition found for {word}; "
                    f"reanalyzing (ending {analysis.preferred_ending})."
                )
            # If the word doesn't end in a standard Esperanto ending (u has already
            # been converted to i), then don't reanalyze.
            #if word[-1] in ["a", "e", "i", "o"]:
            analysis = self._reanalyze(word)
        analysis = copy.copy(analysis)
        analysis.orig_word = orig_word
        return analysis
