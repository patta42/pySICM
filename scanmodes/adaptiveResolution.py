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
import pySICM.utils as Utils
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

class SinglePixelScan(Approach):
    
    def __init__(self):
        super(SinglePixelScan, self).__init__()

        self.xoffset = None
        self.yoffset = None

        self.xdimension = None
        self.ydimension = None

        self.backstep = None
        
        self.resolution = None
        self.writeResponse = None

        self.scan_ready_callback = None

        self.skipFirst = False


    def setResponseCallback(self, cb):
        self.handleResponse = cb
        
    def setResolution(self, res):
        self.resolution = res

    def setBackstep(self, bs):
        self.backstep = bs

    def setXOffset(self, xo):
        self.xoffset = xo

    def setYOffset(self, yo):
        self.yoffset = yo

    def setXDimension(self, xd):
        self.xdimension = xd

    def setYDimension(self, yd):
        self.ydimension = yd
        
    def setWriteResponse(self, wr):
        self.writeResponse = wr

    def setSkipFirst(self, skip):
        self.skipFirst = skip

    def setWaitForLateralPos(self, wait):
        self.wait_for_lateral_pos = wait

    def setScanReadyCallback(self, cb):
        self.scan_ready_callback = cb
        
    def do_scan(self):
        self.x = -1
        self.y = 0

        if self.skipFirst:
            self.x = 0

        self.is_x_synced = False
        self.is_y_synced = False
        
        self.nextDataPoint()

    def increaseCounter(self):
        self.x += 1
        if self.x >= self.resolution:
            self.x = 0
            self.y += 1
            self.y_is_synced = False

        self.x_is_synced = False
        return self.y < self.resolution

    def getXPosInNM(self):
        return self.xpiezo.converter.getConvertedNumber(
            self.xoffset + self.x * self.xdimension / self.resolution,
            Converter.UNIT.nm)

    def getYPosInNM(self):
        return self.ypiezo.converter.getConvertedNumber(
            self.yoffset + self.y * self.ydimension / self.resolution,
            Converter.UNIT.nm)

    def nextDataPoint(self):
        if self.increaseCounter():
            self.setXYPos()
            self.d = self.generateDeferred()
            self.d.addCallback(self.handleResponse)
            self.d.addCallback(self.nextDataPoint)
            self._detectSurface()
        else:
            self.scan_ready_callback()
        
    def setXYPos(self):
        if not self.is_x_synced:
            self.xpiezo.set_pos(
                self.getXPosInNM(),
                wait = self.wait_for_lateral_pos
                )
            self.x_is_synced = True
        if not self.is_y_synced:
            self.ypiezo.set_pos(
                self.getYPosInNM(),
                wait = self.wait_for_lateral_pos
                )
            self.y_is_synced = True
    
    
    

