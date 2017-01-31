# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toolAnalzeSignal.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(342, 377)
        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 90, 291, 31))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(130, 10, 91, 31))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 31))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(230, 10, 31, 31))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(10, 50, 111, 31))
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 50, 91, 31))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.label_5 = QtGui.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(230, 50, 51, 31))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 140, 281, 211))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.LabelMinCurrent = QtGui.QLabel(self.groupBox)
        self.LabelMinCurrent.setObjectName(_fromUtf8("LabelMinCurrent"))
        self.gridLayout.addWidget(self.LabelMinCurrent, 2, 1, 1, 1)
        self.LabelMeanCurrent = QtGui.QLabel(self.groupBox)
        self.LabelMeanCurrent.setObjectName(_fromUtf8("LabelMeanCurrent"))
        self.gridLayout.addWidget(self.LabelMeanCurrent, 0, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setTextFormat(QtCore.Qt.PlainText)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.LabelMaxCurrent = QtGui.QLabel(self.groupBox)
        self.LabelMaxCurrent.setObjectName(_fromUtf8("LabelMaxCurrent"))
        self.gridLayout.addWidget(self.LabelMaxCurrent, 1, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.Label_Resistance = QtGui.QLabel(self.groupBox)
        self.Label_Resistance.setObjectName(_fromUtf8("Label_Resistance"))
        self.gridLayout.addWidget(self.Label_Resistance, 4, 1, 1, 1)
        self.LabelSigma = QtGui.QLabel(self.groupBox)
        self.LabelSigma.setObjectName(_fromUtf8("LabelSigma"))
        self.gridLayout.addWidget(self.LabelSigma, 3, 1, 1, 1)
        self.label234 = QtGui.QLabel(self.groupBox)
        self.label234.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label234.setObjectName(_fromUtf8("label234"))
        self.gridLayout.addWidget(self.label234, 5, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 3, 0, 1, 1)
        self.LabelThreeSigma = QtGui.QLabel(self.groupBox)
        self.LabelThreeSigma.setObjectName(_fromUtf8("LabelThreeSigma"))
        self.gridLayout.addWidget(self.LabelThreeSigma, 5, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.groupBox)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout.addWidget(self.label_10, 6, 0, 1, 1)
        self.LabelFourSigma = QtGui.QLabel(self.groupBox)
        self.LabelFourSigma.setObjectName(_fromUtf8("LabelFourSigma"))
        self.gridLayout.addWidget(self.LabelFourSigma, 6, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton.setText(_translate("Form", "Analyze signal", None))
        self.label.setText(_translate("Form", "Applied voltage", None))
        self.label_2.setText(_translate("Form", "mV", None))
        self.label_4.setText(_translate("Form", "Sensitivity ", None))
        self.label_5.setText(_translate("Form", "mV/nA", None))
        self.groupBox.setTitle(_translate("Form", "Results", None))
        self.LabelMinCurrent.setText(_translate("Form", "?", None))
        self.LabelMeanCurrent.setText(_translate("Form", "?", None))
        self.label_8.setText(_translate("Form", "Resistance", None))
        self.label_6.setText(_translate("Form", "Maximum current", None))
        self.LabelMaxCurrent.setText(_translate("Form", "?", None))
        self.label_7.setText(_translate("Form", "Minimum current", None))
        self.Label_Resistance.setText(_translate("Form", "?", None))
        self.LabelSigma.setText(_translate("Form", "?", None))
        self.label234.setText(_translate("Form", "4 sigma threshold", None))
        self.label_9.setText(_translate("Form", "sigma", None))
        self.LabelThreeSigma.setText(_translate("Form", "?", None))
        self.label_3.setText(_translate("Form", "Mean current", None))
        self.label_10.setText(_translate("Form", "5 sigma threshold", None))
        self.LabelFourSigma.setText(_translate("Form", "?", None))

