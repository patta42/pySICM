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

import sys, json, imp, os, functools, tempfile, tarfile, time
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


from pySICMGUImain import Ui_PySICMGUIMainWindow
from widgetClientWindow import WidgetClientWindow
from statusbarWidget import StatusbarWidget
from dialogServerSettings import DialogServerSettings
from pySICM.error import PySICMError
from pySICM.client import PySicmClientFactory
from pySICM.simplecallback import SimpleCallbackSystem
from actionhandler import ActionHandler

class PySICMGuiMainWindow (QtGui.QMainWindow, Ui_PySICMGUIMainWindow,
                           SimpleCallbackSystem, ActionHandler):

    def __init__(self, reactor, parent = None):
        super(PySICMGuiMainWindow, self).__init__(parent)
        splashpix = QtGui.QPixmap('pySICMgui/pySICMsplash.png')
        self.splash = QtGui.QSplashScreen(splashpix, QtCore.Qt.WindowStaysOnTopHint)
        self.splash.setMask(splashpix.mask())
        self.splash.show()
        self.config = {'controller' : {
                       'ipaddress' : '134.147.65.194',
                       'port'      : 21080}}
        self.reactor = reactor
        self._serverLog = []
        self._connected = False
        self.setupUi(self)
        self.populateSatusbar()
        self.setConnections()
        self.splash.showMessage('Connecting...')
        self.generateClient()
        self.hasControllerWin = False
        self.lastSaveDir = '.'
        self.lastOpenDir = '.'
        self._winIdCounter = 0
        self.setEnabledStatus()
    @property
    def hasControllerWin(self):
        return self._hasControllerWin
    @hasControllerWin.setter
    def hasControllerWin(self, val):
        self._hasControllerWin = val
        self.actionShow_controller_window.setChecked(val)

    @property
    def serverLog(self):
        return self._serverLog

    @serverLog.setter
    def serverLog(self, line):
        self._serverLog.append(line)
        self.fireCallbacks('serverLogAdd', line, passReturn = True)
    
    def _setServerLogCbFunc(self, line, processed, *args):
        self.serverLog.append(line)
        self.fireCallbacks('serverLogAdd', line, passReturn = True)

    @property
    def connected(self):
        return self._connected

    def _setConnected(self, val):
        self._connected = val
        self.fireCallbacks('connectionChanged', val, passReturn = False)

    def populateSatusbar(self):
        self.stat = StatusbarWidget()
        self.statusBar().addPermanentWidget(self.stat, 1)
        self.addCallback('connectionChanged', self._connectionHasChanged)

    def _connectionHasChanged(self, status, *args):
        if status == True:
            self.stat.general_information.setText('Connection status: Connected')
        else:
            self.stat.general_information.setText('Connection status: Not Connected')

    def setConnections(self):
        self.actionOpen.triggered.connect(self.openFile)
        
        self.actionQuit.triggered.connect(self.closeEvent)
        self.actionShow_controller_window.triggered.connect(self._addControllerWin)
        
        self.addActionHandler(self.actionStartScan, 'scan')
        self.addActionHandler(self.actionStop_Scan, 'stop')
        self.addActionHandler(self.actionSave, '_save')
        self.addActionHandler(self.actionSaveAsTemplate, 'saveAsTemplate')
        self.addActionHandler(self.actionSaveAsDefaultTemplate, 'saveAsDefaultTemplate')
        self.mdiArea.subWindowActivated.connect(self.setEnabledStatus)
        
        
        self.actionControllerConnect.triggered.connect(self._controllerConnectCB)
        self.actionControllerDisconnect.triggered.connect(self._controllerDisconnectCB)
        self.actionControllerSettings.triggered.connect(self._controllerSettingsCB)
        


    def _controllerConnectCB(self):
        if not self.connected == True:
            self.generateClient()

    def _controllerDisconnectCB(self):
        if self.connected == True:
            self.client.disconnect()
            
    def _controllerSettingsCB(self):
        result, ip, port = DialogServerSettings.getServerSettings(parent = self)
        if result == True:
            print "IP is: %s"% ip
            print "Port is: %i"% port.toInt()[0]
            self.config['controller']['ipaddress'] = ip
            self.config['controller']['port'] = port.toInt()[0]
            self.generateClient()

    def generateClient(self):
        if self.connected == True:
            self.client.disconnect()
        try:
            self.client.removeCallback('lineReceived', self._setServerLogCbFunc)
            self.client.removeCallback('lineSent', self._setServerLogCbFunc)
            del(self.connection)
        except AttributeError:
            pass
        self.client = PySicmClientFactory(self.connectionSuccess, 
                                          self.connectionFailed, 
                                          self.connectionLost)

        self.connection = self.reactor.connectTCP(self.config['controller']['ipaddress'], 
                                                  self.config['controller']['port'], 
                                                  self.client)
        self.client.addCallback('lineReceived', self._setServerLogCbFunc)
        self.client.addCallback('dataReceived', self._setServerLogCbFunc)
        self.client.addCallback('lineSent', self._setServerLogCbFunc)
    
    def _addControllerWin(self):
        if self.hasControllerWin == False:
            self.controllerWin = WidgetClientWindow(self)
            self._addWindow(self.controllerWin)
            self.hasControllerWin = True
        else:
            self.controllerWin.parent().close()
