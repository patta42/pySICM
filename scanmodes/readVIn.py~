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
from twisted.internet import defer, reactor
import struct
import pycomedi.device as Device
import pycomedi.subdevice as Subdevice
import pycomedi.channel as Channel
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import numpy as np
import time

class MyCallbackReader(Util.Reader):

    def __init__(self, callback=None, count=None, **kwargs):
        self.callback = callback
        self.count = count
        super(MyCallbackReader, self).__init__(**kwargs)

    def start(self):
        super(MyCallbackReader,self).start()
        if self.callback:
            self.callback(self.buffer)
    def run(self):
        count = self.count
        block_while_running = self.block_while_running
        while count is None or count > 0:
            if count is not None:
                count -= 1
            try:
                self.block_while_running = False
                super(MyCallbackReader, self).run()
            finally:
                self.block_while_running = block_while_running

            if self.block_while_running:
                self.block()

    def isAlive(self):
        return super(MyCallbackReader,self,).isAlive()

class ReadVIn (pySICM.sicm._SICMMeasurement):
    
    def __init__(self):
        super(ReadVIn, self).__init__()
        
        
        self._setRequired('InputSignal', 1, pySICM.sicm.InputSignal)
        self._setRequiredOptions('ReadVIn.InputSignal', 1, int, 'Id of the InputSignal to use. (int)')
        self._setRequired('Samples', 1, int)
        self._setRequiredOptions('ReadVIn.Samples', 1, int, 'Number of samples to be read in one run. (int)')
        self._setRequired('Duration', 1, int)
        self._setRequiredOptions('ReadVIn.Duration', 1, int, 'Duration of one run in milliseconds. (int)')
        self._setRequiredOptions('ReadVIn.Loop', 1, bool, 'Loop infinitely? (bool)')
        self._setRequired('Loop', 1, bool)
        self.stop = False
        self.device = None
        self.ai = None
        self.channel = None
        self.runs=0
        self.reader=None
    def checkAndSetConfig(self, settings):
        if 'mode' not in settings:
            return False
        if settings['mode'] != 'readVIn':
            return False
        if 'readVIn' not in settings:
            return False
        rsettings = settings['readVIn']
        if 'Duration' not in rsettings:
            return False
        self.setConfig('Duration', int(rsettings['Duration']))
        if 'Samples' not in rsettings:
            return False
        self.setConfig('Samples', int(rsettings['Samples']))
        if 'Loop' not in rsettings:
            return False
        self.setConfig('Loop', bool(int(rsettings['Loop'])))
        return True
    
    def fake(self, settings, writeResponse):
        self.writeResponse = writeResponse
        self.stop = False
        self.runs=0;
        if self.checkAndSetConfig(settings):
            self.nextFakeDataPoint('')
        else:
            self.writeResponse("NACK\r\n")
        
    def generateFakeDeferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextFakeDataPoint)
    def generateDeferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.writeResponse)
        self.d.addCallback(self.nextDataPoint)

    def checkData(self):
        pass    

    def nextFakeDataPoint(self, args):
        self.runs=self.runs+1
        self.data = []
        global reactor
        self.d = None
        self.generateFakeDeferred()
        if (self.getConfig('Loop') and self.stop is False) or self.runs == 1:
           self.call = reactor.callLater(0,self._fake)
        else:
           self.destroy()

    def _fake(self):


        time.sleep(float(self.getConfig('Duration'))*1e-3)
        y = []
        noise = np.random.normal(0,0.05,1024)
        for i in xrange(self.getConfig('Samples')):
            y.append(np.sin(np.pi*2*i/(self.getConfig('Samples')/4.0))+noise[i%1024])

        y = y - np.min(y)
        y = y / np.max(y)
        y = y * np.iinfo(np.uint16).max
        data = ""
        for i in y:
            data = data + self.mkByte(int(round(i)))
        self.d.callback(data)
        #return d

    def mkByte(self, number):
        # little endian
        a = int(number / 256)
        b = int(number % 256)
        return struct.pack('B',b)+struct.pack('B',a)

    def setStop(self):
        self.stop = True

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
            min = -5,
            max = 5)
        self.channel = self.ai.channel(
            3, 
            factory = Channel.AnalogChannel, 
            aref = CONSTANTS.AREF.ground,
            range = best_range)
        if self.checkAndSetConfig(settings):
            self.frequency = 1e3*(
                float(self.getConfig('Samples'))/float(self.getConfig('Duration')))
         

            command = self.ai.get_cmd_generic_timed(1, scan_period_ns=1e9/self.frequency)
            command.chanlist = [self.channel]
            command.stop_src = CONSTANTS.TRIG_SRC.count
            command.stop_arg = self.getConfig('Samples')
            self.command=command
            buf = np.zeros(self.getConfig('Samples'), np.uint16)
            self.nextDataPoint('');

    def nextDataPoint(self, args):
        self.runs=self.runs+1
        self.ai.cmd = self.command
        while self.ai.get_flags().busy and self.ai.get_flags().running:
            time.sleep(.0001)
            print "Sleeping..."
        self.ai.cancel()
        self.ai.command()
        self.data = []
        global reactor
        self.d = None
        self.generateDeferred()
        if (self.getConfig('Loop') and self.stop is False) or self.runs == 1:
           self.call = reactor.callLater(0,self._scan)
        else:
           self.destroy()
           

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
        super(ReadVIn, self).destroy()
        self.device.close()
