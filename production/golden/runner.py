import sys
sys.path.append('.')

import json
import requests as req

from storage import addSubmission, addResult
from utils   import unixTime, mUnixTime, randomSolution
import goldcfg

import logging
logger = logging.getLogger(__name__)

#   sampleJSON :: StringJSON
def sampleJSON(t, s):
    return '[{"problemId": 0, "seed": 0, "tag": "%s", "solution": "%s"}]' % (t, s)

#   sampleDict :: Int -> Int -> Tag -> Solution -> SubmissionDict
def sampleDict(problem, seed, tag, solution):
    return {'problem': problem, 'seed': seed, 'tag': tag, 'solution': solution}

#   sampleDict0 :: SubmissionDict
def sampleDict0():
    return sampleDict(0, 0, mUnixTime(), randomSolution())

#   runJSON :: SubmissionJSON -> Tag -> Description -> Kind -> SQL ()
def runJSON(s, t, d, k):
    assert(run(s))
    addSubmissionOld(s, t, d, k, unixTime())

#   runDict :: SubmissionDict -> Kind -> SQL ()
def runDict(x, k):
    assert(run(json.dumps([x])))
    addSubmission(x, k)

#   run :: SubmissionJSON -> HTTPRequest
def run(s):
    hdr = {'content-type': 'application/json'}
    r   = req.post(goldcfg.url(), auth=('', goldcfg.token()), data=s, headers=hdr)
    return r.text == 'created'

#   getReferenceResults :: () -> SQL StringJSON
def referenceResults():
    r = req.get(goldcfg.url(), auth=('', goldcfg.token()))
    j = json.loads(r.text)
    for x in j:
        logger.info(x)

#   main :: () -> IO ()
def main():
    global logger
    if False:
        for i in range(10):
            assert(run(sampleJSON(mUnixTime(), randomSolution())))
    addSubmission(sampleDict0(), 'Phony')
    referenceResults()

if __name__ == '__main__':
    main()
