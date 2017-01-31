## Copyright (C) 2015 Patrick Happel <patrick.happel@rub.de>
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

import ConfigParser, re, os
import pycomedi.constant as CONSTANTS
from twisted.internet import reactor
from pycomedi.device import Device
from pycomedi.subdevice import StreamingSubdevice
from pycomedi.channel import AnalogChannel, DigitalChannel
from pycomedi import PyComediError
import pySICM.piezo as Piezo
from pySICM.error import PySICMError
import pySICM.controllable as Controllable
import pySICM.inputsignal as InputSignal
import pySICM.outputsignal as OutputSignal
import pySICM.helpers as Helpers



class Setup(object):
    '''Class for parsing a setup.ini file'''

    DEFAULTINIFILE='/etc/pySICM/setup.ini'
    instrument = {
        'main'           : {},
        'devices'        : {},
        'outputchannels' : {},
        'inputchannels'  : {},
        'piezos'         : {},        
        'controllables'  : {},
        'inputsignals'   : {},
        'outputsignals'  : {},
        'others'         : {}
    }

    files = {
        'inifile'      : '',
        'scanmodesdir' : '',
        'toolsdir'     : '',
        'board_info'   : '/usr/local/bin/comedi_board_info'
        }
    server = {'port' : 0}
    modes = []
    tools = []
        

    def __init__(self, fname = ''):
#        self.pysicm = pySICM.pysicmconf.PysicmConf()
        if fname != '':
            self.filename = fname
        else:
            self.filename = self.DEFAULTINIFILE
        self.parser = ConfigParser.RawConfigParser()
        self.parser.read(self.filename)

        files = self.files
        files['inifiles'] = fname
        files['scanmodesdir'] = self.parser.get('pySICM','scanmodesdir')
        files['toolsdir'] = self.parser.get('pySICM','toolsdir')

        l = os.listdir(self.files['scanmodesdir'])
        for f in l:
            if f.endswith('.py') and f[0] != '_' and f[0]!='.':
                self.modes.append(os.path.splitext(f)[0])

        l = os.listdir(self.files['toolsdir'])
        for f in l:
            if f.endswith('.py') and f[0] != '_' and f[0]!='.':
                self.tools.append(os.path.splitext(f)[0])

        
        self.server['port'] = self.parser.getint('pySICM','port')

#        self.modes
        
        main=self.instrument['main']
        main['devices'] = self.parser.getint('Main','Devices')
        main['outputchannels'] = self.parser.getint('Main','Outputchannels')
        main['inputchannels'] = self.parser.getint('Main','Inputchannels')
        main['piezos'] = self.parser.getint('Main','Piezos')
        main['controllables'] = self.parser.getint('Main','Controllables')
        main['inputsignals'] = self.parser.getint('Main','Inputsignals')
        main['outputsignals'] = self.parser.getint('Main','Outputsignals')
        main['others'] = self.parser.getint('Main','Others')
        self._populateConfig()

    def _populateConfig(self):
        self.generateDevices()
        self.generateChannels('in')
        self.generateChannels('out')
        self.generateControllables()
        self.generateSignals()
