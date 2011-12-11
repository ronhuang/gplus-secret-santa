#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generalplus Secret Santa
# Copyright 2011 Ron Huang
# See MIT-LICENSE.txt for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import time
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


class HomeHandler(webapp.RequestHandler):

    def get(self):
        args = {}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'views', "home.html")
        self.response.out.write(template.render(path, args))


class HelperHandler(webapp.RequestHandler):

    def get(self):
        args = {}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'views', "home.html")
        self.response.out.write(template.render(path, args))


class GoodHandler(webapp.RequestHandler):

    def get(self):
        args = {}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'views', "home.html")
        self.response.out.write(template.render(path, args))


class WelfareHandler(webapp.RequestHandler):

    def get(self):
        args = {}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'views', "home.html")
        self.response.out.write(template.render(path, args))


class AboutHandler(webapp.RequestHandler):

    def get(self):
        args = {}

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'views', "home.html")
        self.response.out.write(template.render(path, args))


def main():
    actions = [
        ('/', HomeHandler),
        ('/helper', HelperHandler),
        ('/good', GoodHandler),
        ('/welfare', WalfareHandler),
        ('/about', AboutHandler),
        ]
    application = webapp.WSGIApplication(actions, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
