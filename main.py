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
import json
import random
import string
import hashlib
from google.appengine.ext import db


class Log(db.Model):
    message = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Good(db.Model):
    ident = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    passwd = db.StringProperty(required=True)
    addedMessage = db.BooleanProperty()
    checkedFirstDraw = db.BooleanProperty()
    checkedSecondDraw = db.BooleanProperty()


class Gift(db.Model):
    ident = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    description = db.StringProperty()
    message = db.StringProperty()
    picture = db.BlobProperty()
    giver = db.ReferenceProperty(Good, collection_name='give_set', required=True)
    taker = db.ReferenceProperty(Good, collection_name='take_set')


class Counter(db.Model):
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(default=1)


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
        self.render_template('helper.html')


class GoodHandler(BaseHandler):
    def get(self):
        self.render_template('home.html')


def inc_counter(key):
    counter = db.get(key)
    count = counter.count
    counter.count += 1
    counter.put()
    return count


def add_log(msg):
    log = Log(message=msg)
    log.put()


class GoodApiHandler(BaseHandler):
    def post(self, action):
        args = {'action': action}

        if action == 'register':
            ident = self.request.get('ident')
            args['ident'] = ident

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM Good WHERE ident = :1", ident)
                good = query.get()

                if good:
                    args['result'] = 'duplicated'
                else:
                    # create weak password
                    passwd = ''.join([random.choice(string.letters + string.digits) for i in range(6)])
                    digest = hashlib.md5(passwd).hexdigest()

                    # gift counter
                    q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'gift')
                    counter = q.get()
                    if not counter:
                        counter = Counter(name='gift')
                        counter.put()
                    count = db.run_in_transaction(inc_counter, counter.key())

                    # create good
                    good = Good(ident=ident, passwd=digest)
                    good.put()

                    # create gift
                    gift = Gift(ident=str(count), giver=good)
                    gift.put()

                    add_log("good: %s and gift: %s registered." % (good.ident, gift.ident))

                    args['result'] = 'success'
                    args['passwd'] = passwd
                    args['gift'] = gift.ident
            else:
                args['result'] = 'invalid_ident'
        elif action == 'delete':
            ident = self.request.get('ident')
            args['ident'] = ident

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM Good WHERE ident = :1", ident)
                good = query.get()

                if not good:
                    args['result'] = 'nonexist'
                else:
                    gift = good.give_set.get()
                    gift.delete()
                    good.delete()
                    add_log("good: %s and gift: %s deleted." % (good.ident, gift.ident))
                    args['result'] = 'success'
            else:
                args['result'] = 'invalid_ident'
        else:
            args['result'] = 'unknown_action'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


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
        ('/api/good/(register|delete)', GoodApiHandler),
        ('/welfare', WelfareHandler),
        ('/about', AboutHandler),
        ], debug=True)
