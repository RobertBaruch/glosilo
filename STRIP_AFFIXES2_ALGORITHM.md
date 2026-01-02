# _strip_affixes2 Algorithm

## Overview

The `_strip_affixes2` function implements an alternative algorithm for decomposing Esperanto words into their morphological components (prefixes, core/root, and suffixes).

## Algorithm Steps

### 1. Strip One Preposition (Optional)
Attempt to strip exactly one preposition from the beginning of the word.
- Check prepositions in order of length (longest first)
- If a match is found, remove it and continue with the remainder
- Store the preposition separately

### 2. Strip All Prefixes
Greedily strip all standard prefixes from the remainder.
- Check prefixes from `consts.PREFIXES`
- Strip as many as possible from left to right
- Store them in order

### 3. Strip All Suffixes
Greedily strip all suffixes from what's left.
- Check suffixes from `consts.SUFFIXES`
- Strip as many as possible from right to left
- Store them in order

### 4. Generate All Reconstruction Combinations
After maximum stripping, we have:
- A minimal core (after stripping everything possible)
- A list of stripped prefixes
- A list of stripped suffixes

Now iterate through all combinations of "unstripping" (adding back) prefixes and suffixes to the core.

For each combination:
- Take the last N prefixes and add them back to the front of the core
- Take the first M suffixes and add them back to the end of the core
- This creates a "reconstructed root"

### 5. Validate Each Reconstructed Root
For each reconstructed root, check if it exists in:
- `rad_dictionary` (the root dictionary)
- `CORE_IMMUNE_CORES` (special exception words)

If valid, store this configuration along with:
- The prefixes that were stripped (not added back to core)
- The reconstructed root
- The suffixes that were stripped (not added back to core)
- The length of the reconstructed root

### 6. Choose the Longest Valid Root
From all valid configurations, select the one with:
- Primary criterion: Longest reconstructed root
- Secondary criterion: Most affixes stripped (to prefer decomposition)

## Example Walkthrough

### Example: "ekvilibrigit"

**Step 1:** Try prepositions
- No preposition matches at the start

**Step 2:** Strip prefixes
- "ek" matches → remainder: "vilibrigit"
- No more prefixes match
- Stripped prefixes: ["ek"]

**Step 3:** Strip suffixes
- "it" matches → remainder: "vilibrig"
- "ig" matches → remainder: "vilibr"
- No more suffixes match
- Stripped suffixes: ["ig", "it"]
- Minimal core: "vilibr"

**Step 4-5:** Try combinations

| Prefixes in core | Suffixes in core | Reconstructed root | In rad_dict? |
|------------------|------------------|-------------------|--------------|
| 0                | 0                | vilibr            | No           |
| 0                | 1                | vilibrig          | No           |
| 0                | 2                | vilibrigit        | No           |
| 1                | 0                | ekvilibr          | **Yes** ✓    |
| 1                | 1                | ekvilibrig        | No           |
| 1                | 2                | ekvilibrigit      | No           |

**Step 6:** Choose longest
- Best match: "ekvilibr" (length 8)
- Result: core="ekvilibr", prefixes=[], suffixes=["ig", "it"]

## Key Features

1. **Exhaustive Search**: Tries all possible decompositions
2. **Dictionary Validation**: Only accepts roots that exist in rad_dictionary
3. **Longest Match Preference**: Always chooses the longest valid root (with penalty scoring)
4. **Preposition Handling**: Treats prepositions specially (only one at most)
5. **Special Case for "ne"**: The word "ne" is both a root and a prefix. It's preferred as a root only when:
   - There are no suffixes, OR
   - The only suffix is "ig" or "ul"
   - Examples: "neig" → core="ne", suffixes=["ig"] ✓
   - Examples: "neul" → core="ne", suffixes=["ul"] ✓
   - Examples: "neebl" → prefixes=["ne"], core="ebl" ✓
   - Examples: "neind" → prefixes=["ne"], core="ind" ✓
6. **Deterministic**: Always produces the same result for the same input

## Comparison with Original Algorithm

The original `_strip_affixes` uses a more complex nested loop approach that tries different numbers of prefixes and suffixes in parallel. Both algorithms produce the same results on all test cases, but `_strip_affixes2` has a clearer, more linear structure:

1. Strip everything first (greedy)
2. Try adding things back (systematic)
3. Pick the best result (simple criterion)

## Test Results

All 15 unit tests pass, including:
- Simple words with no affixes
- Words with prefixes only
- Words with suffixes only
- Words with both prefixes and suffixes
- Compound words (studjar, bonhumor)
- Complex cases (ekvilibrigit, nekomprenebl)
- Preposition prefixes (ensumig)
- Special "ne" cases (neig, neul, neebl, neind)

The algorithm handles the special case for "ne" correctly, preferring it as a root when combined with "ig" or "ul" suffixes, but as a prefix otherwise.
