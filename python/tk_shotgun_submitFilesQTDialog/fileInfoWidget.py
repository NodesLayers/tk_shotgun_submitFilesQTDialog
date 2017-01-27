import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


class FileInfoWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make layout for asset info
        assetInfoLayout = QtGui.QVBoxLayout()

        #Add file label
        self._fileLabel = QtGui.QLabel("File : %s" % self._parentUI._chosenFile)
        assetInfoLayout.addWidget(self._fileLabel)

        #Make layout for type
        typeLayout = QtGui.QVBoxLayout()

        #Add type label and combo box
        typeLabel = QtGui.QLabel("Type")
        typeComboBox = QtGui.QComboBox()
        typeLayout.addWidget(typeLabel)
        typeLayout.addWidget(typeComboBox)

        #Make layout for comment
        commentLayout = QtGui.QVBoxLayout()

        #Add comment label and box
        commentLabel = QtGui.QLabel("Comment (Optional)")
        commentTextEdit = QtGui.QTextEdit()
        commentLayout.addWidget(commentLabel)
        commentLayout.addWidget(commentTextEdit)

        #Add layouts
        newLayout.addLayout(assetInfoLayout)
        newLayout.addStretch(1)
        newLayout.addLayout(typeLayout)
        newLayout.addStretch(1)
        newLayout.addLayout(commentLayout)

        #Add submit button
        submitButtonLayout = QtGui.QHBoxLayout()
        submitButton = QtGui.QPushButton("Submit")
        submitButtonLayout.addWidget(submitButton)
        submitButton.clicked.connect(self.submitButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(submitButtonLayout)

        #Add back button
        backButtonLayout = QtGui.QHBoxLayout()
        backButton = QtGui.QPushButton("Back")
        backButtonLayout.addWidget(backButton)
        backButton.clicked.connect(self.backButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(backButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def updateLabel(self):
        self._fileLabel.setText("File : %s" % self._parentUI._chosenFile)

    def submitButtonHit(self):
        self._parentUI.showWidgetWithID(3)

    def backButtonHit(self):
        self._parentUI.showWidgetWithID(1)
