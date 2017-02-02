import sgtk
import os
import sys
import time

from PySide import QtCore, QtGui


class UploadSuccessWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make text label
        label = QtGui.QLabel('<p style="font-size:32px">Upload Success</p>')
        label.setAlignment(QtCore.Qt.AlignCenter)
        newLayout.addWidget(label)

        #Add done button
        doneButtonLayout = QtGui.QHBoxLayout()
        doneButton = QtGui.QPushButton("Done")
        doneButtonLayout.addWidget(doneButton)
        doneButton.clicked.connect(self.doneButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(doneButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)


    def doneButtonHit(self):
        self._parentUI.showWidgetWithID(1)