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

import argparse
import sys
import os

default_host = '127.0.0.1'
default_port = 5000
default_app = 'rest'
default_setup = 'simple'

parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host",
                    help="Hostname of the Flask app " + \
                         "[default %s]" % default_host,
                    default=default_host)
parser.add_argument("-P", "--port",
                    help="Port for the Flask app " + \
                         "[default %s]" % default_port,
                    default=default_port)
parser.add_argument("-A", "--app",
                    help="Application to run (rest or conf) " + \
                         "[default %s]" % default_app,
                    default=default_app)
parser.add_argument("-S", "--setup",
                    help="REST API setup to load " + \
                         "[default %s]" % default_setup,
                    default=default_setup)

parser.add_argument("-d", "--debug",
                    action="store_true")

args = parser.parse_args()

if args.debug:
    print("path: %s" % (str(sys.path)))

if args.app == 'rest':

    from mocks.pyslurm import MockPySlurm
    from mocks.ldap import MockLdap
    from mocks.settings import MockConfigParserModule

    sys.modules['pyslurm'] = MockPySlurm
    sys.modules['ldap'] = MockLdap
    sys.modules['ConfigParser'] = MockConfigParserModule

    os.environ['SLURM_WEB_CLUSTER_MOCK'] = args.setup
    from slurmweb.restapi.slurmrestapi import app

elif args.app == 'conf':

    from slurmweb.confdashboard.slurmwebconf import app

else:
    print("unknown app %s" % (args.app))
    sys.exit(1)


app.run(debug=args.debug,
        host=args.host,
        port=int(args.port))
