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

from pySICM.setup import pysicmsetup as SETUP
import pySICM.sicm
import pySICM.piezo as Piezo
from scanmodes.approach import Approach
from twisted.internet import defer, reactor, threads
import struct
import pycomedi.device as Device
import pycomedi.subdevice as Subdevice
import pycomedi.channel as Channel
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import numpy as np
import time

class FloatingBackstep (Approach):

    _options = [['FloatingBackstep.x-Size', 1, float, 
                 'Scan dimension in x-direction in micm (float)',
                 0, 0],
                ['FloatingBackstep.y-Size', 1, float, 
                 'Scan dimension in y-direction in micm (float)',
                 0, 1],
                ['FloatingBackstep.x-px', 1, int, 
                 'number of pixels in x-direction (int)',
                 1, 0],
                ['FloatingBackstep.y-px', 1, int, 
                 'number of pixels in y-direction (int)',
                 1, 1],
                ['FloatingBackstep.x-px-pre', 1, int, 
                 'number of pixel in x of the prescan (int)',
                 1, 2],
                ['FloatingBackstep.y-px-pre', 1, int, 
                 'number of pixel in y of the prescan (int)',
                 1, 3],
                ['FloatingBackstep.FallRate', 1, int, 
                 'Fall rate in nm/ms (int)',
                 0, 2],
                ['FloatingBackstep.Threshold', 1, float, 
                 'Stop threshold in percent (float)',
                 0, 3],
                ['FloatingBackstep.BackstepL', 1, float, 
                 'Large vertical retraction distance in micm (float)',
                 0, 4],
                ['FloatingBackstep.BackstepSwitch', 1, float, 
                 'Use small backstep at height differences below(in micm, float)',
                 0, 5],
                ['FloatingBackstep.BackstepS', 1, float, 
                 'Small vertical retraction distance in micm (float)',
                 1, 4],
                ['FloatingBackstep.LateralSpeed', 1, int, 
                 'Lateral movement rate nm/ms (int)',
                 1, 5],
                ['FloatingBackstep.Sensitivity', 1, float, 
                 'Sensitivity in V/nA (float)',
                 0, 6],
                ['FloatingBackstep.Filter', 1, float, 
                'Output filter in kHz (float)',
                 1, 6],
                ['FloatingBackstep.Boost', 1, float, 
                'Use Booster (0: No, 1: Yes)',
                 0, 7]
                
        ]

    mode = 'floatingBackstep'
    
    def __init__(self):
        self.setOptions()
        self.initInternals()

    def setOptions(self):
        for o in self._options:
            self._setRequiredOptions(o[0], o[1], o[2], o[3], col = o[4], pos = o[5])
        
        
    def initInternals(self):
        self.stop = False
        self.runs=0
        for inp in SETUP.instrument['inputsignals'].itervalues():
            self.signal = inp




    def initPiezos(self):
        for con in SETUP.instrument['controllables'].itervalues():
            if con.z():
                self.piezo = con.z()
            if con.x():
                self.xpiezo = con.x()
            if con.y():
                self.ypiezo = con.y()
            if con.zfine():
                self.booster = con.zfine()
        
    def calibrateFrequency(self):
        c = 0
        start = time.time()
        while c < 2**15:
            n = self.signal.read()
            c += 1
        end = time.time()
        self.fq =  2**15/(end-start)
        distance = self.piezo._config._distance
        self.max_points = round(
            1+1.01 *self.fq  *(distance/(1e3*self.getConfig('FallRate'))))      

    def getThresholdInBits(self, i_zero):
        threshold_volts = self.signal.toPhysical(i_zero) * self.getConfig('Threshold')
        return self.signal.toBits(threshold_volts)

    def handleError(self, error):
        print str(error)
        raise PySICMError('An error occured.')

    def scan(self, settings, writeResponse):
        self.initPiezos()
        self.writeResponse = writeResponse
        self.retract = False
        
        if self.checkAndSetConfig(settings):
            self._config['Threshold']/=100
            self.boost = self.getConfig('Boost') == 1
            self.x = None
            self.deltax = 1000*self.getConfig('x-Size')/float(self.getConfig('x-px-pre'))
            self.y = None
            self.deltay = 1000*self.getConfig('y-Size')/float(self.getConfig('y-px-pre'))

            self.y_is_sync = False
            self.x_is_sync = False
            self.maxLine = 0
            self.isPrescan = True
            self.maxX = self.getConfig('x-px-pre')
            self.maxY = self.getConfig('y-px-pre')
            self.data = np.zeros((self.getConfig('x-px-pre'),
                                  self.getConfig('y-px-pre')), np.uint16)
            self.calibrateFrequency()
            self.nextDataPoint(100000)
        else:
            print "Config was not correct"
        
    def _callNextDataPoint(self):
        print "In callback from setting to StartPos"
        self.nextDataPoint('')

    def nextDataPoint(self, args):
        print "In nextDataPoint"
        pos = args
        if self.isPrescan:
            pos += self.getConfig('BackstepL')*1e3
        else:
            pos += self.getBackstep()*1e3
        print "Position: "+str(pos)
        
        if pos > 1e5:
            pos = 1e5

        self.piezo.set_nm_and_wait(pos)
        self._proceed()

    def _proceed(self):
        print "In _proceed"
        if not self.stop:
            if self.y is None:
                self.y = 0
                self.y_is_sync = False
            if self.x is None:
                self.x = 0
                self.x_is_sync = False
            else:
                self.x += 1
                self.x_is_sync = False

            if self.x+1 > self.maxX:
                self.x = 0
                self.y+=1
                self.x_is_sync = False
                self.y_is_sync = False
            if self.y  < self.maxY:
                self.d=None;
                self.generateDeferred()
                self.setXYposAndDetectSurface()
            elif self.y == self.maxY and self.isPrescan:
                self.isPrescan = False
                self.x = 0
                self.y = 0
                self.x_is_sync = False
                self.y_is_sync = False
                self.calculateBacksteps()
                self.maxLine = 1e5-1e3
                self.setXYposAndDetectSurface()
                self.deltax = 1e3*self.getConfig('x-Size')/float(self.getConfig('x-px'))
                self.deltay = 1e3*self.getConfig('y-Size')/float(self.getConfig('y-px'))
                self.maxX = self.getConfig('x-px')
                self.maxY = self.getConfig('y-px')
            else:
                print "Scan finished"
        else:
            print "Stop"
            
    def setXYposAndDetectSurface(self):
        print "In setXYposAndDetectSurface"
        if self.y_is_sync == False:
            print "y not synced"
            if self.x == 0 and self.y == 0:
                print "x and y both are zero"
                if self.piezo.current_nm() + 20 < 1e5: 
                    self.piezo.ramp_to_nm_target(1e5, self.getConfig('LateralSpeed'), self._setYPos)
                else:
                    self._setYPos()
            else:
                print "At least x or y is not zero"
                self.piezo.home()
                time.sleep(0.01)
                self._setYPos()
                
        else:
            self._setXYpos()

    def _setYPos(self):
        print "Ramping to y-pos"
        self.y_is_sync = True
        self.maxLine = 0
        self.ypiezo.ramp_to_nm_target(self.y * self.deltay, self.getConfig('LateralSpeed'), self._setXYpos)

    def _setXYpos(self):
        # wait for piezo to move to y pos:
        time.sleep(.01)
        print "In _setXYPos"
        if self.x_is_sync == False:
            print "Ramping to x-pos"
            self.x_is_sync = True
            self.xpiezo.ramp_to_nm_target(self.x * self.deltax, self.getConfig('LateralSpeed'), self.detectSurface)
        else:
            self.detectSurface()
    def detectSurface(self):
        # wait for piezo to move to x pos:
        print "In detectSurface"
        time.sleep(.001)
        self.generateDeferred()
        self.d = threads.deferToThread(self._detectSurface)
        self.d.addCallback(self._writeResponse)
        self.d.addCallback(self.nextDataPoint)
        self.d.addErrback(self.handleError)
        

    def _detectSurface(self):
        print "I'm in _detectSurface."
        pos =  super(FloatingBackstep, self)._detectSurface(
            returnPos = True, 
            updateFrequency = False)
        
        if self.maxLine < pos:
            self.maxLine = pos
        return pos
        


