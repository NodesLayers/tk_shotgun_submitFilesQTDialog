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
		self._appFolder = self.getAppFolderForCurrentContext()

	def getAppFolderForCurrentContext(self):

		#Check the entity type
        # entityType = dialog._entity['type']

        # #Set the template
        # templateName = None
        # if entityType == 'Shot':
        #     templateName = shotTemplate
        # elif entityType == 'Asset': 
        #     templateName = assetTemplate
        # elif entityType == 'CustomEntity05': #Previs
        #     templateName = previsTemplate
        # else : 
        #     return None

        # #Get the resolved path
        # #Get template and template fields
        # tank = context.tank
        # template = tank.templates[templateName]
        # template_fields = context.as_template_fields(template)
        # template_fields['version'] = 1
        # if entityType == 'CustomEntity05':
        #     template_fields['previs'] = context.entity['name']
        # resolvedPath = template.apply_fields(template_fields)
        # folderPath, fileName = os.path.split(resolvedPath)

		return "TEST FOLDER"