import sgtk
import os
import sys
import time

from PySide import QtCore, QtGui


class FileResultsWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Store the data
        self._currentData = []

        #Make text label
        self._filesLabel = QtGui.QLabel('<p style="font-size:16px">These <b>%s</b> files haven\'t yet been uploaded to Shotgun</p>' % len(self._currentData))
        self._filesLabel.setAlignment(QtCore.Qt.AlignCenter)
        newLayout.addWidget(self._filesLabel)

        #Try and add a table
        self._tableView = FileResultsTableView(self)

        #Setup the table model
        self._tableHeaders = ['File Name', 'Software', 'File Type'] #checkbox and fullPath are blank
        self._tableModel = FileResultsTableModel(self, self._currentData, self._tableHeaders)

        #Set the tableview to use the model
        self._tableView.setModel(self._tableModel)
        self._tableView.resizeColumnsToContents()
        self._tableView.setSortingEnabled(True)
        self._tableView.horizontalHeader().setStretchLastSection(True)

        self._tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self._tableView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        #Add the table to the layout
        newLayout.addWidget(self._tableView)

        #Add select all/none buttons
        allNoneButtonsLayout = QtGui.QHBoxLayout()
        selectAllButton = QtGui.QPushButton("Select All")
        allNoneButtonsLayout.addWidget(selectAllButton)
        selectNoneButton = QtGui.QPushButton("Select None")
        allNoneButtonsLayout.addWidget(selectNoneButton)
        selectAllButton.clicked.connect(self.selectAllButtonHit)
        selectNoneButton.clicked.connect(self.selectNoneButtonHit)

        newLayout.addLayout(allNoneButtonsLayout)
        newLayout.addStretch(1)

        #Add back button
        bottomButtonLayout = QtGui.QHBoxLayout()

        backButton = QtGui.QPushButton("Back")
        bottomButtonLayout.addWidget(backButton)
        backButton.clicked.connect(self.backButtonHit)

        self._submitButton = QtGui.QPushButton("Submit")
        bottomButtonLayout.addWidget(self._submitButton)
        self._submitButton.clicked.connect(self.submitButtonHit)
        
        newLayout.addLayout(bottomButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def selectAllButtonHit(self):
        self._tableView.selectAll()

    def selectNoneButtonHit(self):
        self.updateModelWithNewData(self._currentData)

    def submitButtonHit(self):
        #Get the selected rows
        selected = list(set([x.row() for x in self._tableView.selectedIndexes()]))
        self._parentUI.display_exception("Selected", [str(selected)])

        #This was the logic from the submit this row button
        # #Get file to upload
        # fileToUpload = self._parentUI._currentData[rowID][3]
        # # self._parentUI._parentUI.display_exception("Submit Details", [str(rowID), str(fileToUpload)] )

        # #Call to the main UI
        # self._parentUI.parent().autoFileSelectedForSubmit(fileToUpload)

    def backButtonHit(self):
        self._parentUI.showWidgetWithID(2)

    def updateModelWithNewData(self, newData):
        #Data array is in form [ (filename, software, fileType, 'Full Path')  ]
        self._tableModel = None
        self._currentData = newData
        self._tableModel = FileResultsTableModel(self, self._currentData, self._tableHeaders)
        self._tableView.setModel(self._tableModel)
        self._tableView.setColumnHidden(3, True)
        self._tableView.resizeColumnsToContents()
        self._tableView.horizontalHeader().setStretchLastSection(True)
        self._filesLabel.setText('<p style="font-size:16px">These <b>%s</b> files haven\'t yet been uploaded to Shotgun</p>' % len(self._currentData))


class FileResultsTableView(QtGui.QTableView):
    """
    A simple table to demonstrate the button delegate.
    """
    def __init__(self, parentUI):
        QtGui.QTableView.__init__(self)

        self._parentUI = parentUI

class FileResultsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, dataList, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.dataList = dataList
        self.header = header

    def rowCount(self, parent):
        return len(self.dataList)

    def columnCount(self, parent):
        return len(self.dataList[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.dataList[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None