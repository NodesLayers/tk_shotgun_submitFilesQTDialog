import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

overlay = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

class ProgressSpinnerWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent, message):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Keep track of message
        self._message = message

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Setup overlay and start spinning
        self._overlay = overlay.ShotgunOverlayWidget(self)
        self._overlay.start_spin()

        #Make text label
        self._label = QtGui.QLabel("Progress Spinner")
        newLayout.addWidget(self._label)

        #Add cancel button
        cancelButtonLayout = QtGui.QHBoxLayout()
        self._cancelButton = QtGui.QPushButton("Cancel")
        cancelButtonLayout.addWidget(self._cancelButton)
        self._cancelButton.clicked.connect(self.cancelButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(cancelButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def changeMessage(self, newMessage):
        self._message = newMessage
        self._label.setText(self._message)

    def cancelButtonHit(self):
        self._parentUI.showWidgetWithID(1)
