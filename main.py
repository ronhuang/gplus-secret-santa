#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generalplus Secret Santa
# Copyright 2011 Ron Huang
# See MIT-LICENSE.txt for details.


import webapp2
from webapp2_extras import jinja2
import os
import time
import datetime


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        body = self.jinja2.render_template(filename, **template_args)
        self.response.write(body)


class HomeHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


class HelperHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


class GoodHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


class WelfareHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


class AboutHandler(BaseHandler):

    def get(self):
        self.render_template('home.html')


application = webapp2.WSGIApplication([
        ('/', HomeHandler),
        ('/helper', HelperHandler),
        ('/good', GoodHandler),
        ('/welfare', WelfareHandler),
        ('/about', AboutHandler),
        ], debug=True)
