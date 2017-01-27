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
    	seconds = 3
    	secondsPast = 0
    	while secondsPast < seconds :
    		time.sleep(1)
    		secondsPast += 1
    	# self._uploader._uploadedVersion = "NewVersion3452"
    	self._uploader._uploadedVersion = None

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

		self._uploadedVersion = None


	def uploadVersion(self):

		#Calculate the version name
		versionName = 'TestVersionName'

		# self._dialog.display_exception("Context", [str(self._context), str(self._context.project), str(self._context.entity), str(self._context.task)])

		#Set version data
		versionData = {}
		versionData['project'] = {'type': 'Project','id': self._context.project['id']}
		versionData['code'] = versionName
		versionData['entity'] = self._context.entity
		versionData['sg_path_to_movie'] = self._filePath
		versionData['description'] = self._comment
		versionData['sg_task'] = self._context.task

		self._backgroundThread = ShotgunUploaderBGThread(self)
		self._backgroundThread.finished.connect(self.uploadVersionCompleted)
		self._backgroundThread.start()

	def uploadVersionCompleted(self):

		#Clean up thread
		self._backgroundThread.stop()

		#Get confirmation
		if self._uploadedVersion != None :
			self._dialog.showWidgetWithID(7)
		else :
			self._dialog.showWidgetWithID(8)