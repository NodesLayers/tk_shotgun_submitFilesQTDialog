import sgtk
import os
import sys
import time

from PySide import QtCore, QtGui


class FileNotInOutputFolderWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make text label
        self._label = QtGui.QLabel("Temp")
        self._label.setWordWrap(True)
        newLayout.addWidget(self._label)

        #Add copy button
        copyButtonLayout = QtGui.QHBoxLayout()
        copyButton = QtGui.QPushButton("Copy File")
        copyButtonLayout.addWidget(copyButton)
        copyButton.clicked.connect(self.copyButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(copyButtonLayout)

        #Add back button
        backButtonLayout = QtGui.QHBoxLayout()
        backButton = QtGui.QPushButton("Back")
        backButtonLayout.addWidget(backButton)
        backButton.clicked.connect(self.backButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(backButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def copyButtonHit(self):
        self._parentUI.doCopy()

    def backButtonHit(self):
        self._parentUI.showWidgetWithID(1)

    def updateLabel(self):
        self._label.setText('''
The file %s is not currently in an __OUTPUT folder.

Shotgun can copy it into the correct directory now before publishing.

Would you like to copy the file now?''' % os.path.basename(self._parentUI._chosenFile))