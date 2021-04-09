#!/usr/bin/env python
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

class ClusterSetup(object):

    def __init__(self, name):

        self.conf = None
        self.racks = None
        self.userbase = None
        self.ctld = None

    def feed_mocks(self):
        """Bind mocks global vars with attributes."""

        context.USERBASE = self.userbase
        context.CONF = self.conf
        context.CTLD = self.ctld
        print("feeding mocks CTLD: userbase: %s" % (str(context.CTLD)))
