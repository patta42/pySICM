# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_statusbar.ui'
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

class Ui_ExtStatusBar(object):
    def setupUi(self, ExtStatusBar):
        ExtStatusBar.setObjectName(_fromUtf8("ExtStatusBar"))
        ExtStatusBar.resize(1346, 31)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ExtStatusBar)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(9, -1, 6, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.progressBar = QtGui.QProgressBar(ExtStatusBar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout.addWidget(self.progressBar)
        self.general_information = QtGui.QLineEdit(ExtStatusBar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.general_information.sizePolicy().hasHeightForWidth())
        self.general_information.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.general_information.setFont(font)
        self.general_information.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.general_information.setFrame(False)
        self.general_information.setReadOnly(True)
        self.general_information.setObjectName(_fromUtf8("general_information"))
        self.horizontalLayout.addWidget(self.general_information)
        self.server_information = QtGui.QLineEdit(ExtStatusBar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.server_information.sizePolicy().hasHeightForWidth())
        self.server_information.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.server_information.setFont(font)
        self.server_information.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.server_information.setFrame(False)
        self.server_information.setReadOnly(True)
        self.server_information.setObjectName(_fromUtf8("server_information"))
        self.horizontalLayout.addWidget(self.server_information)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(ExtStatusBar)
        QtCore.QMetaObject.connectSlotsByName(ExtStatusBar)

    def retranslateUi(self, ExtStatusBar):
        ExtStatusBar.setWindowTitle(_translate("ExtStatusBar", "Form", None))