#        self.generateOthers()
        
    def generateDevices(self):
        for i in xrange(self.instrument['main']['devices']):
            devconf = {
                'board': None,
                'analog':{
                    'in' : None,
                    'out':None},
                'digital':{
                    'in': None,
                    'out': None,
                    'io': None},
                'counter': None}

            device = Device(self.parser.get('Device'+str(i),'path'))
            device.open()
            devconf['board'] = device
            
            try:
                devconf['analog']['in'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.ai)
            except PyComediError:
                pass
            try:
                devconf['analog']['out'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.ao, factory = StreamingSubdevice)
            except PyComediError:
                pass
            try:
                devconf['digital']['in'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.di)
            except PyComediError:
                pass
            try:
                devconf['digital']['out'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.do)
            except PyComediError:
                pass
            try:
                devconf['digital']['io'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.dio)
            except PyComediError:
                pass
            try:
                devconf['counter'] = device.find_subdevice_by_type(
                    CONSTANTS.SUBDEVICE_TYPE.counter)
            except PyComediError:
                pass
            self.instrument['devices'][i] = devconf

    def generateChannels(self, inout):
        
        Inout = inout.capitalize()
        
        print "Generating channels for "+str(Inout)+"put"
        
        for i in xrange(self.instrument['main'][inout+'putchannels']):
            dev = self.parser.getint(Inout+'putchannel'+str(i),'device')
            typ = self.parser.get(Inout+'putchannel'+str(i),'type')
            num = self.parser.getint(Inout+'putchannel'+str(i),'number')
            rang = self.parser.get(Inout+'putchannel'+str(i),'vrange')
            if dev in self.instrument['devices']:
                device = self.instrument['devices'][dev]
                if typ == 'a':
                    if device['analog'][inout] is None:
                        raise PySICMError(
                            'An analog channel has been specified for '+inout+'put channel '+str(i)+
                            ', but the device does not have an analog '+inout+'put subdevice.')
                    else:
                        self.instrument[inout+'putchannels'][i] = self.registerAnalogChannel(device['analog']['in'], num, rang)
                elif typ == 'd':
                    if device['digital'][inout] is None:
                        raise PySICMError(
                            'A digital channel has been specified for '+inout+'put channel '+str(i)+
                            ', but the device does not have a digital '+inout+'put subdevice.')
                

               
    def registerAnalogChannel(self, sdev, num, rang):
        print ("registering an analog channel with number " 
               +str(num))
        chan = sdev.channel(
            num, factory = AnalogChannel, aref=CONSTANTS.AREF.ground)
        r = rang.split(",",1)
        r_min = float(r[0])
        r_max = float(r[1])
        tmp_range = chan.find_range(CONSTANTS.UNIT.volt,r_min, r_max)
        if tmp_range < 0:
            raise PySICMError(
                'No suitable range was found for channel '+str(num))
        del chan
        return sdev.channel(
            num, factory = AnalogChannel, aref=CONSTANTS.AREF.ground, 
            range=tmp_range)


    def generateControllables(self):
        for i in xrange(self.instrument['main']['controllables']):
            typ = self.parser.get('Controllable'+str(i),'type')
            try:
                rev = self.parser.get('Controllable'+str(i),'reverseaxes')
                rev = rev.split(",")
            except:
                rev = []
            ctr = {}
            if typ in ['Pipette','Stage']:
                typnum = -1
                if typ == 'Pipette':
                    typnum = Controllable.Controllable.PIPETTE
                if typ == 'STAGE':
                    typnum = Controllable.Controllable.STAGE
                for d in ['x','y','z','xcoarse','ycoarse','zcoarse','zfine']:
                    try:
                        dev = self.parser.get('Controllable'+str(i), d)
                    except:
                        dev = None
                    if dev is not None:
                        try:
                            num = int(dev)
                            dev = 'Piezo'+str(num)
                        except ValueError:
                            pass

                        typ2, num = self._getTypAndNum(dev)
                        if typ2 == 'Piezo':
                            ctr[d] = self._generatePiezo(num, d, rev)
                            self.instrument['piezos'][num] = ctr[d]
                        elif typ2 == 'Other':
                            ctr[d] = self._generateOther(num)
                            self.instrument['others'][num] = ctr[d]
                self.instrument['controllables'][i] = Controllable.Controllable(
                    self.parser.get('Controllable'+str(i),'name'), typnum)
                self.instrument['controllables'][i].axes(**ctr)
                    
    def _generatePiezo(self, num, direction, rev):
        dirs = {'x' : Piezo.PiezoConfig.DIRECTION_X,
                'y' : Piezo.PiezoConfig.DIRECTION_Y,
                'z' : Piezo.PiezoConfig.DIRECTION_Z}
        p = 'Piezo'+str(num)
        dist = self.parser.getint(p, 'distance')
        amp = self.parser.getfloat(p, 'amplification')
        tmp = self.parser.get(p, 'vrange').split(",",1)
        ran = [int(k) for k in self.parser.get(p, 'vrange').split(",",1)]
        ochan = self.instrument['outputchannels'][self.parser.getint(p, 'ochannel')]
        try:
            ichan = self.instrument['inputchannels'][self.parser.getint(p, 'ichannel')]
        except:
            ichan = None;
        cnf = {
            'distance':dist, 'amplification':amp,
            'voltrange': ran, 'direction' : dirs[direction]}
        if ichan is not None:
            cnf['ai_channel'] = ichan.index
        else:
            cnf['ai_channel'] = 0
        pcnf = Piezo.PiezoConfig(ochan.index, **cnf)
        reverse = Piezo.ZPiezoControl.INCREASE
        global reactor
#        reactor = None
        if 'z' in rev:
            reverse = Piezo.ZPiezoControl.DECREASE
        if direction == 'z':
            return Piezo.ZPiezoControl(pcnf,
                                       self.instrument['devices'][0]['analog']['out'],
                                       self.instrument['devices'][0]['analog']['in'],
                                       reactor,
                                       reverse)
        else:
            return Piezo.PiezoControl(pcnf,
                                      self.instrument['devices'][0]['analog']['out'],
                                      self.instrument['devices'][0]['analog']['in'],
                                      reactor)

    def _generateOther(self, num):
        print "Parsing Other "+str(num)
        print "Type is "+str(self.parser.get('Other'+str(num), 'type'))
        if self.parser.get('Other'+str(num), 'type') == 'CoarseStage':
            mod = self.parser.get('Other'+str(num), 'module')
            cls = self.parser.get('Other'+str(num), 'class')
            try:
                path = self.parser.get('Other'+str(num), 'path')
            except ConfigParser.NoOptionError:
                path = None
            return Helpers.getObject(mod, cls, path)()
        if self.parser.get('Other'+str(num), 'type') == 'zBoost':
            chan = self.parser.getint('Other'+str(num), 'channel')
            diochan = self.instrument['devices'][0]['digital']['io'].channel(
                chan, factory = DigitalChannel)
            b = Piezo.Booster(diochan)
            print "Booster found! "+str(b)
            return b
            
            
            
    def generateSignals(self):
        for i in xrange(self.instrument['main']['inputsignals']):
            self.instrument['inputsignals'][i] = InputSignal.InputSignal(
                self.parser.get('Inputsignal'+str(i),'name'),
                self.instrument['inputchannels'][self.parser.getint('Inputsignal'+str(i),'ai')])
        for i in xrange(self.instrument['main']['outputsignals']):
            self.instrument['outputsignals'][i] = OutputSignal.OutputSignal(
                self.parser.get('Outputsignal'+str(i),'name'),
                self.instrument['outputchannels'][self.parser.getint('Outputsignal'+str(i),'ao')])


    def _getTypAndNum(self, string):
        res = re.match('[A-Za-z]+', string)
        try:
            typ = res.group()
        except AttributeError:
            PySICMError('Cannot parse string '+ string)

        return typ, string[len(typ):]
        
try:    
    pysicmsetup
except NameError:
    pysicmsetup = Setup()
    print str(pysicmsetup.instrument['controllables'][0].x()._ao_channel.index)
    print str(pysicmsetup.instrument['controllables'][0].y()._ao_channel.index)
    print str(pysicmsetup.instrument['controllables'][0].z()._ao_channel.index)
