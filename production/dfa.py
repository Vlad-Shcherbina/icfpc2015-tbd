import functools
from collections import defaultdict

class DFA:
    """Class that encapsulates a DFA."""
    def __init__(self, transitionFunction, initialState, finalStates):
        self.delta = transitionFunction
        self.q0 = initialState
        self.F = finalStates
    def deltaHat(self, state, inputString):
        for a in inputString:
            state = self.delta[state][a]
        return state
    def inLanguage(self, inputString):
        return self.deltaHat(self.q0, inputString) in self.F
    def get_delta(self):
        return self.delta


class NFA:
    """Class that encapsulates an NFA."""
    def __init__(self, transitionFunction, initialState, finalStates):
        self.delta = transitionFunction
        self.q0 = initialState
        self.F = set(finalStates)
    def deltaHat(self, state, inputString):
        """deltaHat is smart enough to return the empty set if no transition is defined."""
        states = set([state])
        for a in inputString:
            newStates = set([])
            for state in states:
                try:
                    newStates = newStates | self.delta[state][a]
                except KeyError: pass
                states = newStates
            return states
    def inLanguage(self, inputString):
        return len(self.deltaHat(self.q0, inputString) & self.F) > 0
    def alphabet(self):
        """Returns the NFA's input alphabet, generated on the fly."""
        Sigma = functools.reduce(lambda a,b:set(a)|set(b), [x.keys() for x in self.delta.values()])
        return Sigma
    def states(self):
        """Returns the NFA's set of states, generated on the fly."""
        Q = set([self.q0]) | set(self.delta.keys()) | functools.reduce(lambda a,b:a|b, functools.reduce(lambda a,b:a+b, [x.values() for x in self.delta.values()]))     # {q0, all states with outgoing arrows, all with incoming arrows}
        return Q

