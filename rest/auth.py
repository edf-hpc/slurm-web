#!flask/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 EDF SA
#
# This file is part of slurm-web.
#
# slurm-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# slurm-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with slurm-web.  If not, see <http://www.gnu.org/licenses/>.

import ldap
import json
from flask import request, abort, jsonify
from settings import settings
from functools import wraps
from werkzeug.exceptions import Forbidden
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from ConfigParser import NoSectionError, NoOptionError
import os
import platform
import pwd


guests_allowed = False
all_enabled = True
auth_enabled = settings.get('config', 'authentication') == 'enable'

uids = {}  # cache of user login/names to avoid duplicate NSS resolutions

if auth_enabled:

    if settings.has_option('config', 'secret_key'):
        secret_key_file = settings.get('config', 'secret_key')
    else:
        secret_key_file = '/etc/slurm-web/secret.key'

    # check secret key file exist or print error otherwise
    if not os.path.exists(secret_key_file):
        print "Secret key file %s does not exists" % (secret_key_file)

    try:
        secret_key = open(secret_key_file, 'rb').read()
    except IOError:
        print "IO error with secret key file %s" % (secret_key_file)
        # fallback to bad secret key
        secret_key = b"badsecretkey"

    secret_key += platform.node()

    if settings.has_option('roles', 'guests'):
        guests_allowed_s = settings.get('roles', 'guests')
        if guests_allowed_s == 'enabled':
            guests_allowed = True
        elif not guests_allowed_s == 'disabled':
            print("invalid value '%s' for guests parameter, guests will be "
                  "disabled." % (guests_allowed_s))

    filtered_keys_by_role = {
        'all': settings.get('roles', 'restricted_fields_for_all').split(','),
        'user': settings.get('roles', 'restricted_fields_for_user').split(','),
        'admin': settings.get('roles', 'restricted_fields_for_admin')
        .split(',')
    }

    if settings.has_option('roles', 'all'):
        all_s = settings.get('roles', 'all')
        if all_s == 'disabled':
            all_enabled = False
        elif not all_s == 'enabled':
            print("invalid value '%s' for all parameters, all role will be "
                  "enabled." % (all_s))

    users = settings.get('roles', 'user').split(',')
    admins = settings.get('roles', 'admin').split(',')


# retrieve ACLs for views if exist in configuration
try:
    acl = settings.items('acl')
except NoSectionError:
    acl = []


def get_ldap_connection():

    uri = settings.get('ldap', 'uri')
    conn = ldap.initialize(uri)

    # LDAP/SSL setup
    if uri.startswith('ldaps'):

        conn.protocol_version = ldap.VERSION3
        # Force cert validation
        conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
        if settings.has_option('ldap', 'cacert'):
            cacert = settings.get('ldap', 'cacert')
            # Set path name of file containing all trusted CA certificates
            conn.set_option(ldap.OPT_X_TLS_CACERTFILE, cacert)
        # Force libldap to create a new SSL context
        conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)

    return conn


def filter_dict(to_filter={}, filtered_keys=[]):
    if isinstance(to_filter, dict):
        for key in set(to_filter):
            if key in filtered_keys:
                del to_filter[key]
            else:
                if isinstance(to_filter[key], dict):
                    filter_dict(to_filter[key], filtered_keys)
    if isinstance(to_filter, list):
        for elem in to_filter:
            filter_dict(elem, filtered_keys)


class AuthenticationError(Exception):
    pass


class AllUnauthorizedError(Exception):
    pass


class CORSForbidden(Forbidden):
    def get_headers(self, environ):
        """Prevent CORS error on Forbidden response."""
        return [('Content-Type', 'text/html'),
                ('Access-Control-Allow-Origin', '*')]


abort.mapping.update({403: CORSForbidden})


