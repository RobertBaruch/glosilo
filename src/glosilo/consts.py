"""Constants for the Glosilo project."""

WORDFILE = "EO 15000 Tekstaro filtered with ESPDIC with English translation.txt"
WORDFILE_ADDITIONS = "additions.txt"
DIFFICULT_WORDLIST_FILE = "difficult.txt"
NAMELIST_FILE = "names.txt"

PUNCTUATION_REGEX = "([!?,.:;'“”—()" + '"' + "])"

# When you add a suffix here, you have to also find all words that end in that suffix
# but don't actually have that suffix (e.g. "fari" doesn't have the suffix "ar").
# See CORE_IMMUNE_WORDS below.
SUFFIXES: dict[str, str] = {
    "aĉ": "AWF",
    "ad": "CONT",
    "aĵ": "OBJ",
    "ar": "GRP",
    "ebl": "ABLE",
    "ec": "QUAL",
    "eg": "BIG",
    "ej": "PLC",
    "em": "TEND",
    "et": "DIM",
    "ig": "CAUS",
    "iĝ": "BECM",
    "il": "TOOL",
    "ind": "MRT",
    "ist": "IST",
    "uj": "BOX",
    "ul": "PERS",
    "it": "PST.PPRT",
    "int": "PST.APRT",
    "at": "PRS.PPRT",
    "ant": "PRS.APRT",
    "ot": "FUT.PPRT",
    "ont": "FUT.APRT",
}
# When you add a prefix here, you have to also find all words that start with that
# prefix but don't actually have that prefix (e.g. "disciplini" doesn't have the prefix
# "dis"). See CORE_IMMUNE_WORDS below.
PREFIXES: dict[str, str] = {
    "dis": "DIS",
    "ek": "EK",
    "mal": "OPP",
    "ne": "NOT",
}

# Suffixes which are normally applied to verbs.
VERB_SUFFIXES: set[str] = {
    "it",
    "int",
    "at",
    "ant",
    "ot",
    "ont",
    "il",
    "ig",
    "iĝ",
    "em",
    "ad",
    "ebl",
    "ind",
}

ENDING_ALTERNATIVES: dict[str, list[str]] = {
    "a": ["o", "e", "i"],
    "o": ["a", "e", "i"],
    "e": ["i", "o", "a"],
    "i": ["o", "a", "e"],
}


INTERJECTIONS: set[str] = {
    "aĉ",
    "adiaŭ",
    "ah",
    "aha",
    "aĥ",
    "aj",
    "amen",
    "ba",
    "be",
    "bis",
    "boj",
    "ĉaŭ",
    "fek",
    "fi",
    "fik",
    "fikfek",
    "ha",
    "halo",
    "haĉum",
    "haha",
    "he",
    "hej",
    "help",
    "hik",
    "hm",
    "ho",
    "ve",
    "hola",
    "hu",
    "hura",
    "ĥaĥa",
    "jen",
    "klik",
    "kvivit",
    "miaŭ",
    "mjaŭ",
    "muu",
    "nu",
    "oho",
    "oj",
    "okej",
    "pa",
    "paf",
    "pru",
    "sal",
    "ŝŝ",
    "ups",
    "ŭa",
    "ŭaŭ",
}

ARTICLES: set[str] = {"la"}

PREPOSITIONS: set[str] = {
    "al",
    "anstataŭ",
    "antaŭ",
    "apud",
    "ĉe",
    "ĉirkaŭ",
    "da",
    "de",
    "dum",
    "ekde",
    "ekster",
    "eksteren",
    "el",
    "en",
    "for",
    "ĝis",
    "inter",
    "kontraŭ",
    "krom",
    "kun",
    "laŭ",
    "malgraŭ",
    "ol",
    "per",
    "plus",
    "po",
    "por",
    "post",
    "preter",
    "pri",
    "pro",
    "sen",
    "sub",
    "super",
    "sur",
    "tra",
    "trans",
}

NUMBERS: set[str] = {
    "nul",
    "unu",
    "du",
    "tri",
    "kvar",
    "kvin",
    "ses",
    "sep",
    "ok",
    "naŭ",
    "dek",
    "cent",
    "mil",
}

