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

        #Keep track of whether we came from manual file browse or automatic mode
        self._previousScreen = None #can be automatic or manual

        #Make layout for asset info
        assetInfoLayout = QtGui.QVBoxLayout()

        #Add file label
        self._fileLabel = QtGui.QLabel("File : %s" % self._parentUI._chosenFile)
        self._fileLabel.setAlignment(QtCore.Qt.AlignCenter)
        assetInfoLayout.addWidget(self._fileLabel)

        #Make layout for type
        typeLayout = QtGui.QVBoxLayout()

        #Add type label and combo box
        typeLabel = QtGui.QLabel('<p style="font-size:14px">How would you describe this file?</p>')
        self._typeComboBox = QtGui.QComboBox()

        #Pull values from Shotgun and add
        values = self._parentUI._shotgun.schema_field_read('Version')['sg_version_type']['properties']['valid_values']['value']
        for value in (['Please Choose a Type...']+sorted(values)) :
            self._typeComboBox.addItem(value)

        #Set font size on combobox
        self._typeComboBox.setStyleSheet("font-size: 14px")

        #Connect up the combob box
        self._typeComboBox.currentIndexChanged.connect(self.comboBoxValueChanged)

        #add label/combobox
        typeLayout.addWidget(typeLabel)
        typeLayout.addWidget(self._typeComboBox)

        #Make layout for comment
        commentLayout = QtGui.QVBoxLayout()

        #Add comment label and box
        commentLabel = QtGui.QLabel('<p style="font-size:14px">Comment (Optional)</p>')
        self._commentTextEdit = QtGui.QLineEdit()
        commentLayout.addWidget(commentLabel)
        commentLayout.addWidget(self._commentTextEdit)

        #Add layouts
        newLayout.addLayout(assetInfoLayout)
        newLayout.addStretch(1)
        if not self._parentUI._conceptMode:
            newLayout.addLayout(typeLayout)
            newLayout.addStretch(1)
        newLayout.addLayout(commentLayout)
        newLayout.addStretch(1)

        #Add back button
        buttonLayout = QtGui.QHBoxLayout()
        backButton = QtGui.QPushButton("Back")
        backButton.clicked.connect(self.backButtonHit)
        buttonLayout.addWidget(backButton)

        #Add submit button
        self._submitButton = QtGui.QPushButton("Submit")
        if not self._parentUI._conceptMode:
            self._submitButton.setEnabled(False)
        self._submitButton.clicked.connect(self.submitButtonHit)
        buttonLayout.addWidget(self._submitButton)

        newLayout.addLayout(buttonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def comboBoxValueChanged(self):
        self._submitButton.setEnabled(False)
        if self._typeComboBox.currentIndex() != 0 :
            self._submitButton.setEnabled(True)

    def updateLabel(self):
        self._fileLabel.setText('<p style="font-size:16px">%s</p>' % os.path.split(self._parentUI._chosenFile)[1])

    def submitButtonHit(self):
        self._parentUI.doSubmit()

    def backButtonHit(self):
        if self._previousScreen == 'automatic':
            #Go back to the results screen
            self._parentUI.showWidgetWithID(4)
        else :
            #Go back to the main screen
            self._parentUI.showWidgetWithID(1)
