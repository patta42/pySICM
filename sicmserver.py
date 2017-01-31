from twisted.internet import protocol, reactor, defer, utils
#from twisted.protocols import basic
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from pySICM.setup import pysicmsetup as SETUP
import pySICM.helpers as Helpers
import pySICM.commands as Com
import pySICM.commanddef
import os
import json


class SicmXProt(LineReceiver, Com._CommandManager):

#    knownCommands = ['GET','SET','SCAN','READY', 'FAKE', 'STOP']    

    
    def __init__(self):
        super(SicmXProt, self).__init__()
        pySICM.commanddef.add_command_list(self)
        
    def connectionMade(self):
        d = self.factory.check_connection_allowed()
        
        def onError(err):
            return 'Internal Server Error in SicmXProt::connectionMade'
        
        d.addErrback(onError)
        print "Connection made callback is "+str(d)
        def wR(message):
#            if isinstance (message, list):
                
            self.transport.write(str(message)+"\r\n")
            if message != "ACK":
                self.transport.loseConnection()
        d.addCallback(wR)
    
    def connectionLost(self, reason):
        self.factory.decrease_clients()
    def writeResponse(self, message, newline = True):
        if newline:
            self.transport.write(str(message)+"\r\n")
        else:
            self.transport.write(str(message))

    def lineReceived(self, line):
        _id = None
        if line.startswith("#"):
            _id, _line = line.split(':')
            line = _line
        
        d = self.handle(line, _id = _id)
        try:
            d.addCallback(self.writeResponse)
        except:
            pass
        


class SicmXFactory(Factory):
    protocol =  SicmXProt

    
    def __init__(self):

        self.num_connections = 0
        
    def check_connection_allowed (self):
        if self.num_connections == 0:
            self.num_connections = 1
            return defer.succeed("ACK")
        else:
            return defer.succeed("NAK")
    def decrease_clients(self):
        self.num_connections -= 1
        if self.protocol.modeobj is not None:
            self.protocol.modeobj.setStop()
            self.protocol.modeobj=None
       
#    def writeResponse(self, message, newline=True):
#        self.protocol.writeResponse(message, newline)
        
    

            
if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, SETUP.server['port'])
    endpoint.listen(SicmXFactory())
    reactor.run()

    
