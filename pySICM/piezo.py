# (C) 2014 Patrick Happel <patrick.happel@rub.de>
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

"Simple classes for controling a single piezo"

import numpy
import pycomedi.channel as pyChan
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import sys
import time
from twisted.internet import defer, reactor
import pySICM.converter as Converter

class PiezoConfig(object):
    '''Class for configuring a single piezo device.

    Note that pypiezo by from Trevor King might be a better and more sophisticated solution.

    Required parameters:
    ====================

    ao_channel: Channel number on a DAQ-subdevice for analog output of this piezo axis

    Optional parameters:
    ====================
    
    ai_channel: Channel number for reading the analog signal of the current piezo position.
                Default 0.
    
    amplification: Factor of the amplification between the signals on AO and AI. Not(!) the 
                amplification of the DAQs AO signal and the piezo. Default 1.
    
    voltrange: List containing the maximum and minimum voltages for maximum and minimum piezo
                position in arbetrary order (min and max of the list are used). Default [0, 10]
    
    distance: Travel range (in nanometers) of the piezo axis. Default 100000.

    direction: Integer describing the spatial direction of the piezo. Use the properties 
              DIRECTION_X, DIRECTION_Y or DIRECTION_Z. Default DIRECTION_X. Currently not used.

    hardware: Integer indictaing whether the piezo axis controls the pipette or the scanning 
              stage. Use properties HARDWARE_PIPETTE or HARDWARE_STAGE. Default HARDWARE_PIPETTE.
              Currently not used.
    '''
    

    DIRECTION_X = 0
    DIRECTION_Y = 1
    DIRECTION_Z = 2
    
    HARDWARE_PIPETTE = 0
    HARDWARE_STAGE = 1

    _amplification = 1   # between input and output channel
    _distance = 100000   # in nm
    _voltrange  = [0,10] # in Volts
    _cvoltrange = [0,10] # in Volts
    _ao_channel = 0      # 
    _ai_channel = 0      # Not required
    _direction = 0       # Use constants above
    _hardware = 0        # Use constants above

    def __init__ (self, ao_channel, **kwargs):
        try:
            self._ao_channel = ao_channel.index
        except:
            self._ao_channel = ao_channel
        
        for key, value in kwargs.iteritems():
            if (key == 'ai_channel'):
                try:
                    self._ai_channel = value.index
                except:
                    self._ai_channel = value

            if (key == 'direction'):
                self._direction = value
            if (key == 'hardware'):
                self._hardware = value
            if (key == 'amplification'):
                self._amplification = value
            if (key == 'voltrange'):
                self._voltrange = value
            if (key == 'distance'):
                self._distance = value
        self._deltaVolts = max(self._voltrange)-min(self._voltrange)

    def output_volts_per_nm(self):
        return float(max(self._voltrange)-min(self._voltrange)) / float(self._distance)
    
    def input_volts_per_nm(self):
        return (max(self._cvoltrange)-min(self._cvoltrange)) / self._distance

    def output_bits_per_volt(self):
        return float(2**16) / (max(self._voltrange) - min(self._voltrange))

    def output_bits_per_nm(self):
        return self.output_volts_per_nm() * self.output_bits_per_volt()


    def nm2volt(self, position):
        '''Translates a given position in nanometers to the corresponding 
        voltage.

        Required parameters:
        ====================
        
        position: Position in nanometers

        Returns:
        ========

        Corresponding voltage
        '''
        return (min(self._voltrange) + position *
                float(self._deltaVolts)/float(self._distance))
    
    def um2volt(self, distance):
        '''Translates a given position in micrometers to the corresponding 
        voltage.

        Required parameters:
        ====================
        
        position: Position in micrometers

        Returns:
        ========

        Corresponding voltage
        '''

        return self.nm2volts(1000*distance)

    def volt2nm(self, voltage, offset = 0):
        '''Translates a given voltage (in volts) to the corresponding 
        position (in nanometers).

        Required parameters:
        ====================
        
        voltage: Voltage in volts

        Returns:
        ========

        Corresponding position in nanometers
        '''

        voltage = float(voltage+offset)/self._amplification
        voltage = voltage - min(self._voltrange)
        return self._distance * voltage/float(self._deltaVolts)

    def volt2um(self,volt):
        '''Translates a given voltage (in volts) to the corresponding 
        position (in micrometers).

        Required parameters:
        ====================
        
        voltage: Voltage in volts

        Returns:
        ========

        Corresponding position in micrometers
        '''

        return self.volt2nm(volt)/1000.0

    def in2out(self, volts):
        d_in = max(self._cvoltrange) - min(self._cvoltrange)
        f = float(volts - min(self._cvoltrange)) / float(d_in)
        return min(self._voltrange) + f * (max(self._voltrange) - min(self._voltrange))
    def in2out(self, volts):
        d_out = max(self._voltrange) - min(self._voltrange)
        f = float(volts - min(self._voltrange)) / float(d_out)
        return min(self._cvoltrange) + f * (max(self._cvoltrange) - min(self._cvoltrange))
    
    

