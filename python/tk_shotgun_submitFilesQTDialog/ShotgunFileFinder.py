import sgtk
import os
import sys
import time
import re

from sgtk.platform.qt import QtCore, QtGui

class ShotgunFileFinder(object):

    def __init__(self, dialog, appButtonText):

        self._dialog = dialog
        self._appToSearch = appButtonText.replace(" ", "").lower()
        self._entityType = self._dialog._entity['type']
        self._templateName = "submitFilesToShotgun_%s_%s" % (self._entityType.lower(), self._appToSearch)
        self._template = self._dialog._tank.templates[self._templateName]

        #If you can't find a template for the given app set the finder to invalid
        self._isValid = False
        if self._template == None:
            self._appFolder = None
            self._templateFields = None
        else : 
            self._templateFields = self._dialog._context.as_template_fields(self._template)
            self._appFolder = self._template.apply_fields(self._templateFields)

            #Check folder exists
            if os.path.exists(self._appFolder):
                self._isValid = True

        #If it's valid, set the output folders
        self._outputFolders = []
        if self._isValid == True :
            #Find any folders called __OUTPUT below the self._appFolder
            self._outputFolders = [root for root, subFolders, files in os.walk(self._appFolder) if '__OUTPUT' in root]

        #For each output folder list the files
        self._allFiles = []
        ignoreFiles = [".DS_Store"]
        for outputFolder in self._outputFolders : 
            self._allFiles.extend( [os.path.join(outputFolder, f) for f in os.listdir(outputFolder) if f not in ignoreFiles and os.path.isfile(os.path.join(outputFolder, f))] )


        '''
        At this point we have a list of all files that exist for the choosen app on the current entity
        '''