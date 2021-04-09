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

from mocks import context


class MockNoSectionError(Exception):
    pass


class MockNoOptionError(Exception):
    pass


class MockConfigParserClass(object):

    def read(self, path):
        pass

    def get(self, section, option):

        if section not in context.CONF.keys():
            raise MockNoSectionError(section)
        if option not in context.CONF[section].keys():
            raise MockNoOptionError(section, option)
        return context.CONF[section][option]

    def has_option(self, section, option):
        if section not in context.CONF:
            raise MockNoSectionError(section)
        return option in context.CONF[section]

    def items(self, section):
        return context.CONF[section].keys()


class MockConfigParserModule(object):

    NoSectionError = MockNoSectionError
    NoOptionError = MockNoOptionError
    ConfigParser = MockConfigParserClass