class PiezoControl(object):
    
    def __init__(self, config, ao, ai, reactor):
        self._ao = ao
        self._ai = ai
        self._config = config
        self.reactor = reactor

        self._ao_channel = self._ao.channel(self._config._ao_channel,
                                            factory = pyChan.AnalogChannel, 
                                            aref = CONSTANTS.AREF.ground)
        best_range = self._ao_channel.find_range(unit=CONSTANTS.UNIT.volt, 
                                                 min = min(self._config._voltrange),
                                                 max = max(self._config._voltrange))
        
        if (best_range < 0):
            sys.exit('no suitable range found.')
            
        self._ao_channel = self._ao.channel(self._config._ao_channel,
                                            factory = pyChan.AnalogChannel, 
                                            aref = CONSTANTS.AREF.ground,
                                            range = best_range)

        self._ao_range = best_range
        self._ai_channel = self._ai.channel(self._config._ai_channel,
                                            factory = pyChan.AnalogChannel,
                                            aref=CONSTANTS.AREF.ground)

        best_range = self._ai_channel.find_range(unit=CONSTANTS.UNIT.volt, 
                                                 min = (self._config._amplification * 
                                                        min(self._config._cvoltrange)),
                                                 max = (self._config._amplification * 
                                                        max(self._config._cvoltrange)))

        self._ai_channel = self._ai.channel(self._config._ai_channel,
                                            factory = pyChan.AnalogChannel,
                                            aref=CONSTANTS.AREF.ground,
                                            range=best_range)
        self._ai_range = best_range
        self._ao_converter = self._ao_channel.get_converter()
        self._ai_converter = self._ai_channel.get_converter()
        self._ao_ramp_cmd = None
        self._ao_ramp_data = None
        self.is_running = 0
        self.calibrate()
        self.converter = Converter.NumberConverter(self._config._cvoltrange,
                                                   self._config._voltrange,
                                                   self._config._distance,
                                                   self.calibration)
    # Calibration!

    def _calibrate(self, direction = 1):
        # Calibrates the piezo by slowly outputting the entire voltage
        # range and reading the input channel.
        if direction == -1:
            
            start = self._ao_converter.from_physical(
                self._config.nm2volt(self._config._distance))
            end =  self._ao_converter.from_physical(
                self._config.nm2volt(0))
        else:
            end = self._ao_converter.from_physical(
                self._config.nm2volt(self._config._distance))
            start =  self._ao_converter.from_physical(
                self._config.nm2volt(0))
        self.calibration = numpy.zeros((numpy.absolute(end-start),2),dtype = numpy.uint16);
        
        c = 0;
        print ("Calibrating piezo on output channel "+
               str(self._config._ao_channel)+
               " and input channel "+
               str(self._config._ai_channel)+".")
        self.set_bit(start)
        time.sleep(.1)
        for i in range(start, end, direction):
            self.set_bit(i)
            time.sleep(0.001)
            self.calibration[c,0] = i;
            self.calibration[c,1] = self.current_bit_quick()
            c = c + 1
        print "Done."

    def calibrate(self):
        # Loads the calibration for the piezo, if available, otherwise calls _calibrate
        config_filename = ('/var/pySICM/calibration/'
                           +str(self._config._distance)+'-'+str(self._config._ai_channel)
                           +'-'+str(self._config._ao_channel)+'.calib')
        try:
            calib = numpy.fromfile(config_filename, dtype = numpy.uint16)
            self.calibration = calib.reshape(len(calib)/2,2)
        except:
            # Do physical calibration
            self._calibrate()
            # Save file
            try:
                self.calibration.tofile(config_filename)
            except IOError:
                sys.exit('Cannot save calibration file. '+
                         'Ensure that the directory '+
                         '/var/pySICM/calibration/ '+
                         'is writable.')
        self.fit_calibration()

    def current_pos_quick(self):
        return self.converter.getConvertedNumber(
            self._ai_channel.data_read(),
            Converter.UNIT.bits,
            Converter.CHANNEL.inp)

    def current_pos(self, laenge = 10):
        return self.converter.getConvertedNumber(
            numpy.mean(self._ai_channel.data_read_n(laenge)),
            Converter.UNIT.bits,
            Converter.CHANNEL.inp)

    def fit_calibration(self):
        x = self.calibration[7500:,0];
        y = self.calibration[7500:,1];
        
        self.califit_p = numpy.polyfit(x, y, 1)
        print ("Calibrated to a line with coefficients "
               +str(self.califit_p[0])+ " and "+str(self.califit_p[1]))

    def in2out(self, inval):
        print "Inval is" + str(inval)
        print "outval should be around "+str(float(inval-2**15)*2.0)
        out = int(
                round(
                    float(inval - self.califit_p[1]) / float(self.califit_p[0])
                    ))
        print "outval is: "+str(out)
        return out
    
    def out2in(self, outval):
        return float(self.califit_p[0])*outval + self.califit_p[1]



    # Getting the current values.

    def current_bit(self, laenge = 10):
        return int(round(numpy.mean(
            self._ai_channel.data_read_n(laenge))))
    
    def current_bit_quick(self):
        return self.current_bit(1)

    def input_bits2nm(self, bits):
        
        mi = self._ai_range.min
        ma = self._ai_range.max
        
        offset = min(self._config._cvoltrange) - mi

        b_offset = 2**16 * offset / (ma - mi)

        
        
        print "ma: "+str(ma)
        print "mi: "+str(mi)
        print "bits: "+str(mi)
        
        return self._config._distance * (bits-b_offset) / (2**16 - b_offset) 



    # Setting the position (by simply writing the data)

    def set_bit(self, bit, wait = 0):
        self._ao_channel.data_write(bit)
        if wait != 0:
            old = self.current_bit(laenge=100)
            new = self.current_bit(laenge=100)
            while abs(old -new) > abs(wait):
                old = new
                new = self.current_bit(laenge=100)
    def set_volt(self, volt, wait = 0):
        self.set_bit(
            self._ao_converter.from_physical(volt), wait
            )
        
    def set_nm(self, nm, wait = 0):
        self.set_volt(
            self._config.nm2volt(nm), wait
            )

    # ramps...

    def set_pos(self, pos, wait = 0, overshoot = 0):

        self._ao_channel.data_write(
            int(pos.get_oBits()))
        print "written position: " + str(int(pos.get_oBits()))
