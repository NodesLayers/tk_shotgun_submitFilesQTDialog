import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


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
        label = QtGui.QLabel("Upload Success")
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
