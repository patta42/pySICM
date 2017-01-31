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
from _statusbar import Ui_ExtStatusBar

class StatusbarWidget(QWidget, Ui_ExtStatusBar):
    def __init__(self, parent = None):
        super(StatusbarWidget, self).__init__(parent)
        self.setupUi(self)
        
    def setGeneralInformation(self, txt):
        self.general_information.setText(txt)
