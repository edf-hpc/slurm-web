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

from flask import (Flask, jsonify, request, abort, send_from_directory,
                   render_template)
import pyslurm
import json
import os

# check SLURM_WEB_CLUSTER_MOCK environment variable
# if it exists, load the mock context and setup
if os.getenv('SLURM_WEB_CLUSTER_MOCK') is not None:
    from mocks.setup import setup_mock
    setup_mock(os.environ['SLURM_WEB_CLUSTER_MOCK'])

# for racks description
from slurmweb.restapi.racks import parse_racks

# for CORS
from slurmweb.restapi.cors import crossdomain
from slurmweb.restapi.settings import settings

# for authentication
from slurmweb.restapi.auth import (User, authentication_verify,
                  AuthenticationError, AllUnauthorizedError,
                  guests_allowed, auth_enabled, fill_job_user,
                  get_current_user, CORSForbidden)

from slurmweb.restapi.cache import get_from_cache

# for nodeset conversion
from ClusterShell.NodeSet import NodeSet
import unicodedata

app = Flask(__name__)

origins = settings.get('cors', 'authorized_origins')


@app.errorhandler(403)
def custom403(error):
    response = jsonify({'message': error.description})
    response.status_code = 403

    # This error handle bypasses the @crossdomain decorator so we must do part
    # of its job here. If the request is done with CORS, the Origin header is
    # set and the browser enforces the presence of Access-Control-Allow-Origin
    # in the response header. Then set the latter with the value of the former
    # if existing.
    if 'Origin' in request.headers:
        response.headers['Access-Control-Allow-Origin'] = \
            request.headers['Origin']

    return response


@app.route('/version', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins)
def version():
    return "Slurm-web REST API v2.2"


@app.route('/login', methods=['POST', 'OPTIONS'])
@crossdomain(origin=origins, methods=['POST'],
             headers=['Accept', 'Content-Type', 'X-Requested-With'])
def login():
    if not auth_enabled:
        abort(404)

    data = json.loads(request.data)
    if data.get('guest', None) is True:
        try:
            user = User.guest()
        except AuthenticationError:
            abort(403, "Guests users are not allowed.")
        except AllUnauthorizedError:
            abort(403, "You do not have any role for this cluster")
    elif data.get('trusted_source', None) is True:
        try:
            source = request.remote_addr
            user = User.trusted_source(source)
        except AuthenticationError:
            abort(403, "Unrecognized source.")
        except AllUnauthorizedError:
            abort(403, "No role authorized for this source.")
    else:
        try:
            user = User.user(data['login'],
                             data['password'])
        except AuthenticationError:
            abort(403, "Your login / password doesn't match.")
        except AllUnauthorizedError:
            abort(403, "You do not have any role for this cluster")

    token = user.generate_auth_token()
    resp = {
        'id_token':         token,
        'login':            user.login,
        'role':             user.role,
        'name':             user.get_user_name(),
        'restricted_views': user.restricted_views()
    }
    return jsonify(resp)


