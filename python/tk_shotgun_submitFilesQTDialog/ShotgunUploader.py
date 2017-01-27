import sgtk
import os
import sys
import time

from sgtk.platform.qt import QtCore, QtGui


class ShotgunUploaderBGThread(QtCore.QThread):

    def __init__(self, uploader):
        #Super Init
        QtCore.QThread.__init__(self)

        self._uploader = uploader

    def run(self):
    	# seconds = 3
    	# secondsPast = 0
    	# while secondsPast < seconds :
    	# 	time.sleep(1)
    	# 	secondsPast += 1
    	# # self._uploader._uploadedVersion = "NewVersion3452"
    	# self._uploader._uploadedVersion = None

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

        #Publish
        try : 
        	data = self._uploader._publishData
        	self._uploader._uploadedPublish = sgtk.util.register_publish(data['tk'], data['context'], data['path'], data['name'], data['version_number'])
        except Exception as e :
        	self._uploader._uploadedPublish = None


    def stop(self):
        self.terminate()


class ShotgunUploader(object):

	def setData(self, dialog, context, filePath, versionType, comment):

		self._dialog = dialog
		self._context = context
		self._filePath = filePath
		self._versionType = versionType
		self._comment = comment

		self._backgroundThread = None

		self._versionData = None
		self._publishData = None

		self._uploadedVersion = None
		self._uploadedFile = None
		self._uploadedPublish = None


	def uploadVersion(self):

		#Calculate the version name
		versionName = 'TestVersionName'
		versionNumber = 1
		publishType = "Rendered Image"

		# self._dialog.display_exception("Context", [str(self._context), str(self._context.project), str(self._context.entity), str(self._context.task)])

		#Set version data
		self._versionData = {}
		self._versionData['project'] = {'type': 'Project','id': self._context.project['id']}
		self._versionData['code'] = versionName
		self._versionData['entity'] = self._context.entity
		self._versionData['sg_path_to_movie'] = self._filePath
		self._versionData['description'] = self._comment
		self._versionData['sg_task'] = self._context.task

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

		self._backgroundThread = ShotgunUploaderBGThread(self)
		self._backgroundThread.finished.connect(self.uploadVersionCompleted)
		self._backgroundThread.start()

	def uploadVersionCompleted(self):

		#Clean up thread
		self._backgroundThread.stop()

		#Get confirmation
		if self._uploadedVersion != None and self._uploadedPublish != None :
			self._dialog.showWidgetWithID(7)
		else :
			self._dialog.showWidgetWithID(8)