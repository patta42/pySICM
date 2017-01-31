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


import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import _defaultScanForm as DefaultScanForm
import pySICM.error
import struct
import tempfile
import os.path
import os
import tarfile
import time
import json
import re

from matplotlibwidget import MatplotlibWidget

class DefaultScanWidget(QtGui.QWidget, DefaultScanForm.Ui_DefaultScanForm):

    def __init__(self, mainwin, parent = None, mode = '', **kwargs):
        super (DefaultScanWidget, self).__init__(parent)
        self.mode = mode
        self.mainwin = mainwin
        self.arg_settings = {}
        self.settingConvertFuncs = {}
        if kwargs and kwargs['settings']:
            self.arg_settings = kwargs['settings']
            
        self.client = mainwin.client
        self.setupUi(self)
        self.settings = {}
        self.current_column = 0
        self._columns = [self.formLayout_3]
        self._graphs = {}
        self._dataBuffer = ""
        self.info = {}
        

        
    def getCurrentColumn(self):
        return self._columns[self.current_column]
            
    def setCurrentColumn(self, col):
        self.current_column = col % len(self._columns)
                    
    def addColumn(self):
        self._columns.append(QtGui.QFormLayout())
        self.setCurrentColumn(len(self._columns)-1)
        self.settingsTabLayout.addLayout(self.getCurrentColumn())
        
    def _addSetting(self, label, widget):
        lab = QtGui.QLabel()
        lab.setText(label)
        self.getCurrentColumn().addRow(lab, widget)

    def addSetting(self, name, label, widget, convertFunc = None):
        self.settings[name] = widget
        self._addSetting(label, widget)
        if convertFunc is not None:
            self.settingConvertFuncs[name] = convertFunc

    def addLineEdit(self, name, label, *args, **kwargs):
        ed = QtGui.QLineEdit(*args, **kwargs)
        ftext = re.search('\((.*?)\)', label)
        if ftext is not None:
            f = None
            ftext = ftext.group(1)
            if ftext == 'int':
                f = int
            elif ftext == 'float':
                f = float
            elif ftext == 'bool':
                f = bool
            if f is not None:
                self.addSetting(name, label, ed, convertFunc = f)
            else:
                self.addSetting(name, label, ed)
        else:
            self.addSetting(name, label, ed)
        
    def addComboBox(self, name, label, items, *args, **kwargs):
        ed = QtGui.QComboBox(*args, **kwargs)
        if isinstance(items, QtCore.QStringList):
            ed.addItems(items)
        else:
            for k,v in items.iteritems():
                ed.addItem(k,v)
        self.addSetting(name, label, ed)

    def addCheckBox(self, name, label, *args, **kwargs):
        ed = QtGui.QCheckBox(*args, **kwargs)
        self.addSetting(name, label, ed)
        
    def addGraph(self, name, **kwargs):
        mpw = MatplotlibWidget(**kwargs)
        self._graphs[name] = mpw
        self.dataLayout.addWidget(mpw)

    def getGraph(self, name):
        return self._graphs[name] 

    def expectData(self, callback, length = None, stop = None, form = 'int', rang = [], offset = 0):
        '''This function tells the widget that data is expected.
        
        Args:
            callback (function): The function to which the data is send. 
                The function will be called with one parameter.
            length (int, optional): The length of the data in each line if one works 
                with fixed data lengths. If the line that is recieved is shorter, 
                the function will not call the callback, but instead buffer the data
                and send it when the data is longer or equal the length given here.
                Note that this argument should specify the number of data points in uint16, 
                not bytes or similar.
            stop (string, optional): If one does not work with fixed data lengths, the data will be 
                buffered until this sequence is found at the end of a line (without \r\n)
              
                Both, length and stop are optional, but one has to be given. If both are given, a fixed 
                length is assumed
            form (string, optional): A string specifying the type of the data that is deliverd to the callback 
                function. Valid strings are 'int', 'string', 'byte' and 'float'. 'int' sends integer data, 
                'string' and 'byte' send the data as it has been received, and 'float' converts the data to
                floats.
            rang (list of floats, optional): If form is 'float', the min and max values are used to map
                the data to floats. Two bytes will be used as the number of steps.
            offset (int, optional): If offset is given, the first 'offset' number of chars will be stored in self.data_offset
                for other purposes.
        '''

        # First check the possible errors:
        if length is None and stop is None:
            raise pySICM.error.PySICMError('Either length or stop should be set when calling expectData')
        if form is 'float' and len(rang) < 2:
            raise pySICM.error.PySICMError('To map data to float, the rang parameter must consist of at least two values')
        if form is 'float' and min(rang) == max(rang):
            raise pySICM.error.PySICMError('To map data to float, the rang parameter must consist of at least two different values')
            
        # set the args
        self.expectedData = {
            'length' : length,
            'stop' : stop,
            'form' : form,
            'rang' : rang,
            'callback' : callback,
            'offset' : offset
        }
        self.data_offset = ''
        
        # register the callback
        if self.client.hasCallbackFunc('dataReceived',self._dataReceivedCB)==False:
            self.client.addCallback('dataReceived',self._dataReceivedCB)
        

    def unexpectData(self):
        print "Unexpecting data"
        for i in self.expectedData:
            self.expectedData[i] = None
        if self.client.hasCallbackFunc('dataReceived',self._dataReceivedCB):
            self.client.removeCallback('dataReceived',self._dataReceivedCB)
        self.client.setLineMode()
            

    def _dataReceivedCB(self, data, *args, **kwargs):
        '''This is the internal callback function that receives the data.
        There is no need to call it yourself.

        Args:
            data (string): The data received.
        '''
        
        # Just as a shorthand:
        e = self.expectedData
        #        # Remove the last two characters
        #        data = data
        if e['offset'] > 0 and self.data_offset == '':
            self.data_offset = data[0:e['offset']]
            data = data[e['offset']:]
        if e['length'] is not None:
            # This is fixed length mode.

            # Check the length of the data.
            if len(data) < 2 * e['length']:
                print "Too short line received (%i)"% len(data)
                print "Buffer length is: %i"% len(self._dataBuffer)
                # add the data buffer at the beginning of data
                # include "\r\n" since this is the reason why the data is too short
                if len(self._dataBuffer) > 0:
                    data = self._dataBuffer + "\r\n" + data
                    print "Data updated with buffer content and \\r\\n, length is now: %i"% len(data)
            # Check again
            if len(data) < 2 * e['length']:
                print "However, data is still too short (%i). Expected length is %i"% (len(data), 2*e['length'])
                # Still too short, store data and return
                self._dataBuffer = data
                print "Data buffer updated, length is %i"% len(self._dataBuffer)
                return
            # Data length is fine now, clear the buffer...
            self._dataBuffer = ''
            # ...and call the callback with the converted data
            e['callback'](self._convertReceivedData(data))
        else:
            # Non fixed mode

            # Add the buffer
            data = self._dataBuffer + "\r\n" + data
            
            # Check whether the last values of data are the stop sequence:
            if data[-len(e['stop']):] == e['stop']:
                # clear the buffer
                self._dataBuffer = ''
                # and call the callback
                e['callback'](self._convertReceivedData(data))
            else:
                # store data in buffer and return
                self._dataBuffer = data
                return
            
    def _convertReceivedData(self, data):
        '''This function converts the data to the specified format.
        It is internal.

        Args:
            data (string): The data

        Returns:
            string or list: The returned format depends on the settings
        '''
        # if string or byte is required, return as is
        if self.expectedData['form'] in ['string', 'byte']:
            return data
        # otherwise, convert to integer
        intdata = []
        c = ''
        for i in data:
            c = c + i
            if len(c) == 2:
                a = struct.unpack('B', c[0])[0]
                b = struct.unpack('B', c[1])[0]                    
                c=''
                intdata.append(b * 256 + a)
        # if integer was requested, return data:
        if self.expectedData['form'] == 'int':
            return intdata

        # otherwise, convert to float
        mi = min(self.expectedData['rang'])
        ma = max(self.expectedData['rang'])
        delta = float(ma - mi)/float(2**16)
        floatdata = []
        for i in intdata:
            floatdata.append(mi + float(i)*delta)
        return floatdata
            
    def receiveData(self, command):
        '''This function starts receiving the data by issuing a command.
        
        Arg:
            command (string): A commend that is send to the server.
        '''
        self.client.setDataMode()
        self.client.sendLine(command)

    def _save(self):
        filename =  QtGui.QFileDialog.getSaveFileName(
            parent  = self,
            caption = "Save File",
            directory = self.mainwin.lastSaveDir,
            filter = "pySICM recordings (*.sicm)")
        # convert QString into str! Important!
        filename = str(filename)
        if filename[-5:] != '.sicm':
            filename+='.sicm'
            
        if filename == "":
            return
        path, fn = os.path.split(filename)
        self.mainwin.lastSaveDir = path
        self.save(filename)

        
    def save(self, filename):

        tar = tarfile.open(filename, "w:gz")
        files = self.getFilesToStore()
        f, fn = tempfile.mkstemp(suffix=".mode")
        fo = os.fdopen(f, 'w')
        fo.write(self.getScanMode())
        fo.close()
        files.append((fn, '.mode'))

        for f in files:
            if isinstance(f, tuple):
                fn = f[0]
                arcfn = f[1]
            else:
                fn = f
                arcfn = os.path.split(f)[1]
            
            fo = open(fn, 'rb') 
            finfo = tar.gettarinfo(fn, arcname=arcfn)
            tar.addfile(finfo, fo)
            fo.close()
            os.unlink(fn)
        tar.close()

    def loadDefaults(self):
        try:        
            with open('/etc/pySICMgui/defaults/'+str(self.mode)+'.stpl') as data_file:    
                data = json.load(data_file)
        except:
            return
        for k,v in self.settings.iteritems():
            v.setText(QtCore.QString(data[k]))

        
    def saveAsDefaultTemplate(self):
        self._writeSettings('/etc/pySICMgui/defaults/'+str(self.mode)+'.stpl')
