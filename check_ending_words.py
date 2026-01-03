"""Check all _ENDING_WORDS sets against rad_dictionary.json."""

import json
import sys
import io
from pathlib import Path

# Ensure UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from glosilo import consts

# Load the rad_dictionary
with open('F:/retavortaropy/rad_dictionary.json', encoding='utf-8') as f:
    rad_dict = json.load(f)

# Get all the _ENDING_WORDS sets
ending_word_sets = {
    'ACX_ENDING_WORDS': consts.ACX_ENDING_WORDS,
    'AD_ENDING_WORDS': consts.AD_ENDING_WORDS,
    'AJX_ENDING_WORDS': consts.AJX_ENDING_WORDS,
    'AR_ENDING_WORDS': consts.AR_ENDING_WORDS,
    'EBL_ENDING_WORDS': consts.EBL_ENDING_WORDS,
    'EC_ENDING_WORDS': consts.EC_ENDING_WORDS,
    'EG_ENDING_WORDS': consts.EG_ENDING_WORDS,
    'EJ_ENDING_WORDS': consts.EJ_ENDING_WORDS,
    'EM_ENDING_WORDS': consts.EM_ENDING_WORDS,
    'ET_ENDING_WORDS': consts.ET_ENDING_WORDS,
    'IG_ENDING_WORDS': consts.IG_ENDING_WORDS,
    'IGX_ENDING_WORDS': consts.IGX_ENDING_WORDS,
    'IL_ENDING_WORDS': consts.IL_ENDING_WORDS,
    'IND_ENDING_WORDS': consts.IND_ENDING_WORDS,
    'IST_ENDING_WORDS': consts.IST_ENDING_WORDS,
    'UJ_ENDING_WORDS': consts.UJ_ENDING_WORDS,
    'UL_ENDING_WORDS': consts.UL_ENDING_WORDS,
    'AT_ENDING_WORDS': consts.AT_ENDING_WORDS,
    'IT_ENDING_WORDS': consts.IT_ENDING_WORDS,
    'OT_ENDING_WORDS': consts.OT_ENDING_WORDS,
    'ANT_ENDING_WORDS': consts.ANT_ENDING_WORDS,
    'INT_ENDING_WORDS': consts.INT_ENDING_WORDS,
    'ONT_ENDING_WORDS': consts.ONT_ENDING_WORDS,
}

# Check each set
all_missing = {}
total_words = 0
for set_name, word_set in ending_word_sets.items():
    if not word_set:  # Skip empty sets
        continue
    total_words += len(word_set)
    missing = []
    for word in sorted(word_set):
        if word not in rad_dict:
            missing.append(word)
    if missing:
        all_missing[set_name] = missing

# Print results
if all_missing:
    print('Missing words found:')
    print('=' * 60)
    total_missing = 0
    for set_name, missing in sorted(all_missing.items()):
        print(f'\n{set_name} ({len(missing)} missing):')
        total_missing += len(missing)
        for word in missing:
            print(f'  - {word}')

    print('\n' + '=' * 60)
    print(f'Summary:')
    print(f'  Total words checked: {total_words}')
    print(f'  Total missing: {total_missing}')
    print(f'  Sets with missing words: {len(all_missing)} out of {len([s for s in ending_word_sets.values() if s])}')
else:
    print('✓ All words found in rad_dictionary.json!')
    print(f'  Total words checked: {total_words}')
