#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generalplus Secret Santa
# Copyright 2011 Ron Huang
# See MIT-LICENSE.txt for details.


import logging
import webapp2
from webapp2 import Route
from webapp2_extras import jinja2
from webapp2_extras import sessions
import os
import time
import datetime
import json
import random
import string
import hashlib
from google.appengine.ext import db
import prefs


ROLE_ADMIN = 0
ROLE_WELFARE = 1000
ROLE_HELPER = 2000
ROLE_GOOD = 3000


class User(db.Model):
    ident = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    passwd = db.StringProperty()
    addedMessage = db.BooleanProperty()
    checkedFirstDraw = db.BooleanProperty()
    checkedSecondDraw = db.BooleanProperty()
    executive = db.BooleanProperty(default=False)
    role = db.IntegerProperty(required=True)

    def check_passwd(self, passwd):
        return self.passwd == hashlib.md5(passwd).hexdigest()

    def reset_passwd(self):
        passwd, digest = User.create_passwd()
        self.passwd = digest
        self.put()
        return passwd

    @staticmethod
    def create_passwd():
        passwd = ''.join([random.choice(string.letters + string.digits) for i in range(6)])
        return passwd, hashlib.md5(passwd).hexdigest()


class Gift(db.Model):
    ident = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    description = db.StringProperty()
    message = db.StringProperty()
    picture = db.BlobProperty()
    giver = db.ReferenceProperty(User, collection_name='give_set', required=True)
    taker = db.ReferenceProperty(User, collection_name='take_set')


class Counter(db.Model):
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(default=1)


class Log(db.Model):
    message = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    who = db.ReferenceProperty(User)


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        body = self.jinja2.render_template(filename, **template_args)
        self.response.write(body)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            #webapp2.RequestHandler.dispatch(self)
            super(BaseHandler, self).dispatch()
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
        ident = self.session.get('ident')
        if not ident:
            return
        query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", ident)
        user = query.get()
        return user

    def add_log(self, msg):
        log = Log(message=msg, who=self.auth)
        log.put()


class HomeHandler(BaseHandler):
    def get(self):
        self.render_template('home.html')


class HelperHandler(BaseHandler):
    def get(self):
        if not self.auth:
            return self.redirect_to("login", returnpath="helper")

        if self.auth.role >= ROLE_GOOD:
            return self.render_template('bad.html')

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


class UserApiHandler(BaseHandler):
    def post(self, action):
        args = {'action': action}

        if not self.auth:
            args['result'] = 'unauthorized'
        elif action == 'register':
            args['ident'] = self.request.get('ident')
            ident = self.request.get('ident')
            args['role'] = self.request.get('role')
            role = int(self.request.get('role'))
            executive = self.request.get('executive') and True or False

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", ident)
                user = query.get()

                if user:
                    args['result'] = 'duplicated'
                elif self.auth.role >= role:
                    # lower role has greater permission
                    args['result'] = 'unauthorized'
                else:
                    # gift counter
                    q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'gift')
                    counter = q.get()
                    if not counter:
                        counter = Counter(name='gift')
                        counter.put()
                    count = db.run_in_transaction(inc_counter, counter.key())

                    # create user
                    passwd, digest = User.create_passwd()
                    user = User(ident=ident, passwd=digest, role=role, executive=executive)
                    user.put()

                    # create gift
                    gift = Gift(ident=str(count), giver=user)
                    gift.put()

                    self.add_log("user '%s' and gift '%s' registered." % (user.ident, gift.ident))

                    args['result'] = 'success'
                    args['passwd'] = passwd
                    args['gift'] = gift.ident
            else:
                args['result'] = 'invalid_ident'
        elif action == 'delete':
            ident = self.request.get('ident')
            args['ident'] = ident

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", ident)
                user = query.get()

                if not user:
                    args['result'] = 'nonexist'
                elif self.auth.role >= user.role:
                    # lower role has greater permission
                    args['result'] = 'unauthorized'
                else:
                    gift = user.give_set.get()
                    gift.delete()
                    user.delete()
                    self.add_log("user '%s' and gift '%s' deleted." % (user.ident, gift.ident))
                    args['result'] = 'success'
            else:
                args['result'] = 'invalid_ident'
        elif action == 'reset':
            ident = self.request.get('ident')
            args['ident'] = ident

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", ident)
                user = query.get()

                if not user:
                    args['result'] = 'nonexist'
                elif self.auth.role >= user.role:
                    # lower role has greater permission
                    args['result'] = 'unauthorized'
                else:
                    passwd = user.reset_passwd()
                    self.add_log("user '%s' password reset." % (user.ident))
                    args['passwd'] = passwd
                    args['result'] = 'success'
            else:
                args['result'] = 'invalid_ident'
        else:
            args['result'] = 'unknown_action'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


class WelfareHandler(BaseHandler):
    def get(self):
        if not self.auth:
            return self.redirect_to("login", returnpath="welfare")

        if self.auth.role >= ROLE_HELPER:
            return self.render_template('bad.html')

        self.render_template('welfare.html')


class AboutHandler(BaseHandler):
    def get(self):
        self.render_template('about.html')


class LoginHandler(BaseHandler):
    def get(self):
        returnpath = self.request.get('returnpath')
        unauthorized = False

        flashes = self.session.get_flashes()
        for flash in flashes:
            unauthorized = unauthorized or ('unauthorized' in flash)

        self.render_template('login.html',
                             returnpath=returnpath,
                             unauthorized=unauthorized)


class LogoutHandler(BaseHandler):
    def get(self):
        self.session['ident'] = None
        self.redirect_to('home')


class LoginApiHandler(BaseHandler):
    def post(self):
        ident = self.request.get('ident')
        passwd = self.request.get('passwd')
        returnpath = self.request.get('returnpath')

        # authenticate
        query = db.GqlQuery('SELECT * FROM User WHERE ident = :1', ident)
        user = query.get()
        isValidUser = user and user.ident != 0 and user.check_passwd(passwd)
        if isValidUser and returnpath:
            self.session['ident'] = ident
            self.redirect_to(returnpath)
        elif returnpath:
            self.session.add_flash('unauthorized')
            self.redirect_to('login', returnpath=returnpath)
        else:
            self.redirect_to('home')


class AdminHandler(BaseHandler):
    def get(self):
        # add admin is not already exist
        query = db.GqlQuery("SELECT * FROM User WHERE ident = 0")
        user = query.get()
        if not user:
            user = User(ident='0', role=ROLE_ADMIN)
            user.put()

        self.session['ident'] = '0'
        self.render_template('admin.html')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': prefs.SESSIONS_SECRET_KEY,
}

application = webapp2.WSGIApplication([
        Route(r'/', handler=HomeHandler, name='home'),
        Route(r'/helper', handler=HelperHandler, name='helper'),
        Route(r'/good', handler=GoodHandler, name='good'),
        Route(r'/welfare', handler=WelfareHandler, name='welfare'),
        Route(r'/about', handler=AboutHandler, name='about'),
        Route(r'/login', handler=LoginHandler, name='login'),
        Route(r'/logout', handler=LogoutHandler, name='logout'),
        Route(r'/admin', handler=AdminHandler, name='admin'),
        Route(r'/api/user/<action:register|delete|reset>', handler=UserApiHandler, name='user-api'),
        Route(r'/api/login', handler=LoginApiHandler, name='login-api'),
        ], config=config, debug=True)
