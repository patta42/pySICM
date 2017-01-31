from PyQt4 import QtCore, QtGui
import json
from pySICMgui.toolAnalyzeSignal import Ui_Form

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class WidgetToolAnalyzeSignal(QtGui.QWidget, Ui_Form):
    preferredSize = [216, 136]
    def __init__ (self, mainwin, parent=None):
        super(WidgetToolAnalyzeSignal, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Analyze Signal')
        self.mainwin = mainwin
        self.parent = parent
        self.client = self.mainwin.client
        self.setConnections()

    def setConnections(self):
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.client.sendLine('SET mode=toolAnalyzeSignal')
        self.client.sendLineAndGetAnswer('SCAN', self.analyzeData)
        

    def analyzeData(self, data, *args):
        res = json.loads(data)
        self.setSettings(res)
        mean = self.toCurrent(res['mean'])
        print "mean is"+str(mean)
        self.LabelMeanCurrent.setText("{0:.5f} nA".format(mean))
        std = self.toCurrent(res['std'], isDelta = True)
        self.LabelSigma.setText("{0:.5f} nA".format(std))
        self.LabelMinCurrent.setText("{0:.5f} nA".format(
            self.toCurrent(res['min'])))
        self.LabelMaxCurrent.setText("{0:.5f} nA".format(
            self.toCurrent(res['max'])))
        resistance = float(self.lineEdit.text()) / float(mean)
        self.Label_Resistance.setText("{0:.2f} MOhm".format(resistance))
        fours = (1 - 4*std/mean)*1e2
        fives = (1 - 5*std/mean)*1e2
        self.LabelThreeSigma.setText("{0:.2f}%".format(fours))
        self.LabelFourSigma.setText("{0:.2f}%".format(fives))
        
    def setSettings(self, res):
        print "Max c is " + str(res['c_max'])
        print "Min c is " + str(res['c_min'])
        self.range = float(res['c_max']) - float(res['c_min'])
        self.offset = float(res['c_min'])

        
    def toCurrent(self, data, isDelta = False):
        sensitivity = float(self.lineEdit_2.text())
        frac = float(data) / float(2**16)
        print "Frac is: "+str(frac)
        print "Range is " + str(self.range)
        res = self.range * frac
        if not isDelta:
            res += self.offset
        return  res/sensitivity
        
