import sys
sys.path.append('.')

import json
import requests as req

from storage import addSubmission, storeResultMaybe, getInterestingResults, getContradictingResults
from utils   import unixTime, mUnixTime, randomSolution
import goldcfg

import logging
logger = logging.getLogger(__name__)

#   referenceResults :: () -> Dict
def referenceResults():
    r = req.get(goldcfg.url(), auth=('', goldcfg.token()))
    return json.loads(r.text)

#   sampleJSON :: StringJSON
def sampleJSON(t, s):
    return '[{"problemId": 0, "seed": 0, "tag": "%s", "solution": "%s"}]' % (t, s)

#   sampleDict :: Int -> Int -> Tag -> Solution -> SubmissionDict
def sampleDict(problem, seed, tag, solution):
    return {'problem': problem, 'seed': seed, 'tag': tag, 'solution': solution}

#   sampleDict0 :: SubmissionDict
def sampleDict0():
    return sampleDict(0, 0, mUnixTime(), randomSolution())

#   runDict :: SubmissionDict -> Kind -> SQL ()
def runDict(x, k):
    return runDicts([x], k)

#   runDicts :: [SubmissionDict] -> Kind -< SQL ()
def runDicts(xs, k):
    assert(run(json.dumps(xs)))
    for x in xs:
        addSubmission(x, k)
    return True

#   run :: SubmissionJSON -> HTTPRequest
def run(s):
    hdr = {'content-type': 'application/json'}
    r   = req.post(goldcfg.url(), auth=('', goldcfg.token()), data=s, headers=hdr)
    return r.text == 'created'

#   fetchDelayed :: () -> SQL StringJSON
def fetchDelayed():
    y = referenceResults()
    for i in y:
        if i['score'] != None:
            storeResultMaybe(i, "reference implementation")
    return y

#   main :: () -> IO ()
def main():
    global logger
    logging.basicConfig(level=logging.INFO) 
    if False:
        for i in range(10):
            assert(run(sampleJSON(mUnixTime(), randomSolution())))
        addSubmission(sampleDict0(), 'Phony')
        for x in referenceResults():
            logger.info(x)
        logger.info(getContradictingResults())
        logger.info(getInterestingResults())
    logger.info(fetchDelayed())

if __name__ == '__main__':
    main()
