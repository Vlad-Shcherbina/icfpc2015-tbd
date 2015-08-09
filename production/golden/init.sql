CREATE TABLE IF NOT EXISTS kinds (
    id              INTEGER         NOT NULL        PRIMARY KEY      AUTOINCREMENT
   ,name            TEXT            NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER         NOT NULL        PRIMARY KEY      AUTOINCREMENT
   ,tag             TEXT            NOT NULL UNIQUE
   ,problem         INTEGER         NOT NULL
   ,seed            INTEGER         NOT NULL
   ,solution        TEXT            NOT NULL
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
   ,powerScore      TEXT
   ,PRIMARY KEY (submission, implementation)
);

CREATE TABLE IF NOT EXISTS power_phrases (
    id              INTEGER         NOT NULL        PRIMARY KEY       AUTOINCREMENT
   ,phrase          TEXT            NOT NULL
   ,submission      INTEGER                         REFERENCES     submissions(id)
   ,status          TEXT            NOT NULL DEFAULT "Not verified"
);

CREATE TABLE IF NOT EXISTS last_seen (
    fmtTime         TEXT            NOT NULL DEFAULT "2015-08-08T20:13:03.146Z"
);

INSERT INTO last_seen (fmtTime) VALUES ("2015-08-08T20:13:03.146Z");
