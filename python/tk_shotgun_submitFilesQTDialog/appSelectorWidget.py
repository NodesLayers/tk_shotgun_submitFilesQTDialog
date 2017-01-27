import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


class AppSelectorWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make text label
        label = QtGui.QLabel("Select the app associated with the new file :")
        newLayout.addWidget(label)

        #Make grid layout for app buttons
        gridLayout = QtGui.QGridLayout()
        
        #Get the apps 
        apps = ['After Effects', 'Cinema4D', 'Illustrator', 'Maya', 'Nuke', 'Photoshop']

        #Add buttons - maximum of 3 per row
        maxButtonsPerRow = 3
        for x, app in enumerate(apps) :

            #Create button with app name
            newButton = QtGui.QPushButton(app)

            #Calculate where button sits in grid
            row = x/maxButtonsPerRow
            column = x - (maxButtonsPerRow*row)

            #Add button to correct space
            gridLayout.addWidget(newButton, row, column)

            #Connect buttons
            newButton.clicked.connect(self._parentUI.appSelectorButtonClicked)

        #Add application button layout
        newLayout.addLayout(gridLayout)

        #Add back button
        backButtonLayout = QtGui.QHBoxLayout()
        backButton = QtGui.QPushButton("Back")
        backButtonLayout.addWidget(backButton)
        backButton.clicked.connect(self.backButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(backButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)


    def backButtonHit(self):
        self._parentUI.showWidgetWithID(1)
