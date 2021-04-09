#!usr/bin/env python
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

import re
from mocks import context

class User(object):

    next_uid = 10001

    def __init__(self, firstname, lastname, password, groups):

        self.firstname = firstname.capitalize()
        self.lastname = lastname.capitalize()
        self.password = password
        self.groups = groups
        # pickup the next UID and increment
        self.uid = User.next_uid
        User.next_uid += 1
        self.gid = self.uid

    @property
    def login(self):

        return self.firstname[0].lower() + self.lastname.lower()

    @property
    def name(self):
        return self.firstname + " " + self.lastname

    def __eq__(self, other):

        return self.firstname == other.firstname and self.lastname == other.lastname

    def __hash__(self):

        return hash(self.firstname + self.lastname)

class UserBase(object):

    def __init__(self):
        self._base = set()

    def add(self, user):
        self._base.add(user)

    def __getitem__(self, index):
        return list(self._base)[index]

    def __iter__(self):
        for user in self._base:
            yield user

    def find(self, login):
        for user in self._base:
            if user.login == login:
                return user
        return None

class ExceptionInvalidCredentials(Exception):
    pass

class ExceptionNoSuchObject(Exception):
    pass

class ExceptionServerDown(Exception):
    pass


class MockLdap(object):
    """Class to mock ldap module."""

    SCOPE_SUBTREE = 'foo'
    OPT_X_TLS_NEWCTX = 'foo'
    OPT_X_TLS_REQUIRE_CERT = 'foo'
    OPT_X_TLS_DEMAND = 'foo'
    OPT_X_TLS_CACERTFILE = 'foo'

    INVALID_CREDENTIALS = ExceptionInvalidCredentials
    NO_SUCH_OBJECT = ExceptionNoSuchObject
    SERVER_DOWN = ExceptionServerDown

    VERSION3 = 'foo'

    @staticmethod
    def set_option(*args):
        pass

    @staticmethod
    def initialize(uri):
        return MockLdapConn()

ldap = MockLdap  # alias

def mock_getpwuid(uid):

    result = list()
    for user in context.USERBASE:
        if user.uid == uid:
            result.append(user.login)
            result.append(None)
            result.append(None)
            result.append(None)
            result.append(user.name + ',')
            break
    return result


def mock_getpwnam(login):

    result = list()
    for user in context.USERBASE:
        if user.login == login:
            result.append(user.login)
            result.append(None)
            result.append(None)
            result.append(None)
            result.append(user.name + ',')
            break
    return result


class MockLdapConn(object):

    @staticmethod
    def extract_login(dn):
        """Extract login from dn using regexp."""
        match = re.search('uid=(.*?),', dn)
        login = match.group(1)
        print("login found in search filter: %s" % (login))
        return login

    def set_option(*args):
        pass

    def simple_bind_s(self, dn, password):

        login = MockLdapConn.extract_login(dn)
        user = context.USERBASE.find(login)
        if user is not None:
            if user.password == password:
                return  # OK
        # raise ldap.INVALID_CREDENTIALS on error
        raise ldap.INVALID_CREDENTIALS

    def search_s(self, base, scope, search_filter, attribs):
        # raise ldap.NO_SUCH_OBJECT on error
        # returns a list with group names in [1]['cn'][0]

        login = MockLdapConn.extract_login(search_filter)
        user = context.USERBASE.find(login)
        if user.groups is None:
            raise ldap.NO_SUCH_OBJECT
        return [ [ None, { 'cn': [ group, None ] } ] for group in user.groups ]

    def unbind_s(self):
        pass
