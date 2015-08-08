import sys
sys.path.append('.')

import api

def interestingResults():
    rs = api.getInterestingResults()
    return sqlToHTML(rs)

def sqlToHTML(rs):
    (th, trs) = rs
    html  = ""
    row   = ""
    for h in th:
        row += "<th>" + str(h) + "</th>"
    html += "<tr>" + row + "</tr>"
    for tr in trs:
        row = ""
        for d in tr:
            row += "<td>" + str(d) + "</td>"
        html += "<tr>" + row + "</tr>"
    return "<table>" + html + "</table>"