#        foo = raw_input('Press Enter!\n')
        if wait != 0:
            new = numpy.mean(self._ai_channel.data_read_n(10))
            while wait*float(pos.get_iBits()) - new > 0:
                new = numpy.mean(self._ai_channel.data_read_n(10))

    def ramp_to_nm_target(self, target, speed, callback = None, block = False):
        '''Outputs a ramp from the current position to the target position
        
        Params (required):
        ==================
        target: Target position in nanometers
        speed: Speed for performing the ramp in nm/ms
        '''
        print "ramp_to_nm_target"
        self.ramp_to_volt_target(
            self._config.nm2volt(target),
            self._config.output_volts_per_nm() * speed,
            callback, block)

    def ramp_to_volt_target(self, target, speed, callback = None, block = False):
        '''Outputs a ramp from the current position to the target position
        
        Params (required):
        ==================
        target: Target position in volts
        speed: Speed for performing the ramp in volts/ms
        '''
        print "ramp_to_volt_target"
        self.volt_ramp(target, speed, callback = callback, block = block)
        
        
    def volt_ramp(self, target, speed, callback = None, start = None, block = False):
        if start is None:
            start = self.in2out(self.current_bit())
        else:
            start = self._ao_converter.from_physical(start)
            
        target = self._ao_converter.from_physical(target)
        diff = target - start
        print "diff:" + str(diff)
        print "bits per volt: "+  str(self._config.output_bits_per_volt())
        print "speed: "+str(speed)
        t = float(numpy.abs(diff)) / (float(speed) * self._config.output_bits_per_volt())
        self.timed_volts_ramp(start, target, t, callback, block)
        
    def timed_volts_ramp(self, start, target, tim_e, callback = None, block = False):
        n = numpy.abs(target - start) + 1
        if n > 2**15:
            n = 2**15
        samples = numpy.linspace(start, target, round(n))
        tim_e = tim_e * 1e-3 # now in seconds
        upd_freq = float(n) / tim_e
        self._prepare_command(upd_freq, len(samples))
        
        self._ramp_data = numpy.array([int(round(q)) for q in samples], numpy.uint16)
        self._run_ramp(callback, block)

    def _prepare_command(self, updfreq, n_samples):
        command = self._ao.get_cmd_generic_timed(1, 1e9/updfreq)
        command.stop_src = CONSTANTS.TRIG_SRC.count
        command.start_src = CONSTANTS.TRIG_SRC.int
        command.stop_arg = n_samples
        command.chanlist = [self._ao_channel]
        self._ao.cmd = command
        self._ao.command_test()

    def _run_ramp(self, callback = None, block = False):
        if self._ao.get_flags().busy:
            print "Cannot run ramp, device is busy."
            self._ao.cancel()
            print "Canceled the command."

        b_size = self._ao.get_buffer_size()

        self._ao.command()
        self._ramp_data.tofile(self._ao.device.file)
        self._ao.device.file.flush()
        self._ao.device.do_insn(Util.inttrig_insn(self._ao))
        if callback is not None or block is True:
            c = 0
            while self._ao.get_buffer_contents() > 0:
