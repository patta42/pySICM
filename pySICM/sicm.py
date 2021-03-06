# Copyright (C) 2014 Patrick Happel <patrick.happel@rub.de>
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

# from piezo import 

import sys
import numpy
import json

  
    
    


class SICMConfig(object):
    '''Class for configuring the Setup of a SICM'''
    
    controlables = {}
    
    def __init__(self):
        pass

    def add_controlables(self, **kwargs):
        self.controlables = kwargs
    

class _SICMMeasurement(object):
    '''base class for SICM measurements
    
    '''

    _config = {}
    _requirements = {}
    _reqoptions = {}
    _reactorCall = None

    def __init__(self):
        self.data = []
        self._reqoptions = {}
        
    def _setRequired(self, key, number, typ):
        self._requirements['key'] = {
            'amount': number,
            'type' : typ}

    def _setRequiredOptions(self, key, number, typ, expl, col = None, pos = None):
        self._reqoptions[key] = {
            'number': number,
            'type' : typ,
            'expl' : expl
        }
        if col is not None:
            self._reqoptions[key]['col'] = col
        if pos is not None:
            self._reqoptions[key]['pos'] = pos

    def getRequiredOptions(self):
        print "Hi, I am "+str(self)
        s = self._reqoptions.copy()
        
        for k,v in s.iteritems():
            v.pop('type', None)
        return json.dumps(s)

    def checkConfig(self, config):
        errors = []
        for k,v in self._reqoptions.iteritems():
            if k not in config:
                errors.append('No configuration for '+str(k)+' given.')
                continue
            if len(config[k]) < v['number']:
                errors.append(str(v['number'])+' configuration(s) for '+str(k)+' expected, but '+str(len(config[k]))+' given.')
                continue
            if not isinstance(config[k], dict):
                errors.append('Configuration must be a dictionary, even if indexed with numbers.')
                continue
            for i in xrange(len(config[k])):
                if not isinstance(config[k][i], v['type']):
                    errors.append('Configuration '+str(i)+' for '+str(k)+' is of wrong type. The explanation string is: '+v['expl'])
        return (len(errors) == 0, errors)

    def checkAndSetConfig(self, settings):
        
        if 'mode' not in settings:
            print "Mode not in settings"
            return False
        if settings['mode'] != self.mode:
            print "Mode not self.mode"
            return False
        if self.mode not in settings:
            print "self.mode not in settings (self.mode is "+str(self.mode)+")"
            return False
        rsettings = settings[self.mode]

        for k in self._reqoptions:
            key = k.split(".",1)[-1]
            if key not in rsettings:
                print "key ("+str(key)+") not in rsettings"
                return False
            self.setConfig(key, self._reqoptions[k]['type'](rsettings[key]))
        return True


    def setConfig(self, key, val):
        self._config[key] = val
    def getConfig(self, key):
        return self._config[key]

    def setOptions(self):
        for o in self._options:
            self._setRequiredOptions(o[0], o[1], o[2], o[3], col = o[4], pos = o[5])
    def destroy(self):
        if self._reactorCall is not None:
            self._reactorCall.cancel()
            self = None
    

class BackstepScan (_SICMMeasurement):
    
    def __init__(self, cfg):
        super(BackstepScan, self).__init__(cfg)
    def run(self):
        pixelwidth = 50
        offsetX = 3000
        offsetY = 4000
        q = 1
        for y in range(0,128):
            if y == 0:
                self.y.ramp_to_nm_target(offsetY,100)
                self.y._wait_for_device()
            for x in range(0,128):
                if x == 0:
                    self.x.ramp_to_nm_target(offsetX,100)
                    self.x._wait_for_device()
                ref = self.ai_channel.data_read_n(10)
                ref = numpy.mean(ref)
                d = ref
                print (str(x)+" "+str(y))
                self.z.approach(10)
                
                while q > 0 and  d > 0.98 * ref:
                    d = self.ai_channel.data_read()
                    print(d)
#                    if self.z._ao.get_flags().busy and self.z._ao.get_flags().running:
                    pass
                    #else:
                    #    q = 0
                else:
                    self.z._ao.cancel()
                    self.z.set_volt(9.5)
 #               self.x.ramp_to_nm_target((x+1)*pixelwidth,100.0)
 #               self.x._wait_for_device()
#            self.y.ramp_to_nm_target((y+1)*pixelwidth, 100.0)
#            self.y._wait_for_device()

    
    
