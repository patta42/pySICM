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

import pySICM.sicm 
import pySICM.piezo as Piezo
from twisted.internet import defer, reactor, threads
import struct
import pycomedi.device as Device
import pycomedi.subdevice as Subdevice
import pycomedi.channel as Channel
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import numpy as np
import time

class SimpleScan (pySICM.sicm._SICMMeasurement):
    
    def __init__(self):
        super(SimpleScan, self).__init__()
        self.setOptions()
        self.initInternals()

    def setOptions(self):
        self._setRequired('x-Size',1,float)
        self._setRequiredOptions('SimpleScan.x-Size', 1, float, 
                                 'Scan dimension in x-direction in micm (float)')
        self._setRequired('y-Size',1,float)
        self._setRequiredOptions('SimpleScan.y-Size', 1, float, 
                                 'Scan dimension in y-direction in micm (float)')
        self._setRequired('x-px',1,float)
        self._setRequiredOptions('SimpleScan.x-px', 1, int, 
                                 'number of pixels in x-direction (int)')
        self._setRequired('y-px',1,float)
        self._setRequiredOptions('SimpleScan.y-px', 1, int, 
                                 'number of pixels in y-direction (int)')
        self._setRequired('StartPos', 1, float)
        self._setRequiredOptions('SimpleScan.StartPos', 1, int, 
                                 'Vertical start position of the scan in micm (int)')
        self._setRequired('FallRate', 1, int)
        self._setRequiredOptions('SimpleScan.FallRate', 1, int, 
                                 'Fall rate in nm/ms (int)')
        self._setRequired('LateralSpeed', 1, int)
        self._setRequiredOptions('SimpleScan.LateralSpeed', 1, int, 
                                 'Lateral movement rate nm/ms (int)')

        self._setRequired('Threshold', 1, int)
        self._setRequiredOptions('SimpleScan.Threshold', 1, float, 
                                 'Stop threshold in percent (float)')
        self._setRequired('Sensitivity', 1, float)
        self._setRequiredOptions('SimpleScan.Sensitivity', 1, float, 
                                 'Sensitivity in V/nA (float)')
        self._setRequired('Filter', 1, float)
        self._setRequiredOptions('SimpleScan.Filter', 1, float, 
                                 'Output filter in kHz (float)')
        
    def initInternals(self):
        self.stop = False
        self.device = None
        self.ai = None
        self.channel = None
        self.runs=0
        self.reader=None

    def checkAndSetConfig(self, settings):
        if 'mode' not in settings:
            return False
        if settings['mode'] != 'simpleScan':
            return False
        if 'simpleScan' not in settings:
            return False
        rsettings = settings['simpleScan']
        if 'Threshold' not in rsettings:
            return False
        self.setConfig('Threshold', float(rsettings['Threshold'])/100.0)
        if 'FallRate' not in rsettings:
            return False
        self.setConfig('FallRate', int(rsettings['FallRate']))
        if 'LateralSpeed' not in rsettings:
            return False
        self.setConfig('LateralSpeed', int(rsettings['LateralSpeed']))

        if 'Sensitivity' not in rsettings:
            return False
        self.setConfig('Sensitivity', float(rsettings['Sensitivity']))
        if 'Filter' not in rsettings:
            return False
        self.setConfig('Filter', float(rsettings['Filter']))

        if 'x-px' not in rsettings:
            return False
        self.setConfig('x-px', int(rsettings['x-px']))
        if 'y-px' not in rsettings:
            return False
        self.setConfig('y-px', int(rsettings['y-px']))
        if 'x-Size' not in rsettings:
            return False
        self.setConfig('x-Size', float(rsettings['x-Size']))
        if 'y-Size' not in rsettings:
            return False
        self.setConfig('y-Size', float(rsettings['y-Size']))
        if 'StartPos' not in rsettings:
            return False
        self.setConfig('StartPos', int(rsettings['StartPos']))
        return True

    def initPiezos(self):
        self.ao = self.device.find_subdevice_by_type(
            CONSTANTS.SUBDEVICE_TYPE.ao,
            factory = Subdevice.StreamingSubdevice)
        aochannel = self.ao.channel(
            1,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground)

        best_range_ao = aochannel.find_range(
            unit=CONSTANTS.UNIT.volt, 
            min = 0,
            max = 10)
        z_out = self.ao.channel(
            1,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)

        x_out = self.ao.channel(
            0,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)

        y_out = self.ao.channel(
            2,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)
        
        z_in = self.ai.channel(
            2,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)

        x_in = self.ai.channel(
            0,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)
        y_in = self.ai.channel(
            5,
            factory = Channel.AnalogChannel,
            aref = CONSTANTS.AREF.ground,
            range = best_range_ao)

        piezoCfg_z = Piezo.PiezoConfig(z_out, 
                                     direction = Piezo.PiezoConfig.DIRECTION_Z, 
                                     amplification = 1,
                                     voltrange = [0,10],
                                     distance = 100*1e3,
                                     ai_channel = z_in)
        piezoCfg_x = Piezo.PiezoConfig(x_out, 
                                     amplification = 1,
                                     voltrange = [0,10],
                                     distance = 100*1e3,
                                     ai_channel = x_in)
        piezoCfg_y = Piezo.PiezoConfig(y_out, 
                                     amplification = 1,
                                     voltrange = [0,10],
                                     distance = 100*1e3,
                                     ai_channel = y_in)
        global reactor
        self.zpiezo = Piezo.ZPiezoControl(piezoCfg_z, 
                                         self.ao, 
                                         self.ai, 
                                         reactor, 
                                         Piezo.ZPiezoControl.DECREASE)
        self.xpiezo = Piezo.PiezoControl(piezoCfg_x, 
                                         self.ao, 
                                         self.ai, 
                                         reactor)

        self.ypiezo = Piezo.PiezoControl(piezoCfg_y, 
                                         self.ao, 
                                         self.ai, 
                                         reactor)

        

    def scan(self, settings, writeResponse):
        self.writeResponse = writeResponse
        self.device = Device.Device('/dev/comedi0')
        self.device.open()
        
        self.ai = self.device.find_subdevice_by_type(
            CONSTANTS.SUBDEVICE_TYPE.ai,
            factory = Subdevice.StreamingSubdevice)
        channel = self.ai.channel(
            3,
            factory = Channel.AnalogChannel, 
            aref = CONSTANTS.AREF.ground)
        best_range = channel.find_range(
            unit=CONSTANTS.UNIT.volt, 
            min = 0,
            max = 10)
        self.signalchannel = self.ai.channel(
            3, 
            factory = Channel.AnalogChannel, 
            aref = CONSTANTS.AREF.ground,
            range = best_range)
        self.initPiezos()
        if self.checkAndSetConfig(settings):
            self.x = None
            self.deltax = 1000*self.getConfig('x-Size')/float(self.getConfig('x-px'))
            self.y = None
            self.deltay = 1000*self.getConfig('y-Size')/float(self.getConfig('y-px'))

            self.y_is_sync = False
            self.x_is_sync = False
            self.nextDataPoint('')
    def _callNextDataPoint(self):
        print "In callback from setting to StartPos"
        self.nextDataPoint('')

    def nextDataPoint(self, args):
            self.zpiezo.ramp_to_nm_target(1000*self.getConfig('StartPos'),
                                          self.getConfig('LateralSpeed'),
                                          self._proceed)
    def _proceed(self):
        if self.y is None:
            self.y = 0
            self.y_is_sync = False
        if self.x is None:
            self.x = 0
            self.x_is_sync = False
        else:
            self.x += 1
            self.x_is_sync = False
        if self.x+1 > self.getConfig('x-px'):
            self.x = 0
            self.y+=1
            self.x_is_sync = False
            self.y_is_sync = False
        if self.y  < self.getConfig('y-px'):
            self.d=None;
            self.generateDeferred()
            self.setXYposAndDetectSurface()

    def setXYposAndDetectSurface(self):
        if self.y_is_sync == False:
            print "Ramping to y-pos"
            self.y_is_sync = True
            self.ypiezo.ramp_to_nm_target(self.y * self.deltay, self.getConfig('LateralSpeed'), self._setXYpos)
        else:
            self._setXYpos()


    def _setXYpos(self):
        # wait for piezo to move to y pos:
        time.sleep(.01)
        if self.x_is_sync == False:
            print "Ramping to x-pos"
            self.x_is_sync = True
            self.xpiezo.ramp_to_nm_target(self.x * self.deltax, self.getConfig('LateralSpeed'), self.detectSurface)
        else:
            self.detectSurface()
    def detectSurface(self):
        # wait for piezo to move to x pos:
        time.sleep(.1)
        self.generateDeferred()
        self.d = threads.deferToThread(self._detectSurface)
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextDataPoint)

    def _detectSurface(self):
        
        safety_dist = self.zpiezo.getSignForRetract() * 1000
        i_zero = np.average(self.signalchannel.data_read_n(1000))
        start = time.time()

        self.zpiezo.approach_noThread(self.getConfig('FallRate'))
        signal = np.average(self.signalchannel.data_read_n(10))
        tmp = 0

        # debug
