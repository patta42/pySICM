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
class HandledAction:
    action=None
    function=None
    mdiArea=None
    def __init__(self, action, function, mdiArea):
        self.action = action
        self.function = function
        self.mdiArea = mdiArea
        self.action.triggered.connect(self.actionCalled)

    def actionCalled(self):
        widget = self.mdiArea.currentSubWindow().widget()
        try:
            getattr(widget, self.function)()
        except AttributeError:
            getattr(widget, self.function)()
            print "Widget "+str(widget)+" does not implement a method "+str(self.function)

    def setEnabledStatus(self):
        swin = self.mdiArea.currentSubWindow()
        if swin is not None:
            widget = swin.widget()
        else:
            widget = None
        self.action.setEnabled(hasattr(widget, self.function))
            
class ActionHandler:
    '''This class automates the support of calling a specific function in a
    MdiArea-subwindow if the corresponding widget contains the respective
    function. The main window should inherit from this class.'''

    handlers = []

    def __init__(self):
        pass

    def addActionHandler(self, action, funcname):
        self.handlers.append(HandledAction(action, funcname, self.mdiArea))

    def setEnabledStatus(self):
        for ac in self.handlers:
            ac.setEnabledStatus()

