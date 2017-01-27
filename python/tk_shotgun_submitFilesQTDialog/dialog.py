# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import time

from startScreenWidget import StartScreenWidget
from appSelectorWidget import AppSelectorWidget
from progressSpinnerWidget import ProgressSpinnerWidget
from fileResultsWidget import FileResultsWidget
from fileInfoWidget import FileInfoWidget
from fileNotInOutputFolderWidget import FileNotInOutputFolderWidget

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


def show_dialog(app_instance, entity_type=None, entity_ids=None):
    """
    Shows the main dialog window.
    
    :param entity_type: A Shotgun entity type, e.g. "Shot"
    :param entity_ids: A list of Shotgun entity ids, possibly empty
    """
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Submit Files to Shotgun", app_instance, Dialog)


class AThread(QtCore.QThread):

    def run(self):
        count = 0
        while count < 5:
            time.sleep(1)
            count += 1

    def stop(self):
        self.terminate()

class Dialog(QtGui.QDialog):

    #Init and create the dialogs/add pages
    def __init__(self):

        #Super Init
        QtGui.QDialog.__init__(self)
        
        #Set name
        self.setObjectName("Dialog")

        #Set size/title
        self.resize(600, 350)
        self.setWindowTitle('Submit Files to Shotgun')

        #Store reference to app
        self._app = sgtk.platform.current_bundle()

        #Store reference to chosen context
        self._context = self._app.context

        #Store reference to entity
        self._entity = self._context.entity

        #Store reference to chosen app on auto path
        self._auto_chosenApp = None

        #Store reference to found/selected files
        self._files = []
        self._chosenFile = None

        #Check paths exist
        self._entityPaths = self.checkPathsExist()
        if not self._entityPaths:
            self.display_exception("No paths exist for this asset", [])
            self.close()
            return

        try : 

            #Set main layout
            self._layout = QtGui.QVBoxLayout()
            self.setLayout(self._layout)

            #Make the widgets - one widget per screen
            self._startScreenWidget = StartScreenWidget(self)
            self._auto_appSelectorWidget = AppSelectorWidget(self)
            self._progressSpinnerWidget = ProgressSpinnerWidget(self, "Thinking...")
            self._fileResultsWidget = FileResultsWidget(self)
            self._fileInfoWidget = FileInfoWidget(self)
            self._fileNotInOutputFolderWidget = FileNotInOutputFolderWidget(self)

            #Add all widgets
            self._layout.addWidget(self._startScreenWidget)
            self._layout.addWidget(self._auto_appSelectorWidget)
            self._layout.addWidget(self._progressSpinnerWidget)
            self._layout.addWidget(self._fileResultsWidget)
            self._layout.addWidget(self._fileInfoWidget)
            self._layout.addWidget(self._fileNotInOutputFolderWidget)

            # #Make dicts of widgets
            self._widgetDict = {

                '1' : self._startScreenWidget,
                '2' : self._auto_appSelectorWidget,
                '3' : self._progressSpinnerWidget,
                '4' : self._fileResultsWidget,
                '5' : self._fileInfoWidget,
                '6' : self._fileNotInOutputFolderWidget,

            }

            #Show first widget
            self.showWidgetWithID(1)


        except Exception as e : 
            self.display_exception("ERROR", [str(e)])



    '''

    Check paths

    '''

    def checkPathsExist(self):
        paths = self._context.filesystem_locations
        if len(paths) == 0:
            return None
        return paths



    '''

    Handling Navigation

    '''

    def showWidgetWithID(self, widgetID):

        #Hide all widgets
        for widgetIndex in self._widgetDict :
            self._widgetDict[widgetIndex].setVisible(False)

        #Show the chosen widget
        for widgetIndex in self._widgetDict :        
            if widgetIndex == str(widgetID) :
                self._widgetDict[widgetIndex].setVisible(True)
                break


    def autoModeSelected(self):
        #Progress to the auto page
        self.showWidgetWithID(2)

    def browseButtonClicked(self):

        self.startFileBrowser()

    def appSelectorButtonClicked(self):
        # self.display_exception("App Selected", [self.sender().text()])

        #Set the chosen app
        self._auto_chosenApp = self.sender().text()

        #Set the progress spinner message
        self._progressSpinnerWidget.changeMessage("Looking for new %s files..." % self._auto_chosenApp)

        #Show the progress widget
        self.showWidgetWithID(3)

        #Start the search for files



    '''

    Browse button

    '''

    def startFileBrowser(self):

        #Show a file browser
        startDirectory = self._entityPaths[0]
        title = "Select file to Submit"
        fileFilter = "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
        fname, filterMatch = QtGui.QFileDialog.getOpenFileName(self, title, startDirectory, fileFilter)

        #Ensure that a file was chosen
        if len(fname) == 0:
            return
        if fname == None:
            return

        if not os.path.exists(fname):
            return

        #Store the chosen file
        self._files = [fname]
        self._chosenFile = fname

        #Check if the file is within the asset directory
        if self._entityPaths[0] not in self._chosenFile:
            self.display_exception("File not in Asset Directory", ["The file you have chosen doesn't exist within the current Asset's directory structure, and cannot be submitted."])
            return

        #Check whether the file is in an output folder
        if os.path.basename(os.path.dirname(self._chosenFile)) == "__OUTPUT" :
            #The asset IS in an output directory. Go straight to the info page
            self._fileInfoWidget.updateLabel()
            self.showWidgetWithID(5)
        else : 
            #The asset is not in an output directory. 
            #Get the closest output directory
            closestOutputFolderPath = os.path.join(os.path.split(self._chosenFile)[0], "__OUTPUT")

            #Check it exists
            if not os.path.exists(closestOutputFolderPath):
                self.display_exception("Cannot find an associated __OUTPUT Folder for this file", ["The file you have chosen is not within a directory that contains an __OUTPUT folder. This means that it is NOT in a valid working directory and it cannot be uploaded to Shotgun.", "", "Please ensure that you always work in a valid directory."])
                return

            #File is in a valid working directory. Show copy page.
            self._fileNotInOutputFolderWidget.updateLabel()
            self.showWidgetWithID(6)
            





    '''

    Global functions

    '''

    #Make the Finish button actually close the dialog
    def accept(self):

        #Add shotgun widget overlay
        try :

            #Try thread
            self._bgthread = AThread()
            self._bgthread.finished.connect(self.threadFinished)
            self._bgthread.start()

        except Exception as e : 
            self.display_exception("Error", [str(e)])

    def threadFinished(self):

        self._bgthread.terminate()
        self.close()

    #Allow us to display useful data on screen
    def display_exception(self, msg, exec_info):
        """
        Display a popup window with the error message
        and the exec_info in the "details"

        :param msg: A string
        :param exec_info: A list of strings
        """
        msg_box = QtGui.QMessageBox(
            parent=self,
            icon=QtGui.QMessageBox.Critical
            )
        msg_box.setText(msg)
        msg_box.setDetailedText("\n".join(exec_info))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    #Ensure that esc will close the dialog
    def keyPressEvent(self, evt):
        """
        Catch keyPress event
        Check :
        - If Ctrl-Q or Ctrl-W were pressed,
        
        On Mac, Cmd-Q is caught with closeEvent, not here

        :param evt: A QEvent
        """
        has_control_key = evt.modifiers() == QtCore.Qt.ControlModifier
        key = evt.key()
        if (has_control_key and key in [QtCore.Qt.Key_W, QtCore.Qt.Key_Q]):
            evt.accept()  # We handled this key combo
            # This will call closeEvent to accept
            # or discard the close "order"
            self.close()
        elif (key in [QtCore.Qt.Key_Escape]):
            evt.accept()
            self.close()
        # Fall back to base class implementation
        super(Dialog, self).keyPressEvent(evt)