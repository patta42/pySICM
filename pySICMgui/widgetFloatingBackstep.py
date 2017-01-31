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
'''This module implements a widget that allows reading a Analog Input channel 
on the controller'''


from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLayout, QVBoxLayout, QPalette, QSpinBox, QLabel
from pySICMgui.defaultScanwidget import DefaultScanWidget
import matplotlib.pyplot
import matplotlib.colors
import json, time, struct, numpy, datetime
import pySICM.helpers as Helpers

from matplotlibwidget import MatplotlibWidget
from pySICMgui.DataDisplayWidget import DataDisplayWidget
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class WidgetFloatingBackstep(DefaultScanWidget):

    def __init__ (self, mainwin, parent = None, **kwargs):
        super(WidgetFloatingBackstep, self).__init__(mainwin, parent, mode='floatingBackstep', **kwargs)
        self.setWindowTitle('Floating Backstep Scan')
        self.populateForm()
        
        self.addGraph('data',xlabel='x',ylabel='y')
        self.addGraph('prescan',xlabel='x',ylabel='y')
        self.progressBar.setValue(0)
        self.data = numpy.zeros((128,128), numpy.uint16)
        self.data = numpy.outer(
            numpy.linspace(0,numpy.sqrt(256),128),
            numpy.linspace(0,numpy.sqrt(256),128))

        self.predata = numpy.ones((128,128), numpy.uint16)
        self.getGraph('data').update(self.data)
        self.getGraph('prescan').update(self.data)
        if kwargs:
            if 'data' in kwargs:
                self.getGraph('prescan').update(kwargs['data'])

    def addGraph(self, name, **kwargs):
        mpw = DataDisplayWidget()
        self._graphs[name] = mpw
        if name=='prescan':
            self.dataLayout.addWidget(mpw,0,0)
        else:
            mpw.asNewScanCallback = self.asNewScan
            self.dataLayout.addWidget(mpw,0,1)
            

        
    def getSetting(self, setting): 
        if setting in self.settingConvertFuncs:
            return self.settingConvertFuncs[setting](self.settings[setting].text())

    def sendSettings(self):
        client = self.mainwin.client
        client.sendLine('SET mode=floatingBackstep')
        for setting, field in self.settings.iteritems():
            client.sendLine('SET floatingBackstep.'+str(setting)+'='+str(field.text()))

    def _prepare(self):
        self.mainwin.serverLog=str(time.time())
        self.sendSettings()
        xl = int(self.settings['x-px'].text())
        yl = int(self.settings['y-px'].text())
        xlp = int(self.settings['x-px-pre'].text())
        ylp = int(self.settings['y-px-pre'].text())
        self.data = numpy.zeros((xl, yl), numpy.uint16)
        self.prescan = numpy.zeros((xlp, ylp), numpy.uint16)
        self.progressBar.setMaximum(xlp*ylp)
        self.mainwin.stat.progressBar.setMaximum(xl*yl+xlp*ylp)
        self.expectData(self.updateData, length = 1, form = 'int', rang=[0, 2**16])
        self.x = -1
        self.y = 0
        self.min_data = None
        self.max_data = None
        self.lastDraw = time.time()

    def fake(self):
        self._prepare()
        self.receiveData('FAKE')

    def updateData(self, data, *args):
        finished = False
        self.x+=1
        if self.isPrescan:
            if self.x >=  int(self.settings['x-px-pre'].text()):
                self.y += 1
                self.x = 0
            if self.y  < int(self.settings['y-px-pre'].text()):
                self.prescan[self.y, self.x] = data[0]
                
            if self.x + 1 == int(self.settings['x-px-pre'].text()) and self.y +1 == int(self.settings['y-px-pre'].text()):
                print "Prescan finished"
                self.info['client_prescan_end_timestamp'] = int( round( time.time() * 1e3 ) )
                self.info['client_prescan_duration'] = self.info['client_prescan_end_timestamp'] - self.info['client_prescan_start_timestamp']
                self.info['client_scan_start_timestamp'] = int( round( time.time() * 1e3 ) )
                self.info['client_scan_start_time'] = str( datetime.datetime.now() )
                self.x = -1
                self.y = 0
                self.isPrescan = False
                xl = int(self.settings['x-px'].text())
                yl = int(self.settings['y-px'].text())
                self.progressBar.setMaximum(xl*yl)
                self.getGraph('prescan').update(self.prescan)

            mpw = self.getGraph('prescan')
            d = self.prescan
            progress = int(self.settings['x-px-pre'].text())*self.y+self.x
            total_progress = progress
        else:
            if self.x >=  int(self.settings['x-px'].text()):
                self.y += 1
                self.x = 0
            if self.y  < int(self.settings['y-px'].text()):
                self.data[self.y, self.x] = data[0]

            if self.x +1 == int(self.settings['x-px'].text()) and self.y +1 == int(self.settings['y-px'].text()):
                print "Scan finished"
                finished = True
                self.info['client_scan_end_timestamp'] = int( round( time.time() * 1e3 ) )
                self.info['client_scan_duration'] = self.info['client_scan_end_timestamp'] - self.info['client_scan_start_timestamp']
                self.unexpectData()
                self.lastDraw = 0
                
            d = self.data
            mpw = self.getGraph('data')
            total_progress = (int(self.settings['x-px-pre'].text())
                              *int(self.settings['y-px-pre'].text())
                              +int(self.settings['x-px'].text())
                              *self.y+self.x)
            
            progress = int(self.settings['x-px'].text())*self.y+self.x 

        if time.time() - self.lastDraw > .2 or finished:
            mpw.update(d)
            self.progressBar.setValue(progress)
            self.mainwin.stat.progressBar.setValue(total_progress)
            self.lastDraw = time.time()

#        if finished:
#            
#            try:
                

    def scan(self):
        self._prepare()
        self.isPrescan = True
        self.receiveData('SCAN')
        self.info['client_prescan_start_time'] = str(datetime.datetime.now())
        self.info['client_prescan_start_timestamp'] = int( round( time.time() * 1e3 ) )
                        
    def stop(self):
        self.mainwin.client.sendLine('STOP')
        self.unexpectData()

    def asNewScan(self, selection, data):
        settings = {}
        for k,v in self.settings.iteritems():
            settings[k] = v.text()
        xpxsize = self.getSetting('x-Size') / self.getSetting('x-px')
        ypxsize = self.getSetting('y-Size') / self.getSetting('y-px')

        xoff = round(selection['x']) * xpxsize + self.getSetting('XOffset')
        yoff = round(selection['y']) * ypxsize + self.getSetting('YOffset')
        settings['XOffset'] = str(xoff)
        settings['YOffset'] = str(yoff)
        settings['x-Size'] = str(round(selection['w']) * xpxsize)
        settings['y-Size'] = str(round(selection['w']) * xpxsize)
        self.mainwin.openScanModeWin('floatingBackstep', data=data, settings=settings)
        print "As new scan..."
