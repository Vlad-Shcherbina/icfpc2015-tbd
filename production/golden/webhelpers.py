import sys
sys.path.append('.')

import api

def interestingResults():
    rs = api.getInterestingResults()
    return sqlToHTML(rs)

def contradictingResults():
    rs = api.getContradictingResults()
    return sqlToHTML(rs)

def sqlToHTML(rs, className=""):
    (th, trs) = rs
    html  = ''
    row   = ''
    for h in th:
        h1 = str(h)
        row += '<th class="%s">' % h1 + h1 + '</th>'
    html += '<tr>' + row + '</tr>'
    for tr in trs:
        row = ''
        for n, d in enumerate(tr):
            d1 = str(d)
            c  = str(th[n])
            row += '<td class="%s">' % c + d1 + '</td>'
        html += '<tr>' + row + '</tr>'
    return '<table class="%s">' % className + html + '</table>'