@app.route('/jobs', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_jobs():
    jobs = get_from_cache(pyslurm.job().get, 'get_jobs')

    for jobid, job in jobs.iteritems():
        # add login and user's name (additionally to UID) for each job
        try:
            fill_job_user(job)
        except (KeyError):
            pass

        # convert nodeset in array of nodes
        if job["nodes"] is not None:
            jobs[jobid]["nodeset"] = list(
                NodeSet(job["nodes"].encode('ascii', 'ignore'))
            )
    return filter_entities('jobs', jobs)


@app.route('/job/<int:job_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def show_job(job_id):

    # PySLURM >= 16.05 expects a string in parameter of job.find_id() and
    # returns a list. The expected job dict is the 1st element of this list.
    job = get_from_cache(pyslurm.job().find_id, 'show_job', str(job_id))[0]
    onlyUsersJobs = False
    fill_job_user(job)
    if auth_enabled:
        # If auth_enabled is true, getting the current user becomes
        # possible because authentification_verify decorator has been
        # already checked.

        currentUser = get_current_user()
        onlyUsersJobs = check_private_data_for_entity(currentUser, 'jobs')

    if (onlyUsersJobs and job['login'] != currentUser.login):
        raise AllUnauthorizedError

    return job


@app.route('/nodes', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_nodes():

    nodes = get_from_cache(pyslurm.node().get, 'get_nodes')
    return nodes


@app.route('/cluster', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With'])
def get_cluster():

    nodes = pyslurm.node().get()
    cluster = {}
    cluster['name'] = pyslurm.config().get()['cluster_name']
    cluster['nodes'] = len(nodes.keys())
    cluster['cores'] = 0
    for nodename, node in nodes.iteritems():
        cluster['cores'] += node['cpus']
    resp = jsonify({
        'authentication': {
            'enabled': auth_enabled,
            'guest': guests_allowed
        },
        'data': cluster
    })
    return resp


@app.route('/racks', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_racks():
    try:
        racks = get_from_cache(parse_racks, 'get_racks')
    except Exception as e:
        racks = {'error': str(e)}
    return racks


@app.route('/reservations', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_reservations():

    reservations = get_from_cache(
        pyslurm.reservation().get, 'get_reservations')
    return filter_entities('reservations', reservations)


@app.route('/partitions', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_partitions():

    partitions = get_from_cache(pyslurm.partition().get, 'get_partitions')
    return partitions


def convert_tres_ids(numerical_tres):
    """
       Convert numerical_tres string by replacing all TRES IDs by their
       respective textual form. For ex:
         1=224,4=8 -> cpu=224,node=8

       Here is the TRES constant enum as defined in src/common/slurmdb_defs.h
       of Slurm source code:

         /* This is used to point out constants that exist in the
          * TRES records.  This should be the same order as
          * the enum pointing out the order in the array that is defined in
          * src/slurmctld/slurmctld.h
          */
         typedef enum {
                 TRES_CPU = 1,
                 TRES_MEM,
                 TRES_ENERGY,
                 TRES_NODE,
                 TRES_STATIC_CNT
         } tres_types_t;

    """
    # skip if value is None
    if numerical_tres is None:
        return None

    # map IDs with text according to enum over
    tres_map = {
        '1': 'cpu',
        '2': 'mem',
        '3': 'energy',
        '4': 'node'}
    tres_l = list()
    tres_e = numerical_tres.split(',')
    for tres in tres_e:
        (tres_type, tres_value) = tres.split('=')
        tres_l.append(tres_map[tres_type] + '=' + tres_value)
    return ','.join(tres_l)


@app.route('/qos', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_qos():

    try:
        qos = get_from_cache(pyslurm.qos().get, 'get_qos')
        # for all TRES limits of all QOS, replace TRES type IDs by their
        # textual form using tres_convert_ids()
        for qos_name in qos:
            xqos = qos[qos_name]
            for key, value in xqos.iteritems():
                if value is not None and key.find('_tres') > 0:
                    qos[qos_name][key] = convert_tres_ids(value)

    except Exception as e:
        qos = {'error': str(e)}
    return qos


@app.route('/topology', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_topology():

    try:
        topology = get_from_cache(pyslurm.topology().get, 'get_topology')
        # As of pyslurm 15.08.0~git20160229-2, switches and nodes dict members
        # are strings (or None eventually) representing the hostlist of devices
        # connected to the switch. These hostlist are expanded in lists using
        # Clustershell Nodeset() into new corresponding *list members.
        for switch in topology.itervalues():
            if switch['switches'] is not None:
                switch['switchlist'] = list(NodeSet(switch['switches']))
            if switch['nodes'] is not None:
                switch['nodelist'] = list(NodeSet(switch['nodes']))

    except Exception as e:
        topology = {'error': str(e)}
    return topology


# returns a dict composed with all jobs running on the given node
# with their ID as key
@app.route('/jobs-by-node/<node_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_jobs_by_node_id(node_id):

    jobs = get_from_cache(pyslurm.job().get, 'get_jobs')

    returned_jobs = {}

    # filter jobs by node
    for jobid, job in jobs.iteritems():
        nodes_list = job['cpus_allocated'].keys()
        if node_id in nodes_list:
            returned_jobs[jobid] = job

    for jobid, job in returned_jobs.iteritems():
        fill_job_user(job)

    return filter_entities('jobs', returned_jobs)


# returns a dict composed with all jobs running on the given nodes
# with their ID as key
@app.route('/jobs-by-node-ids', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_jobs_by_node_ids():

    jobs = get_from_cache(pyslurm.job().get, 'get_jobs')

    nodes = json.loads(request.data).get('nodes', [])

    returned_jobs = {}

    # filter jobs by node
    for jobid, job in jobs.iteritems():
        nodes_list = job['cpus_allocated'].keys()

        for node_id in nodes:
            if node_id in nodes_list:
                returned_jobs[jobid] = job

    for jobid, job in returned_jobs.iteritems():
        fill_job_user(job)

    return filter_entities('jobs', returned_jobs)


# returns a dict composed with all nodes ID as key associated to a dict
# composed by all jobs running on the concerned node
@app.route('/jobs-by-nodes', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_jobs_by_nodes():

    jobs = get_from_cache(pyslurm.job().get, 'get_jobs')
    nodes = get_from_cache(pyslurm.node().get, 'get_nodes')

    returned_nodes = {}

    for node_id, node in nodes.iteritems():
        returned_jobs = {}
        # filter jobs by node
        for jobid, job in jobs.iteritems():
            nodes_list = job['cpus_allocated'].keys()
            if node_id in nodes_list:
                returned_jobs[jobid] = job

        returned_nodes[node_id] = filter_entities('jobs', returned_jobs)

    return returned_nodes


# returns a dict composed with all qos ID as key associated to a dict
# composed by all jobs on the concerned node
@app.route('/jobs-by-qos', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def get_jobs_by_qos():

    jobs = get_from_cache(pyslurm.job().get, 'get_jobs')
    qos = get_from_cache(pyslurm.qos().get, 'get_qos')

    returned_qos = {}

    for qos_id, q in qos.iteritems():
        returned_jobs = {}
        # filter jobs by node
        for jobid, job in jobs.iteritems():
            if qos_id == job['qos']:
                returned_jobs[jobid] = job

        returned_qos[qos_id] = filter_entities('jobs', returned_jobs)

    return returned_qos


@app.route('/nodeset', methods=['POST', 'OPTIONS'])
@crossdomain(origin=origins, methods=['POST'],
             headers=['Accept', 'Content-Type', 'X-Requested-With'])
def convert_nodeset():

    data = json.loads(request.data)
    return json.dumps(list(NodeSet(data['nodeset'].encode('ascii', 'ignore'))))


@app.route('/sinfo', methods=['GET', 'OPTIONS'])
@crossdomain(origin=origins, methods=['GET'],
             headers=['Accept', 'Content-Type', 'X-Requested-With', 'Authorization'])
@authentication_verify()
def sinfo():

    # Partition and node lists are required
    # to compute sinfo informations
    partitions = get_from_cache(pyslurm.partition().get, 'get_partitions')
    nodes = get_from_cache(pyslurm.node().get, 'get_nodes')

    # Retreiving the state of each nodes
    nodes_state = dict(
        (node.lower(), attributes['state'].lower())
        for node, attributes in nodes.iteritems()
    )

    # For all partitions, retrieving the states of each nodes
    sinfo_data = {}
    for name, attr in partitions.iteritems():

        for node in list(NodeSet(attr['nodes'])):
            key = (name, nodes_state[node])
            if key not in sinfo_data.keys():
                sinfo_data[key] = []
            sinfo_data[key].append(node)

    # Preparing the response
    resp = []
    for k, nodes in sinfo_data.iteritems():
        name, state = k
        partition = partitions[name]
        avail = partition['state'].lower()
        min_nodes = partition['min_nodes']
        max_nodes = partition['max_nodes']
        total_nodes = partition['total_nodes']
        job_size = "{0}-{1}".format(min_nodes, max_nodes)
        job_size = job_size.replace('UNLIMITED', 'infinite')
        time_limit = partition['max_time_str'].replace('UNLIMITED', 'infinite')

        # Creating the nodeset
        nodeset = NodeSet()
        map(nodeset.update, nodes)

        resp.append({
          'name': name,
          'avail': avail,
          'job_size': job_size,
          'time_limit': time_limit,
          'nodes': total_nodes,
          'state': state,
          'nodelist': str(nodeset),
        })

    # Jsonify <v0.11 can not work on lists, thus using json.dumps
    # And making sure headers are properly set
    indent = None
    separators = (',', ':')
    if app.config.get('JSONIFY_PRETTYPRINT_REGULAR', False) \
            and not request.is_xhr:
        indent = 2
        separators = (', ', ': ')
    return app.response_class(
        (json.dumps(resp, indent=indent, separators=separators), '\n'),
        mimetype='application/json')


# The purpose of the /proxy and /static routes is just to make CORS work on IE9
# with the help of xdomain.js. The dashboard requests /proxy on all clusters
# API servers when running with this browser. The REST API responds with a very
# small HTML code (rendered by templates/proxy.html) which simply includes
# static/xdomain.js and executes one JS function

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route('/proxy')
def proxy():
    masters = ", ".join(map(lambda s: "\"%s\": \"*\"" % s, origins.split(',')))
    return render_template('proxy.html',
                           url_root=request.url_root,
                           masters=masters)


def check_private_data_for_entity(user, entity):
    """
    Return true if the entity is one of the attribute defined previously in
    Private Data settings.
    """
    onlyUsersEntities = False

    if auth_enabled:
        # Fetch the attributs of private_data
        config = pyslurm.config().get()
        private_data = config["private_data_list"]

        if (private_data and entity in private_data and
                user.role != 'admin'):
            onlyUsersEntities = True
    return onlyUsersEntities


def filter_entities(entity, entitiesList):
    """
    Return the list entities filtered if privateData is on for the entities.
    """
    onlyUsersEntities = False
    if auth_enabled:
        # If auth_enabled is true, getting the current user becomes
        # possible because authentification_verify decorator has been
        # already checked.
        currentUser = get_current_user()
        onlyUsersEntities = check_private_data_for_entity(
            currentUser, entity)

    if onlyUsersEntities:
        # if private data is applied and the entities' owner is different from
        # current user, then the entities will not be added to the list to
        # show if auth disabled, onlyUsersEntities becomes always False and all
        # the entities are added to the list to show

        return dict((k, v) for k, v in entitiesList.iteritems()
                    if ((entity == 'reservations' and currentUser.login in
                        v['users']) or (entity == 'jobs' and
                        currentUser.login == v['login'])))

    return entitiesList


if __name__ == '__main__':
    app.run(debug=True)
