import pySICM.commands as Com
import json
import pySICM.helpers as Helpers

from pySICM.setup import pysicmsetup as SETUP
from twisted.internet import utils, defer
from subprocess import check_output


class CmdStop(Com.Command):
    def __init__(self, cmgr):
        super(CmdStop, self).__init__('STOP', self.stop, cmgr)

    def stop(self):
        if self.cmgr.modeobj is not None:
            return self.cmgr.modeobj.setStop()
        else:
            print "Modeobj is None. Doing Nothing."
            return None


class CmdScan(Com.Command):
    def __init__(self, cmgr):
        super(CmdScan, self).__init__('SCAN', self.scan, cmgr)

    def _isTool(self, mode):
        return mode.startswith('tool')

    def scan(self):
        print str(self.cmgr.settings)
        if 'mode' in self.cmgr.settings:
            mode = self.cmgr.settings['mode']
        else:
            print "Going to return NACK (1)"
            return self.nack()
        tmp = []
        for t in SETUP.tools:
            tmp.append('tool'+t[0].upper()+t[1:])
        if mode in tmp+SETUP.modes:
            self.cmgr.modeobj = Helpers.getScanmodeObject(mode, self._isTool(mode))()
            return self.cmgr.modeobj.scan(self.cmgr.settings, self.cmgr.writeResponse)
        else:
            print "Going to return NACK (2)"
            return self.nack()

class CmdGet(Com.CommandWithParam):
    def __init__(self, cmgr):
        super(CmdGet, self).__init__('GET', cmgr)
        self.addParam('BOARDINFO', self.getBoardInfo)
        self.addParam('MODES', self.getModes)
        self.addParam('TOOLS', self.getTools)
        self.addParam('SICMINFO', self.getSicmInfo)
        self.addParam('OPTIONS', self.getOptions)

    def getBoardInfo(self):
        r = {}
        for i in xrange(0, SETUP.instrument['main']['devices']):
            r[i] = check_output([SETUP.files['board_info'],
                                 SETUP.instrument['devices'][i]['board'].filename])
        return self._succesfulWriteDefered(json.dumps(r))
    
    def getModes(self):
        return self._succesfulWriteDefered(SETUP.modes, jsonify = True)

    def getTools(self):
        return self._succesfulWriteDefered(SETUP.tools, jsonify = True)

    def getSicmInfo(self):
        s = {'Controllables':{},
             'Inputsignals': {},
             'Outputsignals':{}}
        count = 0
        for k, v in SETUP.instrument['controllables'].iteritems():
            s['controllables'][count]={
                'name': v.name,
                'x' : (v.x() and v.x()._config._distance) or None,
                'y' : (v.y() and v.y()._config._distance) or None,
                'z' : (v.z() and v.z()._config._distance) or None,
                'xcoarse' : (v.xcoarse() and 1) or None,
                'ycoarse' : (v.ycoarse() and 1) or None,
                'zcoarse' : (v.zcoarse() and 1) or None,
                'zfine' : (v.zfine() and 1) or None}
            count += 1
        count = 0
        for k, v in SETUP.instruments['Outputsignals'].iteritems():
            s['Outputsignals'][count]={'name':v.name}
            count += 1
        count = 0
        for k, v in SETUP.instruments['Inputsignals'].iteritems():
            s['Inputsignals'][count]={'name': v.name}
            count += 1
        return self._succesfulWriteDefered(json.dumps(s))
    
    def getOptions(self):
        if self.cmgr.modeobj is None and 'mode' not in self.cmgr.settings:
            return self.nack()
        if self.cmgr.modeobj is not None:
            if self.cmgr.modeobj.mode == self.cmgr.settings['mode']:
                return self._succesfulWriteDefered(self.cmgr.modeobj.getRequiredOptions())
            else:
                del self.cmgr.modeobj
                self.cmgr.modeobj = None
        if self.cmgr.modeobj is None:
            mode = self.cmgr.settings['mode']
            self.cmgr.modeobj = Helpers.getScanmodeObject(mode)()
            return self._succesfulWriteDefered(self.cmgr.modeobj.getRequiredOptions())
        

class CmdSet(Com.CommandWithParamValue):
    def __init__(self, cmgr):
        super(CmdSet, self).__init__('SET', self.setValue, cmgr)
        
    def setValue(self, key, value):
        print "Key is: "+str(key)
        print "Value is: "+str(value)
        if key.find('.') < 0:
            super(CmdSet, self).setValue(key, value)
        else:
            key, subkey = key.split(".", 1)
            if key not in self.cmgr.settings:
                self.cmgr.settings[key] = {}
            self.cmgr.settings[key][subkey] = value
            
                
            

def add_command_list(cmgr):
    cmgr.addCommand(CmdStop(cmgr))
    cmgr.addCommand(CmdScan(cmgr))
    cmgr.addCommand(CmdGet(cmgr))
    cmgr.addCommand(CmdSet(cmgr))
    
