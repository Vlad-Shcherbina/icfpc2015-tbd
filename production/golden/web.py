import tornado
import tornado.ioloop
import tornado.web
import json

from production.golden import webhelpers as wh

class Main(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(wh.prelude())
        self.write("<style>%s</style>" % wh.css())
        self.write("<script>%s</script>" % wh.js())
        self.write("<h1>ICFPC TBD 2015</h1>")
        self.write("<div onClick=\"simplify_solution()\">Click here to deobfuscate solutions</div>")
        self.write("<h2>Contradictions</h2>"      + wh.contradictingResults())
        self.write("<h2>Scoring submissions</h2>" + wh.interestingResults())

class Submit(tornado.web.RequestHandler):
    def get(self, req):
        self.set_header("Content-Type", "text/html")
        req = json.loads(req)
        from production.golden import api
        api.storeOwnResult(
            req['user'], req['result'], req['solution'],
            '%s playing' % req['user'])
        api.runReference(req['solution'], 'Testing our implementation')
        self.write("Thanks!")

class Run(tornado.web.RequestHandler):
    def get(self, req):
        self.set_header("Content-Type", "text/html")
        req = json.loads(req)
        from production.golden import api
        api.runReference(req, 'Testing our implementation')
        self.write("Thanks!")

application = tornado.web.Application([
  (r"/", Main),
  (r"/submit/(.*)", Submit),
  (r"/run/(.*)", Run),
  ])

if __name__ == "__main__":
    port = 55315
    print("Listening to %s" % port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
