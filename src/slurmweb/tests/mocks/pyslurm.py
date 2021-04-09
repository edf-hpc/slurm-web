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

import time
from ClusterShell.NodeSet import NodeSet
from mocks import context

class SlurmCluster(object):

    def __init__(self, name):

        self.name = name
        self.cores = 0

class SlurmNode(object):
    """
    Example of a node dict as returned by pyslurm.node().get()['cn1'] with
    Slurm 15.08:

    u'cn1': {
      'features': 'f1',
      'weight': 1,
      'energy': {
        'current_watts': 0,
        'consumed_energy': 0,
        'base_consumed_energy': 0,
        'previous_consumed_energy': 0,
        'base_watts': 0
      },
      'cpus': 8,
      'alloc_memory': 0,
      'cpu_spec_list': 'f1',
      'owner': 4294967294,
      'gres_drain': [],
      'real_memory': 1,
      'tmp_disk': 0,
      'slurmd_start_time': 1468911427,
      'reason_time': 0,
      'sockets': 2,
      'state': 'IDLE',
      'version': u'15.08',
      'node_hostname': u'cn1',
      'total_cpus': 8,
      'power_mgmt': {},
      'core_spec_cnt': 0,
      'err_cpus': 0,
      'reason': None,
      'alloc_cpus': 0,
      'threads': 1,
      'boot_time': 1468911393,
      'cores': 4,
      'reason_uid': 4294967294,
      'node_addr': u'cn1',
      'arch': u'x86_64',
      'name': u'cn1',
      'boards': 1,
      'gres': [],
      'free_mem': 127,
      'tres_fmt_str': u'cpu=8,mem=1',
      'gres_used': [],
      'mem_spec_limit': 0,
      'os': u'Linux',
      'cpu_load': 1
    }
    """
    def __init__(self, name):

        self.name = name
        self.cpus = 8
        self.sockets = 2
        self.alloc_cpus = 0
        self.cores = 4
        self.total_cpus = 8
        self.real_memory = 1
        self.alloc_memory = 0
        self.free_mem = 127
        self.state = 'IDLE'
        self.reason = None

        # settings with sane defaults
        self.features = []
        self.weight = 1
        self.energy_current_watts = 0
        self.energy_consumed = 0
        self.energy_base_consumed = 0
        self.energy_previous_consumed = 0
        self.energy_base_watts = 0
        self.threads = 1
        self.boards = 1
        self.cpu_spec_list = []
        self.owner = 2^32 - 2
        self.gres_drain = []
        self.tmp_disk = 0
        self.boot_time = int(time.time())
        self.slurmd_start_time = int(time.time())
        self.reason_time = 0
        self.version = u'15.08'
        self.node_hostname = self.name
        self.power_mgmt = {}
        self.core_spec_cnt = 0
        self.err_cpus = 0
        self.reason_uid = 2^32 - 2
        self.node_addr = self.name
        self.arch = u'x86_64'
        self.gres = []
        self.gres_used = []
        self.mem_spec_limit = 0
        self.os = u'Linux'
        self.cpu_load = 1

    @property
    def tres_fmt_str(self):
        return u"cpu=%d,mem=%d" % (self.cpus, self.real_memory)

    def todict(self):
        return { self.name: {
            'features': self.features,
            'weight': self.weight,
            'energy': {
                'current_watt': self.energy_current_watts,
                'consumed_energy': self.energy_consumed,
                'base_consumed_energy': self.energy_base_consumed,
                'previous_consumed_energy': self.energy_previous_consumed,
                'base_watts': self.energy_base_watts,
            },
            'cpus': self.cpus,
            'alloc_memory': self.alloc_memory,
            'cpu_spec_list': self.cpu_spec_list,
            'owner': self.owner,
            'gres_drain': self.gres_drain,
            'real_memory': self.real_memory,
            'tmp_disk': self.tmp_disk,
            'slurmd_start_time': self.slurmd_start_time,
            'reason_time': self.reason_time,
            'sockets': self.sockets,
            'state': self.state,
            'version': self.version,
            'node_hostname': self.node_hostname,
            'total_cpus': self.total_cpus,
            'power_mgmt': self.power_mgmt,
            'core_spec_cnt': self.core_spec_cnt,
            'err_cpus': self.err_cpus,
            'reason': self.reason,
            'alloc_cpus': self.alloc_cpus,
            'threads': self.threads,
            'boot_time': self.boot_time,
            'cores': self.cores,
            'reason_uid': self.reason_uid,
            'node_addr': self.node_addr,
            'arch': self.arch,
            'name': self.name,
            'boards': self.boards,
            'gres': self.gres,
            'free_mem': self.free_mem,
            'trs_fmt_str': self.tres_fmt_str,
            'gres_used': self.gres_used,
            'mem_spec_limit': self.mem_spec_limit,
            'os': self.os,
            'cpu_load': self.cpu_load } }