#                c+=1
                time.sleep(0)
#                if (c > 10000):
#                    print 
#                    c = 0
            self._ao.cancel()
            if callback is not None:
                print "Calling "+str(callback)+"."
                callback()



##     def _linear_bits_from_volt(self, start, end):
##         bits_start = self._ao_converter.from_physical(start)
##         bits_end = self._ao_converter.from_physical(end)
##         print "Start: "+str(bits_start)+"/"+str(start)+", end: "+str(bits_end)
##         samples = numpy.absolute(bits_end - bits_start) 
##         data = numpy.linspace(bits_start, bits_end, samples)
##         values = numpy.zeros((samples, 1), numpy.uint16)
##         values[:,0] = [numpy.uint16(round(i)) for i in data]
##         return values

##     def _wait_for_device(self):
##         while self._ao.get_flags().running:
## #            print "Waiting for device"
##             _time.sleep(0)            
##         self._ao.cancel()

##     def volts_in2out(self, volt):
##         min_in = min(self._config._cvoltrange)
##         max_in = max(self._config._cvoltrange)
##         min_out = min(self._config._voltrange)
##         max_out = max(self._config._voltrange)
##         f = (volt - min_in)/(max_in - min_in)
##         return min_out + f * (max_out-min_out)
        

##     def _current_volts(self, length=10):
##         data = self._ai_channel.data_read_n(length)
##         return (self._ai_converter.to_physical(numpy.mean(data))
##                 /float(self._config._amplification))

##     def _current_volts_quick(self):
##         return (self._ai_converter.to_physical(self._current_bits_quick())
##                 /float(self._config._amplification))

##     def _current_bits_quick(self):
##         return self._ai_channel.data_read()
    
    
##     def _run_ramp(self):
##         print "in _run_Ramp"
##         f = self._ao.device.file
##         if len(self._ao_ramp_data) == 1:
##             print "In first if!"
##             self.set_bit(self._ao_ramp_data[0])
##             time.sleep(float(self._ao_ramp_cmd.scan_begin_arg)*1e-9)
##         elif len(self._ao_ramp_data) == 0:
##             print "In first elif!"
##         elif len(self._ao_ramp_data) >= 2**15:
##             self._ao_ramp_data = self._ao_ramp_data[:-(2**15)+1]
##             self._ao_ramp_cmd.stop_arg=2**15
##         else:
##             print "In first else!"
##             self._ao.cmd = self._ao_ramp_cmd
##             print "1"
##             self._ao.command_test()
##             print "2"
##             self._ao.command()
##             print "3"
                