#        print "Measurement: " + str(signal/i_zero)
#        print "Card running?: " + str(self.ao.get_flags().running)
        while signal/i_zero > self.getConfig('Threshold') and self.ao.get_flags().running:
            signal = np.average(self.signalchannel.data_read_n(10))
            # debug
#            print signal/i_zero
#            if tmp == 0:
#                print "In while"
#                tmp = 1000
#            tmp -= 1
        self.ao.cancel()
        pos = self.zpiezo.current_nm()
        end = time.time()
        self.zpiezo.set_nm(pos+safety_dist)
        print "Position: "+str(self.x) + " " + str(self.y) + " " +str(pos)
        print "Time required: "+str(end-start)        
        return self.mkByte(int(round(np.iinfo(np.uint16).max*pos/100000)))


        
    def updateXY(self):
        self.x+=1
        if self.x +1 > self.getConfig('x-px'):
            self.x = 0
            self.y+=1
        self.writeResponse(self.mkByte(int(round(1e-3*self.pos/100.0))))
        global reactor
        reactor.callLater(0.001, self.nextDataPoint,'')
        
        

    def dataMeasured(self, data):
#        print "Runs is: %i"% self.runs
#        print "Data Received: %i"%time.time()
        
        print s#self.writeResponse(s)
#        if self.reader.isAlive():
#            self.reader.join()

