import sgtk
import os
import sys
import time

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


class FileResultsWidget(QtGui.QWidget):

	#Init and create the widget
    def __init__(self, parent):

    	#Super Init
        QtGui.QWidget.__init__(self)

        #Keep track of parent
        self._parentUI = parent

        #Set the main layout for the page
        newLayout = QtGui.QVBoxLayout()

        #Make text label
        self._filesLabel = QtGui.QLabel("The following new files have been found :")
        newLayout.addWidget(self._filesLabel)

        #Try and add a table
        self._tableView = FileResultsTableView(self)

        #Setup the table model
        self._currentData = []
        self._tableHeaders = ['File Name', 'Software', 'File Type', '']
        self._tableModel = FileResultsTableModel(self, self._currentData, self._tableHeaders)

        #Set the tableview to use the model
        self._tableView.setModel(self._tableModel)
        self._tableView.resizeColumnsToContents()
        self._tableView.setSortingEnabled(True)
        self._tableView.setColumnHidden(4, True)
        self._tableView.horizontalHeader().setStretchLastSection(True)

        #Add the table to the layout
        newLayout.addWidget(self._tableView)

        #Add back button
        cancelButtonLayout = QtGui.QHBoxLayout()
        cancelButton = QtGui.QPushButton("Cancel")
        cancelButtonLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.cancelButtonHit)
        newLayout.addStretch(1)
        newLayout.addLayout(cancelButtonLayout)

        #Add layout to widget
        self.setLayout(newLayout)

    def cancelButtonHit(self):
        self._parentUI.showWidgetWithID(1)

    def updateModelWithNewData(self, newData):
        #Data array is in form [ (filename, software, fileType, "", 'Full Path')  ]
        self._tableModel = None
        self._currentData = newData
        self._tableModel = FileResultsTableModel(self, self._currentData, self._tableHeaders)
        self._tableView.setModel(self._tableModel)
        self._tableView.setColumnHidden(4, True)
        self._tableView.resizeColumnsToContents()
        self._tableView.horizontalHeader().setStretchLastSection(True)


class FileResultsTableView(QtGui.QTableView):
    """
    A simple table to demonstrate the button delegate.
    """
    def __init__(self, parentUI):
        QtGui.QTableView.__init__(self)

        self._parentUI = parentUI
 
        # Set the delegate for column 0 of our table
        self._buttonDelegate = ButtonDelegate(self)
        self.setItemDelegateForColumn(3, self._buttonDelegate)
 
    def cellButtonClicked(self, rowID):

        #Get file to upload
        fileToUpload = self._parentUI._currentData[rowID][4]
        # self._parentUI._parentUI.display_exception("Submit Details", [str(rowID), str(fileToUpload)] )

        #Call to the main UI
        self._parentUI.parent().autoFileSelectedForSubmit(fileToUpload)

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

class ButtonDelegate(QtGui.QItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtGui.QItemDelegate.__init__(self, parent)
 
    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button = QtGui.QPushButton("Submit this item", self.parent())
            button.clicked.connect(lambda: self.parent().cellButtonClicked(index.row()))
            self.parent().setIndexWidget(
                index, 
                button
            )