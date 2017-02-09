import sgtk
import os
import sys
import time
import re

from PySide import QtCore, QtGui


class ShotgunUploaderBGThread(QtCore.QThread):

    def __init__(self, uploader):

        #Super Init
        QtCore.QThread.__init__(self)

        #Set vars
        self._uploader = uploader

    def run(self):

        if self._uploader._mode == 'version':
            #Make the version
            try: 
                self._uploader._uploadedVersion = self._uploader._dialog._shotgun.create('Version', self._uploader._versionData)
            except Exception as e :
                self._uploader._uploadedVersion = None
                self._uploader._errorData = e

            #If version creation didn't succeed, return
            if not self._uploader._uploadedVersion :
                return

            #Upload file
            try :
                self._uploader._uploadedFile = self._uploader._dialog._shotgun.upload('Version', self._uploader._uploadedVersion['id'], self._uploader._filePath, field_name='sg_uploaded_movie')
            except Exception as e : 
                self._uploader._uploadedFile = None
                self._uploader._errorData = e

        elif self._uploader._mode == 'publish':

            #Publish
            try : 
                data = self._uploader._publishData
                self._uploader._uploadedPublish = sgtk.util.register_publish(data['tk'], data['context'], data['path'], data['name'], published_file_type=data['published_file_type'], version_number=data['version_number'])
            except Exception as e :
                self._uploader._uploadedPublish = None
                self._uploader._errorData = e

        else : 
            return


    def stop(self):
        self.terminate()


class ShotgunUploader(object):

    def uploadFiles(self, dialog, context, dataDict):

        #Set vars
        self._dialog = dialog
        self._context = context
        self._dataDict = dataDict
        self._dataDictKeys = dataDict.keys()

        self._backgroundThread = None
        self._wasCancelled = False
        self._errorData = None

        self._filesLeftToUpload = len(self._dataDict)
        self._currentFileIndex = 0

        #Trigger the upload of the first file
        # self._dialog.display_exception("About to upload", [str(fileDict)])
        self.uploadFile()

    def setData(self, filePath, versionType, comment, mode='publish'):

        self._filePath = filePath
        self._versionType = versionType
        self._comment = comment

        self._versionData = None
        self._publishData = None
        self._conceptData = None

        self._uploadedVersion = None
        self._uploadedFile = None
        self._uploadedPublish = None 

        self._mode = mode

    def returnVersionNumberIntFromStringOrNone(self, fileString):
        regex = "_v\d{4}"
        result = re.search(regex, fileString)
        if not result :
            return None
        versionStringMatch = result.group(0)
        intVersion = int( versionStringMatch[2:] )
        return intVersion

    def returnPrefixToVersionAsStringOrNone(self, fileString):
        regex = "_v\d{4}"
        result = re.split(regex, fileString)
        return result[0]

    def uploadFile(self):

        #Show the progress window
        self._dialog.showProgress(  "Uploading file %s/%s..." % (  (self._currentFileIndex+1), len(self._dataDict)  )  )

        #Get the info for this file
        fileDict = self._dataDict[self._dataDictKeys[self._currentFileIndex]]
        
        #Reset the data for this file
        self.setData(fileDict['filePath'], fileDict['versionType'], fileDict['comment'], fileDict['mode'])

        #Calculate the version name
        versionName = self.returnPrefixToVersionAsStringOrNone(os.path.basename(self._filePath))
        if versionName == None :
            #There was no 4 digit version string in the file name. Just get the name without extension
            fileName, fileExt = os.path.splitext(os.path.basename(self._filePath))
            versionName = fileName

        #Calculate the version number
        versionNumber = self.returnVersionNumberIntFromStringOrNone(self._filePath)
        if versionNumber == None : 
            #There was no version number in the file name. Just set to 1
            versionNumber = 1

        #Get the publish type
        publishType = self._dialog.returnPublishTypeForFile(self._filePath)

        #Set values based upon mode
        if self._mode == 'version':
            #Set version data
            self._versionData = {}
            self._versionData['project'] = {'type': 'Project','id': self._context.project['id']}
            self._versionData['code'] = versionName
            if '.pdf' in self._filePath:
                self._versionData['sg_path_to_frames'] = self._filePath
            else : 
                self._versionData['sg_path_to_movie'] = self._filePath
            self._versionData['description'] = self._comment

            #If not in concept mode - set entity/task, and set version type from dropdown
            if self._dialog._conceptMode != True :
                self._versionData['entity'] = self._context.entity
                self._versionData['sg_task'] = self._context.task
                self._versionData['sg_version_type'] = self._versionType

            #If in concept mode override version type
            else : 
                self._versionData['sg_version_type'] = 'concept'

        elif self._mode == 'publish':

            #Set publish data
            self._publishData = {}
            self._publishData["tk"] = self._context.tank
            self._publishData["context"] = self._context
            self._publishData["comment"] = self._comment
            self._publishData["path"] = self._filePath
            self._publishData["name"] = versionName
            self._publishData["version_number"] = versionNumber
            self._publishData["task"] = self._context.task
            self._publishData["dependency_paths"] = []
            self._publishData["published_file_type"] = publishType
            self._publishData['sg_uploaded_movie'] = {'local_path': self._filePath, 'name': versionName}

        else : 
            self._dialog.display_exception("Upload mode not set correctly", ["Was set to %s" % self._mode])
            return

        #Do the upload
        self._errorData = None
        self._backgroundThread = ShotgunUploaderBGThread(self)
        self._backgroundThread.finished.connect(self.singleFileUploadCompleted)
        self._backgroundThread.start()

    def cancelUpload(self):

        #Clean up thread
        self._backgroundThread.stop()

    def singleFileUploadCompleted(self):

        #If cancelled, do nothing - logic is handled in main Dialog file
        if self._wasCancelled :
            return

        #Clean up thread
        self._backgroundThread.stop()

        #Show errors if any
        if self._errorData != None : 
            self._dialog.display_exception("Upload Error", [str(self._errorData)])

        #Decrease the files left to upload by 1
        self._filesLeftToUpload -= 1

        #Check if this is the last file
        if self._filesLeftToUpload == 0 :
            #We can return 
            self._dialog.showWidgetWithID(7)
        else : 
            #There are still things to upload
            #Set the current file index
            self._currentFileIndex += 1

            #Upload the next file
            self._errorData = None
            self.uploadFile()