class SlurmJob(object):
    """
    Example of a job dict as returned by pyslurm.job().get()[382] with
    Slurm 15.08:

    382: {
      u'qos': None,
      u'sicp_mode': 0,
      u'sockets_per_node': 65534,
      u'pn_min_tmp_disk': 0,
      u'job_state': 'RUNNING',
      u'bitflags': 0,
      u'cpu_freq_gov': 4294967294,
      u'ntasks_per_socket': 65535,
      u'nodes': u'cn1',
      u'suspend_time': 0,
      u'block_id': None,
      u'alloc_sid': 813,
      u'std_in': u'/dev/null',
      u'start_time': 1468912530,
      u'submit_time': 1468912530,
      u'rotate': False,
      u'name': u'sleep.sh',
      u'ntasks_per_board': 0,
      u'conn_type': 'n/a',
      u'cpus_allocated': {'cn1': 1},
      u'show_flags': 2,
      u'group_id': 10001,
      u'time_limit': 525600,
      u'alloc_node': u'login',
      u'std_out': None,
      u'tres_req_str': u'cpu=1,node=1',
      u'eligible_time': 1468912530,
      u'contiguous': False,
      u'ramdisk_image': None,
      u'req_switch': 0,
      u'licenses': {},
      u'state_desc': None,
      u'network': None,
      u'array_task_id': 4294967294,
      u'max_nodes': 0,
      u'reboot': None,
      u'num_nodes': 1,
      u'batch_script': None,
      u'batch_flag': 1,
      u'shared': 65534,
      u'end_time': 1500448530,
      u'ntasks_per_node': 0,
      u'cpu_freq_min': 4294967294,
      u'array_job_id': 0,
      u'pn_min_memory': 0,
      u'wckey': None,
      u'burst_buffer': None,
      u'time_min': 0,
      u'resize_time': 0,
      u'cores_per_socket': 65534,
      u'dependency': None,
      u'cpu_freq_max': 4294967294,
      u'resv_name': None,
      u'boards_per_node': 0,
      u'comment': None,
      u'features': [],
      u'preempt_time': 0,
      u'array_max_tasks': 0,
      u'user_id': 10001,
      u'ntasks_per_core': 65535,
      u'work_dir': u'/home/pierre',
      u'assoc_id': 0,
      u'priority': 4294901759,
      u'power_flags': 0,
      u'pn_min_cpus': 1,
      u'billable_tres': 4294967294.0,
      u'linux_image': None,
      u'ionodes': None,
      u'blrts_image': None,
      u'tres_alloc_str': u'cpu=1,node=1',
      u'wait4switch': 0,
      u'account': None,
      u'gres': [],
      u'batch_host': u'cn1',
      u'requeue': True,
      u'exc_nodes': [],
      u'std_err': None,
      u'cnode_cnt': None,
      u'array_task_str': None,
      u'command': u'/home/pierre/sleep.sh',
      u'resv_id': None,
      u'state_reason': 'None',
      u'num_cpus': 1,
      u'exit_code': 0,
      u'mloader_image': None,
      u'max_cpus': 0,
      u'nice': 10000,
      u'profile': 0,
      u'altered': None,
      u'cpus_per_task': 1,
      u'req_nodes': [],
      u'pre_sus_time': 0,
      u'restart_cnt': 0,
      u'partition': 'normal',
      u'core_spec': 65534,
      u'derived_ec': 0,
      u'sockets_per_board': 0,
      u'threads_per_core': 65534
    }
    """
    def __init__(self, jobid):

        self.jobid = jobid
        self.name = None
        self.qos = None
        self.job_state = 'PENDING'
        self.nodes = None
        self.num_nodes = 1
        self.num_cpus = 1
        self.start_time = 0
        self.time_limit = 3600
        self.cpus_allocated = {}
        self.group_id = 10001
        self.user_id = 10001
        self.account = None
        self.shared = 2^16 - 2
        self.work_dir = u'/home/pierre'
        self.command = u'/home/pierre/sleep.sh'
        self.partition = 'normal'

        # settings with sane defaults
        self.sicp_mode = 0
        self.sockets_per_node = 2^16 - 2
        self.pn_min_tmp_disk = 0
        self.bitflags = 0
        self.cpu_freq_gov = 2^32 - 2
        self.ntasks_per_socket = 2^16 - 1
        self.suspend_time = 0
        self.block_id = None
        self.alloc_sid = 813  # ?
        self.std_in = u'/dev/null'
        self.std_out = None
        self.std_err = None
        self.submit_time = int(time.time())
        self.eligible_time = self.submit_time
        self.rotate = False
        self.ntasks_per_board = 0
        self.conn_type = 'n/a'
        self.show_flags = 2
        self.assoc_id = 0
        self.alloc_node = u'login'
        self.contiguous = False
        self.ramdisk_image = None
        self.req_switch = 0
        self.licenses = {}
        self.state_desc = None
        self.network = None
        self.array_task_id = 2^32 - 2
        self.max_nodes = 0
        self.reboot = None
        self.batch_script = None
        self.batch_flag = 1
        self.ntasks_per_node = 0
        self.cpu_freq_min = 2^32 - 2
        self.array_job_id = 0
        self.pn_min_memory = 0
        self.wckey = None
        self.burst_buffer = None
        self.time_min = 0
        self.resize_time = 0
        self.cores_per_socket = 2^16 - 2
        self.dependency = None
        self.cpu_freq_max = 2^32 - 2
        self.resv_name = None
        self.boards_per_node = 0
        self.comment = None
        self.features = []
        self.preempt_time = 0
        self.array_max_tasks = 0
        self.ntasks_per_core = 2^16 - 1
        self.priority = 1
        self.power_flags = 0
        self.pn_min_cpus = 1
        self.billable_tres = float(2^32 - 2)
        self.linux_image = None
        self.ionodes = None
        self.blrts_image = None
        self.tres_alloc_str = self.tres_req_str
        self.wait4switch = 0
        self.gres = []
        self.requeue = True
        self.exc_nodes = []
        self.cnode_cnt = None
        self.array_task_str = None
        self.resv_id = None
        self.state_reason = 'None'
        self.exit_code = 0
        self.mloader_image = None
        self.max_cpus = 0
        self.nice = 10000
        self.profile = 0
        self.altered = None,
        self.cpus_per_task = 1
        self.req_nodes = []
        self.pre_sus_time = 0
        self.restart_cnt = 0
        self.core_spec = 2^16 - 2
        self.derived_ec = 0
        self.sockets_per_board = 0
        self.threads_per_core = 2^16 - 2

    @property
    def end_time(self):
        return self.start_time + self.time_limit

    @property
    def tres_req_str(self):
        return u'cpu=%s,node=%s' % (self.num_cpus, self.num_nodes)

    @property
    def batch_host(self):
        """If nodes allocated to job, batch_host is the first allocated node,
           None otherwise."""
        if self.nodes is None:
            return None
        return NodeSet(self.nodes)[0]

    def todict(self):

      return { self.jobid: {
          u'qos': self.qos,
          u'sicp_mode': self.sicp_mode,
          u'sockets_per_node': self.sockets_per_node,
          u'pn_min_tmp_disk': self.pn_min_tmp_disk,
          u'job_state': self.job_state,
          u'bitflags': self.bitflags,
          u'cpu_freq_gov': self.cpu_freq_gov,
          u'ntasks_per_socket': self.ntasks_per_socket,
          u'nodes': self.nodes,
          u'suspend_time': self.suspend_time,
          u'block_id': self.block_id,
          u'alloc_sid': self.alloc_sid,
          u'std_in': self.std_in,
          u'start_time': self.start_time,
          u'submit_time': self.submit_time,
          u'rotate': self.rotate,
          u'name': self.name,
          u'ntasks_per_board': self.ntasks_per_board,
          u'conn_type': self.conn_type,
          u'cpus_allocated': self.cpus_allocated,
          u'show_flags': self.show_flags,
          u'group_id': self.group_id,
          u'time_limit': self.time_limit,
          u'alloc_node': self.alloc_node,
          u'std_out': self.std_out,
          u'tres_req_str': self.tres_req_str,
          u'eligible_time': self.eligible_time,
          u'contiguous': self.contiguous,
          u'ramdisk_image': self.ramdisk_image,
          u'req_switch': self.req_switch,
          u'licenses': self.licenses,
          u'state_desc': self.state_desc,
          u'network': self.network,
          u'array_task_id': self.array_task_id,
          u'max_nodes': self.max_nodes,
          u'reboot': self.reboot,
          u'num_nodes': self.num_nodes,
          u'batch_script': self.batch_script,
          u'batch_flag': self. batch_flag,
          u'shared': self.shared,
          u'end_time': self.end_time,
          u'ntasks_per_node': self.ntasks_per_node,
          u'cpu_freq_min': self.cpu_freq_min,
          u'array_job_id': self.array_job_id,
          u'pn_min_memory': self.pn_min_memory,
          u'wckey': self.wckey,
          u'burst_buffer': self.burst_buffer,
          u'time_min': self.time_min,
          u'resize_time': self.resize_time,
          u'cores_per_socket': self.cores_per_socket,
          u'dependency': self.dependency,
          u'cpu_freq_max': self.cpu_freq_max,
          u'resv_name': self.resv_name,
          u'boards_per_node': self.boards_per_node,
          u'comment': self.comment,
          u'features': self.features,
          u'preempt_time': self.preempt_time,
          u'array_max_tasks': self.array_max_tasks,
          u'user_id': self.user_id,
          u'ntasks_per_core': self.ntasks_per_core,
          u'work_dir': self.work_dir,
          u'assoc_id': self.assoc_id,
          u'priority': self.priority,
          u'power_flags': self.power_flags,
          u'pn_min_cpus': self.pn_min_cpus,
          u'billable_tres': self.billable_tres,
          u'linux_image': self.linux_image,
          u'ionodes': self.ionodes,
          u'blrts_image': self.blrts_image,
          u'tres_alloc_str': self.tres_alloc_str,
          u'wait4switch': self.wait4switch,
          u'account': self.account,
          u'gres': self.gres,
          u'batch_host': self.batch_host,
          u'requeue': self.requeue,
          u'exc_nodes': self.exc_nodes,
          u'std_err': self.std_err,
          u'cnode_cnt': self.cnode_cnt,
          u'array_task_str': self.array_task_str,
          u'command': self.command,
          u'resv_id': self.resv_id,
          u'state_reason': self.state_reason,
          u'num_cpus': self.num_cpus,
          u'exit_code': self.exit_code,
          u'mloader_image': self.mloader_image,
          u'max_cpus': self.max_cpus,
          u'nice': self.nice,
          u'profile': self.profile,
          u'altered': self.altered,
          u'cpus_per_task': self.cpus_per_task,
          u'req_nodes': self.req_nodes,
          u'pre_sus_time': self.pre_sus_time,
          u'restart_cnt': self.restart_cnt,
          u'partition': self.partition,
          u'core_spec': self.core_spec,
          u'derived_ec': self.derived_ec,
          u'sockets_per_board': self.sockets_per_board,
          u'threads_per_core': self.threads_per_core } }

