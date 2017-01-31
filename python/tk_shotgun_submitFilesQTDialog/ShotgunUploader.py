import sgtk
import os
import sys
import time
import re

from sgtk.platform.qt import QtCore, QtGui


class ShotgunUploaderBGThread(QtCore.QThread):

    def __init__(self, uploader):

        #Super Init
        QtCore.QThread.__init__(self)

        #Set vars
        self._uploader = uploader

    def run(self):

        if self._uploader._mode == 'concept':
            #Make the concept - it's CustomEntity50
            try: 
                self._uploader._uploadedConcept = self._uploader._dialog._shotgun.create('CustomEntity50', self._uploader._conceptData)
            except Exception as e :
                self._uploader._uploadedConcept = None
                self._uploader._errorData = e

            #If concept creation didn't succeed, return
            if not self._uploader._uploadedConcept :
                return


        elif self._uploader._mode == 'version':
            #Make the version
            try: 
                self._uploader._uploadedVersion = self._uploader._dialog._shotgun.create('Version', self._uploader._versionData)
            except Exception as e :
                self._uploader._uploadedVersion = None

            #If version creation didn't succeed, return
            if not self._uploader._uploadedVersion :
                return

            #Upload file
            try :
                self._uploader._uploadedFile = self._uploader._dialog._shotgun.upload('Version', self._uploader._uploadedVersion['id'], self._uploader._filePath, field_name='sg_uploaded_movie')
            except Exception as e : 
                self._uploader._uploadedFile = None

        elif self._uploader._mode == 'publish':

            #Publish
            try : 
                data = self._uploader._publishData
                self._uploader._uploadedPublish = sgtk.util.register_publish(data['tk'], data['context'], data['path'], data['name'], published_file_type=data['published_file_type'], version_number=data['version_number'])
            except Exception as e :
                self._uploader._uploadedPublish = None
                self._uploader._dialog.display_exception("Pubish Error", [e])

        else : 
            return


    def stop(self):
        self.terminate()


class ShotgunUploader(object):

    def setData(self, dialog, context, filePath, versionType, comment, mode='publish'):

        self._dialog = dialog
        self._context = context
        self._filePath = filePath
        self._versionType = versionType
        self._comment = comment

        self._backgroundThread = None

        self._versionData = None
        self._publishData = None
        self._conceptData = None

        self._uploadedVersion = None
        self._uploadedFile = None
        self._uploadedPublish = None
        self._uploadedConcept = None

        self._wasCancelled = False

        self._errorData = None

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
        if self._mode == 'concept':
            #Set version data
            self._conceptData = {}
            self._conceptData['project'] = {'type': 'Project','id': self._context.project['id']}
            self._conceptData['code'] = versionName
            self._conceptData['sg_file'] = {'local_path': '%s' % self._filePath, 'name': '%s' % versionName}
            self._conceptData['description'] = self._comment

        elif self._mode == 'version':
            #Set version data
            self._versionData = {}
            self._versionData['project'] = {'type': 'Project','id': self._context.project['id']}
            self._versionData['code'] = versionName
            self._versionData['entity'] = self._context.entity
            self._versionData['sg_path_to_movie'] = self._filePath
            self._versionData['description'] = self._comment
            self._versionData['sg_task'] = self._context.task
            self._versionData['sg_version_type'] = self._versionType

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
        self._backgroundThread = ShotgunUploaderBGThread(self)
        self._backgroundThread.finished.connect(self.uploadFileCompleted)
        self._backgroundThread.start()

    def cancelUpload(self):

        #Clean up thread
        self._backgroundThread.stop()

    def uploadFileCompleted(self):

        #If cancelled, do nothing - logic is handled in main Dialog file
        if self._wasCancelled :
            return

        #Clean up thread
        self._backgroundThread.stop()

        # self._dialog.display_exception("Upload Error", [str(self._errorData)])

        #Get confirmation
        if self._uploadedVersion != None or self._uploadedPublish != None or self._uploadedConcept != None :
            self._dialog.showWidgetWithID(7)
        else :
            self._dialog.showWidgetWithID(8)