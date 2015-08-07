import sys
sys.path.append('.')

import json
import requests as req

from storage import addSubmission, addResult
from utils   import unixTime, mUnixTime, randomSolution
import goldcfg

#   sampleJSON :: StringJSON
def sampleJSON(t, s):
    return '[{"problemId": 0, "seed": 0, "tag": "%s", "solution": "%s"}]' % (t, s)

#   runJSON :: SubmissionJSON -> Description -> Kind -> SQL ()
def runJSON(s, d, k):
    addSubmission(s, d, k, unixTime())

#   run :: SubmissionJSON -> HTTPRequest
def run(s):
    hdr = {'content-type': 'application/json'}
    r   = req.post(goldcfg.url(), auth=('', goldcfg.token()), data=s, headers=hdr)
    return r.text == 'created'

#   getReferenceResults :: () -> SQL StringJSON
def referenceResults():
    r = req.get(goldcfg.url(), auth=('', goldcfg.token()))
    return r.text

#   main :: () -> IO ()
def main():
    if False:
        for i in range(10):
            assert(run(sampleJSON(mUnixTime(), randomSolution())))
    print(referenceResults())

if __name__ == '__main__':
    main()
