import sys
sys.path.append('.')

import json
import requests as req

from storage import addSubmission
from utils   import unixTime, mUnixTime, randomSolution
import goldcfg

import logging
logger = logging.getLogger(__name__)

def mkDict(problem, seed, tag, solution):
    return {'problem': int(problem), 'seed': int(seed), 'tag': tag, 'solution': solution}

def referenceResults():
    r = req.get(goldcfg.url(), auth=('', goldcfg.token()))
    return json.loads(r.text)
