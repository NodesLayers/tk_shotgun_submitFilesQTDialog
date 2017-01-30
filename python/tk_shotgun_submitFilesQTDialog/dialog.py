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
import shutil

from startScreenWidget import StartScreenWidget
from appSelectorWidget import AppSelectorWidget
from progressSpinnerWidget import ProgressSpinnerWidget
from fileResultsWidget import FileResultsWidget
from fileInfoWidget import FileInfoWidget
from fileNotInOutputFolderWidget import FileNotInOutputFolderWidget
from uploadSuccessWidget import UploadSuccessWidget
from uploadFailWidget import UploadFailWidget

from ShotgunUploader import ShotgunUploader
from ShotgunFileFinder import ShotgunFileFinder

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


class CopyFileToOutputFolderThread(QtCore.QThread):

    def __init__(self, source, dest):
        #Super Init
        QtCore.QThread.__init__(self)
        self._source = source
        self._dest = dest

    def run(self):
        #Do the copy
        shutil.copy(self._source, self._dest)

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

        #Store reference to app, tank, shotgun
        self._app = sgtk.platform.current_bundle()
        self._tank = self._app.tank
        self._shotgun = self._app.shotgun

        #Store reference to allowed apps
        self._assetApps = self._app.get_setting("asset_apps")
        self._shotApps = self._app.get_setting("shot_apps")

        #Store reference to chosen context
        self._context = self._app.context

        #Store reference to entity
        self._entity = self._context.entity

        #Store reference to chosen app on auto path
        self._auto_chosenApp = None

        #Store reference to found/selected files
        self._files = []
        self._chosenFile = None

        #Store references for files being copied
        self._sourceCopyPath = None
        self._destCopyPath = None

        #Store threads
        self._copyThread = None
        self._uploadThread = None

        #Setup shotgun uploader
        self._shotgunUploader = ShotgunUploader()

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
            self._uploadSuccessWidget = UploadSuccessWidget(self)
            self._uploadFailWidget = UploadFailWidget(self)

            #Add all widgets
            self._layout.addWidget(self._startScreenWidget)
            self._layout.addWidget(self._auto_appSelectorWidget)
            self._layout.addWidget(self._progressSpinnerWidget)
            self._layout.addWidget(self._fileResultsWidget)
            self._layout.addWidget(self._fileInfoWidget)
            self._layout.addWidget(self._fileNotInOutputFolderWidget)
            self._layout.addWidget(self._uploadSuccessWidget)
            self._layout.addWidget(self._uploadFailWidget)

            # #Make dicts of widgets
            self._widgetDict = {

                '1' : self._startScreenWidget,
                '2' : self._auto_appSelectorWidget,
                '3' : self._progressSpinnerWidget,
                '4' : self._fileResultsWidget,
                '5' : self._fileInfoWidget,
                '6' : self._fileNotInOutputFolderWidget,
                '7' : self._uploadSuccessWidget,
                '8' : self._uploadFailWidget,

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

        #Show the progress widget
        # self.showProgress("Looking for new %s files..." % self._auto_chosenApp)

        #Start the search for files that aren't already associated with versions
        self._shotgunFileFinder = ShotgunFileFinder(self, self._auto_chosenApp)
        self.display_exception("App", [self._shotgunFileFinder._appToSearch, self._shotgunFileFinder._templateName, self._shotgunFileFinder._appFolder, str(self._shotgunFileFinder._isValid), str(self._shotgunFileFinder._allFiles)])

    '''

    Browse button

    '''

    def startFileBrowser(self):

        #Show a file browser
        startDirectory = self._entityPaths[0]
        title = "Select file to Submit"
        # fileFilter = "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
        # fileFilter = "Images (*.png *.jpg *.tiff *.tif *.bmp *.exr *.dpx);;Project Files (*.psd *.ai *.aep *.c4d *.ma *.mb *.nk *.psb);;3D Exports (*.abc *.fbx *.obj)"
        fname, filterMatch = QtGui.QFileDialog.getOpenFileName(self, title, startDirectory)

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

    Copy functions

    '''

    def doCopy(self):
        #Set the construct paths
        self._sourceCopyPath = self._chosenFile
        self._destCopyPath = os.path.join(os.path.split(self._chosenFile)[0], "__OUTPUT", os.path.split(self._chosenFile)[1])

        #Check that the dest path doesn't already exist
        if os.path.exists(self._destCopyPath):
            self.display_exception("File already exists", ['The file you are trying to copy already exists in the __OUTPUT directory. Choose that file instead, or change the name of the file you want to upload.'])
            self.showWidgetWithID(1)
            return

        #Show the progress widget
        self.showProgress("Copying file into __OUTPUT folder...")

        #Start the thread
        try : 
            self._copyThread = CopyFileToOutputFolderThread(self._sourceCopyPath, self._destCopyPath)
            self._copyThread.finished.connect(self.copyCompleted)
            self._copyThread.start()
        except Exception as e :
            self.display_exception("THREAD ERROR", [e])
            return



    def copyCompleted(self):
        self._copyThread.stop()
        self._copyThread = None

        #Check if things succeeded
        if not os.path.exists(self._destCopyPath):
            self.display_exception("Copy Error", ["The file copy process failed for an unknown reason. Please check with your Pipeline TD."])
            self.showWidgetWithID(1)
            return
            
        #If they did, update the files/chosen file parameters to the new file
        self._chosenFile = self._destCopyPath
        self._files = [self._destCopyPath]    

        #Remove the source/dest copy vals
        self._sourceCopyPath = self._destCopyPath = None

        #Now go to the 
        self._fileInfoWidget.updateLabel()
        self.showWidgetWithID(5)


    '''

    Submit Functions

    '''

    def doSubmit(self):

        #Get the data
        fileToSubmit = self._chosenFile
        versionType = self._fileInfoWidget._typeComboBox.currentText()
        comment = str(self._fileInfoWidget._commentTextEdit.toPlainText())

        #Set the mode of the uploader
        #If png or movie, mode is version
        #If ANYTHING ELSE, mode is publish
        fileName, fileExt = os.path.splitext(fileToSubmit)
        if fileExt in ['.mov', '.png']:
            mode = 'version'
        else : 
            mode = 'publish'

        #Set the data on the ShotgunUploader object
        self._shotgunUploader.setData(self, self._context, fileToSubmit, versionType, comment, mode)

        #Show progress
        self.showProgress("Submitting file...")

        #Do the version upload
        self._shotgunUploader.uploadFile()


    '''

    Global functions

    '''

    def showProgress(self, message):
        self._progressSpinnerWidget.changeMessage(message)
        self.showWidgetWithID(3)

    #Make the Finish button actually close the dialog
    def accept(self):
        pass

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