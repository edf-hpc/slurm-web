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

from flask import Flask, send_from_directory

app = Flask(__name__)

# Set SEND_FILE_MAX_AGE_DEFAULT to 0 in order to avoid caching effect on the
# dashboard configuration files. This way, configuration changes have effect
# as soon the configuration files change. Default Flask/Werkzeug value is 12h.
# With such value, admins necesseraly had to restart the backend web application
# in order to invalidate the cache when changing settings.
app.config.update(
    SEND_FILE_MAX_AGE_DEFAULT=0,
    SECRET_KEY='secret_key'
)

@app.route('/version', methods=['GET'])
def version():
    return "Slurm-web Dashboard Conf"


@app.route('/<path:path>', methods=['GET'])
def send_file(path):
    return send_from_directory('/etc/slurm-web/dashboard', path)


if __name__ == '__main__':
    app.run(debug=True)
