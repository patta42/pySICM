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
import json, time, struct, numpy
import pySICM.helpers as Helpers
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class WidgetReadVIn(DefaultScanWidget):

    def __init__ (self, mainwin, parent = None):
        super(WidgetReadVIn, self).__init__(mainwin, parent)
        self.setWindowTitle('Read from voltage input')
        self.populateForm()
        self.addGraph('data',xlabel='time/ms',ylabel='voltage/V')
        self.progressBar.hide()


    def populateForm(self):
        self.mainwin.client.sendLineAndGetAnswer('GET SICMINFO', self._populateFormCB)
        
    def _populateFormCB(self, config):
        cfg = json.loads(config)
        cfg = Helpers.makeDictKeysInt(cfg)
        if 'Inputsignals' not in cfg:
            pass
        else:
            signalsin = cfg['Inputsignals']
            it = {}
            for k, item in signalsin.iteritems():
                it[item['name']]=k
            self.addComboBox('InputSignal', 'input signal',  it)
            self.addLineEdit('Duration', 'Duration of one run in milliseconds')
            self.settings['Duration'].setText(str(100))
            spin = QSpinBox()
            spin.setRange(2**8, 2**16)
            spin.setSingleStep(2**8)
            spin.setValue(2**11)
            self.addSetting('Samples', 'Number of bytes to be read.', spin)
            sampling = QLabel()
            sampling.setText(str(2**11/100.0)+' kS/s')
            self.addSetting('Sampling','Resulting sampling rate', sampling)
            self.addCheckBox('Loop','Run infinitely')
            self.settings['Loop'].setChecked(True)
            spin.valueChanged.connect(self.spinValueChangedCB)
            self.settings['Duration'].textChanged.connect(self.durationValueChangedCB)


    def updateSamplingRateCB(self):
        if self.settings['Duration'].text() == '' or float(self.settings['Duration'].text())==0.0:
            val = 'unknown'
        else:
            val = self.settings['Samples'].value() / float(self.settings['Duration'].text())
        self.settings['Sampling'].setText(str(val)+' kS/s')
    def spinValueChangedCB(self, value):
        self.updateSamplingRateCB()
    def durationValueChangedCB(self, value):
        self.updateSamplingRateCB()

    def sendSettings(self):
        client = self.mainwin.client
        client.sendLine('SET mode=readVIn')
        comb = self.settings['InputSignal']
        val = comb.itemData(comb.currentIndex())

        if not isinstance(val, str):
            if isinstance(val, QtCore.QString):
                mystr = str(val)
            else:
                mystr = str(val.toString())
        client.sendLine('SET readVIn.InputSignal='+mystr)
        client.sendLine('SET readVIn.Duration='+str(self.settings['Duration'].text()))
        client.sendLine('SET readVIn.Samples='+str(self.settings['Samples'].text()))
        if self.settings['Loop'].isChecked():
            loop = '1'
        else:
            loop = '0'
        client.sendLine('SET readVIn.Loop='+loop)

    def _prepare(self):
        self.mainwin.serverLog=str(time.time())
        self.sendSettings()
        self.expectData(self.updateData, length = int(self.settings['Samples'].text()), form = 'float', rang=[-5, 5])

    def fake(self):
        self._prepare()
        self.receiveData('FAKE')

    def updateData(self, data, *args):
        #print str(data)
        mpw = self.getGraph('data')
        x = numpy.linspace(0, int(self.settings['Duration'].text()), len(data))
        mpw.axes.plot(x, data)
        mpw.axes.set_xlabel('time/ms')
        mpw.axes.set_ylabel('voltage/V')
        mpw.axes.set_ylim((-5,5))
        mpw.draw()

    def scan(self):
        self._prepare()
        self.receiveData('SCAN')
                        
    def stop(self):
        self.mainwin.client.sendLine('STOP')