CONJUNCTIONS: set[str] = {
    "aŭ",
    "ĉar",
    "do",
    "kaj",
    "ke",
    "nek",
    "sed",
    "tamen",
}

AU_ADVERBS: set[str] = {
    "almenaŭ",
    "ambaŭ",
    "ankaŭ",
    "ankoraŭ",
    "apenaŭ",
    "baldaŭ",
    "ĉirkaŭ",
    "hieraŭ",
    "hodiaŭ",
    "kvazaŭ",
    "morgaŭ",
    "preskaŭ",
}

ADVERBS: set[str] = {
    "for",
    "jam",
    "ĵus",
    "mem",
    "nun",
    "nur",
    "plej",
    "pli",
    "plu",
    "tre",
    "tro",
    "tuj",
} | AU_ADVERBS

CORRELATIVE_PARTICLES: set[str] = {
    "ĉi",
    "ajn",
}

CORRELATIVES: set[str] = {
    "kiu",
    "tiu",
    "iu",
    "ĉiu",
    "neniu",
    "kio",
    "tio",
    "io",
    "ĉio",
    "nenio",
    "kiom",
    "tiom",
    "iom",
    "ĉiom",
    "neniom",
    "kiel",
    "tiel",
    "iel",
    "ĉiel",
    "neniel",
    "kiam",
    "tiam",
    "iam",
    "ĉiam",
    "neniam",
    "kie",
    "tie",
    "ie",
    "ĉie",
    "nenie",
    "kia",
    "tia",
    "ia",
    "ĉia",
    "nenia",
    "kial",
    "tial",
    "ial",
    "ĉial",
    "nenial",
    "kies",
    "ties",
    "ies",
    "ĉies",
    "nenies",
}

PRONOUNS: set[str] = {
    "mi",
    "vi",
    "li",
    "ŝi",
    "ĝi",
    "ni",
    "ili",
    "oni",
    "si",
    "ri",
}

# "Little words". These don't conform to the general orthography of Esperanto
# words. They are not verbs, nouns, adjectives, or adverbs formed from roots.
VORTETOJ: set[str] = (
    INTERJECTIONS
    | PREPOSITIONS
    | CONJUNCTIONS
    | NUMBERS
    | ADVERBS
    | CORRELATIVE_PARTICLES
    | CORRELATIVES
    | ARTICLES
    | PRONOUNS
)

# Words which look like they end in a plural or accusative ending, but don't.
STRIP_PLURAL_ACC_IMMUNE_WORDS: set[str] = {
    w for w in VORTETOJ if w.endswith(("n", "j"))
}

# Words which look like they end in a standard ending, but don't.
CORE_IMMUNE_WORDS: set[str] = {
    w for w in VORTETOJ if w.endswith(("a", "e", "i", "o", "u", "as", "is", "os", "us"))
}

