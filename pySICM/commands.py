import json
from pySICM.error import PySICMError
from twisted.internet import defer
class Command(object):
    command = ''
    cb = None
    _id = None
    
    def __init__(self, command, cb, cmgr):
        self.command = command.upper()
        self.cb = cb
        self.cmgr = cmgr
        
    def setId(self, _id):
        self._id = _id

    def _succesfulWriteDefered(self, output, jsonify = False):
        print str(output)
        if jsonify:
            out = json.dumps(output)
        else:
            out = output
        print str(out)
        d = defer.succeed(out)
        return d
    
    def nack(self):
        return self._succesfulWriteDefered('NACK')
    def getCommandString(self):
        return self.command

    def _execute(self, value, _id = None):
        print "Value (in _execute) is: "+str(value)
        def addId(val):
            if _id is not None:
                return str(_id) + ":" + val
            else:
                return val
        if value is not None:
            try:
                value.addCallback(addId)
            except:
                value = str(_id) + value
        return value
    
    def execute(self, param = '', _id = None):
        return self._execute(self.cb(), _id)
        
class CommandWithParam(Command):

    params = {}
    def __init__(self, command, cmgr):
        self.command = command.upper()
        self.cmgr = cmgr
        
    def addParam(self, param, cb):
        self.params[param] = cb

    def execute(self, param, _id = None):
        print "Trying to call "+str(self.command)+" with param: "+str(param)
#        print "The callback is "+ str(self.params[param])
        if param in self.params:
            print "Param is known"
            return self._execute(self.params[param](), _id = _id)
        else:
            PySICMError('Parameter '+str(param)+' not defined for command '+str(self.command))

class CommandWithParamValue(Command):
    def __init__(self, command, cb, cmgr):
        super(CommandWithParamValue, self).__init__(command, cb, cmgr)
 
    def execute(self, param, _id = None):
        key, value = param.split("=")
        self.setValue(key, value)
        
    def setValue(self, key, value):
        self.cmgr.settings[key] = value
        print str(self.cmgr.settings)

    

class _CommandManager(object):
    commands = {}
    settings = {'myint' : 21080}
    modeobj = None
    def __init__(self):
        pass

    def addCommand(self, command):
        try:
            command.getCommandString
        except:
            raise PySICMError('Command does not have the method `getCommandString`. Might be the wrong type.')

        self.commands[command.getCommandString()] = command

    def hasCommand(self, com):
        print "Command is known? " + str(com.upper() in self.commands)
        return com.upper() in self.commands
        

    def splitCommand(self, com):
        tmp = com.split(" ", 1)
        try:
            tmp[1]
        except:
            tmp.append('')
        return tmp[0].upper(), tmp[1]
    
    def handle(self, comstring, _id = None):
        com, param = self.splitCommand(comstring)
        if not self.hasCommand(com):
            print "Unknown command"
            PySICMError('Command '+com+' unknown')
        else:
            print "Trying to execute "+str(com.upper())
            return self.commands[com.upper()].execute(param, _id = _id)
