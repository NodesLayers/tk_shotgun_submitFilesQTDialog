import sgtk
import os
import sys
import time
import re

from sgtk.platform.qt import QtCore, QtGui

class ShotgunFileFinderBGThread(QtCore.QThread):

    def __init__(self, fileFinder):

        #Super Init
        QtCore.QThread.__init__(self)

        #Set vars
        self._fileFinder = fileFinder

    def run(self):

        #Setup appFolder
        self._fileFinder.setupTemplate()

        #Setup output folders
        self._fileFinder.setupOutputFolders()

        #Get files
        self._fileFinder.findAllFilesInFolders()

        #Get all publishes/versions on the server
        self._fileFinder.findAllVersionsAndPublishesOnSG()

        #Get a list of all files that do not exist as versions/publishes on SG
        self._fileFinder.findAllNonShotgunFiles()

        '''
        At this point we have a list of all files that exist for the choosen app on the current entity
        '''



class ShotgunFileFinder(object):

    def __init__(self, dialog, appButtonText):

        self._dialog = dialog
        self._appsToSearch = [appButtonText.replace(" ", "").lower()]

        #Update the progress
        self._dialog.showProgress("Comparing local files to Publishes/Versions in Shotgun...")

        #If _appsToSearch is 'allapps', replace with all apps
        if self._appsToSearch[0] == 'allapps':
            if self._dialog._entity['type'] == "Asset":
                self._appsToSearch = [x.replace(" ", "").lower() for x in self._dialog._assetApps]
            else :
                self._appsToSearch = [x.replace(" ", "").lower() for x in self._dialog._shotApps]

        self._appFolders = []
        self._existingVersions = []
        self._existingPublishes = []
        self._existingFilePaths = []
        self._filesThatArentInShotgun = []

        #Do the upload
        self._backgroundThread = ShotgunFileFinderBGThread(self)
        self._backgroundThread.finished.connect(self.fileFinderBGThreadFinished)
        self._backgroundThread.start()

    def fileFinderBGThreadFinished(self):
        joinedNonSGFiles = '\n'.join(self._filesThatArentInShotgun)
        joinedSGFiles = '\n'.join(self._existingFilePaths)
        self._dialog.showProgress("BG Thread finished. Found %s existing Versions, and %s existing Publishes.\n\nThere are %s filepaths associated with those SG assets.\n\nThere are %s files not uploaded.\n\nThose files are :\n%s\n\nAlready on SG :\n%s" % ( len( self._existingVersions ), len( self._existingPublishes ), len( self._existingFilePaths ), len( self._filesThatArentInShotgun ),  joinedNonSGFiles, joinedSGFiles ) )

    def setupTemplate(self):

        self._entityType = self._dialog._entity['type']

        #Loop through every app we need to search
        for app in self._appsToSearch:

            #Get the template name for that app
            currentAppTemplateName = "submitFilesToShotgun_%s_%s" % (self._entityType.lower(), app)
            currentAppTemplate = self._dialog._tank.templates[currentAppTemplateName]

            #If you can't find a template for the given app set the finder to invalid
            isValidTemplate = False
            if currentAppTemplate != None:
                currentAppTemplateFields = self._dialog._context.as_template_fields(currentAppTemplate)
                currentAppFolderPath = currentAppTemplate.apply_fields(currentAppTemplateFields)

                #Check folder exists
                if os.path.exists(currentAppFolderPath):
                    isValidTemplate = True

            #If it's a valid template, add the app path
            if isValidTemplate:
                self._appFolders.append(currentAppFolderPath)


    def setupOutputFolders(self):
        self._outputFolders = []
        for appFolder in self._appFolders:
            #Find any folders called __OUTPUT below the self._appFolder
            self._outputFolders.extend([root for root, subFolders, files in os.walk(appFolder) if '__OUTPUT' in root])

    def findAllFilesInFolders(self):
        #For each output folder list the files
        self._allFiles = []
        ignoreFiles = [".DS_Store"]
        for outputFolder in self._outputFolders : 
            self._allFiles.extend( [os.path.join(outputFolder, f) for f in os.listdir(outputFolder) if f not in ignoreFiles and os.path.isfile(os.path.join(outputFolder, f))] )


    def findAllVersionsAndPublishesOnSG(self):

        #Setup filters and fields for the search
        filters = [['entity', 'is', self._dialog._entity]]
        versionFields = ['id', 'code', 'sg_path_to_movie']
        publishFields = ['id', 'code', 'path']

        self._existingVersions = self._dialog._shotgun.find('Version', filters, versionFields)
        self._existingPublishes = self._dialog._shotgun.find('PublishedFile', filters, publishFields)


    def findAllNonShotgunFiles(self):

        #We have a list of all versions and publishes. Extract the file paths
        self._existingFilePaths = []
        for existingVersion in self._existingVersions:
            if existingVersion['sg_path_to_movie'] != None:
                self._existingFilePaths.append(str(existingVersion['sg_path_to_movie']))
        for existingPublish in self._existingPublishes:
            if existingPublish['path'] != None:
                self._existingFilePaths.append(existingPublish['path']['local_path'])

        #For each file we want to upload, check if it's in the existing paths.
        #If it is, skip, if not, store
        self._filesThatArentInShotgun = []
        for localFilePath in self._allFiles:
            if localFilePath not in self._existingFilePaths:
                self._filesThatArentInShotgun.append(localFilePath)



