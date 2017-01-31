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

from PyQt4.QtGui import QWidget
from PyQt4 import QtCore
import clientwindow 

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class WidgetClientWindow(QWidget, clientwindow.Ui_ClientWindow):
    
    def __init__ (self, mainwin, parent = None):
        super(WidgetClientWindow, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.client = mainwin.client
        self.mainwin = mainwin
        self.setupUi(self)
        self.pushButton.clicked.connect(self.sendMessage)
        self.callbacks = []
        self.callbacks.append({
            'add' : self.mainwin.addCallback,
            'del' : self.mainwin.removeCallback,
            'cbs' : {
                'serverLogAdd': [self.updateText],
                'connectionChanged' : [self.enableOrDisable]
            }})
        self.handleCallbacks('add')
        self.plainTextEdit.appendPlainText("\n".join(map(str, self.mainwin.serverLog)))
        self.enableOrDisable(self.mainwin.connected)

    def handleCallbacks(self, fnckey):
        for cbstruct in self.callbacks:
            fnc = cbstruct[fnckey]
            for k, v in cbstruct['cbs'].iteritems():
                for cb in v:
                    fnc(k, cb)

    def enableOrDisable(self, connected, *args):
        self.lineEdit.setEnabled(connected)
        self.plainTextEdit.setEnabled(connected)
        self.pushButton.setEnabled(connected)

    def sendMessage(self):
        self.client.sendLine(str(_fromUtf8(self.lineEdit.text())))
        self.lineEdit.setText('')

    def updateText(self, orig, processed, *args, **kwargs):
        self.plainTextEdit.appendPlainText(orig)
        return orig

    def closeEvent(self, e):
        self.handleCallbacks('del')
        self.mainwin.hasControllerWin=False

