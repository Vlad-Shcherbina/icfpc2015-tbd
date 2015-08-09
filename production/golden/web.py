import tornado
import tornado.ioloop
import tornado.web
import json

from production.golden import webhelpers as wh
from production.golden import api

class Main(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(wh.prelude())
        self.write("<style>%s</style>" % wh.css())
        self.write("<script>%s</script>" % wh.js())
        self.write("<h1>ICFPC TBD 2015</h1>")
        self.write("""
        <h2 onclick="toggle('contradicting')">Contradictions<sup>click to toggle</sup></h2>%s
        """ % wh.contradictingResults())
        self.write("""
        <h2 onclick="toggle('interesting')">Scoring submissions<sup>click to toggle</sup></h2>%s
        """ % wh.interestingResults())

class Own(tornado.web.RequestHandler):
    def get(self, req):
        req = json.loads(req)
        api.storeOwnResult( req['user']
                          , req['result']
                          , req['solution']
                          , 'Output by %s' % req['user'] )
        self.write('Thanks!')

class Snd(tornado.web.RequestHandler):
    def get(self, req):
        req = json.loads(req)
        api.runReference(req['solution'], 'Testing %s' % req['user'])
        self.write('Thanks!')

class Submit(tornado.web.RequestHandler):
    def get(self, req):
        self.set_header("Content-Type", "text/html")
        req = json.loads(req)
        reason_own, reason_ref = req['reasons'] if 'reasons' in req else ('%s playing' % req['user'], 'Testing our implementation')
        api.storeOwnResult(
            req['user'], req['result'], req['solution'], reason_own)
        api.runReference(req['solution'], reason_ref)
        self.write("Thanks!")

class Run(tornado.web.RequestHandler):
    def get(self, req):
        self.set_header("Content-Type", "text/html")
        req = json.loads(req)
        from production.golden import api
        api.runReference(req, 'Testing our implementation')
        self.write("Thanks!")

class GetSubmission(tornado.web.RequestHandler):
    def get(self, req):
        self.set_header("Content-Type", "text/json")
        data = api.getSubmission(req)
        if not data:
            raise tornado.web.HTTPError(404)
        self.write(json.dumps(
            [{'seed': data[1][0][0],
              'tag': data[1][0][1],
              'problemId': data[1][0][2],
              'solution': data[1][0][3]}
            ]))

application = tornado.web.Application([
  (r"/", Main),
  (r"/submit/(.*)", Submit),
  (r"/run/(.*)", Run),
  (r"/submission/(.*)", GetSubmission),
  (r"/snd/(.*)", Snd),
  (r"/own/(.*)", Own)
  ])

if __name__ == "__main__":
    port = 55315
    print("Listening to %s" % port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
