import json

from production.golden import api

def rearrangeSubmissionTable(rs):
    def rearrangeRow(xs):
        (name, id, tag, problem, seed, solution, status, kind, timestamp, score, powerScore) = xs
        return (name, id, tag, score, powerScore, problem, seed, status, kind, timestamp, solution)
    # was ['name', 'id', 'tag', 'problem', 'seed', 'solution', 'status', 'kind', 'timestamp', 'score', 'powerScore']
    cells = ['name', 'id', 'tag', 'score', 'powerScore', 'problem', 'seed', 'status', 'kind', 'timestamp', 'solution']
    data  = map(rearrangeRow, rs[1])
    return (cells, data)

def interestingResults():
    rs = rearrangeSubmissionTable(api.getInterestingResults())
    return sqlToHTML(rs, "interesting", rewriteSolutionTags)

def contradictingResults():
    rs = rearrangeSubmissionTable(api.getContradictingResults())
    return sqlToHTML(rs, "contradicting", rewriteSolutionTags)

def rewriteSolutionTags(d, c):
    if c in ('solution', 'tag'):
        return '<input class="clickable" onclick="this.select()" value="%s" />' % d
    return d

def sqlToHTML(rs, className="", rewrite=lambda x: x):
    if not rs:
        return '<div class="empty">∅</div>'
    (th, trs) = rs
    html  = ''
    row   = ''
    tbody = ''
    for h in th:
        h1 = str(h)
        row += '<th class="%s">' % h1 + h1 + '</th>'
    html += '<thead><tr>' + row + '</tr></thead>'
    for tr in trs:
        row = ''
        for n, d in enumerate(tr):
            d1 = str(d)
            c  = str(th[n])
            row += '<td class="%s">' % c + rewrite(d1, c) + '</td>'
        tbody += '<tr>' + row + '</tr>'
    html += '<tbody>' + tbody + '</tbody>'
    return '<table class="%s">' % className + html + '</table>'

def prelude():
    return """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8" />
    </head>
    <body>
    """

def css():
    return """
    %s
    .solution {
        max-width: 400px;
    }
    .name {
        max-width: 100px;
    }
    """ % cssBoilerplate()

def js():
    return """
    setTimeout(function() {location.reload()}, 1000 * 120);
    """

def cssBoilerplate():
    return """
    * {
        font-family: monospace;
    }
    table {
        border-color: #600;
        border-width: 0 0 2px 2px;
        border-style: solid;
    }
    th, td {
        border-color: #600;
        border-width: 1px 1px 0 0;
        border-style: solid;
        margin: 0;
        padding: 4px;
        background-color: #FFC;
    }
    th {
        text-transform: uppercase;
    }
    input.clickable {
        background: #FFC !important;
    }
    table.contradicting td {
        background-color: #FCC !important;
    }
    table.contradicting input.clickable {
        background: #FCC !important;
    }
    """