#        i_zero = self.signal.read()
#        signal = i_zero
#        data=np.zeros((self.max_points+1,1),np.uint16)
#        threshold = self.getThresholdInBits(i_zero)
#        c = -#1
#        start = time.time()*1e3#

#        if self.boost:
#            self.booster.home()
#       
#        self.zpiezo.approach_noThread(self.getConfig('FallRate'))
#        while  signal > threshold and c < self.max_points:
#            c+=1
#            signal = self.signal.read()
#            data[c,0]=signal
#            if c%25000 == 0:
#                print "run "+str(c)+" of "+str(self.max_points)
#        if self.boost:
#            self.booster.up()
#        self.zpiezo.stop()
#        pos = self.zpiezo.current_nm()
#        end = time.time()*1e3
#        self.zpiezo.set_nm(pos+safety_dist)
#        print "Position: "+str(self.x) + " " + str(self.y) + " " +str(pos)
#        print "Time required: "+str(end-start)

    #    return pos

    def _writeResponse(self, pos):
        print "pos:" +str(pos)
        if pos > 100000:
            pos = 100000
            print "Position cut at max piezo pos"
        self.writeResponse(
            self.mkByte(int(round(np.iinfo(np.uint16).max*pos/100000))))
        return pos
        
    def updateXY(self):
        self.x+=1
        if self.x +1 > self.getConfig('x-px'):
            self.x = 0
            self.y+=1
        self.writeResponse(self.mkByte(int(round(1e-3*self.pos/100.0))))
        global reactor
        reactor.callLater(0.001, self.nextDataPoint,'')
        
    def destroy(self):
        self.runs=0
        super(Approach, self).destroy()
        self.device.close()


    def generateDeferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextDataPoint)


    def mkByte(self, number):
        # little endian
        print number
        a = int(number / 256)
        b = int(number % 256)
        try:
            return struct.pack('B',b)+struct.pack('B',a)
        except:
            print "b: "+str(b)
            print "a: "+str(a)

            
    def setStop(self):
        self.stop = True

    def calculateBacksteps(self):
        BACKSTEP_SET = True
        BACKSTEP_NONE = False
        bs = np.zeros((self.getConfig('x-px'),
                       self.getConfig('y-px')),np.bool_)

        _bs = np.zeros(self.data.shape) 

        for y in range(_bs.shape[0]-2):
            for x in range(_bs.shape[1]-2):
                if self.data[x+1,y] - self.data[x,y] > self.getConfig('BackstepSwitch'):
                    _bs[x,y] = BACKSTEP_SET
                else:
                    _bs[x,y] = BACKSTEP_NONE

#        if not ignoreLast:
#            _bs[:,-1] = BACKSTEP_SET
#            _bs[-1,:] = BACKSTEP_SET

        ratioX = float(self.getConfig('x-px')) / self.data.shape[0]
        ratioY = float(self.getConfig('y-px')) / self.data.shape[1]

        for y in range(_bs.shape[0]-1):
            for x in range(_bs.shape[1]-1):
                if _bs[x,y] or _bs[x+1,y] or _bs[x,y+1] or _bs[x+1,y+1]:
                    bs[int(x*np.ceil(ratioX)):int((x+1)*np.ceil(ratioX)),
                       int(y*np.ceil(ratioY)):int((y+1)*np.ceil(ratioY))] = BACKSTEP_SET
                else:
                    bs[int(x*np.ceil(ratioX)):int((x+1)*np.ceil(ratioX)),
                       int(y*np.ceil(ratioY)):int((y+1)*np.ceil(ratioY))] = BACKSTEP_NONE
        self.backsteps = bs

    def getBackstep(self):
        if self.backsteps[self.x, self.y]:
            return self.getConfig('BackstepL')
        else:
            return self.getConfig('BackstepS')
 
