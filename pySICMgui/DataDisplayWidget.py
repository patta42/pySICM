from matplotlibwidget import MatplotlibWidget
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
import matplotlib.pyplot
import matplotlib.colors
from mpl_toolkits.mplot3d import Axes3D

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import numpy
import functools

class DataDisplayWidget(QtGui.QWidget):


    def __init__(self):
        super(DataDisplayWidget, self).__init__()

        # Defaults

        self.cm = 'hot'
        self.ipm = 'none'
        self.is3D = False
        self.asNewScanCallback = None
        
        self.xlabel = 'x'
        self.ylabel = 'y'
        self.cmapdata = numpy.zeros((32,256), numpy.uint16)
        for i in xrange(0,31):
            self.cmapdata[i,:] = numpy.linspace(0,255,256)

        #Setup UI and stuff

        self.setupUI()
        self.generateContextMenu()
        self.setupActions()
        self.registerCMs()

        
        self.data = numpy.zeros((128,128), numpy.uint16)
        self.data = numpy.outer(
            numpy.linspace(0,numpy.sqrt(256),128),
            numpy.linspace(0,numpy.sqrt(256),128))

        ltz = self.data>0
        self.maxData = numpy.max(self.data[ltz])
        self.minData = numpy.min(self.data[ltz])

        self.setAutoscale(True)
        self._hasSelection(False)
        self._draw()

        
        
    def setupUI(self):
        self.majorLayout = QtGui.QVBoxLayout(self)
        self.dataWidget = MatplotlibWidget()
        self.dataWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.majorLayout.addWidget(self.dataWidget)

        self.cbar = MatplotlibWidget()

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbar.sizePolicy().hasHeightForWidth())
        self.cbar.setSizePolicy(sizePolicy)
        self.cbar.setMaximumSize(QtCore.QSize(2**15-1, 32))
        self.updCM()
