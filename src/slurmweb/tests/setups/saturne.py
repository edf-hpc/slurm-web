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

import time

from setups.generic import ClusterSetup
from mocks.ldap import UserBase, User
from mocks.pyslurm import SlurmCtld, SlurmNode, SlurmPartition, SlurmQos, SlurmJob
from mocks.racks import MockRacksXML

def setup_cluster():

    name = u"saturne"
    print("setting up cluster %s" % (name))
    setup = ClusterSetup(name)
    setup.conf = {
            'cors': {
                'authorized_origins': 'http://10.5.0.1:8080',
            },
            'config': {
                'authentication': 'enable',
                'racksxml': '/etc/slurm-web/racks.xml',
            },
            'roles': {
                'guests': 'enabled',
                'all': 'enabled',
                'user': '@user',
                'admin': '@admin',
                'restricted_fields_for_all': 'command',
                'restricted_fields_for_user': 'command',
                'restricted_fields_for_admin': '',
            },
            'acl': {
            },
            'ldap': {
                'uri': 'ldap://localhost:ldap',
                'base_people': 'ou=people,dc=cluster,dc=local',
                'base_group': 'ou=group,dc=cluster,dc=local',
                'expiration': '1296000',
            },
            'cache': {
                'redis_host': '',
                'redis_port': '',
                'jobs_expiration': '',
                'global_expiration': '',
            }
    }

    setup.racks = MockRacksXML()
    setup.racks.add_nodetype('nodetype1', 'model type 1', '1', '1')
    row = setup.racks.add_racksrow('0')
    rack = setup.racks.add_rack(row, 'rack1', '0')
    setup.racks.add_nodeset(rack, 'cn[01-20]', 'nodetype1', '0', '2')

    setup.userbase = UserBase()
    setup.userbase.add(User('pierre', 'curie', 'toto', ['user', 'admin']))
    # define mcurie as regular user to test private_data
    setup.userbase.add(User('marie', 'curie', 'toto', ['user']))

    setup.ctld = SlurmCtld(name)
    # Set private_data configuration
    setup.ctld.private_data = 73
    setup.ctld.private_data_list = ['jobs', 'usage', 'reservations']
    for nodeid in range(1, 30):
        nodename = u"cn%02d" % (nodeid)
        node = SlurmNode(nodename)
        if nodeid == 3:
            node.state = 'MIXED'
        setup.ctld.nodes.add(node)

    partition = SlurmPartition('compute')
    partition.nodes = 'cn[01-30]'
    partition.total_nodes = 30
    partition.total_cpus = 8 * 30
    partition.total_mem = 1 * 30
    setup.ctld.partitions.add(partition)


    xqos = SlurmQos('qos_test')
    xqos.grp_jobs = 10
    xqos.max_tres_pj = u'1=224,4=8'
    xqos.priority = 100
    setup.ctld.qos.add(xqos)

    job = SlurmJob('1234')
    job.name = 'test.sh'
    job.qos = xqos.name
    job.job_state = 'RUNNING'
    job.nodes = 'cn03'
    job.num_nodes = 1
    job.num_cpus = 1
    job.start_time = int(time.time() - 10)
    job.time_limit = 3600
    job.cpus_allocated = { 'cn3': 1 }
    job.group_id = setup.userbase[0].gid
    job.user_id = setup.userbase[0].uid
    job.account = 'physic'
    job.shared = 2^16 - 2
    job.work_dir = u'/home/pierre'
    job.command = u'/home/pierre/sleep.sh'
    job.partition = partition.name
    setup.ctld.jobs.add(job)

    # Add another job from  diffrent user to test private_data
    job = SlurmJob('2235')
    job.name = 'test.sh'
    job.qos = xqos.name
    job.job_state = 'RUNNING'
    job.nodes = 'cn03'
    job.num_nodes = 1
    job.num_cpus = 1
    job.start_time = int(time.time() - 10)
    job.time_limit = 3600
    job.cpus_allocated = {'cn3': 1}
    job.group_id = setup.userbase[1].gid
    job.user_id = setup.userbase[1].uid
    job.account = 'physic'
    job.shared = 2 ^ 16 - 2
    job.work_dir = u'/home/pierre'
    job.command = u'/home/pierre/sleep.sh'
    job.partition = partition.name
    setup.ctld.jobs.add(job)

    return setup
