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

import sys
import os
from subprocess import Popen
import http.server
import socketserver
import requests

host = '0.0.0.0'

tests_dir     = os.path.abspath(os.path.join(
                    os.path.realpath(__file__), '../..'))
dashboard_dir = os.path.abspath(os.path.join(
                    os.path.realpath(__file__), '../../../dashboard'))
os.environ['PYTHONPATH'] = "%s" % (tests_dir)

port = 2000
cmd = [ 'python', 'tests/run-app.py', '--debug',
        '--app', 'rest', '--setup', 'saturne',
        '--host', host, '--port', str(port) ]
p1 = Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

port = 2001
cmd = [ 'python', 'tests/run-app.py', '--debug',
        '--app', 'rest', '--setup', 'jupiter',
        '--host', host, '--port', str(port) ]
p1 = Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

port = 2010
cmd = [ 'python', 'tests/run-app.py', '--debug',
        '--app', 'conf', '--host', host, '--port', str(port) ]
p2 = Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

os.chdir(dashboard_dir)

def extract_ip_from_httphost(host):

    host_m = host.split(':')
    if len(host_m) >= 2:
        return host_m[0]
    return host

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/html/index.html'
        elif self.path == '/3d-view.html':
            self.path = '/html/3d-view.html'
        elif self.path.startswith('/css'):
            f = open(os.path.join(os.getcwd(), self.path[1:]))
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        elif self.path.startswith('/slurm-web-conf'):
            filename = self.path.split('/')[-1]
            r = requests.get('http://localhost:2010/' + filename)
            self.send_response(r.status_code)
            for key, value in r.headers.iteritems():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(r.content)
            return
        elif self.path.startswith('/javascript'):
            r = requests.get('http://localhost' + self.path)
            self.send_response(r.status_code)
            print("url: %s status_code: %d: headers: %s" \
                      % (r.url,
                         r.status_code,
                         str(r.headers)))
            for key, value in r.headers.iteritems():
                if key not in [ 'connection',
                                'keep-alive',
                                'content-encoding',
                                'content-length',
                                'accept-ranges' ]:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(r.content)
            return
        elif self.path.startswith('/slurm-restapi'):
            path = "/".join(self.path.split('/')[2:])
            ipaddr = extract_ip_from_httphost(self.headers['Host'])
            print("API path: %s" % (path))
            self.send_response(301)
            self.send_header('Location',"http://%s:2000/%s" % (ipaddr, path))
            self.end_headers()
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith('/slurm-restapi'):
            path = "/".join(self.path.split('/')[2:])
            ipaddr = extract_ip_from_httphost(self.headers['Host'])
            # temporary redirect to make browser send another POST
            self.send_response(307)
            self.send_header('Location',"http://%s:2000/%s" % (ipaddr, path))
            self.end_headers()
            return

Handler = MyRequestHandler
server = socketserver.TCPServer(('0.0.0.0', 8080), Handler)
server.serve_forever()

#p1.wait()
#p2.wait()
