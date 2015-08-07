mv tbd.db{,.$(git log -n 1 --pretty=format:"%H")}
sqlite3 tbd.db < init.sql
