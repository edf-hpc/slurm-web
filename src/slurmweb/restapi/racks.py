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

import xml.etree.ElementTree as ET
from ClusterShell.NodeSet import NodeSet
from slurmweb.restapi.settings import settings
from configparser import NoOptionError


class NodeType(object):

    def __init__(self, name, model, height, width):
        self.name = name
        self.model = model
        self.height = height
        self.width = width


class Racksrow(object):

    def __init__(self, posx, racks={}):
        self.posx = posx
        self.racks = racks

    @staticmethod
    def racksrow2dict(racksrow):
        xracks = {}
        for name, rack in racksrow.racks.iteritems():
            xracks[rack.name] = Rack.rack2dict(rack)
        return xracks

    @staticmethod
    def racksrow_array2dict_array(racksrows):
        xracksrows = []
        for racksrow in racksrows:
            xracksrows.append(Racksrow.racksrow2dict(racksrow))
        return xracksrows


class Rack(object):

    def __init__(self, name, posx, posy):
        self.name = name
        self.posx = posx
        self.posy = posy
        self.nodes = []  # list of nodes in the rack

    def __repr__(self):

        rackrepr = "rack %s (posx: %d, posy: %d):\n" % (self.name, self.posx,
                                                        self.posy)
        for node in self.nodes:
            rackrepr += " - %s\n" % (str(node))
        return rackrepr

    def _sort_nodes(self):
        self.nodes.sort(key=lambda node: node.name)

    @staticmethod
    def rack2dict(rack):
        xrack = {}
        xrack['name'] = rack.name
        xrack['posx'] = rack.posx
        xrack['posy'] = rack.posy
        xrack['nodes'] = []

        for node in rack.nodes:
            xrack['nodes'].append(Node.node2dict(node))
        return xrack


class Node(object):

    def __init__(self, name, rack, nodetype, posx, posy):

        self.name = name
        self.rack = rack
        self.nodetype = nodetype
        self.posx = posx
        self.posy = posy

    def __repr__(self):
        noderepr = "%s (model: %s, posx: %f, posy %f)" % (self.name,
                                                          self.nodetype.model,
                                                          self.posx, self.posy)
        return str(noderepr)

    @staticmethod
    def node2dict(node):
        xnode = {}
        xnode['name'] = node.name
        xnode['type'] = node.nodetype.model
        xnode['posx'] = node.posx
        xnode['posy'] = node.posy
        xnode['height'] = node.nodetype.height
        xnode['width'] = node.nodetype.width
        return xnode


def parse_racks():

    try:
        FILE = settings.get('config', 'racksxml')
    except NoOptionError:
        FILE = None
    if not FILE:
        FILE = '/etc/slurm-web/racks.xml'
    try:
        with open(FILE, 'r') as f_xml:
            xml_s = f_xml.read()
        root = ET.fromstring(xml_s)
    except ET.ParseError as error:
        print("parse error: %s" % (str(error)))
        return None

    # parse nodetypes and fill nodetypes dict with
    # NodeType objects
    nodetypes = {}
    nodetypes_e = root.find('nodetypes').findall('nodetype')
    for nodetype_e in nodetypes_e:
        nodetype = NodeType(nodetype_e.get('id'),
                            nodetype_e.get('model'),
                            float(nodetype_e.get('height')),
                            float(nodetype_e.get('width')))
        nodetypes[nodetype.name] = nodetype

    racks = []
    # parse racks with nodes
    racks_root_e = root.find('racks')

    posx = racks_root_e.get('posx') if racks_root_e.get('posx') else 0
    posy = racks_root_e.get('posy') if racks_root_e.get('posy') else 0
    width = racks_root_e.get('width') if racks_root_e.get('width') else 0
    depth = racks_root_e.get('depth') if racks_root_e.get('depth') else 0
    rackwidth = racks_root_e.get('rackwidth') if racks_root_e.get('rackwidth')\
        else 1

    room = {
        'posx': posx,
        'posy': posy,
        'width': width,
        'depth': depth,
        'rackwidth': rackwidth
    }

    racksrows_e = racks_root_e.findall('racksrow')
    for racksrow_e in racksrows_e:
        racks_posx = int(racksrow_e.get('posx')) \
            if racksrow_e.get('posx') else 0
        racksrow = {}
        racks_e = racksrow_e.findall('rack')

        for rack_e in racks_e:
            rack_posy = int(rack_e.get('posy')) if rack_e.get('posy') else 0
            rack = Rack(rack_e.get('id'), racks_posx, rack_posy)
            racksrow[rack.name] = rack

            # parse nodes
            nodes_e = rack_e.find('nodes').findall('node')
            for node_e in nodes_e:
                nodetype = nodetypes[node_e.get('type')]
                node_posx = float(node_e.get('posx')) \
                    if node_e.get('posx') else 0
                node_posy = float(node_e.get('posy')) \
                    if node_e.get('posy') else 0
                node = Node(node_e.get('id'), rack, nodetype, node_posx,
                            node_posy)
                # add node to rack
                rack.nodes.append(node)

            # parse nodesets
            nodesets_e = rack_e.find('nodes').findall('nodeset')
            for nodeset_e in nodesets_e:
                nodeset = NodeSet(nodeset_e.get('id'))
                draw_dir = 1 if (not nodeset_e.get('draw') or
                                 nodeset_e.get('draw') == "up") else -1
                nodetype = nodetypes[nodeset_e.get('type')]
                cur_x = float(nodeset_e.get('posx')) \
                    if nodeset_e.get('posx') else 0
                cur_y = float(nodeset_e.get('posy')) \
                    if nodeset_e.get('posy') else 0
                for xnode in nodeset:
                    node = Node(xnode, rack, nodetype, cur_x, cur_y)
                    rack.nodes.append(node)
                    cur_x += nodetype.width
                    if cur_x == 1:
                        cur_x = float(0)
                        cur_y += nodetype.height * draw_dir

        racks.append(Racksrow(racks_posx, racksrow))

    return {
        'racks': Racksrow.racksrow_array2dict_array(racks),
        'room': room
    }
