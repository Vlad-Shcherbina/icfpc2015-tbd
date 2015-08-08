import json

from production.golden import api

def interestingResults():
    rs = api.getInterestingResults()
    return sqlToHTML(rs)

def contradictingResults():
    rs = api.getContradictingResults()
    return sqlToHTML(rs)

def sqlToHTML(rs, className=""):
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
            if c == 'solution':
                d1 = '<pre>' + d1 + '</pre>'
            row += '<td class="%s">' % c + d1 + '</td>'
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
        word-wrap: break-word;
        max-width: 200px;
    }
    """ % cssBoilerplate()

def js():
    return """
    lookup = {
      "p":"p", "'":"p", "!":"p", ".":"p", "0":"p", "3":"p",
      "b":"b", "c":"b", "e":"b", "f":"b", "y":"b", "2":"b",
      "a":"a", "g":"a", "h":"a", "i":"a", "j":"a", "4":"a",
      "l":"l", "m":"l", "n":"l", "o":"l", " ":"l", "5":"l",
      "d":"d", "q":"d", "r":"d", "v":"d", "z":"d", "1":"d",
      "k":"k", "s":"k", "t":"k", "u":"k", "w":"k", "x":"k"
    }

    function deobfuscate(phrase) {
      return phrase.replace(/./g, function(m){console.log(m, " : ", lookup[m]); return lookup[m];});
    }

    function simplify_solution() {
      solutions = document.getElementsByClassName('solution');
      for (i=1; i < solutions.length; ++i) {
        solutions[i].textContent = deobfuscate(solutions[i].textContent);
      }
    }
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
    """
