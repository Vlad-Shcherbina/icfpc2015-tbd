# GenTM is a generic Turing machine implementation that provides high-level
# versatile way to express the flavour of most of the Turing machine variants.
#
# In this note we use pseudocode that is suspiciously similar to Haskell, to
# explain the ideas behind stuff. Names mentioned here don't (yet) correspond to
# the names used in the real implementaiton.
# 
# Design philosophy — 
# 
# GenTM is a type that has the following things inside:
#  + [Tape] — an array of tapes, containing some number of carets and some
#    symbols. Both symbols and carets are probabilistic (see below)
#  + CompTransition — a composition of transition functions. It is very
#    high-level, and users of GenTM should put the most of effort in
#    implementing this composition. GenTM provides helpers to aid in doing that.
#    Type signature of CompTransition is Dist GenTM -> Dist GenTM.
#  + CompHalt — a composition of functions that determine if Turing machine is
#    in halting state.
#    Type signature of this function is Dist (GenTM, Bool) -> Dist (GenTM, Bool)
#  + [Letter] — ditto
#  + Epsilon  — ditto
#
# Tape is a type that has the following things inside:
#  + [Dist Letter] — array of probabilistic letters
#  + [Dist Caret]  — array of probabilistic carets pointing to some positions
#
# Dist is a type that represents probabilistic distribution.
# Think Dist a :: [(Float, a)], but with assertions that
#  + All probabilities are non-negative:
#    ``dist == filter ((>= 0) . fst) dist``
#  + Probabilities add up to 1.0
#    ``1.0  == foldl (flip $ (+) . fst) 0 dist``
