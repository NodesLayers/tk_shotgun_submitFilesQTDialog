import sgtk
import os
import sys
import time

from PySide import QtCore, QtGui


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
        label = QtGui.QLabel('<p style="font-size:16px">Select the app associated with the new file</p>')
        label.setAlignment(QtCore.Qt.AlignCenter)
        newLayout.addWidget(label)
        newLayout.addStretch(1)

        #Make grid layout for app buttons
        gridLayout = QtGui.QGridLayout()

        #Get the correct apps
        if self._parentUI._conceptMode :
            apps = []
        elif self._parentUI._entity['type'] == "Asset":
            apps = [x for x in self._parentUI._assetApps]
        else :
            apps = [x for x in self._parentUI._shotApps]

        #Add an 'All Apps' button
        apps.append("All Apps")

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
