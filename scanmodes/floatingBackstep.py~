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
import pySICM.error as PySICMError
import pySICM.converter as Converter 
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
                 'Use small backstep at height differences below, micm(float)',
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
                'Use Booster [0: No, 1: Yes] (bool)',
                 0, 7],
                ['FloatingBackstep.XOffset', 1,float,
                 'X-Offset in micm (float)',
                 1,7],
                ['FloatingBackstep.YOffset', 1,float,
                 'Y-Offset in micm (float)',
                 1,8],
                ['FloatingBackstep.StartXMoveFraction', 1,float,
                 'Start lateral movement after this percentage of the backstep (float)',
                 0,8],
                ['FloatingBackstep.StartApproachFraction', 1,float,
                 'Start vertical movement after this percentage of lateral step (float)',
                 0,9],
                ['FloatingBackstep.UseDifferentResolutions', 1,int,
                 'Use smaller resolution for flat areas (bool)',
                 1,9],
                ['FloatingBackstep.SmallResolution', 1,int,
                 'Resolution for small resolution areas in pixels (int)',
                 0,10]
                
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
        
    ## def calibrateFrequency(self):
    ##     c = 0
    ##     start = time.time()
    ##     while c < 2**15:
    ##         n = self.signal.read()
    ##         c += 1
    ##     end = time.time()
    ##     self.fq =  2**15/(end-start)
    ##     distance = self.piezo._config._distance
    ##     self.max_points = round(
    ##         1+1.01 *self.fq  *(distance/(1e3*self.getConfig('FallRate'))))      

    ## def getThresholdInBits(self, i_zero):
    ##     threshold_volts = self.signal.toPhysical(i_zero) * self.getConfig('Threshold')
    ##     return self.signal.toBits(threshold_volts)

    def handleError(self, error):
        print str(error)
        raise PySICMError('An error occured.')

    def scan(self, settings, writeResponse):
        self.initPiezos()
        self.writeResponse = writeResponse
        self.retract = False
        
        if self.checkAndSetConfig(settings):
            self.xoffset = self.getConfig('XOffset') * 1e3
            self.yoffset = self.getConfig('YOffset') * 1e3
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
            self.startFrom = None
            self.maxX = self.getConfig('x-px-pre')
            self.maxY = self.getConfig('y-px-pre')
            self.data = np.zeros((self.getConfig('x-px-pre'),
                                  self.getConfig('y-px-pre')), np.int32)
            self.readFrequency = self.getReadFrequency()
            
            #self.debugCounter = 0
            r = self._detectSurface()
            
            self.nextDataPoint(
                self.piezo.converter.getConvertedNumber(r, Converter.UNIT.nm)
                )
        else:
            print "Config was not correct"
        
    def nextDataPoint(self, args):

        pos = args
        if self.isPrescan:
            pos2 = pos + Converter.UNumber(self.getConfig('BackstepL')*1e3, Converter.UNIT.nm)
        else:
            pos2 = pos + Converter.UNumber(self.getBackstep(), Converter.UNIT.nm)
            
        self.piezo.set_pos(pos2, wait=self.getConfig('StartXMoveFraction')/100, overshoot = 000)

        print "Pos aimed:"+ str(pos2)

        print "Pos reached:" + str(self.piezo.current_pos())

        if self.isPrescan:
            if self.x is not None and self.y is not None:
                self.data[self.x, self.y] = pos.getValue(Converter.UNIT.nm)

        if self.maxLine < pos.getValue(Converter.UNIT.nm):
            self.maxLine = pos.getValue(Converter.UNIT.nm)
#        if self.boost:
#            self.booster.home()
        self.startFrom = pos2
        self._proceed()

    def _proceed(self):
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
                self.maxLine = np.max(self.data) 
                if self.maxLine > 1e5/1.1:
                    self.maxLine = 1e5/1.1
                self.startFrom = self.piezo.converter.getConvertedNumber(
                    1.1 * self.maxLine, Converter.UNIT.nm)
                self.deltax = 1e3*self.getConfig('x-Size')/float(self.getConfig('x-px'))
                self.deltay = 1e3*self.getConfig('y-Size')/float(self.getConfig('y-px'))
                self.maxX = self.getConfig('x-px')
                self.maxY = self.getConfig('y-px')
                self.setXYposAndDetectSurface()

            else:
                self.piezo.home()
                self.xpiezo.set_nm(0)
                self.ypiezo.set_nm(0)
                print "Scan finished"
        else:
            print "Stop"
            self.piezo.home()
            self.xpiezo.set_nm(0)
            self.ypiezo.set_nm(0)

            
    def setXYposAndDetectSurface(self):

        if self.y_is_sync == False:

            if self.x == 0 and self.y == 0:
                self._setYPos()
            else:
                self.piezo._ao.cancel()
                
                p = self.piezo.converter.getConvertedNumber(
                        1.1*self.maxLine,Converter.UNIT.nm)
                print "Retracting due to unsynced y"
                self.piezo.set_pos(p,
                    wait=self.getConfig('StartXMoveFraction')/100)
                self.startFrom=p
                self._setYPos()
                
        else:
            self._setXYpos()

    def _setYPos(self):

        self.y_is_sync = True
        self.maxLine = 0
        self.ypiezo.set_pos(
            self.ypiezo.converter.getConvertedNumber(
                self.yoffset + self.y * self.deltay, Converter.UNIT.nm),
            wait=self.getConfig('StartApproachFraction')/100)
        self._setXYpos()


    def _setXYpos(self):

        if self.x_is_sync == False:

            self.x_is_sync = True
            self.xpiezo.set_pos(
                self.xpiezo.converter.getConvertedNumber(
                    self.xoffset + self.x * self.deltax, Converter.UNIT.nm),
                wait=.999)
            self.detectSurface()
        else:
            self.detectSurface()
    def detectSurface(self):
        # wait for piezo to move to x pos:

#        time.sleep(.001)
        self.generateDeferred()
        self.d = threads.deferToThread(self._detectSurface)
        self.d.addCallback(self._writeResponse)
        self.d.addCallback(self.nextDataPoint)
        self.d.addErrback(self.handleError)
        

    def _detectSurface(self):
        r =  super(FloatingBackstep, self)._detectSurface(
            returnPos = True, 
            updateFrequency = False,
            currPos = self.startFrom)
        
        pos = r['end_pos']

        return pos

    def _writeResponse(self, pos):

        if pos > 100000:
            pos = 100000

        self.writeResponse(
            self.mkByte(int(round(np.iinfo(np.uint16).max*(pos)/100000))))
        return self.piezo.converter.getConvertedNumber(pos, Converter.UNIT.nm)
        
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

        
        sh = self.data.shape
        print sh
        bs = np.empty(sh, np.float64)
        bs.fill(np.float64(self.getConfig('BackstepL')*1e-3))

        for y in xrange(0,sh[1]-1):
            for x in xrange(0,sh[0]-1):
                d = self.data[x+1,y] - self.data[x,y]
                if d < 0:
                    d = 0
                bs[x,y] = np.float64(d)

        self.backsteps = bs
        print self.backsteps
        
    def getBackstep(self):
        x = self.x//self.getConfig('x-px-pre')
        y = self.y//self.getConfig('y-px-pre')
        bs = self.backsteps[x, y]
        if bs > self.getConfig('BackstepS') * 5e2:
            print "Returnig " + str(bs)
            return bs
        else:
            print "Returnig " + str(self.getConfig('BackstepS')*5e2)
            return self.getConfig('BackstepS')*5e2
 