class SlurmPartition(object):
    """
    Example of a partition dict as returned by pyslurm.partition().get()['cn1'] with
    Slurm 15.08:

    u'normal': {
      u'billing_wights_str': None,
      u'def_mem_per_cpu': 0,
      u'max_mem_per_cpu': 0,
      u'allow_alloc_nodes': [],
      u'total_nodes': 3,
      u'min_nodes': 1,
      u'deny_accounts': [],
      u'preempt_mode': 'GANG,UNKNOWN',
      u'deny_qos': [],
      u'allow_qos': [],
      u'cr_type': 0,
      u'alternate': None,
      u'priority': 1,
      u'nodes': 'cn[1-3]',
      u'total_cpus': 24,
      u'tres_fmt_str': u'cpu=24,mem=3,node=3',
      u'default_time': 'no_value',
      u'qos_char': None,
      u'allow_accounts': [],
      u'max_cpus_per_node': 4294967295,
      u'max_share': 1,
      u'name': u'normal',
      u'grace_time': 0,
      u'flags': {
        u'RootOnly': 0,
        u'Default': 1,
        u'DisableRootJobs': 0,
        u'ExclusiveUser': 0,
        u'LLN': 0,
        u'Shared': u'EXCLUSIVE',
        u'Hidden': 0
      },
      u'state_up': 'up',
      u'max_time': 4294967295,
      u'max_nodes': 4294967295,
      u'allow_groups': []
    }
    """
    def __init__(self, name):

        self.name = name
        self.total_nodes = 0
        self.nodes = None,
        self.total_cpus = 0
        self.total_mem = 0  # used for tres_fmt_str

        # settings with sane defaults
        self.billing_wights = None
        self.def_mem_per_cpu =  0
        self.max_mem_per_cpu = 0
        self.allow_alloc_nodes = []
        self.min_nodes = 1
        self.deny_accounts = []
        self.preempt_mode = 'GANG,UNKNOWN'
        self.deny_qos = []
        self.allow_qos = []
        self.cr_type = 0
        self.alternate = None
        self.priority = 1
        self.default_time = 'no_value'
        self.qos_char = None
        self.allow_accounts = []
        self.max_cpus_per_node = 2^32 - 1
        self.max_share = 1
        self.grace_time = 0
        self.flag_root_only = 0
        self.flag_default = 1
        self.flag_disable_root_jobs = 0
        self.flag_exclusive_user = 0
        self.flag_lln = 0
        self.flag_shared = u'EXCLUSIVE'
        self.flag_hidden = 0
        self.state_up = 'up',
        self.max_time = 2^32 - 1
        self.max_nodes = 2^32 - 1
        self.allow_groups = []

    @property
    def tres_fmt_str(self):
        return u"cpu=%d,mem=%d,node=%d" % \
                   (self.total_cpus,
                    self.total_mem,
                    self.total_nodes)

    def todict(self):
        return { self.name: {
            u'billing_wights_str': self.billing_wights,
            u'def_mem_per_cpu': self.def_mem_per_cpu,
            u'max_mem_per_cpu': self.max_mem_per_cpu,
            u'allow_alloc_nodes': self.allow_alloc_nodes,
            u'total_nodes': self.total_nodes,
            u'min_nodes': self.min_nodes,
            u'deny_accounts': self.deny_accounts,
            u'preempt_mode': self.preempt_mode,
            u'deny_qos': self.deny_qos,
            u'allow_qos': self.allow_qos,
            u'cr_type': self.cr_type,
            u'alternate': self.alternate,
            u'priority': self.priority,
            u'nodes': self.nodes,
            u'total_cpus': self.total_cpus,
            u'tres_fmt_str': self.tres_fmt_str,
            u'default_time': self.default_time,
            u'qos_char': self.qos_char,
            u'allow_accounts': self.allow_accounts,
            u'max_cpus_per_node': self.max_cpus_per_node,
            u'max_share': self.max_share,
            u'name': self.name,
            u'grace_time': self.grace_time,
            u'flags': {
                u'RootOnly': self.flag_root_only,
                u'Default': self.flag_default,
                u'DisableRootJobs': self.flag_disable_root_jobs,
                u'ExclusiveUser': self.flag_exclusive_user,
                u'LLN': self.flag_lln,
                u'Shared': self.flag_shared,
                u'Hidden': self.flag_hidden
            },
            u'state_up': self.state_up,
            u'max_time': self.max_time,
            u'max_nodes': self.max_nodes,
            u'allow_groups': self.allow_groups } }

