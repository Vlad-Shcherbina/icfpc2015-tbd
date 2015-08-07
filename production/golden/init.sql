CREATE TABLE IF NOT EXISTS kinds (
    id              INTEGER         NOT NULL        PRIMARY KEY      AUTOINCREMENT
   ,name            TEXT            NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER         NOT NULL        PRIMARY KEY      AUTOINCREMENT
   ,description     TEXT            NOT NULL
   ,hash            TEXT            NOT NULL UNIQUE
   ,request         TEXT            NOT NULL
   ,status          TEXT            NOT NULL DEFAULT "In progress"
   ,kind            INTEGER         NOT NULL        REFERENCES           kinds(id)
   ,timestamp       INTEGER         NOT NULL
);

CREATE TABLE IF NOT EXISTS implementations (
    id              INTEGER         NOT NULL        PRIMARY KEY      AUTOINCREMENT
   ,name            TEXT            NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS scores (
    submission      INTEGER         NOT NULL        REFERENCES     submissions(id)
   ,implementation  INTEGER         NOT NULL        REFERENCES implementations(id)
   ,score           TEXT
);
