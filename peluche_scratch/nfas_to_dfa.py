# NFAtoDFA.py :
# This is Python code for representing finite automata, DFAs and NFAs, 
# and for converting from an NFA into a DFA.  
#
# Ben Reichardt, 1/17/2011
#
import functools

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
        # comments: 
        #       * python dictionary keys must be immutable
        #       * it is a KeyError to extract an entry using a non-existent key

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

def convertNFAtoDFA(N):
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

def add_catch_all(d, alphabet):
        """
        for each node, if a transition from the alphabet is missing
        it is added to point to start
        """
        for vals in d.values():
                for letter in alphabet:
                        if letter not in vals:
                                vals[letter] = set(["start"])

def nfas_to_dfa(list_nfa, end_states, alphabet, start_state='start'):
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
        add_catch_all(nfa, alphabet)
        N = NFA(nfa, start_state, end_states)
        D = convertNFAtoDFA(N)
        return D.get_delta()

def create_final_state_lookup(dfa, final_states):
        """
        create a lookup table of final-states (states where a power phrase has been matched)
        each state in the DFA is represented as a frozenset (to be hashable)
        the lookup table returned is of type:
          frozenset -> [power_phrase1, ...]
        """
        lookup = {}
        for frozenset_states in dfa.keys():
                for state in final_states:
                        if state in frozenset_states:
                                lookup.setdefault(frozenset_states, []).append(state)
        return lookup

def example():
       # node format: <power phrase>_<index starting at 1>_<letter>
        abcabcx = {
                'abcabcx_1_a': {'b': set(['abcabcx_2_b']), 'a': set(['abcabcx_1_a'])},
                'abcabcx_2_b': {'c': set(['abcabcx_3_c']), 'a': set(['abcabcx_1_a'])},
                'abcabcx_3_c': {'a': set(['abcabcx_4_a'])},
                'abcabcx_4_a': {'b': set(['abcabcx_5_b']), },
                'abcabcx_5_b': {'c': set(['abcabcx_6_c']), 'a': set(['abcabcx_1_a'])},
                'abcabcx_6_c': {'x': set(['abcabcx_7_x']), 'a': set(['abcabcx_4_a'])},
                'abcabcx_7_x': {'a': set(['abcabcx_1_a'])} # here we score
                }

        abx = {
                'abx_1_a': {'b': set(['abx_2_b']), 'a': set(['abx_1_a'])},
                'abx_2_b': {'x': set(['abx_3_x']), 'a': set(['abx_1_a'])},
                'abx_3_x': {'a': set(['abx_1_a'])} # here we score
                }

        start_nfa = {
                'start': {'a': set(['abcabcx_1_a', 'abx_1_a'])}
                }

        dfa = nfas_to_dfa([abcabcx, abx, start_nfa],  # all NFAs to join, including the start one
                          ['abcabcx_7_x', 'abx_3_x'], # all the end states
                          "abcdx"                     # the alphabet
                          )
        import pprint
        pp = pprint.PrettyPrinter(depth=6).pprint
        pp(dfa)

        lookup = create_final_state_lookup(dfa,
                                           ['abcabcx_7_x', 'abx_3_x'], # all the end states
                                           )
        pp(lookup)

if __name__ == '__main__':
        example()
