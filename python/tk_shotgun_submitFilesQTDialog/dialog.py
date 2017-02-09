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


#PySide is imported from <config>/install/core/scripts/PySide directory - if it's not there, this won't work.
from PySide import QtCore, QtGui


def show_dialog(app_instance, entity_type=None, entity_ids=None):
    """
    Shows the main dialog window.
    
    :param entity_type: A Shotgun entity type, e.g. "Shot"
    :param entity_ids: A list of Shotgun entity ids, possibly empty
    """
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    appTitle = app_instance.get_setting("app_title") or "Submit Files to Shotgun"
    app_instance.engine.show_dialog(appTitle, app_instance, Dialog)


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

        self._conceptMode = self._app.get_setting("concept_mode")
        if self._conceptMode:
            self.setWindowTitle(self._app.get_setting("app_title"))


        #Store reference to allowed apps
        self._assetApps = self._app.get_setting("asset_apps")
        self._shotApps = self._app.get_setting("shot_apps")

        #Store reference to chosen context
        self._context = self._app.context

        #Store reference to entity
        self._entity = self._context.entity

        #Check paths exist
        self._entityPaths = self.checkPathsExist()
        if not self._entityPaths:
            self.display_exception("No paths exist for this asset", [])
            self.close()
            return

        #Store reference to chosen app on auto path
        self._auto_chosenApp = None

        #Store reference to found/selected files
        self._files = []
        self._chosenFiles = []

        #Store references for files being copied
        self._sourceCopyPath = None
        self._destCopyPath = None

        #Store threads
        self._copyThread = None
        self._uploadThread = None

        #Setup shotgun uploader
        self._shotgunUploader = ShotgunUploader()


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

    def conceptButtonClicked(self):
        self.startFileBrowser(conceptMode=True)

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
        self.showProgress("Starting the search for files...")

        #Start the search for files that aren't already associated with versions, on the BG Thread
        self._shotgunFileFinder = ShotgunFileFinder(self, self._auto_chosenApp)
        # self.display_exception("App", [str(self._shotgunFileFinder._appsToSearch), str(self._shotgunFileFinder._appFolders), str(self._shotgunFileFinder._outputFolders), str(self._shotgunFileFinder._allFiles)])
        # self.display_exception("App", [str(self._shotgunFileFinder._appsToSearch)])

    '''

    Browse button

    '''

    def startFileBrowser(self, conceptMode=False):

        #Get the concept folder
        conceptTemplate = self._tank.templates['submitFilesToShotgun_conceptOutputDirectory']
        conceptFields = self._context.as_template_fields(conceptTemplate)
        self._conceptFolderPath = conceptTemplate.apply_fields(conceptFields)

        #Show a file browser
        if conceptMode : 
            startDirectory = self._conceptFolderPath
            title = "Select Concept to Submit"
        else : 
            startDirectory = self._entityPaths[0]
            title = "Select file to Submit"

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
        self._chosenFiles = [fname]

        #Check if the file is within the required directory (projectdir for concepts, entity dir for entities)
        if self._entityPaths[0] not in self._chosenFiles[0]:
            self.display_exception("File not in Asset Directory", ["The file you have chosen doesn't exist within the current Asset's directory structure, and cannot be submitted."])
            return

        #Check whether the file is in an output folder
        isInCorrectFolder = False
        if self._conceptMode:
            #Just check if __OUTPUT is in the filename and that the file is in the concept folder somewhere
            if ('__OUTPUT' in self._chosenFiles[0]) and (self._conceptFolderPath in self._chosenFiles[0]):
                isInCorrectFolder = True
        else : 
            #Check if the last folder in the path is __OUTPUT
            if os.path.basename(os.path.dirname(self._chosenFiles[0])) == "__OUTPUT" :
                isInCorrectFolder = True

        #React to file location
        if isInCorrectFolder :
            #The asset IS in an output directory. Go straight to the info page
            self._fileInfoWidget.updateLabel()
            self.showWidgetWithID(5)
        else : 
            #The asset is not in an output directory. 
            #Get the path to the closest output folder
            if self._conceptMode :
                #Get the path from the appBundle
                closestOutputFolderPath = self._conceptFolderPath
            else : 
                closestOutputFolderPath = os.path.join(os.path.split(self._chosenFiles[0])[0], "__OUTPUT")

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
        self._sourceCopyPath = self._chosenFiles[0]
        if self._conceptMode:
            self._destCopyPath = os.path.join(self._conceptFolderPath, os.path.split(self._chosenFiles[0])[1])
        else :
            self._destCopyPath = os.path.join(os.path.split(self._chosenFiles[0])[0], "__OUTPUT", os.path.split(self._chosenFiles[0])[1])

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
        self._chosenFiles = [self._destCopyPath]
        self._files = [self._destCopyPath]    

        #Remove the source/dest copy vals
        self._sourceCopyPath = self._destCopyPath = None

        #Now go to the info screen
        self._fileInfoWidget.updateLabel()
        self._fileInfoWidget._previousScreen = 'manual'
        self.showWidgetWithID(5)


    '''

    Submit Functions

    '''

    def doSubmit(self):

        #Get all files to submit
        filesToSubmit = self._chosenFiles

        #Make a dict that contains all the data the uploader needs
        dataDict = {}

        #Loop through all the files
        for x, fileToSubmit in enumerate(filesToSubmit) :

            newDict = {}

            #Store the file
            newDict['filePath'] = fileToSubmit

            #Get the version type and comment
            if self._conceptMode :
                newDict['versionType'] = "concept"
            else :
                newDict['versionType'] = self._fileInfoWidget._typeComboBox.currentText()
            newDict['comment'] = str(self._fileInfoWidget._commentTextEdit.text())


            #Set the mode of the uploader
            #If png or movie, mode is version
            #If ANYTHING ELSE, mode is publish
            fileName, fileExt = os.path.splitext(fileToSubmit)

            if fileExt in ['.mov', '.png', '.jpg']:
                newDict['mode'] = 'version'
            else : 
                newDict['mode'] = 'publish'

            #Store the values
            dataDict[os.path.split(fileToSubmit)[1]] = newDict

        #Set the data on the ShotgunUploader object
        # self._shotgunUploader.setData(self, self._context, fileToSubmit, versionType, comment, mode)

        #Trigger the upload
        self._shotgunUploader.uploadFiles(self, self._context, dataDict)


    def progressCancelButtonHit(self):

        #Cancel the upload - TODO : DO THIS BETTER
        self._shotgunUploader._wasCancelled = True
        self._shotgunUploader.cancelUpload()

        #Show the info screen
        self.showWidgetWithID(5)


    '''

    File Finder


    '''

    def fileFinderFinished(self):

        #Need to update the info model
        newModelData = []
        for app in self._shotgunFileFinder._filesThatArentInShotgun:
            for fileToUpload in self._shotgunFileFinder._filesThatArentInShotgun[app]:
                fileName = os.path.split(fileToUpload)[1]
                software = app
                fileType = self.returnPublishTypeForFile(fileName)
                fullPath = fileToUpload
                newModelData.append((fileName, software, fileType, fullPath))
        self._fileResultsWidget.updateModelWithNewData(newModelData)

        #Show the info screen
        self.showWidgetWithID(4)



    '''

    Auto find file submission

    '''

    def autoFilesSelectedForSubmit(self, filesToUpload):

        #Update vars
        self._chosenFiles = filesToUpload

        #Update info screen and show
        self._fileInfoWidget.updateLabel()
        self._fileInfoWidget._previousScreen = 'automatic'
        self.showWidgetWithID(5)



    '''

    Global functions

    '''

    def returnPublishTypeForFile(self, fileString):
        '''
        3D Export - abc, obj, fbx
        After Effects Project - aep
        Cinema4D Project - c4d
        Illustrator File - ai
        Image - png, jpg, tiff, tif, bmp, gif
        Image (VFX) - exr, dpx
        Maya Scene - ma, mb
        Nuke Script - nk
        Other - ANYTHING ELSE
        Photoshop File - psd, psb
        Quicktime - mp4, mov
        '''
        fileName, fileExtensionWithDot = os.path.splitext(os.path.basename(fileString))
        fileExtension = fileExtensionWithDot.replace(".", "")

        if fileExtension in ['abc', 'obj', 'fbx']:
            return '3D Export'
    
        if fileExtension in ['aep']:
            return 'After Effects Project'        

        if fileExtension in ['c4d']:
            return 'Cinema4D Project'

        if fileExtension in ['ai']:
            return 'Illustrator File'

        if fileExtension in ['png', 'jpg', 'tiff', 'tif', 'bmp', 'gif']:
            return 'Image'

        if fileExtension in ['exr', 'dpx']:
            return 'Image (VFX)'

        if fileExtension in ['ma', 'mb']:
            return 'Maya Scene'

        if fileExtension in ['nk']:
            return 'Nuke Script'

        if fileExtension in ['psd', 'psb']:
            return 'Photoshop File'

        if fileExtension in ['mov', 'mp4']:
            return 'Quicktime'

        return "Other"

    def showProgress(self, message, cancelHidden=True):
        self._progressSpinnerWidget.changeMessage(message)
        self._progressSpinnerWidget._cancelButton.setHidden(cancelHidden)
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