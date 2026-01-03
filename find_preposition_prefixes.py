"""Find words in _ENDING_WORDS sets that have preposition prefixes."""

import sys
import io
from glosilo import consts, eostem

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

rad_dict = eostem._get_rad_dictionary()

# Check each _ENDING_WORDS set
ending_word_sets = {
    'AT_ENDING_WORDS': consts.AT_ENDING_WORDS,
    'IT_ENDING_WORDS': consts.IT_ENDING_WORDS,
    'UL_ENDING_WORDS': consts.UL_ENDING_WORDS,
    'ANT_ENDING_WORDS': consts.ANT_ENDING_WORDS,
    'INT_ENDING_WORDS': consts.INT_ENDING_WORDS,
    'ONT_ENDING_WORDS': consts.ONT_ENDING_WORDS,
    'OT_ENDING_WORDS': consts.OT_ENDING_WORDS,
    'IG_ENDING_WORDS': consts.IG_ENDING_WORDS,
    'IL_ENDING_WORDS': consts.IL_ENDING_WORDS,
    'EG_ENDING_WORDS': consts.EG_ENDING_WORDS,
}

print("Words that can be removed (have preposition prefixes):")
print("=" * 70)

total_removable = 0
for set_name, word_set in ending_word_sets.items():
    removable = []
    for word in sorted(word_set):
        # Try each preposition
        for prep in sorted(consts.PREPOSITIONS, key=len, reverse=True):
            if word.startswith(prep):
                remainder = word[len(prep):]
                # Check if remainder is a valid root
                if remainder in consts.CORE_IMMUNE_CORES or remainder in rad_dict:
                    removable.append(f"{word} → {prep}+{remainder}")
                    break

    if removable:
        print(f"\n{set_name} ({len(removable)} removable):")
        for item in removable:
            print(f"  {item}")
        total_removable += len(removable)

print(f"\n{'=' * 70}")
print(f"Total removable: {total_removable}")