# Any word which, when stripped of prefixes and suffixes, leave behind these cores,
# should be considered a core word and not stripped any further.
#
# Some of this was gleaned from reta-vortaro.de, and a lot from PIV.
# Some were from just running the glosser and finding incorrect glosses.
#
# I couldn't think of a reasonable algorithm that would detect these conditions.
#
# "faro" gets cored to "f+ar+o", which would be "a group of f's". But "faro" is
# actually a word, so why not far+o? I think an Esperantist would just say "aro de foj"
# rather than "faro".
#
# So we'd need access to a dictionary that only lists the core words, not all
# possible words. So a dictionary that lists "faranto" would fail to core this to
# "far+ant+o", because our algorithm would treat "faranto" as a core word. Even if we
# searched for words by getting rid of affixes one by one, we'd get to "faro" and then
# "fo" which we know to be incorrect.
#
# The ultimate problem is that we need a dictionary that shows the root of each word.
# So "faranto" and "faro" would have a root of "far". Wiktionary takes a stab at
# this: the definition for faranto contains the formula {{eo-form of|far|anto}},
# but the definition for faro contains no such formula. It does have something that
# could be useful in the etymology section:
# {{af|eo|fari|t1=to do|-o|pos2=nominal suffix}}
#
# In any case, we're stuck manually handling these situations.
ACX_ENDING_WORDS: set[str] = {"taĉ"}
AD_ENDING_WORDS: set[str] = {"iomgrad", "kanad", "nead"}
AJX_ENDING_WORDS: set[str] = {"laĵ"}
AR_ENDING_WORDS: set[str] = {
    "artefar",
    "bonfar",
    "refar",
    "registrar",
    "restar",
    "studjar",
    "urbregistar",
}
EBL_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
EC_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
EG_ENDING_WORDS: set[str] = {"laŭtleg", "releg", "voĉleg"}
EJ_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
EM_ENDING_WORDS: set[str] = {"piedprem"}
ET_ENDING_WORDS: set[str] = {"almozpet", "disket", "pardonpet"}
IG_ENDING_WORDS: set[str] = {"eksig", "korlig"}
IGX_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
IL_ENDING_WORDS: set[str] = {"jarmil", "milmil", "rebril", "trembril", "ŝil"}
IND_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
IST_ENDING_WORDS: set[str] = {"eksist", "krist", "kuneksist"}
UJ_ENDING_WORDS: set[str] = set()  # All words in rad_dictionary
UL_ENDING_WORDS: set[str] = {
    "alkohol-brul",
    "bluokul",
    "bunsen-brul",
    "celtabul",
    "duoninsul",
    "ekbrul",
    "friul",
    "kvarangul",
    "memortabul",
    "rektangul",
    "respegul",
    "sangomakul",
    "sanregul",
    "stratangul",
    "triangul",
    "ŝaktabul",
}
AT_ENDING_WORDS: set[str] = {
    "amrilat",
    "animstat",
    "bofrat",
    "bonstat",
    "gefrat",
    "labormerkat",
    "limdat",
    "manplat",
    "membroŝtat",
    "mensostat",
    "mortbat",
    "naskiĝdat",
    "neadekvat",
    "pactraktat",
    "piedbat",
    "plenumkomitat",
    "prieksperimentat",
    "rebat",
    "sakstrat",
    "sanstat",
    "senŝpat",
    "sortobat",
}
IT_ENDING_WORDS: set[str] = {
    "efrit",
    "hobit",
    "kreit",
    "krucmilit",
    "mondmilit",
    "tradicio-lig",
    "ĉefdelegit",
}
OT_ENDING_WORDS: set[str] = {"florpot", "piednot"}
ANT_ENDING_WORDS: set[str] = {
    "adoleskant",
    "eksprezidant",
    "eldonkvant",
    "grimpoplant",
    "luigant",
    "popolkant",
    "vicprezidant",
    "ĉefleŭtenant",
}
INT_ENDING_WORDS: set[str] = {"montopint", "piedpint"}
ONT_ENDING_WORDS: set[str] = {"bankkont", "energifont", "glacimont", "tont"}
DIS_STARTING_WORDS: set[str] = {
    "disec",
    "diserv",
    "disking",
    "diskodorm",
    "diskturn",
    "diskutrond",
    "dispel",
}
EK_STARTING_WORDS: set[str] = {
    "eklez",
    "eksklusiv",
    "eksmod",
    "ekspanc",
    "ekspedic",
    "eksplicit",
    "ekspozic",
    "eksprezident",
    "eksterland",
    "eksternorm",
    "eksterordinar",
    "eksterter",
    "ekstradic",
    "ekstremdekstr",
    "ekvador",
}
MAL_STARTING_WORDS: set[str] = set()  # All words in rad_dictionary
NE_STARTING_WORDS: set[str] = {"nederland", "nenio"}
FAKEOUT_WORDS: set[str] = {"ĉiela", "ĉielo"}

