#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generalplus Secret Santa
# Copyright 2011 Ron Huang
# See MIT-LICENSE.txt for details.


from __future__ import with_statement

import json, random, string, hashlib, logging, re, urllib, itertools, webapp2

from google.appengine.api import images, files
from google.appengine.ext import db, blobstore, deferred

from webapp2 import Route
from webapp2_extras import jinja2
from webapp2_extras import sessions

import prefs


ROLE_ADMIN = 0
ROLE_WELFARE = 1000
ROLE_HELPER = 2000
ROLE_GOOD = 3000

STATE_REGISTER_START = 0
STATE_REGISTER_END = 1
STATE_GENERAL_RESULT = 2
STATE_SPECIAL_RESULT = 3
STATE_EVENT_END = 4
STATE_MAINTENANCE = 5

STATES = (STATE_REGISTER_START,
          STATE_REGISTER_END,
          STATE_GENERAL_RESULT,
          STATE_SPECIAL_RESULT,
          STATE_EVENT_END,
          STATE_MAINTENANCE)

STATE_LABELS = (u'開放登錄禮物',
                u'截止登錄禮物',
                u'開放第一次抽獎結果',
                u'開放第二次抽獎結果',
                u'活動結束',
                u'維修')

MIN_FILE_SIZE = 1 # bytes
MAX_FILE_SIZE = 1000000 # bytes
ACCEPT_FILE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')


class User(db.Model):
    ident = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    passwd = db.StringProperty()
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
    picture = blobstore.BlobReferenceProperty()
    giver = db.ReferenceProperty(User, collection_name='give_set', required=True)
    taker = db.ReferenceProperty(User, collection_name='take_set')

    @property
    def is_complete(self):
        return self.description and self.message and self.picture

    @property
    def url(self):
        if self.picture:
            return images.get_serving_url(self.picture)

    @property
    def thumbnail_url(self):
        if self.picture:
            return images.get_serving_url(self.picture, 250, False)

    @property
    def grid_url(self):
        if self.picture:
            return images.get_serving_url(self.picture, 150, True)

    @property
    def orbit_url(self):
        if self.picture:
            return images.get_serving_url(self.picture, 383, True)


class Counter(db.Model):
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(default=1)


class Log(db.Model):
    message = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    who = db.ReferenceProperty(User)


class State(db.Model):
    state = db.IntegerProperty(required=True, default=STATE_REGISTER_START)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        if not template_args:
            template_args = {}
        if not 'auth' in template_args:
            template_args['auth'] = self.auth

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
        query = db.GqlQuery("SELECT * FROM Gift WHERE picture != NULL ORDER BY picture DESC, updated DESC LIMIT 10")
        self.render_template('home.html', query=query, count=query.count())


class GiftsHandler(BaseHandler):
    def get(self):
        query = db.GqlQuery("SELECT * FROM Gift ORDER BY created")
        self.render_template('gifts.html', gifts=query, count=query.count())


class HelperHandler(BaseHandler):
    def get(self):
        if not self.auth:
            return self.redirect_to("login", returnpath="helper")

        if self.auth.role > ROLE_HELPER:
            return self.render_template('bad.html')

        self.render_template('helper.html')


class GoodHandler(BaseHandler):
    def get(self):
        if not self.auth:
            return self.redirect_to("login", returnpath="good")

        if self.auth.role > ROLE_GOOD:
            return self.render_template('bad.html')

        current = State.get_or_insert('current').state
        if current == STATE_REGISTER_START:
            self.register_gift()
        elif current == STATE_REGISTER_END:
            self.wait_for_result()
        elif current == STATE_GENERAL_RESULT:
            self.general_result()
        elif current == STATE_SPECIAL_RESULT:
            self.special_result()
        elif current == STATE_EVENT_END:
            self.event_end()
        elif current == STATE_MAINTENANCE:
            self.maintenance()
        else:
            self.redirect_to('home')

    def register_gift(self):
        gift = self.auth.give_set.get()
        args = None

        flashes = self.session.get_flashes()
        for flash in flashes:
            args = flash[0]

        self.render_template('register.html', gift=gift, args=args)

    def wait_for_result(self):
        gift = self.auth.give_set.get()
        self.render_template('wait-for-result.html', gift=gift)

    def general_result(self):
        gift = self.auth.take_set.get()
        user = self.auth
        self.render_template('general-result.html', gift=gift, user=user)

    def special_result(self):
        pass

    def event_end(self):
        pass

    def maintenance(self):
        self.render_template('maintenance.html')


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
        elif action == 'update':
            ident = self.request.get('ident')
            args['ident'] = ident
            role = int(self.request.get('role'))

            if ident and len(ident) == 5:
                query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", ident)
                user = query.get()

                if not user:
                    args['result'] = 'nonexist'
                elif self.auth.role >= user.role:
                    # lower role has greater permission
                    args['result'] = 'unauthorized'
                else:
                    old_role = user.role
                    user.role = role
                    user.put()

                    self.add_log("user '%s' role changed from %d to %d." % (user.ident, old_role, user.role))
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

        if self.auth.role > ROLE_WELFARE:
            return self.render_template('bad.html')

        current = State.get_or_insert('current').state
        self.render_template('welfare.html', current=current, states=STATE_LABELS)


