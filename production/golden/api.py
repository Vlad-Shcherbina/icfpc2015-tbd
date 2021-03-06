import json
import requests as req

from production.golden import storage
from production.golden import goldcfg
from production.golden import runner
from production.golden import utils

import logging
logger = logging.getLogger(__name__)

# Ditto
def mkDict(problem, seed, tag, solution):
    return {'problem': int(problem), 'seed': int(seed), 'tag': tag, 'solution': solution}

# Stores locally computed score on central server
# without submitting it to organizers 
def httpOwn(user, result):
    return req.get(goldcfg.us() + '/own/%s' % json.dumps({ 'user':      user
                                                         , 'result':    result
                                                         , 'solution':  solution }))

# Submits solution to organizers 
# without storing it on central server.
def httpSubmit(user, solution):
    return req.get(goldcfg.us() + '/snd/%s' % json.dumps({ 'user':     user
                                                         , 'solution': solution }))

# Submits solution to organizers and stores it on central server.
def httpSubmitOwn(user, result, solution, reasons=None):
    payload = { 'user': user, 'result': result, 'solution': solution }
    if reasons:
        payload['reasons'] = reasons
    return req.get(goldcfg.us() + '/submit/%s' % json.dumps(payload))

# Runs a solution against reference implementation,
# stores promise to provide score in SQLite.
# Dict must be an dictionary that translates to valid JSON
# see mkDict above.
def runReference(x, k="Unknown purpose"):
    if isinstance(x, dict):
        return runner.runDict(x, k)
    return runner.runDicts(x, k)

# Ditto
def runReferenceJSON(x, k="Unknown purpose"):
    return runReference(json.loads(x), k)

# Ditto
def justRunReference(x, k="Unknown purpose"):
    if isinstance(x, dict):
        return runner.runDict(x, k, withSQL=False)
    return runner.runDicts(x, k, withSQL=False)

# Ditto
def justRunReferenceJSON(x, k="Unknown purpose"):
    return justRunReference(json.loads(x), k)

# Stores result, computed by one of our own implementation.
# For submission and result is similar to reference API except
# it doesn't require result to contain meta-fields such as
# ``team``.
# Just to re-iterate, ``submission`` MUST have the following fields:
#  + tag
#  + problemId
#  + seed
#  + solution
#
# result MUST have the following fields:
#  + score
#  + powerScore
#  + tag (matching the one in submission)
#  + problemId
#  + seed
#  + solution
#
# You SHOULD provide ``kind`` argument which will articulate intention
# of storing a particular result.
# For instance, @graphite will use "Power phrases" as kind.
#
# NB! Here result and submission aren't lists of dicts, but just one dicts!
def storeOwnResult(implementationName, result, submission, kind="Unknown purpose"):
    storage.ensureSubmission(submission, kind)
    return storage.storeResultMaybe(result, implementationName)

# Ditto
def storeOwnResultJSON(implementationName, result, submission, kind="Unknown purpose"):
    return storeOwnResult(implementationName, json.loads(result), json.loads(submission), kind)

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

def getSubmission(tag_id):
    return storage.run("SELECT seed, tag, problem, solution FROM submissions WHERE tag = :tag",
        {'tag': tag_id})
