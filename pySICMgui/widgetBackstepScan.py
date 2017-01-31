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
import json, time, struct, numpy
import pySICM.helpers as Helpers
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class WidgetBackstepScan(DefaultScanWidget):

    def __init__ (self, mainwin, parent = None):
        super(WidgetBackstepScan, self).__init__(mainwin, parent)
        self.setWindowTitle('Backstep Scan')
        self.populateForm()
        self.addGraph('data',xlabel='x',ylabel='y')
        self.progressBar.setValue(0)
#        mainwin.progressBar.setValue(0)
        self.cyanAndRedHot={
            'red':   ((0.0, 0.0, 0.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 1.0, 1.0),
                      (1.0, 1.0, 1.0),),

            'green': ((0.0, 1.0, 1.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 0.0, 0.0),
                      (0.2+1.6/3.0, 1.0, 1.0),
                      (1.0, 1.0, 1.0)),

            'blue':  ((0.0, 1.0, 1.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 0.0, 0.0),
                      (0.2+1.6/3.0, 0.0, 0.0),
                      (1.0, 1.0, 1.0))
        }
        cm = matplotlib.colors.LinearSegmentedColormap('CyanAndRedHot', self.cyanAndRedHot)
        matplotlib.pyplot.register_cmap(cmap=cm)
        self.data = numpy.zeros((128,128))
        self.getGraph('data').axes.imshow(self.data, interpolation='none', cmap = 'CyanAndRedHot')
        self.getGraph('data').draw()
        
    def populateForm(self):
#        self.mainwin.client.sendLineAndGetAnswer('GET SICMINFO', self._populateFormCB)
        self._populateFormCB('')
        
    def _populateFormCB(self, config):
        #cfg = json.loads(config)
        #cfg = Helpers.makeDictKeysInt(cfg)

        self.addLineEdit('x-Size', 'Scan dimension in x-direction in micm (float)')
        self.addLineEdit('y-Size', 'Scan dimension in y-direction in micm (float)')
        self.addLineEdit('x-px', 'number of pixels in x-direction (int)')
        self.addLineEdit('y-px', 'number of pixels in y-direction (int)')
        self.addColumn()
        self.addLineEdit('Backstep', 'Vertical retraction distance in micm (int)')
        self.addLineEdit('FallRate', 'Fall rate in nm/ms (int)')
        self.addLineEdit('LateralSpeed', 'Lateral movement rate in nm/ms (int)')
        self.addLineEdit('Threshold', 'Stop threshold in percent (float)')
        self.addLineEdit('Sensitivity', 'Sensitivity in V/nA (float)')
        self.addLineEdit('Filter', 'Output filter in kHz (float)')

    def getSetting(self, setting): 
        if setting in self.settingConvertFuncs:
            self.settingConvertFuncs[setting](self.settings[setting].text())

    def sendSettings(self):
        client = self.mainwin.client
        client.sendLine('SET mode=backstepScan')
        for setting, field in self.settings.iteritems():
            client.sendLine('SET backstepScan.'+setting+'='+str(field.text()))
    def _prepare(self):
        self.mainwin.serverLog=str(time.time())
        self.sendSettings()
        xl = int(self.settings['x-px'].text())
        yl = int(self.settings['y-px'].text())
        self.data = numpy.zeros((xl, yl), numpy.uint16)
        self.progressBar.setMaximum(xl*yl)
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
        #print str(data)
        if self.min_data is None:
            self.min_data = data[0]
        if self.max_data is None:
            self.max_data = data[0]
            
        if data[0] < self.min_data:
            self.min_data = data[0]
        if data[0] > self.max_data:
            self.max_data = data[0]
        self.x+=1
        if self.x >=  int(self.settings['x-px'].text()):
            self.y += 1
            self.x = 0
        if self.y  < int(self.settings['y-px'].text()):
            self.data[self.y, self.x] = data[0]
        if self.x +1 == int(self.settings['x-px'].text()) and self.y +1 == int(self.settings['y-px'].text()):
            print "Scan finished"
            self.unexpectData()
            fname = '/Daten/SICM/dev/testsic'+str(time.time())+'.dat'
            
            self.data.tofile(fname)
        print "x: "+str(self.x)+" y: "+str(self.y)
        if time.time() - self.lastDraw > .2 or self.y == int(self.settings['y-px'].text()):
            mpw = self.getGraph('data')
            
            imgplotobj = mpw.axes.imshow(self.data, interpolation='none', cmap='hot')
            print "Unique values: "+ str(len(numpy.unique(self.data)))
            imgplotobj.set_clim(vmin=self.min_data, vmax=self.max_data)
#        mpw.axes.set_xlabel('time/ms')
#        mpw.axes.set_ylabel('voltage/V')
#        mpw.axes.set_ylim((-5,5))

            mpw.draw()
            self.progressBar.setValue(int(self.settings['x-px'].text())*self.y+self.x)
            self.lastDraw = time.time()

    def scan(self):
        self._prepare()
        self.receiveData('SCAN')
                        
    def stop(self):
        self.mainwin.client.sendLine('STOP')