class FullDfa:

    def __init__(self, words, alphabet):
        self._results = defaultdict(int)
        transitions = [{}]
        start_transition = transitions[-1]
        end_state = []
        for word in words:
            assert word != ''
            word = word.lower()
            transitions.append({})
            transition = transitions[-1]
            end_state.append(self.print_state(word,len(word)))
            for character_index in range(1, len(word) + 1):
                for character in alphabet:
                    next_match = self.calculate_suffix_prefix(word[:character_index], character)
                    if character_index != len(word):
                        if character == word[character_index]:
                            next_match = character_index + 1
                    self.set_transition(transition, self.print_state(word, character_index), character, self.print_state(word, next_match))
            ## start transitions. Important
            for character in alphabet:
                if character == word[0]:
                    self.set_transition(start_transition, self.start_state(), character, self.print_state(word, 1))
                else:
                    self.set_transition(start_transition, self.start_state(), character, self.start_state())

        #print(transitions)
        self._dfa = self.nfas_to_dfa(transitions, end_state, alphabet)
        self._end_state_lookup = self.create_final_state_lookup(self._dfa, end_state)
        self._current_state = frozenset([self.start_state()])

    def get_dfa(self):
        return self._dfa

    def add_letter(self, c):
        self._current_state = self._dfa[self._current_state][c]
        if self._current_state in self._end_state_lookup:
            for word in self._end_state_lookup[self._current_state]:
                self._results[word] += 1

    def get_scores(self):
        return self._results

    def print_dfa(self):
        import pprint
        pp = pprint.PrettyPrinter(depth=4).pprint
        pp(self._dfa)
        pp(self._end_state_lookup)

    def convertNFAtoDFA(self,N):
        """Converts the input NFA into a DFA.
        The output DFA has a state for every *reachable* subset of states in the input NFA.
        In the worst case, there will be an exponential increase in the number of states.
        """
        q0 = frozenset([N.q0])  # frozensets are hashable, so can key the delta dictionary
        Q = set([q0])
        unprocessedQ = Q.copy() # unprocessedQ tracks states for which delta is not yet defined
        delta = {}
        F = []
        Sigma = N.alphabet()

        while len(unprocessedQ) > 0:
            qSet = unprocessedQ.pop()
            delta[qSet] = {}
            for a in Sigma:
                nextStates = functools.reduce(lambda x,y: x|y, [N.deltaHat(q,a) for q in qSet], set())
                nextStates = frozenset(nextStates)
                delta[qSet][a] = nextStates
                if not nextStates in Q:
                    Q.add(nextStates)
                    unprocessedQ.add(nextStates)
        for qSet in Q:
            if len(qSet & N.F) > 0:
                F.append(qSet)
        M = DFA(delta, q0, F)
        return M

    def add_catch_all(self, d, alphabet):
        """
        for each node, if a transition from the alphabet is missing
        it is added to point to start
        """
        for vals in d.values():
            for letter in alphabet:
                if letter not in vals:
                    vals[letter] = set(["start"])

    def nfas_to_dfa(self,list_nfa, end_states, alphabet, start_state='start'):
        """
        join all the incomplete NFAs into a single incomplete NFA,
        add the catch all that goes back to 'start' for each missing char in the alphabet
        then convert it to a DFA and return it

        suggested state format: <power phrase>_<index>_<letter>
        the NFAs should be of the form:
        match_abx = {
            'abx_1_a': {'b': set(['abx_2_b']),
                        'a': set(['abx_1_a'])},
            'abx_2_b': {'x': set(['abx_3_x']),
                        'a': set(['abx_1_a'])},
            'abx_3_x': {'a': set(['abx_1_a'])} # here we score
            }

        additionally a NFA with the 'start' node and a transitions to each other NFA
        should be provided like:
        start_nfa = {
            'start': {'a': set(['abx_1_a', 'apple_1_a'])
                      'b': set(['banana_1_b'])
                      ... }
            }
        """
        nfa = {}
        for n in list_nfa:
                nfa.update(n)
        self.add_catch_all(nfa, alphabet)
        N = NFA(nfa, start_state, end_states)
        D = self.convertNFAtoDFA(N)
        return D.get_delta()

    def create_final_state_lookup(self, dfa, final_states):
        """
        create a lookup table of final-states (states where a power phrase has been matched)
        each state in the DFA is represented as a frozenset (to be hashable)
        the lookup table returned is of type:
        frozenset -> [power_phrase1, ...]
        """
        lookup = {}
        # print(final_states)
        for frozenset_states in dfa.keys():
            for state in final_states:
                if state in frozenset_states:
                    lookup.setdefault(frozenset_states, []).append(state.split("_")[0])
        return lookup


    # states in the transition tables are of the form abx_a_1
    def print_state(self,word, position):
        if position == 0:
            return self.start_state()
        return word + "_" + str(position) + "_" + word[position - 1]

    # when construction the ininitial dfa's we need to match the longest
    # prefix that is also a suffix in case we get a wrong next character
    def calculate_suffix_prefix(self,word, next_character):
        new_word = word + next_character
        for prefix_length in range(len(new_word) - 1, -1, -1):
            offset = len(new_word) - prefix_length
            if word[0:prefix_length] == new_word[offset:len(new_word)]:
                return prefix_length
        return 0
    def get_final_state_lookup(self):
        return self._end_state_lookup
    def start_state(self):
        return "start"

    def set_transition(self,transitions, initial_state, character, second_state):
        if initial_state in transitions:
            if character in transitions[initial_state]:
                transitions[initial_state][character].add(second_state)
            else:
                transitions[initial_state][character] = set([second_state])
        else:
            transitions[initial_state] = {character : set([second_state])}

'''
if __name__ == '__main__':
    words = ["abcabcx", "abx"]
    alphabet = ['a','b','c','x']
    test_dfa = FullDfa(words, alphabet)
    test_value = "aabcabcabcxxabxabxaabx"
    # test_dfa.print_dfa()
    for letter in test_value:
        test_dfa.add_leter(letter)
    assert(len(test_dfa.get_scores()) == 4)


    words = ["aa", 'aaaa']
    alphabet = ['a','b','c','x']
    test_dfa = FullDfa(words, alphabet)
    # 14 'a's
    test_value = "aaaaaaaaaaaaaa"
    # test_dfa.print_dfa()
    for letter in test_value:
        test_dfa.add_leter(letter)
    # print(test_dfa.get_scores())
    test_dfa.print_dfa()
    assert(len(test_dfa.get_scores()) == 24)

    ##### STRESS TEST #####
    import string
    import random
    def id_generator(size=6, chars=string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))
    new_words = []
    for i in range(0,18):
        new_words.append(id_generator(50))
    alphabet = string.ascii_lowercase
    test_dfa = FullDfa(new_words, alphabet)
    #print(new_words)
    #print(alphabet)
    #test_dfa.print_dfa()
    #print(len(test_dfa.get_dfa().keys()))
'''
