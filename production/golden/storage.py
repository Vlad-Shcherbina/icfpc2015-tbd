import sys
sys.path.append('.')

import sqlite3 as s
import logging

db = s.connect('tbd.db')
logger = logging.getLogger(__name__)

def one(q, a=()):
  return run(q, a, lambda x: x.fetchone())

def run(q, a=(), f=(lambda x: x.fetchall())):
    global db
    global logger
    logger.info("<Query>\n%s\nwith\n%s" % (q, a))
    with db:
        e = db.cursor()
        e.execute(q, a)
        y = f(e)
        logger.info("=> %s\n</Query>" % y)
        return y

def addSubmissionOld(submission, tag, description, kind, timestamp):
    return "???"

def addResult(submissionId, implementationId, score):
    return "???"

def ensureKind(x):
    return run("""
    INSERT OR IGNORE INTO kinds (name) VALUES (?)
    """, (x,)) 

def ensureImplementation(x):
    return run("""
    INSERT OR IGNORE INTO implementations (name) VALUES (?)
    """, (x,)) 

def qSubmission(insertMode=""):
    return """
    INSERT %s INTO submissions (tag, problem, solution, status, kind, timestamp)
    SELECT :tag                                AS tag
         , :problemId                          AS problem
         , :solution                           AS solution
         , (SELECT "In progress"               AS status)
         , K.id                                AS kind
         , (SELECT strftime('%%s', 'now')       AS timestamp)
    FROM ( kinds AS K )
    WHERE K.name = :kind
    """ % insertMode

def ensureSubmission(x, kind):
    ensureKind(kind)
    x['kind'] = kind
    return run(qSubmission("OR REPLACE"), x)

def addSubmission(x, kind):
    ensureKind(kind)
    x['kind'] = kind
    return run(qSubmission(), x)

def storeResultMaybe(x, implementation):
    ensureImplementation(implementation)
    ensureSubmission(x, "Old one")
    x['implementation'] = implementation
    return (
        run("""
        INSERT OR REPLACE INTO scores (submission, implementation, score, powerScore)
        SELECT S.id                 AS submission
             , I.id                 AS implementation
             , :score               AS score
             , :powerScore          AS powerScore
        FROM ( submissions     AS S
             , implementations AS I )
        WHERE S.tag   = :tag
          AND I.name  = :implementation
        """, x),
        run("""
        UPDATE submissions AS S SET status = "Done" WHERE S.tag = :tag
        """, x)
    )
