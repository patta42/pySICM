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
import re
import pyAPT.pt1
from pySICM.setup import pysicmsetup as SETUP
from scanmodes.approach import Approach

class AutomaticApproach (Approach):
    _add_options = [['AutomaticApproach.CoarseStepSize', 1, float, 
                 'Step size of coarse approach in mm (float)', 
                 0, 0],
                ['AutomaticApproach.Distance', 1, int, 
                 'Final distance in micm (int)',
                 0, 2]
                ]

    mode = 'automaticApproach'

    def __init__(self):
        for opt in self._options:
            opt[0] = re.sub('[A-Za-z_]+\.','AutomaticApproach.',opt[0])
            self._add_options.append(opt)
        self._options  = self._add_options
        super(AutomaticApproach, self).__init__()


#        self.setOptions()
        self.stop = False
        

            
    def init_devices(self):
        for c in SETUP.instrument['controllables'].itervalues():
            if c.zcoarse():
                self.coarseStage = c.zcoarse()

    def scan(self, settings, writeResponse):
        self.writeResponse = writeResponse
        if self.checkAndSetConfig(settings):
            self._config['Threshold']/=100
            self.init_devices()
            self._init_internals()
            self.calibrate()
            self.detectSurface()
#            self.makeContact()

    def calibrate(self):
        f = []
        for i in range(0,4):
            j = 0
            s = time.time()
            while j < 2**15:
                self.signal.read()
                j += 1
            e = time.time()
            f.append(float(2**15/(e-s)))

        m_freq = np.mean(f)
        s_freq = np.std(f)

        freq = m_freq + 5*s_freq
        
        if freq < 10000:
            print "Reading data with less than 10kHz."
        distance = self.piezo._config._distance
        print distance
        self.max_approach_points = freq * distance/(1e3*self.getConfig('FallRate'))
        
    def makeContact(self):
        zero = self.signal.read()
        if self.signal.toPhysical(zero) > 1:
            print "There is a decent current flowing. Assuming that I'm in bath"
            self.detectSurface()
        else:
            coarse_step = self.getConfig('CoarseStepSize')
            ok = True
            diff = 0
        
            while ok is True and diff < 2000:
                ok = self.coarseStage.move(coarse_step)
                diff = np.absolute(self.signal.read() - zero)
            if ok:
                print "In contact"
                print "Diff was: "+str(diff)
                self.detectSurface()
            else:
                print "Cannot reach bath"
            
    def detectSurface(self):
        self.generateDeferred()
        self.retract = True
        self.boost = True
        self.readFrequency = self.getReadFrequency()
        self.d = threads.deferToThread(self._detectSurface)
        self.d.addCallback(self.writeData)
        self.d.addErrback(self.handleError)


    def _detectSurface(self):
        touched = 0
        distance = 0.95 * 1e-6 * self.piezo._config._distance
        lastApp = 0
        while touched != 2:
            app_data = super(AutomaticApproach, self)._detectSurface(returnPos = True)
            print str(app_data)
            if app_data['threshold_detected'] is False:
                touched = 0
                if time.time()-lastApp < 2:
                    print "Waiting"
                    time.sleep(2)
                lastApp = time.time()
                self.coarseStage.down(distance)
            else:
                if touched == 0:
                    touched = 1
                    travelled_distance = abs(app_data['start_pos'] - app_data['end_pos'])
                    delta = self.getConfig('Distance') - (self.piezo._config._distance  
                             -travelled_distance) * 1e-3 
                    print "After first approach I was "+str(delta)+" micm away"
                    if delta == 0:
                        touched = 2
                    elif delta < 0:
                        print "Raising pipette by "+str(-1*1e-3*delta)+"mm"
                        self.coarseStage.up(-1*1e-3*delta)
                    elif delta > 0:
                        print "Lowering pipette by "+str(1e-3*delta)+"mm"
                        self.coarseStage.down(1e-3*delta)
                elif touched == 1:
                    touched = 2
                    
                    
        return app_data
    
