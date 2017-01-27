import sgtk
import os
import sys
import time

class ShotgunUploader(object):

	def setData(self, filePath, versionType, comment):

		self._filePath = filePath
		self._versionType = versionType
		self._comment = comment