CORE_IMMUNE_CORES: set[str] = (
     ACX_ENDING_WORDS
    | AD_ENDING_WORDS
    | AJX_ENDING_WORDS
    | AR_ENDING_WORDS
    | EBL_ENDING_WORDS
    | EC_ENDING_WORDS
    | EG_ENDING_WORDS
    | EJ_ENDING_WORDS
    | EM_ENDING_WORDS
    | ET_ENDING_WORDS
    | IG_ENDING_WORDS
    | IGX_ENDING_WORDS
    | IL_ENDING_WORDS
    | IND_ENDING_WORDS
    | IST_ENDING_WORDS
    | UJ_ENDING_WORDS
    | UL_ENDING_WORDS
    | AT_ENDING_WORDS
    | IT_ENDING_WORDS
    | OT_ENDING_WORDS
    | ANT_ENDING_WORDS
    | INT_ENDING_WORDS
    | ONT_ENDING_WORDS
    | DIS_STARTING_WORDS
    | EK_STARTING_WORDS
    | NE_STARTING_WORDS
    | MAL_STARTING_WORDS
    | FAKEOUT_WORDS
)

# Words which should not be glossed. Generally in the top 100 most common words in
# Esperanto.
COMMON_WORDS: set[str] = {
    # Articles, conjunctions, subphrase introducers, adverbs
    "la",
    "kaj",
    "ne",
    "ke",
    "por",
    "sed",
    "kun",
    "pli",
    "plej",
    "aŭ",
    "nur",
    "ankaŭ",
    "ĉu",
    "se",
    "ĉar",
    "dum",
    "eĉ",
    "jam",
    "nun",
    "tre",
    "tamen",
    "ja",
    "do",
    "ĝis",
    "mem",
    "ankoraŭ",
    "ajn",
    # Prepositions
    "de",
    "en",
    "al",
    "pri",
    "el",
    "sur",
    "per",
    "da",
    "pro",
    "post",
    "ol",
    "ĉe",
    "inter",
    "laŭ",
    "antaŭ",
    "kontraŭ",
    "je",
    # Derivations from prepositions
    #"posta",
    #"poste",
    #"antaŭa",
    #"antaŭe",
    #"kontraŭa",
    #"kontraŭe",
    # Pronouns
    "mi",
    "mia",
    "li",
    "lia",
    "ili",
    "ilia",
    "vi",
    "via",
    "ĝi",
    "ĝia",
    "si",
    "sia",
    "ŝi",
    "oni",
    "ni",
    "nia",
    # Table words
    "kiu",
    "tiu",
    "iu",
    "ĉiu",
    "neniu",
    "kio",
    "tio",
    "io",
    "ĉio",
    "nenio",
    "kiom",
    "tiom",
    "iom",
    "ĉiom",
    "neniom",
    "kiel",
    "tiel",
    "iel",
    "ĉiel",
    "neniel",
    "kiam",
    "tiam",
    "iam",
    "ĉiam",
    "neniam",
    "kie",
    "tie",
    "ie",
    "ĉie",
    "nenie",
    "kia",
    "tia",
    "ia",
    "ĉia",
    "nenia",
    "kial",
    "tial",
    "ial",
    "ĉial",
    "nenial",
    "kies",
    "ties",
    "ies",
    "ĉies",
    "nenies",
    # Other (literally)
    "alio",
    "alia",
    # This
    "ĉi",
    # Nouns and adjectives
    "jaro",
    "granda",
    "homo",
    "lingvo",
    "lando",
    "esperanto",
    "nova",
    "multa",
    "tute",
    "kelka",
    "tuta",
    "internacia",
    # Verbs
    "esti",
    "veni",
    "okazi",
    "scii",
    "vidi",
    "voli",
    "devi",
    "havi",
    "povi",
    "diri",
    "fari",
    # Cardinals
    "unu",
    "du",
    "tri",
    "kvar",
    "kvin",
    "ses",
    "sep",
    "ok",
    "naŭ",
    "dek",
    "cent",
    "mil",
    # Ordinals
    "unua",
    "dua",
    "tria",
    "kvara",
    "kvina",
    "sesa",
    "sepa",
    "oka",
    "naŭa",
    "deka",
    "centa",
    "mila",
    # Named numbers
    "unuo",
    "duo",
    "trio",
    "kvaro",
    "kvino",
    "seso",
    "sepo",
    "oko",
    "naŭo",
    "deko",
    "cento",
    "milo",
}