class User(object):
    def __init__(self, login, role, groups=None):
        self.login = login
        self.role = role
        self.groups = groups

    # create authenticated user
    @staticmethod
    def user(login, password):
        groups = User.get_groups_from_ldap(login, password)
        role = User.get_role(login, groups)
        if role == 'all' and not all_enabled:
            raise AllUnauthorizedError
        return User(login, role, groups)

    # create a guest user
    @staticmethod
    def guest():
        if not guests_allowed:
            raise AuthenticationError
        if not all_enabled:
            raise AllUnauthorizedError
        return User('guest', 'all')

    @staticmethod
    def get_groups_from_ldap(login, password):

        # here deal with ldap to get user groups
        conn = get_ldap_connection()

        try:
            base_people = settings.get('ldap', 'base_people')
            base_group = settings.get('ldap', 'base_group')

            # authenticate user on ldap
            user_dn = "uid=%s,%s" % (login, base_people)
            conn.simple_bind_s(user_dn, password)

            print "User %s authenticated" % login

            # search for user's groups
            look_filter = "(|(&(objectClass=*)(member=%s)))" % (user_dn)
            results = conn.search_s(base_group,
                                    ldap.SCOPE_SUBTREE,
                                    look_filter, ['cn'])
            groups = [result[1]['cn'][0] for result in results]
            return groups

        except ldap.SERVER_DOWN:
            print 'The LDAP server is unreachable.'
            raise AuthenticationError

        except ldap.INVALID_CREDENTIALS:
            print "Authentication failed: login id or password is incorrect."
            raise AuthenticationError

        except ldap.NO_SUCH_OBJECT as e:
            print "No result found: %s " + str(e)
            raise AuthenticationError

        finally:
            conn.unbind_s()

    @staticmethod
    def get_role(login, groups):
        if login in admins:
            return 'admin'
        for group in groups:
            if ("@" + group) in admins:
                return 'admin'
        if login in users:
            return 'user'
        for group in groups:
            if ("@" + group) in users:
                return 'user'
        return 'all'

    def generate_auth_token(
        self, expiration=int(settings.get('ldap', 'expiration'))
    ):
        s = Serializer(secret_key, expires_in=expiration)
        token = s.dumps({
            'login': self.login,
            'role':  self.role
        })
        print "generate_auth_token : token -> %s" % token
        return token

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
            print "verify_auth_token : data -> login id: %s role: %s" \
                  % (data['login'], data['role'])
        except SignatureExpired:
            print "verify_auth_token : SignatureExpired "
            return None  # valid token, but expired
        except BadSignature:
            print "verify_auth_token : BadSignature "
            return None  # invalid token
        except TypeError:
            print "verify_auth_token : TypeError"
            return None

        if data['login'] == 'guest':
            return User.guest()

        user = User(data['login'], data['role'])

        return user

    def restricted_views(self):

        views = set([xacl[0] for xacl in acl])

        for xacl in acl:
            view = xacl[0]
            members = xacl[1].split(',')
            for member in members:
                if member and member[0] == '@' and self.groups is not None \
                   and member[1:] in self.groups:
                    views.remove(view)
                    break
                elif member == self.login:
                    views.remove(view)
                    break
        return list(views)

    def get_user_name(self):
        # return user's name from the 1st item of gecos field
        if self.login == 'guest':
            return 'guest'
        # try to retrieve password from LDAP
        try:
            conn = get_ldap_connection()
            base_people = settings.get('ldap', 'base_people')
            user_filter = "(uid=%s)" % self.login
            # search in LDAP for the given name of this user
            given_name = conn.search_s(base_people,
                                       ldap.SCOPE_SUBTREE,
                                       user_filter,
                                       attrlist=['givenname'])
            # get the given name and format it properly
            if not len(given_name) == 0:
                user_name = given_name[0][1]['givenName'][0].decode('utf-8')
                return user_name
        except:
            print "Can't retrieve username from LDAP for %s" % self.login
        # try to retrieve it for system
        try:
            return pwd.getpwnam(self.login)[4].split(',')[0]
        except:
            print "Can't retrieve username from system for %s" % self.login
        # return user login if the other steps have failed
        return "%s" % self.login


def authentication_verify():
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            resp = f(*args, **kwargs)
            if not auth_enabled:
                return jsonify(resp)

            user = get_current_user()

            filter_dict(resp, filtered_keys_by_role[user.role])
            return jsonify(resp)

        return inner

    return decorator


def get_current_user():
    """
    Retrieve user and user's role from the authenticaton token.
    Abort when loggin as guest but guest is disactivated or the
    retrieved user does not have any eligible role.
    """
    if not auth_enabled:
        return abort(403, "Authentication has \
            to be enabled to retrieve current user")

    token = retrieve_token()

    try:
        user = User.verify_auth_token(token)
    except AuthenticationError:
        return abort(403, "authentication failed")
    except AllUnauthorizedError:
        return abort(403, "access forbidden to role all")

    if user is None:
        return abort(403, "authentication failed")
    return user


def retrieve_token():
    """
    Return token from the header content after 'Authorization'
    if 'Authorization' figured in the header and if the content
    is not empty after 'Authorization'.
    """
    if 'Authorization' not in request.headers:
        return abort(403, "No valid token provided")

    token = request.headers['Authorization'].split()[1]
    if token is None:
        return abort(403, "No valid token provided")
    return token


def fill_job_user(job):
    uid = job['user_id']
    uid_s = str(uid)
    if uid_s not in uids:
        pw = pwd.getpwuid(uid)
        uids[uid_s] = {}
        uids[uid_s]['login'] = pw[0]
        # user name is the first part of gecos
        uids[uid_s]['username'] = pw[4].split(',')[0]
    job['login'] = uids[uid_s]['login']
    job['username'] = uids[uid_s]['username']
