import json

from production.golden import api

def rearrangeSubmissionTable(rs):
    if not rs:
        return ()
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
    if c in ('solution',):
        return '<input class="clickable" onclick="this.select()" value="%s" />' % d
    if c in ('tag',):
        return """
            <span class="clickable" 
                   onclick="document.execCommand('selectAll',false,null)"
                   contenteditable="true">%s</span>
            """ % d
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
        # dirty-dirty hack for highlighting non-matching results
        impl, score, wrong = '', '', False
        row = ''
        for n, d in enumerate(tr):
            d1 = str(d)
            c  = str(th[n])
            # 2nd part of a dirty-dirty hack
            if c == 'name':
                impl = d1
            elif c == 'tag':
                if ':' in d1 and impl == 'reference implementation':
                    score = d1.split(':')[-1]
            elif c == 'score':
                if score and score != d1:
                    wrong = True
            row += '<td class="%s">' % c + rewrite(d1, c) + '</td>'
        tbody += ('<tr class="wrong">' if wrong else '<tr>') + row + '</tr>'
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
    function toggle(className, visibleMode) {
        if (!visibleMode)
            visibleMode = 'table'
        var el = document.querySelectorAll('.' + className)[0]
        if (el.style.display === visibleMode || el.style.display === '') {
            el.style.display = 'none'
        } else {
            el.style.display = visibleMode
        }

    }
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
    table.contradicting td, tr.wrong td {
        background-color: #FCC !important;
    }
    table.contradicting input.clickable {
        background: #FCC !important;
    }
    """
