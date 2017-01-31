# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_defaultScanForm.ui'
#
# Created by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DefaultScanForm(object):
    def setupUi(self, DefaultScanForm):
        DefaultScanForm.setObjectName(_fromUtf8("DefaultScanForm"))
        DefaultScanForm.resize(999, 798)
        self.verticalLayout = QtGui.QVBoxLayout(DefaultScanForm)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(DefaultScanForm)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.settingsTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingsTab.sizePolicy().hasHeightForWidth())
        self.settingsTab.setSizePolicy(sizePolicy)
        self.settingsTab.setObjectName(_fromUtf8("settingsTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.settingsTab)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.settingsTabLayout = QtGui.QHBoxLayout()
        self.settingsTabLayout.setMargin(6)
        self.settingsTabLayout.setObjectName(_fromUtf8("settingsTabLayout"))
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.settingsTabLayout.addLayout(self.formLayout_3)
        self.verticalLayout_3.addLayout(self.settingsTabLayout)
        self.tabWidget.addTab(self.settingsTab, _fromUtf8(""))
        self.dataTab = QtGui.QWidget()
        self.dataTab.setObjectName(_fromUtf8("dataTab"))
        self.dataTabLayout = QtGui.QHBoxLayout(self.dataTab)
        self.dataTabLayout.setMargin(0)
        self.dataTabLayout.setObjectName(_fromUtf8("dataTabLayout"))
        self.dataLayout = QtGui.QGridLayout()
        self.dataLayout.setObjectName(_fromUtf8("dataLayout"))
        self.dataTabLayout.addLayout(self.dataLayout)
        self.tabWidget.addTab(self.dataTab, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.progressBar = QtGui.QProgressBar(DefaultScanForm)
        self.progressBar.setProperty("value", 42)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(DefaultScanForm)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(DefaultScanForm)

    def retranslateUi(self, DefaultScanForm):
        DefaultScanForm.setWindowTitle(_translate("DefaultScanForm", "Default Scan Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), _translate("DefaultScanForm", "Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dataTab), _translate("DefaultScanForm", "Data", None))

