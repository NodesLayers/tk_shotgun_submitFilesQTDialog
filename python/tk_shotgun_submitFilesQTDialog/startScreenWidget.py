import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


class StartScreenWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make text label
        label = QtGui.QLabel("Please choose whether you want Shotgun to find files automatically, or whether you want to manually upload a file :")
        label.setWordWrap(True)
        newLayout.addWidget(label)

        #Make button layout
        buttonLayout = QtGui.QHBoxLayout()

        #Make buttons
        self._autoButton = QtGui.QPushButton("Automatic")
        self._manualButton = QtGui.QPushButton("Manual")

        #Connect the buttons
        self._autoButton.clicked.connect(self._parentUI.autoModeSelected)
        self._manualButton.clicked.connect(self._parentUI.manualModeSelected)

        #Add buttons to button layout
        buttonLayout.addWidget(self._autoButton)
        buttonLayout.addWidget(self._manualButton)

        #Add button layout to content layout
        newLayout.addLayout(buttonLayout)

        #Add layout to widget
        self.setLayout(newLayout)