class SlurmReservation(object):
    """
    Example of a reservation dict as returned by
    pyslurm.reservation().get()['pierre_2'] with Slurm 15.08:

    'pierre_2': {
      u'features': [],
      u'resv_watts': 4294967294,
      u'start_time': 1468918170,
      u'partition': None,
      u'node_list': u'cn3',
      u'flags': 'SPEC_NODES',
      u'end_time': 1468918530,
      u'accounts': [],
      u'burst_buffer': [],
      u'licenses': {},
      u'core_cnt': 8,
      u'tres_str': u'cpu=8',
      u'node_cnt': 1,
      u'users': ['pierre']
    }
    """
    def __init__(self, name):

        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.node_list = None
        self.core_cnt = 0
        self.node_cnt = 1
        self.users = []

        # settings with sane defaults
        self.features = []
        self.resv_watts = 2^32 - 2
        self.partition = None
        self.flags = 'SPEC_NODES'
        self.accounts = []
        self.burst_buffer = []
        self.licenses = {}

    @property
    def tres_str(self):
      return u"cpu=%d" % (self.core_cnt)

    def todict(self):
        return { self.name: {
            u'features': self.features,
            u'resv_watts': self.resv_watts,
            u'start_time': self.start_time,
            u'partition': self.partition,
            u'node_list': self.node_list,
            u'flags': self.flags,
            u'end_time': self.end_time,
            u'accounts': self.accounts,
            u'burst_buffer': self.burst_buffer,
            u'licenses': self.licenses,
            u'core_cnt': self.core_cnt,
            u'tres_str': self.tres_str,
            u'node_cnt': self.node_cnt,
            u'users': self.users } }


