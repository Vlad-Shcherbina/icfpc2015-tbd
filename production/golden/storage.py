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
    with db:
        e = db.cursor()
        e.execute(q, a)
        y = f(e)
        if not y:
            return y
        else:
            return (list(map(lambda x: x[0], e.description)), y)

def valueArray(xs):
    xs1 = list(map(lambda x: str(x), xs))
    return '(' + ','.join(xs1) + ')'

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

def qResults(andClause=""):
    return """
    SELECT I.name
         , S.*
         , C.score
         , C.powerScore 
    FROM ( implementations AS I
         , submissions AS S
         , scores AS C )
    WHERE I.id = C.implementation
      AND S.id = C.submission
      %s
    """ % andClause

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
        UPDATE submissions SET status = "Done" WHERE tag = :tag
        """, x)
    )

def getInterestingResults():
    return run(qResults("AND C.score > 0"))

# I was sleepy and I gave up writing idiomatic SQL here
def getContradictingResults():
    submissions = run("""
    SELECT S.id
         , C.score
         , C.powerScore
    FROM ( submissions AS S
         , scores      AS C )
    WHERE C.submission = S.id
    """)[1]
    candidates = {}
    contradictions = []
    for (sid, score, powerScore) in submissions:
        if sid not in candidates:
            candidates[sid] = (score, powerScore)
        (invScore, invPowerScore) = candidates[sid]
        if (invScore != score) or (invPowerScore != powerScore):
            contradictions.append(sid)
    return run(qResults("AND S.id in %s" % valueArray(contradictions)))