#            self.controllerWin.hide()
            del(self.controllerWin)

            
    def getNextWinId(self):
        self._winIdCounter += 1
        return self._winIdCounter
    
    def _addWindow(self, widget, width=600, height=200):
        sub = self.mdiArea.addSubWindow(widget)
        sub.widget().WinNum = self.getNextWinId()
        sub.show()

        try:
            width = widget.preferredSize[0]
            height = widget.preferredSize[1]
        except:
            pass
        sub.resize(QtCore.QSize(width, height))

    def openFile(self):
        filename =  QtGui.QFileDialog.getOpenFileName(
            parent  = self,
            caption = "Open File",
            directory = self.lastOpenDir,
            filter = "pySICM recordings (*.sicm)")
        filename = str(filename)
        p,f = os.path.split(filename)
        self.lastOpenDir = p
        if not os.access(filename, os.R_OK):
            print "Can't access the file "+str(filename)
            return
        if tarfile.is_tarfile(filename):
            self._openFile(filename)
        else:
            print "The format of " +str(filename)+ " is not supported"
        
    def _openFile(self, filename):
        tdir = tempfile.mkdtemp()
        print "Temp dir: "+str(tdir)
        tar = tarfile.open(filename, 'r:gz')
        tar.extractall(tdir)
        tar.close()
        modefn = os.path.join(tdir, '.mode')
        if os.path.isfile(modefn):
            try:
                fo = open(modefn, "r")
                module = fo.read()
                fo.close()
            except:
                print "Cannot access the contents of file "+str(filename)+"."
            else:
                self.openScanModeWin(module)
        else:
            print "The file "+str(filename)+" does not seem to be a proper .sicm file"    
            

    def populateScanmodes(self):
        self.client.sendLineAndGetAnswer('GET MODES', self._populateScanmodes)
        
    def depopulateScanmodes(self):
        self.menuScanmodes.clear()
    def openScanModeWin(self, mode):
        istool = False
        if mode.startswith('__tool__'):
            mode = "tool"+mode[8].capitalize()+mode[9:]
            istool = True
        widgetfile = os.path.join(os.path.dirname(__file__),
                                  'widget'+mode[0].capitalize()+mode[1:]+'.py')
        if os.path.exists(widgetfile):
            pymod = imp.load_source(mode, widgetfile)
            instance = getattr(pymod, 'Widget'+mode[0].capitalize()+mode[1:])
            if istool:
                self._addWindow(instance(self), None, None)
            else:
                self._addWindow(instance(self),800,600)
        else:
            raise PySICMError('No widget found for scan mode %s' % mode)
        

    def _populateScanmodes(self, modes, *args):
        modes = json.loads(modes)
        for mode in modes:
            ac = QtGui.QAction(mode, self)

            ac.triggered.connect(functools.partial(self.openScanModeWin, mode))
            self.menuScanmodes.addAction(ac)


    def _populateTools(self, tools, *args):
        print "Tools received: "+str(tools)
        tools = json.loads(tools)
        for tool in tools:
            mode="tool"+tool[0].capitalize()+tool[1:]
            ac = QtGui.QAction(mode, self)
            ac.triggered.connect(functools.partial(self.openScanModeWin, mode))
            self.menuTools.addAction(ac)
            

    def connectionSuccess(self):
        self.serverLog = ('--- Connection succeeded ---')
        self._setConnected(True)
        self.populateScanmodes()
        self.client.sendLineAndGetAnswer('GET TOOLS', self._populateTools)
        try:
            self.splash.finish(self)
            self.show()
        except:
            pass
    def connectionFailed(self, reason):
        self.serverLog = ('--- Connection failed: '+str (reason)+' ---')
        self._setConnected(False)
        try:
            self.splash.finish(self)
            self.show()
        except:
            pass


    def connectionLost(self, reason):
        self.serverLog = ('--- Connection lost: '+str(reason)+' ---')
        self.depopulateScanmodes()
        self._setConnected(False)
#        self.stat.setGeneralInformation('Connection lost: '+str(reason))

            
    def closeEvent(self, e):
        self.reactor.stop()
    


#def run():
#    
#    app = QApplication(sys.argv)
#    window = PySICMGuiMainWindow()
#    window.show()
#    PySicmCore(PySicmCore.CLIENT)
#    print "I'm here!"
#   
#    sys.exit(app.exec_())
#
#if __name__ == '__main__':
#    run()
