mv tbd.db{,.$(git log -n 1 --pretty=format:"%H")}} 2>/dev/null
sqlite3 tbd.db < init.sql
