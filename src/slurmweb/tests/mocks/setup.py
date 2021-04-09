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

import importlib
import mock
from mocks.ldap import mock_getpwuid, mock_getpwnam

def setup_mock(context):

    setup_m = importlib.import_module('setups.' + context)

    setup = setup_m.setup_cluster()
    setup.feed_mocks()

    xml_s = setup.racks.doc.toprettyxml(indent='  ', encoding='UTF-8').strip()
    m_open = mock.mock_open(read_data=xml_s)
    p_open = mock.patch("racks.open", m_open, create=True)
    p_open.start()

    m_getpwuid = mock.Mock()
    m_getpwuid.side_effect = mock_getpwuid
    p_getpwuid = mock.patch("pwd.getpwuid", m_getpwuid, create=True)
    p_getpwuid.start()

    m_getpwnam = mock.Mock()
    m_getpwnam.side_effect = mock_getpwnam
    p_getpwnam = mock.patch("pwd.getpwnam", m_getpwnam, create=True)
    p_getpwnam.start()
