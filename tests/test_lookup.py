"""
Tests for glosilo.lookup functionality using pytest framework.
"""

import io
import json
import pathlib
from typing import Any
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest

from glosilo.lookup import (
    Definition,
    LookupResult,
    Result,
    Results,
    try_lookup_with_endings,
    lookup_word_definitions,
    lookup_word_to_dict,
    lookup_words,
    convert_to_results,
    load_kap_dictionary,
    load_senses,
)
from glosilo.structs import CoredWord


class TestDataclasses:
    """Test the dataclass structures."""

    def test_definition_creation(self):
        """Test creating a Definition instance."""
        definition = Definition(
            core_word="parol",
            lookup_word="paroli",
            senses={"1": "to speak", "2": "to talk"},
        )
        assert definition.core_word == "parol"
        assert definition.lookup_word == "paroli"
        assert definition.senses == {"1": "to speak", "2": "to talk"}

    def test_lookup_result_creation(self):
        """Test creating a LookupResult instance."""
        definition = Definition(
            core_word="parol", lookup_word="paroli", senses={"1": "to speak"}
        )
        lookup_result = LookupResult(
            found=True,
            lookup_method="exact",
            lookup_word="paroli",
            article_id="parol",
            definitions=[definition],
        )
        assert lookup_result.found is True
        assert lookup_result.lookup_method == "exact"
        assert lookup_result.lookup_word == "paroli"
        assert lookup_result.article_id == "parol"
        assert len(lookup_result.definitions) == 1

    def test_result_creation(self):
        """Test creating a Result instance."""
        definition = Definition(
            core_word="parol", lookup_word="paroli", senses={"1": "to speak"}
        )
        lookup_result = LookupResult(
            found=True,
            lookup_method="exact",
            lookup_word="paroli",
            article_id="parol",
            definitions=[definition],
        )
        result = Result(
            word="parolas",
            prefixes=[],
            core=["parol"],
            suffixes=[],
            ending="as",
            lookup=lookup_result,
        )
        assert result.word == "parolas"
        assert result.core == ["parol"]
        assert result.ending == "as"
        assert result.lookup.found is True

    def test_results_creation(self):
        """Test creating a Results instance."""
        definition = Definition(
            core_word="parol", lookup_word="paroli", senses={"1": "to speak"}
        )
        lookup_result = LookupResult(
            found=True,
            lookup_method="exact",
            lookup_word="paroli",
            article_id="parol",
            definitions=[definition],
        )
        result = Result(
            word="parolas",
            prefixes=[],
            core=["parol"],
            suffixes=[],
            ending="as",
            lookup=lookup_result,
        )
        results = Results(results=[result])
        assert len(results.results) == 1
        assert results.results[0].word == "parolas"


class TestTryLookupWithEndings:
    """Test the try_lookup_with_endings function."""

    def test_exact_match(self):
        """Test finding an exact match in kap_dict."""
        kap_dict = {"paroli": "parol", "esti": "est"}
        lookup_word, article_id = try_lookup_with_endings("paroli", kap_dict)
        assert lookup_word == "paroli"
        assert article_id == "parol"

    def test_with_ending_i(self):
        """Test finding a word with 'i' ending."""
        kap_dict = {"paroli": "parol", "esti": "est"}
        lookup_word, article_id = try_lookup_with_endings("parol", kap_dict)
        assert lookup_word == "paroli"
        assert article_id == "parol"

    def test_with_ending_o(self):
        """Test finding a word with 'o' ending."""
        kap_dict = {"hundo": "hund", "kato": "kat"}
        lookup_word, article_id = try_lookup_with_endings("hund", kap_dict)
        assert lookup_word == "hundo"
        assert article_id == "hund"

    def test_with_ending_as(self):
        """Test finding a word with 'as' ending."""
        kap_dict = {"parolas": "parol"}
        lookup_word, article_id = try_lookup_with_endings("parol", kap_dict)
        assert lookup_word == "parolas"
        assert article_id == "parol"

    def test_not_found(self):
        """Test when word is not found with any ending."""
        kap_dict = {"paroli": "parol"}
        lookup_word, article_id = try_lookup_with_endings("hund", kap_dict)
        assert lookup_word is None
        assert article_id is None

    def test_empty_kap_dict(self):
        """Test with empty kap dictionary."""
        kap_dict: dict[str, str] = {}
        lookup_word, article_id = try_lookup_with_endings("parol", kap_dict)
        assert lookup_word is None
        assert article_id is None


