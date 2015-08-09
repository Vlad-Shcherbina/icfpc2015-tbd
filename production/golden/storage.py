import sqlite3 as s
import logging
import os

from production import utils

logger = logging.getLogger(__name__)

def one(q, a=()):
  return run(q, a, lambda x: x.fetchone())

def run(q, a=(), f=(lambda x: x.fetchall())):
    db = s.connect(os.path.join(utils.get_project_root(), 'production', 'golden', 'sshfs-db', 'tbd.db'))
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

def qSubmission(insertMode="", status="Not submitted"):
    return """
    INSERT %s INTO submissions (tag, problem, seed, solution, status, kind, timestamp)
    SELECT :tag                                AS tag
         , :problemId                          AS problem
         , :seed                               AS seed
         , :solution                           AS solution
         , (SELECT "%s"                        AS status)
         , K.id                                AS kind
         , (SELECT strftime('%%s', 'now')      AS timestamp)
    FROM ( kinds AS K )
    WHERE K.name = :kind
    """ % (insertMode, status)

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
    return run(qSubmission("OR IGNORE"), x)

def addSubmission(x, kind):
    ensureKind(kind)
    x['kind'] = kind
    status = run("""SELECT status FROM submissions WHERE tag = :tag""", x)
    if status and status[1][0][0] != 'In progress' and status[1][0][0] != 'Done':
        run("""UPDATE submissions SET status = "In progress" WHERE tag = :tag""", x)
        return
    return run(qSubmission("OR IGNORE", "In progress"), x)

def storeResultMaybe(x, implementation, own=True):
    ensureImplementation(implementation)
    ensureSubmission(x, "Old one")
    x['implementation'] = implementation
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
    if not own:
        run("""
            UPDATE submissions SET status = "Done" WHERE tag = :tag
        """, x)

def getInterestingResults(orderClause=""):
    return run(qResults("AND (C.score > 0 OR C.powerScore > 0)" + orderClause))

# I was sleepy and I gave up writing idiomatic SQL here
def getContradictingResults(orderClause=""):
    submissions = run("""
    SELECT S.id
         , C.score
         , C.powerScore
         , I.name
    FROM ( submissions     AS S
         , scores          AS C 
         , implementations AS I )
    WHERE C.submission = S.id AND C.implementation = I.id
    """)[1]
    candidates = {}
    contradictions = []
    for (sid, score, powerScore, implementation) in submissions:
        if implementation != 'reference implementation':
            score = score + powerScore
        if sid not in candidates:
            candidates[sid] = (score, powerScore)
        (invScore, invPowerScore) = candidates[sid]
        # powerScore is computed in a strange way in reference implementation, ignore it for now
        # if (invScore != score) or (invPowerScore != powerScore):
        if invScore != score:
            contradictions.append(sid)
    return run(qResults(("AND S.id in %s" + orderClause) % valueArray(contradictions)))