class SlurmQos(object):
    """
    Example of a QOS dict as returned by pyslurm.qos().get()['cn_0224c_048h']
    with Slurm 15.08:

    'cn_0224c_048h': {
      u'grp_tres': None,
      u'grp_tres_mins': None,
      u'grp_tres_run_mins': None,
      u'grp_jobs': 100,
      u'max_tres_mins_pj': None,
      u'preempt_mode': 'OFF',
      u'usage_factor': 1.0,
      u'max_tres_pn': None,
      u'max_tres_pj': u'1=224,4=8',
      u'priority': 300,
      u'max_tres_pu': None,
      u'description': u'cn_0224c_048h',
      u'usage_thres': 4294967295.0,
      u'grp_submit_jobs': 200,
      u'grp_wall': 4294967295,
      u'min_tres_pj': u'1=1',
      u'name': u'cn_0224c_048h',
      u'grace_time': 0,
      u'max_jobs_pu': 8,
      u'max_submit_jobs_pu': 4294967295,
      u'max_tres_run_mins_pu': None,
      u'flags': 0,
      u'max_wall_pj': 2880
    }
    """
    def __init__(self, name):

        self.name = name
        self.grp_jobs = 0
        self.grp_submit_jobs = 0
        self.max_jobs_pu = 2^32 - 1
        self.max_tres_pj = None
        self.max_wall_pj = 2^32 - 1
        self.priority = 0

        # settings with sane defaults
        self.grp_tres = None
        self.grp_tres_mins = None
        self.grp_tres_run_mins = None
        self.max_tres_mins_pj = None
        self.preempt_mode = 'OFF'
        self.usage_factor = 1.0
        self.max_tres_pn = None
        self.max_tres_pu = None
        self.description = self.name
        self.usage_thres =  float(2^32 - 1)
        self.grp_wall = 2^32 - 1
        self.min_tres_pj = u'1=1'
        self.grace_time = 0
        self.max_submit_jobs_pu = 2^32 - 1
        self.max_tres_run_mins_pu = None
        self.flags = 0

    def todict(self):
        return { self.name: {
            u'grp_tres': self.grp_tres,
            u'grp_tres_mins': self.grp_tres_mins,
            u'grp_tres_run_mins': self.grp_tres_run_mins,
            u'grp_jobs': self.grp_jobs,
            u'max_tres_mins_pj': self.max_tres_mins_pj,
            u'preempt_mode': self.preempt_mode,
            u'usage_factor': self.usage_factor,
            u'max_tres_pn': self.max_tres_pn,
            u'max_tres_pj': self.max_tres_pj,
            u'priority': self.priority,
            u'max_tres_pu': self.max_tres_pu,
            u'description': self.description,
            u'usage_thres': self.usage_thres,
            u'grp_submit_jobs': self.grp_submit_jobs,
            u'grp_wall': self.grp_wall,
            u'min_tres_pj': self.min_tres_pj,
            u'name': self.name,
            u'grace_time': self.grace_time,
            u'max_jobs_pu': self.max_jobs_pu,
            u'max_submit_jobs_pu': self.max_submit_jobs_pu,
            u'max_tres_run_mins_pu': self.max_tres_run_mins_pu,
            u'flags': self.flags,
            u'max_wall_pj': self.max_wall_pj } }


