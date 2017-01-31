# -*- coding: utf-8 -*-
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


import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
from pySICMgui.toolStagePT1 import Ui__ToolStagePT1

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class WidgetToolStagePT1(QtGui.QWidget, Ui__ToolStagePT1):
    preferredSize = [216, 136]
    def __init__ (self, mainwin, parent=None):
        super(WidgetToolStagePT1, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Control PT1 Stage')
        self.mainwin = mainwin
        self.parent = parent
        self.client = self.mainwin.client
        self.setConnections()

    def setConnections(self):
        self.buttonHome.clicked.connect(self.home)
        self.buttonUp.clicked.connect(self.up)
        self.buttonDown.clicked.connect(self.down)
        self.buttonGoto.clicked.connect(self.goto)


    def _sendCommand(self, command, param=''):
        self.client.sendLine('SET mode=toolStagePT1')
        self.client.sendLine('SET toolStagePT1.command='+str(command));
        self.client.sendLine('SET toolStagePT1.param='+str(param));
        self.client.sendLine('SCAN')

    def up(self):
        self._sendCommand('up', self.lineEditUpDown.text())

    def down(self):
        self._sendCommand('down', self.lineEditUpDown.text())

    def goto(self):
        self._sendCommand('down', self.lineEditGoto.text())

    def home(self):
        self._sendCommand('home')
