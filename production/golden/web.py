import sys
sys.path.append('.')

import tornado
import tornado.ioloop
import tornado.web
import sys

import webhelpers as wh

class Main(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write("<h1>ICFPC TBD 2015</h1>")
        self.write(wh.contradictingResults())
        self.write(wh.interestingResults())

application = tornado.web.Application([ (r"/", Main) ])

if __name__ == "__main__":
    port = 55315
    print("Listening to %s" % port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
