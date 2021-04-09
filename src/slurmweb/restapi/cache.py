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
#
#
# Decorator for cache mechanism

try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False

import json
from functools import wraps
from slurmweb.restapi.settings import settings
from configparser import NoOptionError, NoSectionError


def get_int_setting(param, default):
    try:
        port = settings.get('cache', param)
        return not port and default or int(port)
    except ValueError as e:
        print("Error while parsing %s, check restapi.conf : %s" % \
                (param, str(e)))
    except (NoOptionError, NoSectionError):
        return default


try:
    if settings.get('config', 'cache') == 'enable':
        if redis_available:
            enabled = True
            try:
                redis_host = settings.get('cache', 'redis_host') or 'localhost'
            except (NoOptionError, NoSectionError):
                redis_host = 'localhost'

            redis_port = get_int_setting('redis_port', 6379)
            jobs_expiration = get_int_setting('jobs_expiration', 10)
            global_expiration = get_int_setting('global_expiration', 60)

            if redis_available:
                r = redis.Redis(redis_host, redis_port)

    else:
        enabled = False
        print(("Package python-redis unavailable, cache mechanism won't" +
               "be enabled"))

except (NoOptionError, NoSectionError):
    enabled = False


def get_from_cache(f, overrideName=None, *args, **kwargs):
    """Return cached entities according to input function f if cache enabled.
       The name of the input function is used as cache key unless overrideName
       is set."""

    if not enabled:
        return f(*args, **kwargs)

    cache_key = "%s-%s" % (
        f.__name__ if overrideName is None else overrideName,
        ''.join("%s-%r" % (key, val) for (key,
                                          val) in kwargs.iteritems())
    )

    try:

        data = r.get(cache_key)
        if data is not None:
            print("get %s from cache" % cache_key)
            return json.loads(data)

        if 'job' in f.__name__:
            expiration = jobs_expiration
        else:
            expiration = global_expiration

        resp = f(*args, **kwargs)
        if isinstance(resp, dict):
            print("set %s in cache with expiration %d" % (cache_key,
                                                        expiration))
            r.set(cache_key, json.dumps(resp))
            r.expire(cache_key, expiration)

    except redis.ConnectionError:
        print("WARNING: ConnectionError from Redis, server unreachable")
        return f(*args, **kwargs)

    return resp