class AboutHandler(BaseHandler):
    def get(self):
        self.render_template('about.html')


class StatsHandler(BaseHandler):
    def get(self):
        if not self.auth:
            return self.redirect_to("login", returnpath="stats")

        if self.auth.role > ROLE_WELFARE:
            return self.render_template('bad.html')

        users = db.GqlQuery("SELECT * FROM User WHERE ident != :1", "0")
        gifts = db.GqlQuery("SELECT * FROM Gift")
        self.render_template('stats.html', users=users, gifts=gifts)


def assign_taker(gift_key, taker_key, auth_key):
    gift = db.get(gift_key)
    taker = db.get(taker_key)
    gift.taker = taker
    gift.put()

    msg = "gift %s assigned to user %s" % (gift.ident, taker.ident)
    auth = db.get(auth_key)
    log = Log(message=msg, who=auth)
    log.put()


class DrawApiHandler(BaseHandler):
    def valid(self, a, b):
        # make sure no one gets their own gift
        for i, j in itertools.izip(a, b):
            if i == j:
                return False
        return True

    def shuffle(self, items):
        orig = list(items)
        while not self.valid(orig, items):
            random.shuffle(items)

    def draw(self):
        gifts = db.GqlQuery("SELECT * FROM Gift")
        gift_keys = []
        taker_keys = []
        for gift in gifts:
            gift_keys.append(gift.key())
            taker_keys.append(gift.giver.key())

        self.shuffle(taker_keys)

        count = gifts.count()
        auth_key = self.auth.key()
        for i in range(count):
            deferred.defer(assign_taker, gift_keys[i], taker_keys[i], auth_key)

    def get(self):
        # check if the draw process is complete
        if not self.auth:
            return self.redirect_to("login", returnpath="draw-api")

        if self.auth.role > ROLE_WELFARE:
            return self.render_template('bad.html')

        query = db.GqlQuery("SELECT * FROM Gift WHERE taker = NULL")
        left = query.count()

        args = {}
        if left == 0:
            args['result'] = 'success'
        else:
            args['result'] = 'incomplete'
            args['left'] = left
            query = db.GqlQuery("SELECT * FROM Gift")
            total = query.count()
            args['total'] = total

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))

    def post(self):
        current = State.get_or_insert('current').state
        args = {}

        if not self.auth or self.auth.role > ROLE_WELFARE:
            args['result'] = 'unauthorized'
        elif current != STATE_REGISTER_END:
            args['result'] = 'invalid_state'
        else:
            self.draw()
            self.add_log('draw')
            args['result'] = 'incomplete'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


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
            self.add_log('user %s login successful' % (ident))
            self.session['ident'] = ident
            self.redirect_to(returnpath)
        elif returnpath:
            self.add_log('user %s login failed' % (ident))
            self.session.add_flash('unauthorized')
            self.redirect_to("login", returnpath=returnpath)
        else:
            self.redirect_to('home')


class AdminHandler(BaseHandler):
    def get(self):
        # add admin is not already exist
        query = db.GqlQuery("SELECT * FROM User WHERE ident = :1", "0")
        user = query.get()
        if not user:
            user = User(ident='0', role=ROLE_ADMIN)
            user.put()

        self.session['ident'] = '0'
        users = db.GqlQuery("SELECT * FROM User WHERE ident != :1 ORDER BY ident", "0")
        self.render_template('admin.html', users=users)


