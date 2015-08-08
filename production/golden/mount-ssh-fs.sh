DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
mkdir $DIR/sshfs-db
sshfs dork@memorici.de:/home/dork/icfpc2015-tbd/production/golden/sshfs-db $DIR/sshfs-db -p 21984 -o IdentityFile=~/.ssh/id_rsa