class SlurmTopology(object):
    """
    Example of a topology dict as returned by
    pyslurm.topology().get()['switch2'] with Slurm 15.08:

    u'switch2': {
      u'link_speed': 1,
      u'switches': u'swib[1-2]',
      u'nodes': u'pocg[001-042]',
      u'name': u'switch[1-2]',
      u'level': 0
    }
    """
    def __init__(self, switch):

        self.switch = switch
        self.switches = None
        self.nodes = None
        self.level = 0

        # settings with sane defaults
        self.link_speed = 1

    def todict(self):

        return { self.switch: {
            u'link_speed': self.link_speed,
            u'switches': self.switches,
            u'nodes': self.nodes,
            u'name': self.switch,
            u'level': self.level } }

class SlurmCtld(object):

    def __init__(self, cluster):

        self.cluster = SlurmCluster(cluster)
        self.nodes = set()
        self.partitions = set()
        self.jobs = set()
        self.qos = set()
        self.reservations = set()
        self.topology = set()
        # Add private_data to mock config()
        self.private_data = set()
        self.private_data_list = set()

    @property
    def config(self):
        return {
            u'cluster_name': self.cluster.name,
            # Add private_data to mock config()
            u'private_data': self.private_data,
            u'private_data_list': self.private_data_list}

    def find_node(self, nodename):
        for node in self.nodes:
            if node.name == nodename:
                return node
        return None

