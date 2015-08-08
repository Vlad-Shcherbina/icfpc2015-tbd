import sys
import unittest
import logging

logger = logging.getLogger(__name__)

import re
import nose
from nose.tools import eq_
import hypothesis
import hypothesis.strategies as st
from collections import Counter

from production.dfa import FullDfa
from production import testing_utils

def count_overlapping_occurences(word, sentence):
    return len(re.findall(r'(?=(%s))' % re.escape(word), sentence))

def count_for_all(words, sentence):
    return {word : count_overlapping_occurences(word, sentence) for word in words
            if count_overlapping_occurences(word, sentence)}

class DfaTests(unittest.TestCase):

    @hypothesis.given(
        phrase=st.text(alphabet="abcd", min_size=1, max_size=10),
        moves=st.text(alphabet="abcd", max_size=1000))
    def dfa_with_single_phrase_test(self, phrase, moves):
        full_dfa = FullDfa([phrase], "abcd")
        for move in moves:
            full_dfa.add_letter(move)
        scores = full_dfa.get_scores()

        eq_(scores[phrase], count_overlapping_occurences(phrase, moves))

    @hypothesis.given(
        phrases=st.lists(st.text(alphabet="abcd", min_size=1, max_size=10), min_size=1, max_size=18),
        moves=st.text(alphabet="abcd", max_size=200))
    def dfa_with_several_phrase_test(self, phrases, moves):
        # no repeated phrases of power
        phrases = set(phrases)

        full_dfa = FullDfa(phrases, "abcd")
        for move in moves:
            full_dfa.add_letter(move)
        scores = full_dfa.get_scores()

        eq_(scores, count_for_all(phrases, moves))


if __name__ == '__main__':
    hypothesis.Settings.default.max_examples = 1000
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
