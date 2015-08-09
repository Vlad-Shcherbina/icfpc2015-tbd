from production.golden.api import httpSubmitOwn
from production.power.utils import get_phrase_submission
from production.interfaces import POWER_PHRASES
import sys
from time import sleep


class InvalidPhrase(BaseException):
    pass


def check_phrase(phrase):
    submission = get_phrase_submission(phrase)
    if submission is None:
        raise InvalidPhrase
    solution, result = submission
    ok = httpSubmitOwn('Power Phrase Verifier', result, solution,
                       reasons=['Power phrase own', 'Power phrase reference'])
    if (200, 'Thanks!') == (ok.status_code, ok.text):
        return True
    return False


def main():
    if len(sys.argv) == 1:
        print('Usage: python phrase_checker.py [file1] [file2]...')
        return
    known_phrases = set(POWER_PHRASES)
    for f in sys.argv[1:]:
        with open(f) as phrase_file:
            phrases = phrase_file.read().split("\n")
        for phrase in phrases:
            if not phrase:
                continue
            print('Checking phrase "%s"' % phrase)
            phrase = phrase.replace('-', '')
            try:
                if phrase.lower() in known_phrases:
                    print("Already known")
                    continue
                while not check_phrase(phrase):
                    sleep(1)
                print("SUCCESS")
                sleep(1) # just in case
            except InvalidPhrase:
                print("ERROR: phrase invalid")


if __name__ == "__main__":
    main()
