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

from PyQt4.QtGui import QDialog
import PyQt4.QtCore as QtCore
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from serversettings import Ui_ServerSettings
class DialogServerSettings(QDialog, Ui_ServerSettings):
    def __init__(self, parent=None):
        super(DialogServerSettings, self).__init__(parent)
        self.setupUi(self)
        
        
    @staticmethod
    def getServerSettings(parent=None):
        dialog = DialogServerSettings(parent)
        ip = parent.config['controller']['ipaddress'].split('.')
        dialog.lineEditIP1.setText(ip[0])
        dialog.lineEditIP2.setText(ip[1])
        dialog.lineEditIP3.setText(ip[2])
        dialog.lineEditIP4.setText(ip[3])
        dialog.lineEditPort.setText(str(parent.config['controller']['port']))
        result =  dialog.exec_()
        ipaddress = ".".join([str(_fromUtf8(dialog.lineEditIP1.text())),
                              str(_fromUtf8(dialog.lineEditIP2.text())),
                              str(_fromUtf8(dialog.lineEditIP3.text())),
                              str(_fromUtf8(dialog.lineEditIP4.text()))])
        port = dialog.lineEditPort.text()
        
        return (result==QDialog.Accepted, ipaddress, port)
                    
