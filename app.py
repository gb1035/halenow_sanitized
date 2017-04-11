#!/usr/bin/env python
## -*- coding: utf-8 -*-
import os
import tornado.ioloop
import tornado.httpserver
import sys


from settings import *
from views import *


# Assign handler to the server root  (127.0.0.1:PORT/)
application = tornado.web.Application([
    (r"/", Index),
    (r"/admin_login",AdminLogin),
    (r"/admin",Admin),
    (r"/api/get_num",GetCurrentNumber),
    (r"/api/next",IncrementNumber),
    (r"/api/set_num",SetNumber),
    (r"/api/get_state",GetState),
    (r"/api/set_state",SetState),
    (r"/api/clear_schedule",ClearSchedule),
    (r"/api/get_table",GetTable),
], static_path=STATIC_PATH,cookie_secret=TORNADO_SECRET,xsrf_cookies=XSRF_COOKIES,)


if __name__ == "__main__":
    # Setup the server
    if not check_db() or '--setup' in sys.argv:
        print 'It appears the database is not setup, entering first time setup...'
        setup_db()
        print 'Setup complete, now starting server.'
    if (HTTPS):
        http_server = tornado.httpserver.HTTPServer(application, ssl_options={
            "certfile": CERTFILE,
            "keyfile": KEYFILE,
        })
        http_server.listen(HTTPS_PORT)
    else:
        application.listen(HTTP_PORT)
    tornado.ioloop.IOLoop.instance().start()
