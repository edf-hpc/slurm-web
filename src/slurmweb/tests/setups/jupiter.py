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

from ClusterShell.NodeSet import NodeSet
from setups.generic import ClusterSetup
from mocks.ldap import UserBase, User
from mocks.pyslurm import SlurmCtld, SlurmNode, SlurmPartition, SlurmQos, SlurmJob, SlurmTopology
from mocks.racks import MockRacksXML

def setup_cluster():

    name = u"jupiter"
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
                'all': 'disabled',
                'user': '@user',
                'admin': '@admin',
                'restricted_fields_for_all': 'command',
                'restricted_fields_for_user': 'command',
                'restricted_fields_for_admin': '',
            },
            'acl': {
            },
            'ldap': {
                'uri': 'ldaps://localhost:ldaps',
                'base_people': 'ou=people,dc=cluster,dc=local',
                'base_group': 'ou=group,dc=cluster,dc=local',
                'expiration': '1296000',
                'cacert': '/path/to/cert'
            },
            'cache': {
                'redis_host': '',
                'redis_port': '',
                'jobs_expiration': '',
                'global_expiration': '',
            }
    }

    setup.racks = MockRacksXML()
    setup.racks.add_nodetype('blade', 'blade x2', '4', str(1./5))
    #setup.racks.add_nodetype('blade', 'blade x2', '1', str(1./2))
    row = setup.racks.add_racksrow('0')
    rack = setup.racks.add_rack(row, 'A', '0')
    setup.racks.add_nodeset(rack, 'cn[001-040]', 'blade', '0', '2')
    rack = setup.racks.add_rack(row, 'B', '0')
    setup.racks.add_nodeset(rack, 'cn[041-080]', 'blade', '0', '2')
    rack = setup.racks.add_rack(row, 'C', '0')
    setup.racks.add_nodeset(rack, 'cn[081-120]', 'blade', '0', '2')
    rack = setup.racks.add_rack(row, 'D', '0')
    setup.racks.add_nodeset(rack, 'cn[121-160]', 'blade', '0', '2')
    rack = setup.racks.add_rack(row, 'E', '0')
    setup.racks.add_nodeset(rack, 'cn[161-200]', 'blade', '0', '2')
    rack = setup.racks.add_rack(row, 'F', '0')
    setup.racks.add_nodeset(rack, 'cn[201-240]', 'blade', '0', '2')

    setup.userbase = UserBase()
    setup.userbase.add(User('pierre', 'curie', 'toto', ['user','admin']))
    setup.userbase.add(User('marie', 'curie', 'toto', ['user','admin']))
    setup.userbase.add(User('jacques', 'curie', 'toto', ['user']))
    setup.userbase.add(User('thomas', 'curie', 'toto', []))

    setup.ctld = SlurmCtld(name)
    setup.ctld.private_data = 0
    setup.ctld.private_data_list = []
    nodeset = NodeSet('cn[001-240]')

    for nodename in nodeset:
        node = SlurmNode(nodename)
        node.cpus = 24
        node.cores = node.cpus / node.sockets
        setup.ctld.nodes.add(node)

    partition = SlurmPartition('compute')
    partition.nodes = str(nodeset)
    partition.total_nodes = len(nodeset)
    partition.total_cpus = 10 * partition.total_nodes
    partition.total_mem = 1 * partition.total_nodes
    setup.ctld.partitions.add(partition)

    switch = SlurmTopology('swibmaster1')
    switch.switches = 'swibleaf[1-8]'
    switch.nodes = 'cn[001-240]'
    switch.level = 1
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibmaster2')
    switch.switches = 'swibleaf[1-8]'
    switch.nodes = 'cn[001-240]'
    switch.level = 1
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf1')
    switch.nodes = 'cn[001-030]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf2')
    switch.nodes = 'cn[031-060]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf3')
    switch.nodes = 'cn[061-090]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf4')
    switch.nodes = 'cn[091-120]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf5')
    switch.nodes = 'cn[121-150]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf6')
    switch.nodes = 'cn[151-180]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf7')
    switch.nodes = 'cn[181-210]'
    setup.ctld.topology.add(switch)
    switch = SlurmTopology('swibleaf8')
    switch.nodes = 'cn[211-240]'
    setup.ctld.topology.add(switch)

    xqos = SlurmQos('qos_test')
    xqos.grp_jobs = 10
    xqos.max_tres_pj = u'1=224,4=8'
    xqos.priority = 100
    setup.ctld.qos.add(xqos)

    first_id = 1235
    # get the number of cpus from the first node
    nb_cores = list(setup.ctld.nodes)[0].cpus

    for jobid in range(first_id, first_id+1000):

        nodename = nodeset[int((jobid-first_id)/nb_cores)]
        node = setup.ctld.find_node(nodename)
        #cpu = node.alloc_cpus  # pick up the first not allocated cpu

        job = SlurmJob(str(jobid))
        job.name = 'test.sh'
        job.qos = xqos.name
        job.job_state = 'RUNNING'
        job.nodes = nodename
        job.num_nodes = 1
        job.num_cpus = 1
        job.start_time = int(time.time() - 10)
        job.time_limit = 3600
        job.cpus_allocated = { nodename: 1 }
        job.group_id = setup.userbase[0].gid
        job.user_id = setup.userbase[0].uid
        job.account = 'physic'
        job.shared = 2^16 - 2
        job.work_dir = u'/home/pierre'
        job.command = u'/home/pierre/test.sh'
        job.partition = partition.name
        if jobid > 1245:
            job.wckey = u'Routine'
        else:
            job.wckey = u'Confidential'
        setup.ctld.jobs.add(job)

        node.alloc_cpus += 1
        if node.alloc_cpus == node.cpus:
            node.state = u"ALLOCATED"
        else:
            node.state = u"MIXED"

    return setup