class TestLoadKapDictionary:
    """Test the load_kap_dictionary function."""

    def test_load_existing_file(self):
        """Test loading an existing kap_dictionary.json file."""
        mock_data = {"paroli": "parol", "esti": "est"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
                result = load_kap_dictionary()
                assert result == mock_data

    def test_file_not_exists(self):
        """Test when kap_dictionary.json does not exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = load_kap_dictionary()
            assert result == {}


class TestLoadSensesFromXml:
    """Test the load_senses_from_xml function."""

    @patch("zipfile.ZipFile")
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_existing_xml(self, mock_exists, mock_zipfile):
        """Test loading senses from an existing JSON file in zip."""
        mock_senses = {"paroli": {"1": "to speak", "2": "to talk"}}

        # Mock the zip file operations
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        mock_zip.namelist.return_value = ["parol.json"]
        mock_zip.open.return_value.__enter__.return_value = io.BytesIO(
            json.dumps(mock_senses).encode('utf-8')
        )

        result = load_senses("parol")
        assert result == mock_senses

    @patch("pathlib.Path.exists", return_value=False)
    def test_xml_not_exists(self, mock_exists):
        """Test when zip file does not exist."""
        result = load_senses("nonexistent")
        assert result == {}

    @patch("zipfile.ZipFile", side_effect=Exception("Zip error"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_exception_handling(self, mock_exists, mock_zipfile):
        """Test exception handling when loading from zip fails."""
        result = load_senses("parol")
        assert result == {}


class TestLookupWordDefinitions:
    """Test the lookup_word_definitions function."""

    def test_exact_match_strategy(self):
        """Test Strategy 1: exact word match."""
        word = "paroli"
        cored = CoredWord(
            orig_word="paroli",
            prefixes=[],
            core=["parol"],
            suffixes=[],
            preferred_ending="i",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        kap_dict = {"paroli": "parol"}
        rad_dict = {"parol": "parol"}

        with patch("glosilo.lookup.load_senses_from_xml") as mock_load:
            mock_load.return_value = {"paroli": {"1": "to speak", "2": "to talk"}}

            result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

            assert result["found"] is True
            assert result["lookup_method"] == "exact"
            assert result["lookup_word"] == "paroli"
            assert result["article_id"] == "parol"
            assert "parol" in result["definitions"]
            assert "paroli" in result["definitions"]["parol"]

    def test_with_ending_strategy(self):
        """Test Strategy 2: word with different endings."""
        word = "parolanto"
        cored = CoredWord(
            orig_word="parolanto",
            prefixes=[],
            core=["parol"],
            suffixes=["ant"],
            preferred_ending="o",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        kap_dict = {"parolanti": "parol"}
        rad_dict = {"parol": "parol"}

        with patch("glosilo.lookup.load_senses_from_xml") as mock_load:
            mock_load.return_value = {"parolanti": {"1": "speaker (one who speaks)"}}

            result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

            assert result["found"] is True
            assert result["lookup_method"] == "with_ending"

    def test_suffix_stripped_strategy(self):
        """Test Strategy 2.5: suffix stripping."""
        word = "parolado"
        cored = CoredWord(
            orig_word="parolado",
            prefixes=[],
            core=["parol"],
            suffixes=["ad"],
            preferred_ending="o",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        kap_dict = {"paroli": "parol"}
        rad_dict = {"parol": "parol"}

        with patch("glosilo.lookup.load_senses_from_xml") as mock_load:
            mock_load.return_value = {"paroli": {"1": "to speak"}}

            result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

            assert result["found"] is True
            assert result["lookup_method"] == "suffix_stripped"
            assert "parol" in result["definitions"]

    def test_core_strategy(self):
        """Test Strategy 3: looking up cores (when other strategies fail)."""
        # Use a word where strategies 1, 2, and 2.5 won't work
        # but core lookup will succeed
        word = "unknownword"
        cored = CoredWord(
            orig_word="unknownword",
            prefixes=["pre"],  # Adding a prefix so the base reconstruction is "pretest"
            core=["test"],
            suffixes=[],
            preferred_ending="xyz",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        # "pretest" with any ending won't be found, so strategies 1 and 2 fail
        # But when looking up by core, "testi" will be found
        kap_dict = {"testi": "test"}
        rad_dict = {"test": "test"}

        with patch("glosilo.lookup.load_senses_from_xml") as mock_load:
            mock_load.return_value = {"testi": {"1": "to test"}}

            result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

            assert result["found"] is True
            assert result["lookup_method"] == "core"
            assert "test" in result["definitions"]

    def test_compound_word(self):
        """Test looking up a compound word with multiple cores."""
        word = "vortaro"
        cored = CoredWord(
            orig_word="vortaro",
            prefixes=[],
            core=["vort", "ar"],
            suffixes=[],
            preferred_ending="o",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        kap_dict = {"vorto": "vort", "aro": "ar"}
        rad_dict = {"vort": "vort", "ar": "ar"}

        with patch("glosilo.lookup.load_senses_from_xml") as mock_load:

            def load_senses_side_effect(article_id):
                if article_id == "vort":
                    return {"vorto": {"1": "word"}}
                elif article_id == "ar":
                    return {"aro": {"1": "group, collection"}}
                return {}

            mock_load.side_effect = load_senses_side_effect

            result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

            assert result["found"] is True
            assert result["lookup_method"] == "core"
            assert "vort" in result["definitions"]
            assert "ar" in result["definitions"]

    def test_not_found(self):
        """Test when word cannot be found."""
        word = "xyzabc"
        cored = CoredWord(
            orig_word="xyzabc",
            prefixes=[],
            core=["xyzab"],
            suffixes=[],
            preferred_ending="c",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        kap_dict = {}
        rad_dict = {}

        result = lookup_word_definitions(word, cored, kap_dict, rad_dict)

        assert result["found"] is False
        assert result["lookup_method"] is None
        assert result["lookup_word"] is None
        assert result["definitions"] == {}


class TestLookupWordToDict:
    """Test the lookup_word_to_dict function."""

    @patch("glosilo.lookup.lookup_word_definitions")
    def test_lookup_word_to_dict(self, mock_lookup_defs):
        """Test converting a word lookup to dictionary format."""
        mock_stemmer = Mock()
        mock_cored = CoredWord(
            orig_word="paroli",
            prefixes=[],
            core=["parol"],
            suffixes=[],
            preferred_ending="i",
            definitions=[],
            preferred_definition="",
            core_definition="",
        )
        mock_stemmer.core_word.return_value = mock_cored
        mock_stemmer.get_rad_dictionary.return_value = {"parol": "parol"}

        mock_lookup_defs.return_value = {
            "found": True,
            "lookup_method": "exact",
            "lookup_word": "paroli",
            "article_id": "parol",
            "definitions": {"parol": {"paroli": {"1": "to speak"}}},
        }

        kap_dict = {"paroli": "parol"}
        rad_dict = {"parol": "parol"}

        result = lookup_word_to_dict(mock_stemmer, "paroli", kap_dict, rad_dict)

        assert result["word"] == "paroli"
        assert result["prefixes"] == []
        assert result["core"] == ["parol"]
        assert result["suffixes"] == []
        assert result["ending"] == "i"
        assert "lookup" in result
        assert result["lookup"]["found"] is True


class TestLookupWords:
    """Test the lookup_words function."""

    @patch("glosilo.lookup.lookup_word_to_dict")
    @patch("glosilo.lookup.load_kap_dictionary")
    @patch("glosilo.eostem.Stemmer")
    def test_single_word(self, mock_stemmer_class, mock_load_kap, mock_lookup_word):
        """Test looking up a single word."""
        mock_stemmer = Mock()
        mock_stemmer.get_rad_dictionary.return_value = {}
        mock_stemmer_class.return_value = mock_stemmer
        mock_load_kap.return_value = {}

        mock_lookup_word.return_value = {
            "word": "paroli",
            "prefixes": [],
            "core": ["parol"],
            "suffixes": [],
            "ending": "i",
            "lookup": {"found": False},
        }

        result = lookup_words("paroli")

        assert len(result) == 1
        assert result[0]["word"] == "paroli"

    @patch("glosilo.lookup.lookup_word_to_dict")
    @patch("glosilo.lookup.load_kap_dictionary")
    @patch("glosilo.eostem.Stemmer")
    def test_multiple_words(self, mock_stemmer_class, mock_load_kap, mock_lookup_word):
        """Test looking up multiple words."""
        mock_stemmer = Mock()
        mock_stemmer.get_rad_dictionary.return_value = {}
        mock_stemmer_class.return_value = mock_stemmer
        mock_load_kap.return_value = {}

        def mock_lookup_side_effect(stemmer, word, kap_dict, rad_dict):
            return {
                "word": word,
                "prefixes": [],
                "core": [word[:-1]],
                "suffixes": [],
                "ending": word[-1],
                "lookup": {"found": False},
            }

        mock_lookup_word.side_effect = mock_lookup_side_effect

        result = lookup_words("paroli esti")

        assert len(result) == 2
        assert result[0]["word"] == "paroli"
        assert result[1]["word"] == "esti"

    @patch("glosilo.lookup.lookup_word_to_dict")
    @patch("glosilo.lookup.load_kap_dictionary")
    @patch("glosilo.eostem.Stemmer")
    def test_punctuation_stripping(
        self, mock_stemmer_class, mock_load_kap, mock_lookup_word
    ):
        """Test that punctuation is stripped from words."""
        mock_stemmer = Mock()
        mock_stemmer.get_rad_dictionary.return_value = {}
        mock_stemmer_class.return_value = mock_stemmer
        mock_load_kap.return_value = {}

        mock_lookup_word.return_value = {
            "word": "paroli",
            "prefixes": [],
            "core": ["parol"],
            "suffixes": [],
            "ending": "i",
            "lookup": {"found": False},
        }

        result = lookup_words("paroli, esti!")

        assert len(result) == 2
        # Check that lookup was called with stripped words
        calls = mock_lookup_word.call_args_list
        assert calls[0][0][1] == "paroli"
        assert calls[1][0][1] == "esti"

    @patch("glosilo.eostem.Stemmer")
    def test_empty_input(self, mock_stemmer_class):
        """Test with empty input."""
        result = lookup_words("")
        assert result == []

    @patch("glosilo.eostem.Stemmer")
    def test_only_punctuation(self, mock_stemmer_class):
        """Test with only punctuation."""
        result = lookup_words("... !!! ???")
        assert result == []


class TestConvertToResults:
    """Test the convert_to_results function."""

    def test_convert_single_result(self):
        """Test converting a single lookup result to Results dataclass."""
        lookup_data = [
            {
                "word": "paroli",
                "prefixes": [],
                "core": ["parol"],
                "suffixes": [],
                "ending": "i",
                "lookup": {
                    "found": True,
                    "lookup_method": "exact",
                    "lookup_word": "paroli",
                    "article_id": "parol",
                    "definitions": {
                        "parol": {"paroli": {"1": "to speak", "2": "to talk"}}
                    },
                },
            }
        ]

        results = convert_to_results(lookup_data)

        assert isinstance(results, Results)
        assert len(results.results) == 1
        assert isinstance(results.results[0], Result)
        assert results.results[0].word == "paroli"
        assert results.results[0].core == ["parol"]
        assert results.results[0].ending == "i"
        assert isinstance(results.results[0].lookup, LookupResult)
        assert results.results[0].lookup.found is True
        assert results.results[0].lookup.lookup_method == "exact"
        assert len(results.results[0].lookup.definitions) == 1
        assert isinstance(results.results[0].lookup.definitions[0], Definition)
        assert results.results[0].lookup.definitions[0].core_word == "parol"
        assert results.results[0].lookup.definitions[0].lookup_word == "paroli"
        assert results.results[0].lookup.definitions[0].senses == {
            "1": "to speak",
            "2": "to talk",
        }

    def test_convert_compound_word(self):
        """Test converting a compound word with multiple definitions."""
        lookup_data = [
            {
                "word": "vortaro",
                "prefixes": [],
                "core": ["vort", "ar"],
                "suffixes": [],
                "ending": "o",
                "lookup": {
                    "found": True,
                    "lookup_method": "core",
                    "lookup_word": "vort|ar",
                    "article_id": None,
                    "definitions": {
                        "vort": {"vorto": {"1": "word"}},
                        "ar": {"aro": {"1": "group, collection"}},
                    },
                },
            }
        ]

        results = convert_to_results(lookup_data)

        assert isinstance(results, Results)
        assert len(results.results) == 1
        assert results.results[0].core == ["vort", "ar"]
        assert len(results.results[0].lookup.definitions) == 2

        # Check that both cores are represented
        core_words = {d.core_word for d in results.results[0].lookup.definitions}
        assert core_words == {"vort", "ar"}

    def test_convert_multiple_results(self):
        """Test converting multiple lookup results."""
        lookup_data = [
            {
                "word": "paroli",
                "prefixes": [],
                "core": ["parol"],
                "suffixes": [],
                "ending": "i",
                "lookup": {
                    "found": True,
                    "lookup_method": "exact",
                    "lookup_word": "paroli",
                    "article_id": "parol",
                    "definitions": {"parol": {"paroli": {"1": "to speak"}}},
                },
            },
            {
                "word": "esti",
                "prefixes": [],
                "core": ["est"],
                "suffixes": [],
                "ending": "i",
                "lookup": {
                    "found": True,
                    "lookup_method": "exact",
                    "lookup_word": "esti",
                    "article_id": "est",
                    "definitions": {"est": {"esti": {"1": "to be"}}},
                },
            },
        ]

        results = convert_to_results(lookup_data)

        assert isinstance(results, Results)
        assert len(results.results) == 2
        assert results.results[0].word == "paroli"
        assert results.results[1].word == "esti"

    def test_convert_empty_definitions(self):
        """Test converting result with empty definitions."""
        lookup_data = [
            {
                "word": "xyzabc",
                "prefixes": [],
                "core": ["xyzab"],
                "suffixes": [],
                "ending": "c",
                "lookup": {
                    "found": False,
                    "lookup_method": None,
                    "lookup_word": None,
                    "article_id": None,
                    "definitions": {},
                },
            }
        ]

        results = convert_to_results(lookup_data)

        assert isinstance(results, Results)
        assert len(results.results) == 1
        assert results.results[0].lookup.found is False
        assert len(results.results[0].lookup.definitions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