#        self.majorLayout.addWidget(self.cbar)

        self.minDataEdit = QtGui.QLineEdit()
        self.maxDataEdit = QtGui.QLineEdit()


        editSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

        self.minDataEdit.setSizePolicy(editSizePolicy)
        self.maxDataEdit.setSizePolicy(editSizePolicy)
        self.minDataEdit.setMaximumSize(QtCore.QSize(128, 32))
        self.maxDataEdit.setMaximumSize(QtCore.QSize(128, 32))

        self.minDataEdit.setMinimumSize(QtCore.QSize(64, 32))
        self.maxDataEdit.setMinimumSize(QtCore.QSize(64, 32))



        self.cbarlayout = QtGui.QHBoxLayout()
        self.cbarlayout.addWidget(self.minDataEdit)
        self.cbarlayout.addWidget(self.cbar)
        self.cbarlayout.addWidget(self.maxDataEdit)


        self.majorLayout.addLayout(self.cbarlayout)
        # Expose properties of mpw


        
    def setupActions(self):
        self.maxDataEdit.textChanged.connect(self.maxDataChanged)
        self.minDataEdit.textChanged.connect(self.minDataChanged)
        self.dataWidget.customContextMenuRequested.connect(self.openContextMenu)

    def onSelect(self, eclick, erelease):
        x = numpy.min([eclick.xdata, erelease.xdata])
        y = numpy.min([eclick.ydata, erelease.ydata])

        w = abs(eclick.xdata - erelease.xdata)
        h = abs(eclick.ydata - erelease.ydata)


        try:
            self.selectionRect.remove()
        except:
            pass
        if h > 3 and w > 3:
            self.selection={'x':x,'y':y,'w':w,'h':h}
            self.selectionRect = Rectangle((x,y),w,h, fill=False)
            self.dataWidget.figure.axes[0].add_patch(self.selectionRect)
            self.dataWidget.draw()
            self._hasSelection(True)
        else:
            self._hasSelection(False)
            self.selection={'x':None,'y':None,'w':None,'h':None}


    def _hasSelection(self, yn):
        self.hasSelection = yn
        self.acAsNewScan.setEnabled(yn)
        

    def maxDataChanged(self, txt):
        if float(txt) >= self.minData:
            self.maxData = float(txt)
            self._draw()

    def minDataChanged(self, txt):
        if float(txt) <= self.maxData:
            self.minData = float(txt)
            self._draw()

    def setXLabel(self, xlabel):
        self.xlab = xlabel

    def setYLabel(self, ylabel):
        self.ylab = ylabel

    def update(self, data):
        self.data = data
        self._draw()
        
    def _draw(self, **kwargs):
        if self.is3D:
            self.draw3D()
        else:
            if (self.isAutoScale):
                idx = self.data > 0
                self.maxData = numpy.max(self.data[idx])
                self.minData = numpy.min(self.data[idx])
                print "min data is: "+ str(self.minData)
                self.minDataEdit.setText(str(self.minData))
                self.maxDataEdit.setText(str(self.maxData))
            self.dataWidget.axes.imshow(self.data, cmap = self.cm,
                                        clim=(self.minData, self.maxData),
                                        interpolation = self.ipm)
            self.selector = RectangleSelector(self.dataWidget.axes,
                                              self.onSelect, button=1,
                                              useblit = True)
                
            self.dataWidget.draw()
                
    def draw3D(self):
        print "3D drawing not yet implemented"
        
    def openContextMenu(self, point):
        self.popMenu.exec_(self.dataWidget.mapToGlobal(point))


    def generateContextMenu(self):
        self.popMenu = QtGui.QMenu(self)
        self.acSetAutoScale = QtGui.QAction('Autoscale', self)
        self.acSetAutoScale.setCheckable(True)
        self.acSetAutoScale.setChecked(True)
        self.popMenu.addAction(self.acSetAutoScale)

        
        self.acSetAutoScale.toggled.connect(self.setAutoscale)

        self.acSet3D = QtGui.QAction('3D', self)
        self.acSet3D.setCheckable(True)
        self.acSet3D.setChecked(False)
        self.popMenu.addAction(self.acSet3D)

        self.acgCM = QtGui.QActionGroup(self)
        
        
        self.CMmenu = QtGui.QMenu(self)
        self.CMmenu.setTitle('Colormaps')

        for cm in ("gray|red|green|blue|red white|green white|blue white|"+
                   "cyan|magenta|cyan white|jet|"+
                   "magenta white|hot|cyan hot|afmhot|bmg").split("|"):
            ac = QtGui.QAction(cm, self.acgCM)
            ac.triggered.connect(functools.partial(self.setCM, cm))
            ac.setCheckable(True)
            if cm == self.cm:
                ac.setChecked(True)
        ip_methods = ['none', 'nearest', 'bilinear', 'bicubic', 'spline16',
           'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
           'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

        self.acgIP = QtGui.QActionGroup(self)
        for ip in ip_methods:
            ac = QtGui.QAction(ip, self.acgIP)
            ac.triggered.connect(functools.partial(self.setIP, ip))
            ac.setCheckable(True)

            self.acgIP.addAction(ac)

        self.IPmenu = QtGui.QMenu(self)
        self.IPmenu.setTitle('Interpolation')
        self.IPmenu.addActions(self.acgIP.actions())

        self.CMmenu.addActions(self.acgCM.actions())
        
        self.popMenu.addSeparator()
        self.popMenu.addMenu(self.CMmenu)
        self.popMenu.addSeparator()
        self.popMenu.addMenu(self.IPmenu)

        self.acAsNewScan =  QtGui.QAction("Use selection as new scan", self.popMenu)
        self.acAsNewScan.triggered.connect(self.onAsNewScan)
        self.acAsNewScan.setEnabled(False)
        self.popMenu.addSeparator()
        self.popMenu.addAction(self.acAsNewScan)


    def setIP(self, ip):
        self.ipm = ip;
        self._draw()

    def setAutoscale(self, chk):
        self.isAutoScale = chk
        self.minDataEdit.setEnabled(not chk)
        self.maxDataEdit.setEnabled(not chk)
        
    def set3D(self, chk):
        self.is3D = chk
        
    def setCM(self, cm):
        self.cm = cm
        self._draw()
        self.updCM()

    def updCM(self):
        self.cbarplt = self.cbar.axes.imshow(self.cmapdata, cmap = self.cm)
        self.cbar.axes.axis('off')
        self.cbar.axes.axis('tight')
        self.cbar.draw()
            
    def registerCMs(self):
        cyanAndRedHot={
            'red':   ((0.0, 0.0, 0.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 1.0, 1.0),
                      (1.0, 1.0, 1.0),),

            'green': ((0.0, 1.0, 1.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 0.0, 0.0),
                      (0.2+1.6/3.0, 1.0, 1.0),
                      (1.0, 1.0, 1.0)),

            'blue':  ((0.0, 1.0, 1.0),
                      (0.2, 0.0, 0.0),
                      (0.2+0.8/3.0, 0.0, 0.0),
                      (0.2+1.6/3.0, 0.0, 0.0),
                      (1.0, 1.0, 1.0))
            }
        cm = matplotlib.colors.LinearSegmentedColormap('cyan hot', cyanAndRedHot)
        matplotlib.pyplot.register_cmap(cmap=cm)

        red = {
            'red':((0,0,0),(1,1,1)),
            'green':((0,0,0),(1,0,0)),
            'blue':((0,0,0),(1,0,0)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('red', red)
        matplotlib.pyplot.register_cmap(cmap=cm)

        green = {
            'red':((0,0,0),(1,0,0)),
            'green':((0,0,0),(1,1,1)),
            'blue':((0,0,0),(1,0,0)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('green', green)
        matplotlib.pyplot.register_cmap(cmap=cm)

        blue = {
            'red':((0,0,0),(1,0,0)),
            'green':((0,0,0),(1,0,0)),
            'blue':((0,0,0),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('blue', blue)
        matplotlib.pyplot.register_cmap(cmap=cm)


        magenta = {
            'red':((0,0,0),(1,1,1)),
            'green':((0,0,0),(1,0,0)),
            'blue':((0,0,0),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('magenta', magenta)
        matplotlib.pyplot.register_cmap(cmap=cm)

        cyan = {
            'red':((0,0,0),(1,0,0)),
            'green':((0,0,0),(1,1,1)),
            'blue':((0,0,0),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('cyan', cyan)
        matplotlib.pyplot.register_cmap(cmap=cm)

        redwhite = {
            'red':((0,0,0),(.5,1,1),(1,1,1)),
            'green':((0,0,0),(0.5,0,0), (1,1,1)),
            'blue':((0,0,0),(0.5,0,0),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('red white', redwhite)
        matplotlib.pyplot.register_cmap(cmap=cm)
        greenwhite = {
            'red':((0,0,0),(.5,0,0),(1,1,1)),
            'green':((0,0,0),(0.5,1,1), (1,1,1)),
            'blue':((0,0,0),(0.5,0,0),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('green white', greenwhite)
        matplotlib.pyplot.register_cmap(cmap=cm)
        bluewhite = {
            'red':((0,0,0),(.5,0,0),(1,1,1)),
            'green':((0,0,0),(0.5,0,0), (1,1,1)),
            'blue':((0,0,0),(0.5,1,1),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('blue white', bluewhite)
        matplotlib.pyplot.register_cmap(cmap=cm)

        bmg = {
            'red':((0,0,0),(.5,1,1),(1,0,0)),
            'green':((0,0,0),(0.5,1,1), (1,1,1)),
            'blue':((0,0,0),(0.5,1,1),(1,0,0)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('bmg', bmg)
        matplotlib.pyplot.register_cmap(cmap=cm)

        magentawhite = {
            'red':((0,0,0),(.5,1,1),(1,1,1)),
            'green':((0,0,0),(0.5,0,0), (1,1,1)),
            'blue':((0,0,0),(0.5,1,1),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('magenta white', magentawhite)
        matplotlib.pyplot.register_cmap(cmap=cm)

        cyanwhite = {
            'red':((0,0,0),(.5,0,0),(1,1,1)),
            'green':((0,0,0),(0.5,1,1), (1,1,1)),
            'blue':((0,0,0),(0.5,1,1),(1,1,1)),
            }

        cm = matplotlib.colors.LinearSegmentedColormap('cyan white', cyanwhite)
        cm.set_over((0,0,1))
        matplotlib.pyplot.register_cmap(cmap=cm)

        
        
    def onAsNewScan(self):
        try:
            x = int(round(self.selection['x']))
            y = int(round(self.selection['y']))
            w = int(round(self.selection['w']))
            h = int(round(self.selection['h']))
            self.asNewScanCallback(self.selection, self.data[ y:y+h, x:x+w])
        except AttributeError:
            print "No Callback set for opening selection in a new scan."
            self.asNewScanCallback(self.selection, self.data[ y:y+h, x:x+w])