##             self._ao_ramp_data.tofile(f)
##             print "4"
##             f.flush()
##             print "5"
##             self.is_running = 1
##             print "6"
##             self._ao.device.do_insn(Util.inttrig_insn(self._ao))
##             print "7"
##             t = 0
##             print "8"
##             while self._ao.get_flags().running:
##                 if t == 0 :
##                     print "waiting for piezo in ramp"
##                     t=1
##                 time.sleep(0.000001)
                
##         print "finished ramp"
##         self._ao.cancel()
##         self.is_running = 0
##         global reactor
##         if self._ao_ramp_callback is not None:
##             print "calling callback"
##             reactor.callFromThread(self._ao_ramp_callback)

##     def isRunning(self):
##         return self.is_running == 1

##     def timed_volts_ramp(self, start, end, time, callback=None):
##         print "Start (timed_volts_ramp): "+str(start)
##         self.prepare_timed_volts_ramp(start, end, time)
##         self._ao_ramp_callback = callback
##         foo = reactor.callInThread(self._run_ramp)

##     def prepare_timed_volts_ramp(self, start, end, time):
##         values = self._linear_bits_from_volt(start,end)
##         samples = len(values[:,0])
##         updatefrequency = float(samples)/(float(time)/1000)
##         if updatefrequency == 0:
##             updatefrequency = 1e6
##         command = self._ao.get_cmd_generic_timed(1,
##                                                  1e9/updatefrequency)
##         command.stop_src = CONSTANTS.TRIG_SRC.count
##         command.start_src = CONSTANTS.TRIG_SRC.int
##         command.stop_arg = samples
##         command.chanlist = [self._ao_channel]
        
            
##         self._ao_ramp_cmd = command 
##         self._ao_ramp_data = values
    

##     def unbusy_device(self, t):
##         if not self._ao.get_flags().busy:
##             return
##         start = time.time()
##         while self._ao.get_flags().busy and time.time() - start < t:
##             time.sleep(0.0001)
        
##         if self._ao.get_flags().busy:
##             self._ao.cancel()
        
##     def _stop_thread_and_call_cb(self):
##         if self._ao_ramp_callback is not None:
##             self._ao_ramp_callback()
##     def timed_nm_ramp(self, start, end, time):
##         self.timed_volts_ramp(self._config.nm2volt(start),
##                               self._config.nm2volt(end), time)

##     def timed_um_ramp(self, start, end, time):
##         self.timed_nm_ramp(1000*start, 1000*end, time)
    
##     def set_volt(self, volt):
##         bit = self._ao_converter.from_physical(volt)
##         self.set_bit(bit)

##     def set_bit(self, bit):
##         self._ao_channel.data_write(bit)


##     def set_nm(self, pos):
##         self.set_volt(self._config.nm2volt(pos))

##     def set_um(self, pos):
##         self.set_volt(self._config.nm2volt(1000*pos))


##     def volts_ramp(self, start, end, speed, callback = None):
##         '''Outputs a ramp from "start" to "end" with a defined speed.

##         Params:
##         =======
##         start: Start voltage in volt
##         end:  End voltage in volt
##         speed: Speed in voltages per millisecond
##         '''
##         print "In volts_ramp"
##         if (speed<=0):
##             print "Speed is: "+str(speed);
##             sys.exit('negative or zero speed cannot be processed')
##         self.timed_volts_ramp(start, end, numpy.absolute(start-end)/speed, callback)
    
##     def nm_ramp(self, start, end, speed):
##         '''Outputs a ramp from "start" to "end" with a defined speed.

##         Params:
##         =======
##         start: Start voltage in nanometers
##         end:  End voltage in nanometers
##         speed: Speed in nm per millisecond
##         '''
##         self.volts_ramp(self._config.nm2volt(start), self._config.nm2volt(end),
##                         self._config.nm2volt(speed))
##     def um_ramp(self, start, end, speed):
##         '''Outputs a ramp from "start" to "end" with a defined speed.

##         Params (required):
##         ==================
##         start: Start voltage in micrometers
##         end:  End voltage in micrometers
##         speed: Speed in micrometers per millisecond
##         '''
##         self.nm_ramp(1000*start, 1000*end, 1000*speed)
    
##     def ramp_to_volt_target(self, target, speed, callback = None):
##         '''Outputs a ramp from the current voltage to the specified target voltage.
        
##         Params (required):
##         ==================
##         target: Target voltage (in volts)
##         speed: Speed for performing the ramp (in voltages per millisecond)
##         '''
        