#        self.nextDataPoint()

    def _scan(self):
        buf = np.zeros(self.getConfig('Samples'),np.uint16);
        reader = Util.Reader(self.ai, buf);
        reader.start()
        reader.join()
        print "Length after reader joined: %i" % len(reader.buffer)
        s = ''
        for i in reader.buffer:
            s = s + self.mkByte(i)
        self.d.callback(s)
        
    def destroy(self):
        self.runs=0
        super(Approach, self).destroy()
        self.device.close()

    def fake(self, settings, writeResponse):
        self.writeResponse = writeResponse
        self.stop = False
        self.stoppos = 20.0;
        self.C = 0.105;
        self.pos = 100.0
        if self.checkAndSetConfig(settings):
            self.nextFakeDataPoint('')
        else:
            self.writeResponse("NACK\r\n")

    def generateDeferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextDataPoint)
    def generateFakeDeferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextFakeDataPoint)

    def nextFakeDataPoint(self, args):
        self.data = []
        global reactor
        self.d = None
        self.generateFakeDeferred()
        if self.stop is False:
           self.call = reactor.callLater(0,self._fake)

    def _fake(self):
        self.d.callback(data)


    def mkByte(self, number):
        # little endian
#        print number
        a = int(number / 256)
        b = int(number % 256)
        try:
            return struct.pack('B',b)+struct.pack('B',a)
        except:
            print "b: "+str(b)
            print "a: "+str(a)

            
    def setStop(self):
        self.stop = True
