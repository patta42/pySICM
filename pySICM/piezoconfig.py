import numpy
import pycomedi.channel as pyChan
import pycomedi.constant as CONSTANTS
import pycomedi.utility as Util
import sys
import time
from twisted.internet import defer, reactor

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
        return f * 

