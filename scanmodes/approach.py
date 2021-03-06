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
from pySICM.setup import pysicmsetup as SETUP
from pySICM.converter import UNIT, CHANNEL
from twisted.internet import defer, reactor, threads
from pySICM.error import PySICMError

import struct
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import numpy as np
import time

    
class Approach (pySICM.sicm._SICMMeasurement):

    _options = [['Approach.FallRate', 1, int, 
                 'Fall rate in nm/ms (int)',
                 0, 0],
                ['Approach.Threshold', 1, float, 
                 'Stop threshold in percent (float)',
                 0, 1],
                ['Approach.Sensitivity', 1, float, 
                 'Sensitivity in V/nA (float)',
                 0, 2],
                ['Approach.Filter', 1, float, 
                'Output filter in kHz (float)',
                 0, 3],
                ['Approach.Retract',1, int,
                 'Retract pipette after approach? (0: No, 1: Yes)',
                 0,4],
                ['Approach.Boost',1, int,
                 'Use Booster to retract pipette? (0: No, 1: Yes)',
                 0,5]
        ]

    mode = 'approach'

    

    def __init__(self):
        super(Approach, self).__init__()
        self.setOptions()
    
        
    def calcDistance(self, n):
        fr = self.getConfig('FallRate')
        return fr*1e3*n/self.readFrequency

    
    def generateDeferred(self, *args, **kwargs):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.generateDeferred)

    def setStop(self):
        self.stop = True

    def _init_internals(self):
        
        for con in SETUP.instrument['controllables'].itervalues():
            if con.z():
                self.piezo = con.z()
            if con.zfine():
                self.booster = con.zfine()
        for inp in SETUP.instrument['inputsignals'].itervalues():
            self.signal = inp

    def getReadFrequency(self):
        c = 0
        start = time.time()
        while c < 2**15:
            n = self.signal.read()
            c += 1
        end = time.time()
        print('frequency: ' + str(2**15/(end-start)))
        return 2**15/(end-start)
        

    def scan(self, settings, writeResponse):
        
        if self.checkAndSetConfig(settings):
            self._config['Threshold']/=100
            self._init_internals()
            self.writeResponse = writeResponse
            self.detectSurface()
        else:
            print "Config was not correct"
    

    def detectSurface(self):
        self.generateDeferred()
        self.retract = self.getConfig('Retract') == 1
        self.boost = self.getConfig('Boost') == 1
        if self.boost:
            self.booster.home()
        self.readFrequency = self.getReadFrequency()
        self.d = threads.deferToThread(
            self._detectSurface, returnPos = True)
        # print "I am back from '_detectSurface'"
        self.d.addErrback(self.handleError)
        self.d.addCallback(self.writeData)

    def handleError(self, error):
        print str(error)
        raise PySICMError('An error occured!')

    def getThresholdInBits(self, i_zero):
        
        threshold_volts = self.signal.toPhysical(i_zero) * self.getConfig('Threshold')
        return self.signal.toBits(threshold_volts)
    
    def _detectSurface(self, returnPos = False, returnData = True, 
                       updateFrequency = True, currPos = None,
                       target = None, threshold = None):
        '''This function atually runs the approach and reads the data
        It has six optional options:
          returnPos (boolean, defaults False): Indicates whether the
            position of the piezo when the approach is stopped is
            returned.
          returnData (boolean, defaults True): Indicates whether the
            data signal recorded during the approach is returned.
          updateFrequency (boolean, defaults False): Indicates whether
            the readFrequency should be updated befor the approach.
          currPos (int16, defaults None): The current position of the
            piezo (in bits). If none, the function will determine the
            position.
          target (int16, defaults None): The target position of the
            approach curve. If none, it is determined as the maximum
            deflection of the piezo.

          If returnPos and returnData both are set to True, the first
          four bytes of the data will indicate the start position of the
          approach (currPos) in nm, followed by the position at the end of
          the approach (4 bytes) in nm, and the data.
        '''
        
        # Update the read frequency, if requested
        if updateFrequency:
            self.readFrequency = self.getReadFrequency()
        npoints = np.floor(self.readFrequency / (1e3*self.getConfig('Filter')))
        if npoints < 1:
            npoints = 1
        # If currPos is not provided, read it
        if currPos is None:
            currPos = self.piezo.current_pos()
            print "Current position has been read."

        # If target is not provided, get it
        if target is None:
            target = self.piezo.getApproachTarget()
        # Distance of the approach (in bits)

        dist = float(target.get_oBits() - currPos.get_oBits())
        # The speed of the approach is given in nm/ms. We need it in bits/s.
        #
        s = self.piezo.converter.getConvertedNumber(0, UNIT.nm)
        e = self.piezo.converter.getConvertedNumber(10000, UNIT.nm)
        per_nm = float(e.get_oBits() - s.get_oBits())/10000.0
        speed_in_bits_per_s = float(per_nm) * self.getConfig('FallRate') * 1e3

        # Now a problem occurs. We might have to write more bits than fit in the buffer,
        # but we need to read the input channel as fast as possible. Reading the input
        # channel in a while loop to seems to block other threads, hence writing the
        # data to the buffer in a second thread does not help. We omit every second value
        # if the apporach data is too large.

        # Buffer size in uint16

        b_size = self.piezo._ao.get_buffer_size() / np.dtype(np.uint16).itemsize


        # Check whether the data range is too large:

        if abs(dist) > b_size:
            f = np.sign(dist) * 2
        else:
            f = np.sign(dist)


        speed_in_bits_per_s/= np.abs(f)

        # Compute the ramp data
        start = int(currPos.get_oBits()) + int(np.sign(f))
        ende = int(target.get_oBits())
        print "Ramp info:"
        print "====================="
        print "From "+str(start)+" (in bits: "+str(currPos.get_oBits())+")"
        print "To "+str(target)+" (in bits: "+str(target.get_oBits())+")"
        print "====================="
        ramp_data = np.array(
            xrange(start, ende, 
                   int(f)), np.uint16)
        if ramp_data[-1] != int(target.get_oBits()) and len(ramp_data) < b_size:
            np.append(ramp_data, int(target.get_oBits()))
        
        print str(ramp_data)

        # Prepare the command

        self._prepareApproachCommand(len(ramp_data), speed_in_bits_per_s)

        # Compute the threshold
        if threshold is None:
            i_zero = self.signal.read_n(10)
            
            signal =int(np.mean(i_zero))
            threshold = self.getThresholdInBits(signal)
        print ('Threshold is ' + str(threshold));
        # Compute maximum number of points to be read
        max_points = int(2*round(abs(dist)  * float(self.readFrequency) /
                               float(speed_in_bits_per_s))/npoints)
        data = np.zeros(max_points,np.uint16)

        # Issue the command

        self.piezo._ao.command()

        # Write data to the buffer:

        ramp_data.tofile(self.piezo._ao.device.file)
        self.piezo._ao.device.file.flush()

        c = 0

        # Run the loop

        # Booster down
        if self.boost and c < max_points:
            self.booster.home()
        time.sleep(0.001)
        n = 0
        q = 0
        start = time.time()
        while c < max_points:
            if c < 1:
                self.piezo._ao.device.do_insn(Util.inttrig_insn(self.piezo._ao))
            signal = np.mean(self.signal.read_n(npoints))
            data[c] = np.floor(signal)
            c += 1
            
            if signal <= threshold:
                n = n + 1
                q = q + 1;
            else:
                n = 0
            if n > 2:
               break

        # Boost up
        print ('q is '+str(q))
        if self.boost and c < max_points:
            self.booster.up()
          

        # Stop the piezo from approaching
        self.piezo.stop()


        # Read position
        if returnPos:
            pos = self.piezo.current_pos()

        
        if c == max_points:
            print "Max number of data points reached."
        else:
            print "Threshold detected."
        if self.retract:
            print "retacting to home."
            self.piezo.home()
        end = time.time()
        print "approach-time was: "+ str(end-start)

        if returnData:
            ret = data[:c]
        else:
            ret = np.array([], np.uint16)
            
        if returnPos:
            st = int(self.piezo.deflection(currPos).get_nm())
            en = int(self.piezo.deflection(pos).get_nm())

            ret = np.concatenate(([int(st / (2**16)), int(st % (2**16)),
                                   int(en / (2**16)), int(en % (2**16))], ret))
        else:
            st = None
            en = None

        appData = {
            'data' : ret,
            'threshold_detected' : c < max_points,
            'start_pos' : st,
            'end_pos' : en}
        return appData
        


        
    def destroy(self):
        self.runs=0
        super(Approach, self).destroy()
        self.device.close()


    def mkByte(self, number):
        # little endian
        a = int(number / 256)
        b = int(number % 256)
        try:
            return struct.pack('B',b)+struct.pack('B',a)
        except:
            print "b: "+str(b)
            print "a: "+str(a)

    def writeData(self, data):
        data = data['data']
        print "In writeData!"

        
        #distance = int(round(self.calcDistance(len(data))))
        #a = int(float(distance) / 2**16)
        #b = distance - a*2**16
        #s = self.mkByte(a)+self.mkByte(b)
        s = ''
        for i in data:
            s+=self.mkByte(int(round(i)))
            if len(s) == 1024:
                self.writeResponse(s, False)                
                s=''
        
        stop = [0, np.iinfo(np.uint16).max,                
                0, np.iinfo(np.uint16).max,                
                0, np.iinfo(np.uint16).max]                
        for i in stop:
            s+=self.mkByte(i)
            
        self.writeResponse(s, True)


    def _prepareApproachCommand(self, datalength, speed):
        
        cmd = self.piezo._ao.get_cmd_generic_timed(1,
                                                   1e9/speed)
        cmd.stop_src = CONSTANTS.TRIG_SRC.count
        cmd.start_src = CONSTANTS.TRIG_SRC.int
        cmd.stop_arg = datalength
        cmd.chanlist = [self.piezo._ao_channel]

        self.piezo._ao.cmd = cmd
        self.piezo._ao.command_test()
        
