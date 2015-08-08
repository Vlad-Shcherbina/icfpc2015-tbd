import sys
sys.path.append('.')

import json
import requests as req

import storage
import goldcfg
import runner
import json

import logging
logger = logging.getLogger(__name__)

# Ditto
def mkDict(problem, seed, tag, solution):
    return {'problem': int(problem), 'seed': int(seed), 'tag': tag, 'solution': solution}

# Runs a solution against reference implementation,
# stores promise to provide score in SQLite.
# Dict must be an dictionary that translates to valid JSON
# see mkDict above.
def runReference(x, k="Unknown purpose"):
    return runner.runDict(x, k)

# Ditto
def runJSONReference(x, k="Unknown purpose"):
    return runner.runDict(json.loads(x), k)

# Returns all the reference results of our team
# and stores newly fetched ones in SQLite
def storeReferenceResults():
    return runner.fetchDelayed()

# Simply gets all the reference results, doesn't do
# any IO.
def justGetReferenceResults():
    return runner.referenceResults()

# Gets results that have non-zero scores
# Provides data from several tables with columns
# 'name', 'id', 'tag', 'problem', 'solution', 'status', 'kind', 'timestamp', 'score', 'powerScore'
# Returns tuple ([column], [(value)])
def getInterestingResults(orderBy="timestamp", desc=True):
    orderClause = "ORDER BY " + orderBy
    if desc:
        orderClause += " DESC"
    return storage.getInterestingResults(orderClause)

# Gets results that have score deviation between implementations.
# Return value the same as in getInterestingResults
def getContradictingResults(orderBy="timestamp", desc=True):
    orderClause = "ORDER BY " + orderBy
    if desc:
        orderClause += " DESC"
    return storage.getContradictingResults(orderClause)
