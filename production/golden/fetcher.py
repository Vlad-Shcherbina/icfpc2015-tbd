# Fetches new results every minute.

from time import sleep
from datetime import datetime
import logging
from production.golden.api import storeReferenceResults

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fetcher')

def main():
    while True:
        try:
            logger.info('{} | Fetching results...'.format(datetime.now()))
            storeReferenceResults()
            logger.info('{} | Results fetched successfully'.format(datetime.now()))
        except BaseException as e:
            logger.error('{} | An exception occured: {}'.format(datetime.now(), e))
        sleep(60)

if __name__ == "__main__":
    main()
