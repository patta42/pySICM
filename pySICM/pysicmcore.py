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

import sys, os
from pySICM.error import PySICMError
from PyQt4.QtGui import QApplication

class PySicmCore(object):
    '''PySicmCore is the core class of pySICM.'''
    SERVER = 0
    CLIENT = 1
    
    def __init__(self, mode):
        if mode not in [self.SERVER, self.CLIENT]:
            raise PySICMError('Core initialized with unknown mode. Mode was: '+str(mode))
        self._mode = mode
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
        if mode == self.SERVER:
            self._initServer()
        elif mode == self.CLIENT:
            self._initClient()



    def _initServer(self):
        
        pass
    def _initClient(self):
        self.app = QApplication(sys.argv)


        import pySICMgui.qt4reactor
        pySICMgui.qt4reactor.install()

        from twisted.internet import reactor

        import pySICMgui.pySICMgui
        
        self.window = pySICMgui.pySICMgui.PySICMGuiMainWindow(reactor)
        #self.window.show()
        reactor.run()
        
