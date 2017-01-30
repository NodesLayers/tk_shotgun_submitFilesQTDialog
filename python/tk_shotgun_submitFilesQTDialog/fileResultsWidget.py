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
        self._tableView = FileResultsTableView(self._parentUI)

        #Setup the table model
        self._testData = [("My File.png", "After Effects", "Image", ""), ("Another New", "After Effects", "Movie", ""), ("Another File that is longer.mov", "Test", "Movie", "")]
        self._tableHeaders = ['File Name', 'Software', 'File Type', '']
        self._tableModel = FileResultsTableModel(self, self._testData, self._tableHeaders)

        #Set the tableview to use the model
        self._tableView.setModel(self._tableModel)
        self._tableView.resizeColumnsToContents()
        self._tableView.setSortingEnabled(False)

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
        #Data array is in form [ (filename, software, fileType, "")  ]
        self._tableModel = None
        self._tableModel = FileResultsTableModel(self, newData, self._tableHeaders)
        self._tableView.setModel(self._tableModel)


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
 
    def cellButtonClicked(self):

        #Get clicked item index
        clickedItemIndex = int(self.sender().text().split(" ")[-1])
        self._parentUI.display_exception("Button %s clicked" % clickedItemIndex, [])

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
            button = QtGui.QPushButton("Submit Item %s" % (index.row()+1), self.parent())
            button.clicked.connect(self.parent().cellButtonClicked)
            self.parent().setIndexWidget(
                index, 
                button
            )