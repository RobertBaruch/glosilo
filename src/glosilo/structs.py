"""Data structures for the Glosilo project."""

from __future__ import annotations
import dataclasses


@dataclasses.dataclass
class GlossColumn:
    """A one-word column in a gloss."""

    word: str
    gloss: str
    colloquialism: str


@dataclasses.dataclass
class AnalyzedDefinition:
    """An analyzed definition."""

    word: str
    root: str
    prefixes: list[str]
    definition: tuple[str, str]
    suffixes: list[str]


@dataclasses.dataclass
class CoredWord:
    """A cored word."""

    orig_word: str
    prefixes: list[str]
    # The core of a word is the part that is left after all prefixes and suffixes
    # and endings have been removed. For compound words, this is a list of roots
    # (e.g., ['blu', 'okul'] for bluokul). Linking vowels are included as separate
    # elements (e.g., ['mult', 'e', 'hom'] for multehom).
    core: list[str]
    suffixes: list[str]
    preferred_ending: str
    definitions: list[str]
    preferred_definition: str
    core_definition: str
    parts: list[CoredWord] = dataclasses.field(default_factory=list)

    def __str__(self) -> str:
        from glosilo.eostem import core_display

        parts = ", ".join(str(part) for part in self.parts)
        core_str = core_display(self.core)
        return (
            f"{self.orig_word} = {self.prefixes}+{core_str}({self.core_definition})"
            f"+{self.suffixes}+{self.preferred_ending} = {self.preferred_definition} "
            f"[{parts}]"
        )