class AdaptiveResolution (Approach):
    _options = [['AdaptiveResolution.x-Size', 1, float, 
                 'Scan dimension in x-direction in micm (float)',
                 0, 0],
                ['AdaptiveResolution.y-Size', 1, float, 
                 'Scan dimension in y-direction in micm (float)',
                 0, 1],
                ['AdaptiveResolution.Threshold', 1, float, 
                 'Stop threshold in percent (float)',
                 0, 2],
                ['AdaptiveResolution.FallRate', 1, int, 
                 'Pipette fall rate in nm/ms (int)',
                 0, 3],
                ['AdaptiveResolution.FinalImageSize', 1, int, 
                 'Final image size in pixels (int)',
                 0, 4],
                ['AdaptiveResolution.PrescanSpan', 1, int, 
                 'Prescan size in final image pixels (int)',
                 0, 5],
                ['AdaptiveResolution.LowResolution', 1, int, 
                 'Low resolution image size in pixels (int)',
                 0, 6],
                ['AdaptiveResolution.Backstep', 1, float, 
                 'Large backstep in micm (float)',
                 1, 0],
                ['AdaptiveResolution.MinimumBackstep', 1, float, 
                 'Minimum backstep in micm (float)',
                 1, 1],
                ['AdaptiveResolution.startXMoveFraction', 1, float, 
                 'Start moving in x-direction if this percentage of the backstep was retracted, in percent (float)',
                 1, 2],
                ['AdaptiveResolution.startApproachFraction', 1, float, 
                 'Start approaching if this percentage of the x-step was performed, in percent (float)',
                 1, 3],
                ['AdaptiveResolution.OffsetX', 1, float, 
                 'X-Offset in micm (float)',
                 1, 4],
                ['AdaptiveResolution.OffsetY', 1, float, 
                 'Y-Offset in micm (float)',
                 1, 5],
                ['AdaptiveResolution.RetractFirst', 1, bool, 
                 'Retract Z-Piezo before starting scan (0:No, 1:Yes)',
                 1, 6]
                ]
    mode = 'adaptiveResolution'

    def __init__(self):
        super(AdaptiveResolution, self).__init__()
        self.threshold = None

    def settingsPercent2Fraction(self, keys):
        for k in keys:
            self._config[k]/=100

    def settingsMicm2Nm(self, keys):
        for k in keys:
            self._config[k]*=1e3


    def scan (self, settings, writeResponse):
        if self.checkAndSetConfig(settings):
            self.settingsPercent2Fraction([
                'startXMoveFraction',
                'Threshold', 'startApproachFraction'])
            self.settingsMicm2Nm([
                'XOffset','YOffset','Backstep',
                'MinimumBackstep','x-Size','y-Size'])
            self.writeResponse = writeResponse
            self.setup()
            self.do_scan()
        else:
            print "Configuration not correct"

    def setup(self):
        self._init_internals()
        
        self.x = -1
        self.y = 0

        self.x_is_synced = False
        self.y_is_synced = False

        self.corner_counter = 0

        fullRes = self.getConfig('FinalImageSize')
        self.resolution = fullRes / self.getConfig('PrescanSpan')
        
        self.xoffset = self.getConfig('OffsetX')
        self.yoffset = self.getConfig('OffsetY')

        self.prescan_dim_x = self.getConfig('x-Size') / float(self.resolution)
        self.prescan_dim_y = self.getConfig('y-Size') / float(self.resolution)
        
        self.highres = fullRes / self.resolution
        self.lowres = self.getConfig('LowResolution') / self.resolution

        self.data = numpy.zeros((fullRes, fullRes))
        self.data[:] = numpy.nan

        self.init_scanner()

        

    def init_scanner(self):
        s = SinglePixelScan()
        s.setXOffset(self.XOffset)
        s.setYOffset(self.YOffset)
        s.setXDimension(self.prescan_dim_x)
        s.setYDimension(self.prescan_dim_y)
        s.setWaitForLateralPos(self.getConfig('startApproachFraction'))
        s.setResponseCallback(self.handleResponse)
        self.scanner = s

    def setXYPos(self):
        if not self.x_is_synced:
            self.xpiezo.set_pos(
                self.xpiezo.getConvertedNumber(
                    self.xoffset +
                    (self.x + self.corner_counter % 2) * self.prescan_dim_x,
                    Converter.UNIT.nm
                ),
                wait = self.getConfig('startApproachFraction'))
            self.x_is_synced = True
        if not self.y_is_synced:
            self.ypiezo.set_pos(
                self.ypiezo.getConvertedNumber(
                    self.yoffset +
                    (self.y + self.corner_counter // 2) * self.prescan_dim_y,
                    Converter.UNIT.nm
                ),
                wait = self.getConfig('startApproachFraction'))
            self.y_is_synced = True
        
    def do_scan(self):
        self.nextDataPoint()

    def increaseCounter(self):
        self.corner_counter += 1
        self.corner_counter %= 4
        if self.corner_counter == 0:
            self.x += 1
            if self.x >= self.resolution:
                self.x = 0
                self.y += 1
        return self.corner_counter > 0

    def finished(self):
        return self.y >= self.resolution

    def handleResponse(self, response):
        px_x = self.x * self.getConfig('PrescanSpan')
        px_y = self.y * self.getConfig('PrescanSpan')
        pos = response['end_pos']
        self.data[px_x, px_y] = pos
        
        s = Utils.mkByte(px_x) + Utils.mkByte(px_y) + Utils.mkByte(pos, r = 24)
        
        self.writeResponse(s)

    def computePlaneCoeffsFromPoints(self, p1, p2, p3):
        xv1 = p2[1] - p1[1]
        yv1 = p2[2] - p1[2]
        zv1 = p2[3] - p1[3]

        xv2 = p3[1] - p1[1]
        yv2 = p3[2] - p1[2]
        zv2 = p3[3] - p1[3]

        cross = numpy.cross([xv1, yv1, zv1], [xv2, yv2, zv2])

        cross.append(-1*(cross[0] * p1[0] + cross[1]*p1[1] + cross[2]*p1[2]))
        return cross
    
    def computeResolution(self):

        shift = self.getConfig('PrescanSpan')

        p = []

        for x,y in [(self.x, self.y), (self.x + shift, self.y),
                    (self.x, self.y + shift), (self.x + shift, self.y + shift)]:
            p.append((x, y, data[x,y])

        all_coeffs = [self.computePlaneCoeffsFromPoints(p[0], p[1], p[2]),
                      self.computePlaneCoeffsFromPoints(p[0], p[1], p[3]),
                      self.computePlaneCoeffsFromPoints(p[0], p[2], p[3]),
                      self.computePlaneCoeffsFromPoints(p[1], p[2], p[3])]
        points = [p3, p2, p1, p0]
        diffs = []
        for i in xrange(4):
            a = all_coeffs[i][0]
            b = all_coeffs[i][1]
            c = all_coeffs[i][2]
            d = all_coeffs[i][3]
            z = (-d - c * points[i][0] - b * points[i][1]) / c
            diffs.append(self.data[self.x + (i % 2) * shift, self.y + (i // 2) * shift] - z)
        
        
    def nextDataPoint(self):
        if self.increaseCounter():
            self.setXYPos()
            self.d = threads.deferToThread(
                self._detectSurface, returnPos = True, returnData = False
                )
            self.d.addCallback(self.handleResponse)
            self.d.addCallback(self.nextDataPoint)
        else:
            res = self.computeResolution()
            self.scanner.setResolution(res)
            self.scanner.setXOffset(self.xoffset + self.x * self.prescan_dim_x)
            self.scanner.setYOffset(self.yoffset + self.y * self.prescan_dim_y)
            self.scanner.setScanReadyCallback(self.nextDataPoint)
            self.scanner.do_scan()
            
            
        
