from production.golden.api import httpSubmitOwn
from production.power.utils import get_phrase_submission


def check_phrase(phrase):
    submission = get_phrase_submission(phrase)
    if submission is None:
        return False
    solution, result = submission
    ok = httpSubmitOwn('Power Phrase Verifier', result, solution,
                       reasons=['Power phrase own', 'Power phrase reference'])
    if (200, 'Thanks!') == (ok.status_code, ok.text):
        return True
    return False


print(check_phrase('blablabla'))