#    def saveAsTemplate(self):
#        settings = {'__mode__':self.mode}
#        for k,v in self.settings.iteritems():
#            settings[k] = v.text()
            
        self._writeSettings('/etc/pySICMgui/defaults/'+str(self.mode)+'.stpl')
    def getFilesToStore(self):
        files = []
        files.append((self._writeSettings(), 'settings.json'))
        files+=self._writeData()
        return files

    def _writeSettings(self, fn = None):
        settings = {}
        for k,v in self.settings.iteritems():
            settings[k] = str(v.text())
        if fn is None:
            f, fn = tempfile.mkstemp(text=True, suffix='.settings')
            print "Settings temporary file: "+str(fn)
            os.close(f)
        fo = open(fn, 'w')
        s = json.dumps(settings, separators=(',',':'))
#        fo = os.fdopen(f, 'w')
        try:
            fo.write(s)
        except:
            print "Problems with writeing to filename: "+str(fn)
        fo.close()
        return fn

    def _writeData(self):
        ret = []
        f, fn = tempfile.mkstemp(prefix = '')
        fo = os.fdopen(f, 'w')
        try:
            self.data.tofile(fo)
        except:
            print "Problem..."
            
        f2 = open (fn+'.info','w')
        s = json.dumps( self.info, separators=( ',', ':' ) )

        f2.write(s)
        f2.close()
        ret += [fn, fn+'.info']
        return ret
        
    def getScanMode(self):
        mode = self.__class__.__name__[6:]
        return mode[0].lower() + mode[1:]

    def getOptions(self):
        self.client.sendLine('SET mode='+str(self.mode))
        self.client.sendLineAndGetAnswer('GET OPTIONS', self._processOptions)

    def _processOptions(self, optstring, third_arg):

        print "My id is "+str(self.WinNum)
        self.options = json.loads(optstring)
        cols = {}
        for opt, optdef in self.options.iteritems():
            if 'col' in optdef:
                c = int(optdef['col']) 
                if c not in cols:
                    cols[c] = {}
                cols[c][opt] = optdef
            else:
                if 0 not in cols:
                    cols[0] = {}
                cols[0][opt] = optdef

        sortedcols = {}
        for c, col in cols.iteritems():
            sortedcols[c] = {}
            for key, item in col.iteritems():
                if 'pos' in item:
                    p = int(item['pos'])
                    if p not in sortedcols[c]:
                        sortedcols[c][p] = item
                        sortedcols[c][p]['key'] = key
                        col[key] = None
            k = 0
            for key, item in col.iteritems():
                if item is None:
                    continue
                while k in sortedcols[c]:
                    k += 1
                item['key'] = key
                sortedcols[c][k] = item
        self.sortedcols = sortedcols
        self.populateFormCallback()
        
    def populateForm(self):
        self.getOptions()

    def populateFormCallback(self):
        c = 0
        for col, content in self.sortedcols.iteritems():
            if c > 0:
                self.addColumn()
            else:
                c += 1
            for k in sorted(content):
                self.addSettingsItem(content[k])
        if self.arg_settings:
            for k,v in self.settings.iteritems():
                v.setText(QtCore.QString(self.arg_settings[k]))
        else:
            self.loadDefaults()
    def _stripPrefix(self, s):
        # This removes the prefix and the connecting dot 
        l  = len(self.mode) + 1
        return s[l:]
        
                
    def addSettingsItem(self, item):
        self.addLineEdit(self._stripPrefix(item['key']), item['expl'])
        
