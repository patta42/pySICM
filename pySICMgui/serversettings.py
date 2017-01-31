# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'serversettings.ui'
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

class Ui_ServerSettings(object):
    def setupUi(self, ServerSettings):
        ServerSettings.setObjectName(_fromUtf8("ServerSettings"))
        ServerSettings.resize(556, 154)
        self.verticalLayout = QtGui.QVBoxLayout(ServerSettings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ServerSettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEditIP1 = QtGui.QLineEdit(ServerSettings)
        self.lineEditIP1.setObjectName(_fromUtf8("lineEditIP1"))
        self.horizontalLayout_2.addWidget(self.lineEditIP1)
        self.label_2 = QtGui.QLabel(ServerSettings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEditIP2 = QtGui.QLineEdit(ServerSettings)
        self.lineEditIP2.setObjectName(_fromUtf8("lineEditIP2"))
        self.horizontalLayout_2.addWidget(self.lineEditIP2)
        self.label_3 = QtGui.QLabel(ServerSettings)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.lineEditIP3 = QtGui.QLineEdit(ServerSettings)
        self.lineEditIP3.setObjectName(_fromUtf8("lineEditIP3"))
        self.horizontalLayout_2.addWidget(self.lineEditIP3)
        self.label_4 = QtGui.QLabel(ServerSettings)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.lineEditIP4 = QtGui.QLineEdit(ServerSettings)
        self.lineEditIP4.setObjectName(_fromUtf8("lineEditIP4"))
        self.horizontalLayout_2.addWidget(self.lineEditIP4)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.label_5 = QtGui.QLabel(ServerSettings)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_5)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lineEditPort = QtGui.QLineEdit(ServerSettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditPort.sizePolicy().hasHeightForWidth())
        self.lineEditPort.setSizePolicy(sizePolicy)
        self.lineEditPort.setInputMask(_fromUtf8(""))
        self.lineEditPort.setMaxLength(5)
        self.lineEditPort.setObjectName(_fromUtf8("lineEditPort"))
        self.horizontalLayout_3.addWidget(self.lineEditPort)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.formLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ServerSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ServerSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ServerSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ServerSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(ServerSettings)

    def retranslateUi(self, ServerSettings):
        ServerSettings.setWindowTitle(_translate("ServerSettings", "Server Settings", None))
        self.label.setText(_translate("ServerSettings", "Server IP address", None))
        self.label_2.setText(_translate("ServerSettings", ".", None))
        self.label_3.setText(_translate("ServerSettings", ".", None))
        self.label_4.setText(_translate("ServerSettings", ".", None))
        self.label_5.setText(_translate("ServerSettings", "Port", None))

