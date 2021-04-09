Slurm-web tests
===============

Quickstart
----------

This directory contains scripts and various modules to run an emulated testing
environment for Slurm-web.

First install all slurm-web deps:

* apache2
* libapache2-mod-wsgi
* python-flask
* python-pyslurm (>= 15.08.0~git20160229-2)
* clustershell
* python-ldap
* python-itsdangerous
* python-redis
* javascript-common
* libjs-bootstrap
* libjs-jquery
* libjs-jquery-flot
* libjs-jquery-tablesorter
* libjs-requirejs
* libjs-requirejs-text
* libjs-three (>= 72)
* libjs-bootstrap-typeahead
* libjs-bootstrap-tagsinput
* libjs-d3
* libjs-handlebars
* libjs-async

Or you can use the more conveniant requirements.txt file:
```
    $ pip install -r requirements.txt
```

(Please checkout `debian/control` file to get an updated list of slurm-web
dependencies.)

Then install the slurm-web-confdashboard package because it is not emulated yet
by the testing scripts.

Then add the following content to
`/etc/slurm-web/dashboard/clusters.config.json`:

```
[
  {
    "name": "saturne",
    "api": {
      "url": "http://10.5.0.1:2000",
      "path": ""
    }
  },
  {
    "name": "jupiter",
    "api": {
      "url": "http://10.5.0.1:2001",
      "path": ""
    }
  }
]
```

Finally, the testing environment is created using the script:

    $ python tests/run-testbed.py

It is recommended to run this script as a simple user and avoid root superuser.

Internal
--------

This script does basically the 4 following things:

- Setup the $PYTHONPATH to add the tests, dashboard and rest dirs into Python
  modules lookups paths. It uses environment variable because it spawns other
  processes and the PYTHONPATH must be set for all those processes.
- Launches the slurm-web backend Flask app to deliver dashboard/conf/* files.
- Launches the slurm-web REST API Flask app,
- Runs a HTTP server to serve the dashboard and redirect connections to various
  other HTTP servers.

The role of this HTTP server is to:

- deliver the HTML and CSS files of the dashboard.
- reverse-proxy for slurm-web backend using the previously launched Flask app
- reverse-proxy external javascript/css libraries using localhost:80 HTTP server
- redirect (301 for GET, 307 for POST) requests to the REST API server

We can use redirect for REST API server because it supports CORS, whereas the
backend and system HTTP server do not.

The Flask apps are launched using the tests/run-app.py script with various
parameters. All available parameters and their default values can be get with:

    $ python tests/run-app.py -h

When this script launches the REST API Flask app, it also plugs mocked PySlurm
and LDAP modules to avoid using the real libraries and provide fake data.

It also set the SLURM_WEB_CLUSTER_MOCK environment variable. When it is set,
the REST API Flask app guesses it runs in development mode and it should setup
all the mocks with fake data before responding to the first request. The value
of the environment variable is the name of the setup module (as available in
tests/setups/*.py) to load to setup the mocks data.

An environment variable is used for this purpose because Flask/Werkzeug spawns
a sub-processes to server HTTP requests, then all the real mocks must be setup
in the context that process. There is no other easy/obvious way to give this
kind of information to the Flask app.

The Flask REST API set the mocks with the plug_mocks() function with
@before_first_request decorator, which makes Flask run the function before
responding to the first HTTP request.