class MockPySlurmConfig(object):

    def get(self):
        return context.CTLD.config


class MockPySlurmNode(object):

    def get(self):
        result = None
        for node in context.CTLD.nodes:
            if result is None:
                result = node.todict().copy()
            else:
                result.update(node.todict())
        if result is None:
            result = {}
        return result


class MockPySlurmJob(object):

    def get(self):
        result = None
        for job in context.CTLD.jobs:
            if result is None:
                result = job.todict().copy()
            else:
                result.update(job.todict())
        if result is None:
            result = {}
        return result

    def find_id(self, jobid):
        for job in context.CTLD.jobs:
            if job.jobid == jobid:
                return [job.todict()[jobid]]
        return None

class MockPySlurmReservation(object):

    def get(self):
        result = None
        for reservation in context.CTLD.reservations:
            if result is None:
                result = reservation.todict().copy()
            else:
                result.update(reservation.todict())
        if result is None:
            result = {}
        return result


class MockPySlurmPartition(object):

    def get(self):
        result = None
        for partition in context.CTLD.partitions:
            if result is None:
                result = partition.todict().copy()
            else:
                result.update(partition.todict())
        if result is None:
            result = {}
        return result


class MockPySlurmQOS(object):

    def get(self):
        result = None
        for xqos in context.CTLD.qos:
            if result is None:
                result = xqos.todict().copy()
            else:
                result.update(xqos.todict())
        if result is None:
            result = {}
        return result


class MockPySlurmTopology(object):

    def get(self):
        result = None
        for switch in context.CTLD.topology:
            if result is None:
                result = switch.todict().copy()
            else:
                result.update(switch.todict())
        if result is None:
            result = {}
        return result


class MockPySlurm(object):

    config = MockPySlurmConfig
    node = MockPySlurmNode
    job = MockPySlurmJob
    reservation = MockPySlurmReservation
    partition = MockPySlurmPartition
    qos = MockPySlurmQOS
    topology = MockPySlurmTopology
