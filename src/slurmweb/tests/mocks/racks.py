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

from xml.dom.minidom import DOMImplementation

class MockRacksXML(object):

    def __init__(self):
        """
          <?xml version="1.0" encoding="UTF-8"?>
          <!DOCTYPE rackmap SYSTEM "/usr/share/slurm-web/restapi/schema/dtd/racks.dtd">
          <rackmap>
            <nodetypes/>
            <racks posx="0" posy="0" width="10" depth="10"/>
          </rackmap>
        """

        self.imp = DOMImplementation()
        self.doctype = self.imp.createDocumentType(
            qualifiedName='rackmap',
            publicId='',
            systemId='/usr/share/slurm-web/restapi/schema/dtd/racks.dtd',
        )
        self.doc = self.imp.createDocument(None, 'rackmap', self.doctype)

        #self.root = self.doc.createElement('rackmap')
        #self.doc.appendChild(self.root)

        self.root = self.doc.documentElement

        self.nodetypes = self.doc.createElement('nodetypes')
        self.root.appendChild(self.nodetypes)
        self.racks = self.doc.createElement('racks')
        self.racks.setAttribute('posx', '0')
        self.racks.setAttribute('posy', '0')
        self.racks.setAttribute('width', '10')
        self.racks.setAttribute('depth', '10')
        self.root.appendChild(self.racks)

    def add_nodetype(self, name, model, height, width):
        """
           <nodetype id="m32x4321"
              model="Vendor A 32 x4321"
              height="1"
              width="0.5"
              />
        """
        nodetype = self.doc.createElement('nodetype')

        nodetype.setAttribute("id", name)
        nodetype.setAttribute("model", model)
        nodetype.setAttribute("height", height)
        nodetype.setAttribute("width", width)

        self.nodetypes.appendChild(nodetype)

    def add_racksrow(self, posx):
        """
          <racksrow posx="0"/>
          Return the <racksrow/> element.
        """
        racksrow = self.doc.createElement('racksrow')
        racksrow.setAttribute('posx', posx)
        self.racks.appendChild(racksrow)
        return racksrow

    def add_rack(self, row, name, posy):
        """
          <rack id="A1" posy="0">
            <nodes/>
          </rack>
          Return <nodes/> element.
        """
        rack = self.doc.createElement('rack')
        rack.setAttribute('id', name)
        rack.setAttribute('posy', posy)
        row.appendChild(rack)
        nodes = self.doc.createElement('nodes')
        rack.appendChild(nodes)
        return nodes

    def add_nodeset(self, nodes, nodelist, nodetype, posx, posy, draw=None):
        """
          <nodeset id="cn[505-518]"
                   type="m32x4321"
                   posx="0"
                   posy="2"
                   draw="down" />
        """
        nodeset = self.doc.createElement('nodeset')
        nodeset.setAttribute('id', nodelist)
        nodeset.setAttribute('type', nodetype)
        nodeset.setAttribute('posx', posx)
        nodeset.setAttribute('posy', posy)
        if draw is not None:
            nodeset.setAttribute('draw', draw)
        nodes.appendChild(nodeset)
