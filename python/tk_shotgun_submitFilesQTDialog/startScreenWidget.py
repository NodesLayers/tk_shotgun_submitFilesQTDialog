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
        label = QtGui.QLabel("You are Submitting a file for :")
        entityLabel = QtGui.QLabel("%s %s" % (parent._entity['type'], parent._entity['name']))
        newLayout.addWidget(label)
        newLayout.addWidget(entityLabel)

        #Make button layout
        buttonLayout = QtGui.QHBoxLayout()

        #Make buttons
        self._browseButton = QtGui.QPushButton("Browse for File")
        self._autoButton = QtGui.QPushButton("Automatic")

        #Connect the buttons
        self._browseButton.clicked.connect(self._parentUI.browseButtonClicked)
        self._autoButton.clicked.connect(self._parentUI.autoModeSelected)

        #Add buttons to button layout
        buttonLayout.addWidget(self._browseButton)
        buttonLayout.addWidget(self._autoButton)

        #Add button layout to content layout
        newLayout.addLayout(buttonLayout)

        #Add layout to widget
        self.setLayout(newLayout)