class GiftApiHandler(BaseHandler):
    def validate(self, info):
        if info['size'] < MIN_FILE_SIZE:
            info['error'] = 'minFileSize'
        elif info['size'] > MAX_FILE_SIZE:
            info['error'] = 'maxFileSize'
        elif not ACCEPT_FILE_TYPES.match(info['type']):
            info['error'] = 'acceptFileTypes'
        else:
            return True
        return False

    def get_file_size(self, handle):
        handle.seek(0, 2) # Seek to the end of the file
        size = handle.tell() # Get the position of EOF
        handle.seek(0) # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)

    def handle_upload(self, args):
        pic = None
        for name, field in self.request.POST.items():
            if type(field) is unicode:
                continue
            if hasattr(field, 'filename'):
                pic = field
                break

        if not hasattr(pic, 'filename'):
            args['result'] = 'invalid'
            return None, args

        blob_key = None
        info = {
            'name': re.sub(r'^.*\\', '', pic.filename),
            'type': pic.type,
            'size': self.get_file_size(pic.file),
            }

        if self.validate(info):
            blob_key = self.write_blob(pic.value, info)
            try:
                url = images.get_serving_url(blob_key)
            except: # Could not get an image serving url
                args['result'] = 'invalid'
                blob_key = None
        else:
            args['result'] = 'invalid'
            args['invalid'] = info['error']

        return blob_key, args

    def post(self, action):
        args = {'action': action}

        if not self.auth:
            args['result'] = 'unauthorized'
        elif action == 'register':
            gift = self.auth.give_set.get()
            gift.description = self.request.get('desc')
            gift.message = self.request.get('bless')
            gift.put()

            if not gift.is_complete:
                args['result'] = 'more'
                more = []
                if not gift.description:
                    more.append(u'禮物描述')
                if not gift.message:
                    more.append(u'祝福語')
                if not gift.picture:
                    more.append(u'照片')
                args['more'] = u'、'.join(more)
            else:
                args['result'] = 'success'
        elif action == 'upload':
            blob_key, args = self.handle_upload(args)

            if not blob_key:
                # image uploaded unsuccesfully
                self.session.add_flash(args)
                return self.redirect_to("good")

            # image uploaded succesfully
            gift = self.auth.give_set.get()
            old_blob = gift.picture
            blob = blobstore.get(blob_key)
            gift.picture = blob
            gift.put()

            if old_blob:
                old_blob.delete()

            if not gift.is_complete:
                args['result'] = 'more'
                more = []
                if not gift.description:
                    more.append(u'禮物描述')
                if not gift.message:
                    more.append(u'祝福語')
                if not gift.picture:
                    more.append(u'照片')
                args['more'] = u'、'.join(more)
            else:
                args['result'] = 'success'

            self.session.add_flash(args)
            return self.redirect_to("good")
        else:
            args['result'] = 'unknown_action'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


class StateApiHandler(BaseHandler):
    def post(self, action):
        args = {'action': action}

        if not self.auth or self.auth.role > ROLE_WELFARE:
            args['result'] = 'unauthorized'
        elif action == 'change':
            state = int(self.request.get('state'))
            args['state'] = state

            if state in STATES:
                current = State.get_or_insert('current')
                old_state = current.state
                current.state = state
                current.put()

                self.add_log("state changed from %d to %d." % (old_state, state))

                args['result'] = 'success'
                args['state_label'] = STATE_LABELS[state]
            else:
                args['result'] = 'invalid_state'
        else:
            args['result'] = 'unknown_action'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


class ResultApiHandler(BaseHandler):
    def post(self, action):
        args = {'action': action}

        if not self.auth:
            args['result'] = 'unauthorized'
        elif action == 'fetch':
            user = self.auth
            user.checkedFirstDraw = True
            user.put()

            self.add_log("user %s fetched first result." % (user.ident))

            args['result'] = 'success'
        else:
            args['result'] = 'unknown_action'

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(args))


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': prefs.SESSIONS_SECRET_KEY,
}

application = webapp2.WSGIApplication([
        Route(r'/', handler=HomeHandler, name='home'),
        Route(r'/gifts', handler=GiftsHandler, name='gifts'),
        Route(r'/helper', handler=HelperHandler, name='helper'),
        Route(r'/good', handler=GoodHandler, name='good'),
        Route(r'/welfare', handler=WelfareHandler, name='welfare'),
        Route(r'/about', handler=AboutHandler, name='about'),
        Route(r'/stats', handler=StatsHandler, name='stats'),
        Route(r'/login', handler=LoginHandler, name='login'),
        Route(r'/logout', handler=LogoutHandler, name='logout'),
        Route(r'/admin', handler=AdminHandler, name='admin'),
        Route(r'/api/draw', handler=DrawApiHandler, name='draw-api'),
        Route(r'/api/user/<action:register|delete|reset|update>', handler=UserApiHandler, name='user-api'),
        Route(r'/api/login', handler=LoginApiHandler, name='login-api'),
        Route(r'/api/gift/<action:register|upload>', handler=GiftApiHandler, name='gift-api'),
        Route(r'/api/state/<action:change>', handler=StateApiHandler, name='state-api'),
        Route(r'/api/result/<action:fetch>', handler=ResultApiHandler, name='result-api'),
        ], config=config, debug=True)
