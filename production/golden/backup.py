from datetime import datetime
from time import sleep
import os

while True:
    os.system('cp sshfs-db/tbd.db  /home/dork/db-backup/tbd.{}.db'.format(str(datetime.now()).replace(' ', '_')))
    sleep(600)
