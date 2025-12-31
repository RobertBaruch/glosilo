"""Natural language processing utilities.

This module now imports stemming functionality from the eostem module.
"""

from glosilo import eostem

# Re-export all stemming functions for backwards compatibility
maybe_strip_plural_acc_ending = eostem.maybe_strip_plural_acc_ending
replace_verb_ending = eostem.replace_verb_ending
core_word = eostem.core_word
