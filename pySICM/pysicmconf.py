# Copyright (C) 2015 Patrick Happel <patrick.happel@rub.de>
#
# This file is part of pySICM.
#
# pySICM is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# pySICM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pySICM. If not, see <http://www.gnu.org/licenses/>.

import os
#import pySICM.setup
import pySICM.helpers as Helpers
class _PysicmConfPaths(object):
    setupfile = '/etc/pySICM/setup.ini'
    scanmodesdir = '/home/happel/coding/python/sicm/scanmodes/'
    toolsdir = '/home/happel/coding/python/sicm/tools/'
    boardinfo = '/usr/local/bin/comedi_board_info'


class PysicmConf(object):
    '''Class containing the pySICM configuration (files etc)
    
    This class is used to store default file paths and so 
    on. For configuring the SICM setup, see the setup.ini 
    file.
    '''
        
    PATHS = _PysicmConfPaths()
    MODES = []
    HARDWARE = {}
    def __init__(self):
#        if RunningMode() == Helpers.SERVER:
        self._readscanmodes()
#        tmp = pySICM.setup.Setup()
#        self.HARDWARE = tmp.config 
    def _readscanmodes(self):
        l = os.listdir(self.PATHS.scanmodesdir)
        for f in l:
            if f.endswith('.py') and f[0] != '_':
                self.MODES.append(os.path.splitext(f)[0])
            
        l = os.listdir(self.PATHS.toolsdir)
        for f in l:
            if f.endswith('.py') and f[0] != '_':
                self.MODES.append('__tool__'+os.path.splitext(f)[0])

    