##         self.volts_ramp(self.volts_in2out(self._current_volts()), target, speed, callback)

##     def ramp_to_nm_target(self, target, speed, callback = None):
##         '''Outputs a ramp from the current position to the target position
        
##         Params (required):
##         ==================
##         target: Target position in nanometers
##         speed: Speed for performing the ramp in nm/ms
##         '''
##         print "ramp_to_nm_target"
## #        print "-----------------"
## #        print "Target (nm): " +str(target)
## #        print "Speed (nm/ms): " +str(speed)
## #       print "---- end --------"
        

##         self.ramp_to_volt_target(self._config.nm2volt(target),
##                                  self._config.nm2volt(speed)-self._config.nm2volt(0),
##                                  callback)

##     def ramp_to_um_target(self, target, speed, callback = None):
##         '''Outputs a ramp from the current position to the target position
        
##         Params (required):
##         ==================
##         target: Target position in micrometers
##         speed: Speed for performing the ramp in micm/ms
##         '''
##         self.ramp_to_nm_target(1000*target, 1000*speed, callback)

##     def ramp_by_volts(self, diff, speed):
##         '''Outputs a ramp from the current voltage to the current voltage+diff
        
##         Params (required):
##         ==================
##         diff: Volts to add/substract from the current output
##         speed: Speed for performing the ramp in volt/ms
##         '''
        
##         curr = self._current_volts()
## #        print("Current: " +str(curr))
## #        print("Difference: " +str(diff))
## #        print("Speed: "+ str(speed))
##         self.volts_ramp(curr, curr+diff, speed)
        
##     def ramp_by_nm(self, diff, speed):
##         '''Outputs a ramp from the position to current+diff position
        
##         Params (required):
##         ==================
##         diff: Nanometers to add/substract from the current position
##         speed: Speed for performing the ramp in nm/ms
##         '''
        
##         self.ramp_by_volts(self._config.nm2volt(diff),
##                            self._config.nm2volt(speed))
            

class ZPiezoControl (PiezoControl):
    DECREASE = 0
    INCREASE = 1

    approach_direction = 0

    
    def __init__(self, config, ao, ai, reactor, approachdir):
        if(config._direction != PiezoConfig.DIRECTION_Z):
            config._direction = PiezoConfig.DIRECTION_Z
        self.approach_direction = approachdir;
        super(ZPiezoControl, self).__init__(config, ao, ai, reactor)
        self.home()



    def home(self):
        print "Setting piezo to home position"
        if (self.approach_direction == self.DECREASE):
            self.set_nm(self._config._distance)
        elif (self.approach_direction == self.INCREASE):
            self.set_nm(0)

    def deflection(self, bits):
        return bits
#        if self.approach_direction == self.DECREASE:
#            return self._config._distance - self.input_bits2nm(bits)
#        else:
#            return self.input_bits2nm(bits)


    def getApproachTarget(self):
        if (self.approach_direction == self.DECREASE):
            v = self.converter.getConvertedNumber(0, Converter.UNIT.nm)
        elif (self.approach_direction == self.INCREASE):
            v = self.converter.getConvertedNumber(self._config._distance, Converter.UNIT.nm)
        return v
    
    def approach(self, speed):
        global reactor

        if (self.approach_direction == self.DECREASE):
            print "Will call thread. (1)"
            reactor.callInThread(
            self.ramp_to_nm_target, 0, speed)
            print "Have called thread. (1)"
        elif (self.approach_direction == self.INCREASE):
            print "Will call thread. (2)"
            reactor.callInThread(
                self.ramp_to_nm_target,self._config._distance, speed)
            print "Have called thread. (2)"

##     def approach_noThread(self, speed):
##         #select target position
##         if (self.approach_direction == self.DECREASE):
##             target = 0
##         elif (self.approach_direction == self.INCREASE):
##             target = self._config._distance
##         self.ramp_to_nm_target_noThread(target, speed)

##     def ramp_to_nm_target_noThread(self, target, speed):
## #        print "Target: "+str(target)
## #        print "Speed: "+str(speed)
##         self.ramp_to_volts_noThread(self._config.nm2volt(target),
##                                     self._config.nm2volt(speed)-self._config.nm2volt(0))

