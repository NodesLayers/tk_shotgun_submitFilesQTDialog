# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):

        Dialog.setObjectName("Dialog")

        Dialog.resize(771, 416)
        
        #Add vertical layout
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.entityLabel = QtGui.QLabel()
        self.verticalLayout.addWidget(self.entityLabel)
        
        #Add bottom buttons
        self.button_box = QtGui.QDialogButtonBox(Dialog)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        #Set/translate dialog title 
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

        #Connect slots
        QtCore.QMetaObject.connectSlotsByName(Dialog)