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

        #Get label strings
        if not self._parentUI._conceptMode :
            labelString = '<p style="font-size:16px">You are Submitting a file for the %s</p>' % self._parentUI._entity['type']
            entityLabelString = '<p style="font-size:32px">%s</p>' % self._parentUI._entity['name']
        else : 
            labelString = ''
            entityLabelString = '<p style="font-size:32px">Upload New Concept</p>'

        #Create labels and add
        label = QtGui.QLabel(labelString)
        label.setAlignment(QtCore.Qt.AlignCenter)
        entityLabel = QtGui.QLabel(entityLabelString)
        entityLabel.setAlignment(QtCore.Qt.AlignCenter)
        newLayout.addStretch(1)
        newLayout.addWidget(label)
        newLayout.addWidget(entityLabel)
        newLayout.addStretch(1)

        #Make button layout
        buttonLayout = QtGui.QHBoxLayout()

        #Make buttons
        if not self._parentUI._conceptMode : 
            self._browseButton = QtGui.QPushButton("Browse for File")
            self._autoButton = QtGui.QPushButton("Automatic")
            self._browseButton.clicked.connect(self._parentUI.browseButtonClicked)
            self._autoButton.clicked.connect(self._parentUI.autoModeSelected)
            buttonLayout.addWidget(self._browseButton)
            buttonLayout.addWidget(self._autoButton)
        else : 
            self._conceptButton = QtGui.QPushButton("Upload New Concept")
            self._conceptButton.clicked.connect(self._parentUI.conceptButtonClicked)
            buttonLayout.addWidget(self._conceptButton)

        #Add button layout to content layout
        newLayout.addLayout(buttonLayout)

        #Add layout to widget
        self.setLayout(newLayout)