##     def ramp_to_volts_noThread(self, target, speed):
##         start=self.calibrated_volts_from_bits(self._current_bits_quick())
##         self.prepare_timed_volts_ramp(start, target, 
##                                       numpy.absolute(start-target)/float(speed))
##         f = self._ao.device.file
##         print "Expecting " +str(self._ao_ramp_cmd.stop_arg)+" samples"
##         print "Data length is  " +str(len(self._ao_ramp_data))+" samples"
##         print "Target is "+str(target)
##         self._ao.cmd = self._ao_ramp_cmd
##         self._ao.command_test()
##         self._ao.command()
##         l = self._ao_ramp_data[-1]
##         r = self._ao_ramp_data
##         t = 0;
##         c = 0;
##         while len(r) >= 2 ** 15:
##             print "In while "+str(c)
##             c = c +1
##             s = r[0:2**15];
##             print "Writing "+str(len(s))+" bytes"
##             t = t + len(s)
##             st = time.time()
##             print "Buffer contents: "+str(self._ao.get_buffer_contents())
##             s.tofile(f)
##             e = time.time()
##             print "Time for writing 1: "+str(e-st)
            
##             st = time.time()
##             f.flush()
##             e = time.time()
##             print "Time for flushing 1: "+str(e-st)            
##             if t == len(s):
##                 print "Triggering"
##                 self.is_running = 1
##                 st = time.time()
##                 self._ao.device.do_insn(Util.inttrig_insn(self._ao)) 
##                 en = time.time()
##                 print "Triggering took: "+str(en-st)
##             r = r[2**15:-1]
##         if len(r) > 0:
##             global reactor
##             self.remainingData = r
##             reactor.callInThread(self.writeRemainingApproachData)

##             if self.is_running != 1:
##                 print "Triggering"
##                 self.is_running = 1
##                 st = time.time()
##                 self._ao.device.do_insn(Util.inttrig_insn(self._ao)) 
##                 en = time.time()
##                 print "Triggering 2 took: "+str(en-st)

##         print "Total bytes written: "+str(t)
##         q = 0;
## #        while self._ao.get_flags().busy and self._ao.get_flags().running:
## #            if q == 0:
## #                print "Still busy"
## #            q = q + 1
## #            q = q%100000

## #        self._ao.cancel()
## #        self.is_running = 0
        

##     def writeRemainingApproachData(self):
##         f = self._ao.device.file
##         while len(self.remainingData) > 0:
##             if len(self.remainingData) > 2**15:
##                 s = self.remainingData[0:2**15]
##                 self.remainingData=self.remainingData[2**15:-1]
##             else:
##                 s = self.remainingData
##                 self.remainingData=[]
##             s.tofile(f);
##             f.flush()

##     def approach_and_retract(self, speed, retract_to):
##         self._retract_pos = retract_to
##         if (self.approach_direction == self.DECREASE):
##             self.ramp_to_nm_target(0, speed, self._retract)
##         elif (self.approach_direction == self.INCREASE):
##             self.ramp_to_nm_target(self._config._distance, speed, self._retract)

    def stop(self):
        print "Cancelling"
        self._ao.cancel()
        self.isRunning=0
        n = self._ao.get_buffer_contents()
        print "Will delete "+str(n)+" bytes."
        self._ao.mark_buffer_written(n)

##     def _retract(self):
##         self._ao.cancel()
##         self.ramp_to_nm_target(self._retract_pos,1000)

    def current_nm(self):
        nm = self.input_bits2nm(self.current_bit_quick())
        return nm

##     def getSignForApproach(self):
##         if self.approach_direction == self.DECREASE:
##             return -1
##         return 1
    
##     def getSignForRetract(self):
##         return -1 * self.getSignForApproach()


class Booster(object):

    def __init__(self, channel):
        self.channel = channel
        self.channel.dio_config(CONSTANTS.IO_DIRECTION.output)
        self.home()
    def up(self):
        self.channel.dio_write(1)

    def home(self):
        self.channel.dio_write(0)
    

###
# This is a suggestion for approaching and measuring
#
# inf_curr = numpy.average(ai_channel.read_n(1000))
# zpiezo.approach(speed)
# m = numpy.average(ai.channel.read_n(100))
# while m/inf_curr > threshold and zpiezo.isRunning():
#     m = numpy.average(ai.channel.read_n(100))
# aodevice.cancel()
# zpiezo.set_nm(pos)
