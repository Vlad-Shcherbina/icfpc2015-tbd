import tornado
import tornado.ioloop
import tornado.web

from production.golden import webhelpers as wh

class Main(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(wh.prelude())
        self.write("<style>%s</style>" % wh.css())
        self.write("<script>%s</script>" % wh.js())
        self.write("<h1>ICFPC TBD 2015</h1>")
        self.write("<h2>Contradictions</h2>"      + wh.contradictingResults())
        self.write("<h2>Scoring submissions</h2>" + wh.interestingResults())

application = tornado.web.Application([ (r"/", Main) ])

if __name__ == "__main__":
    port = 55315
    print("Listening to %s" % port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
