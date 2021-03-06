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


#from twisted.internet import reactor
from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver
LineReceiver.MAX_LENGTH=2**20
from pySICM.simplecallback import SimpleCallbackSystem
import time
class PySicmClientProtocol(LineReceiver):

    data = []
    def connectionMade(self):
        self.factory.clientReady(self)

#    def dataReceived(self, data):
#        self.factory.dataReceived(data)
#        "As soon as any data is received, write it back."
#        if data=="ACK":
#            print "Server said:", self.data
#            self.transport.loseConnection()
#        else:
#            self.data.append(data)
#            print (data)
#            print "Appending data. Data now has "+str(len(self.data))+" lines."

    def lineReceived(self, line):
        self.factory.lineReceived(line)
    def connectionLost(self, reason):
        print "connection lost"
    def rawDataReceived(self, data):
        print "Raw data: " + data
    def lineLengthExceeded(self, line):
        print "Uhhh, line length was: "+str(len(line))

class PySicmClientFactory(protocol.ClientFactory, SimpleCallbackSystem):
    
    protocol = PySicmClientProtocol
    callbacks={}    
    tcallbacks={}
    mode = 'line'

    def __init__(self,
                 successCallback,
                 failedCallBack,
                 lostCallBack):
        self.failedCallBack = failedCallBack
        self.lostCallBack = lostCallBack
        self.successCallback = successCallback
    
#    def __init__(self):
#        self.protocol.

    def clientConnectionFailed(self, connector, reason):
        self.failedCallBack(reason)

    def clientConnectionLost(self, connector, reason):
        self.lostCallBack(reason)

    def clientReady(self, client):
        self.client = client
        self.successCallback()

    def lineReceived(self, line):
        #print "received: %s" % line
        _id = None
        if line == "ACK" or line == "":
            return
        if self.mode == 'line':
            if line.startswith("#"):
                _id, _line = line.split(":",1)
                line = _line
            self.fireCallbacks('lineReceived', line, passReturn = True, _id = _id)
        else:
            self.fireCallbacks('dataReceived', line, passReturn = True)


    def sendLineAndGetAnswer(self, line, cb):
        _id = "#{:6f}".format(time.time())
        self.addSingleCallbackWithId('lineReceived', cb, _id)
        self.sendLine(_id+':'+line)
    def addLineReceivedCallback(self, cb):
        self._addCallback('lineReceived', cb)

    def addSendCallback(self, cb):
        self._addCallback('send', cb)

    def sendLine(self, line):
        ret = line
        self.fireCallbacks('lineSent', line, passReturn = True)
        print "Sending %s"% ret
        self.client.transport.write(ret+"\r\n")
    def disconnect(self):
        self.client.transport.loseConnection()
    def setMode(self, mode):
        self.mode = mode
    def setDataMode(self):
        self.setMode('data')
    def setLineMode(self):
        self.setMode('line')
