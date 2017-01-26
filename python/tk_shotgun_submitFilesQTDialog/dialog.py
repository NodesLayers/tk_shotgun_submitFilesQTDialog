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

from startScreenWidget import StartScreenWidget
from appSelectorWidget import AppSelectorWidget
from fileDragDropBrowseWidget import FileDragDropBrowseWidget

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

overlay = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")


def show_dialog(app_instance, entity_type=None, entity_ids=None):
    """
    Shows the main dialog window.
    
    :param entity_type: A Shotgun entity type, e.g. "Shot"
    :param entity_ids: A list of Shotgun entity ids, possibly empty
    """
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Submit Files to Shotgun", app_instance, Dialog)


class AThread(QtCore.QThread):

    def run(self):
        count = 0
        while count < 5:
            time.sleep(1)
            count += 1

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

        #Store reference to app
        self._app = sgtk.platform.current_bundle()


        try : 

            #Set main layout
            self._layout = QtGui.QVBoxLayout()
            self.setLayout(self._layout)

            #Make the widgets - one widget per screen
            self._startScreenWidget = StartScreenWidget(self)
            self._auto_appSelectorWidget = AppSelectorWidget(self)
            self._manual_fileDragDropBrowseWidget = FileDragDropBrowseWidget(self)

            #Add all widgets
            self._layout.addWidget(self._startScreenWidget)
            self._layout.addWidget(self._auto_appSelectorWidget)
            self._layout.addWidget(self._manual_fileDragDropBrowseWidget)

            # #Make dicts of widgets
            self._widgetDict = {

                '1' : self._startScreenWidget,
                '2' : self._auto_appSelectorWidget,
                '3' : self._manual_fileDragDropBrowseWidget

            }

            #Show first widget
            self.showWidgetWithID(1)


        except Exception as e : 
            self.display_exception("ERROR", [str(e)])








    '''

    Handling Navigation

    '''

    def showWidgetWithID(self, widgetID):

        #Loop through widgets in dict
        for widgetIndex in self._widgetDict :

            #Show the chosen widget
            if widgetIndex == str(widgetID) :
                self._widgetDict[widgetIndex].setVisible(True)
                continue

            #Hide the rest
            self._widgetDict[widgetIndex].setVisible(False)


    def autoModeSelected(self):
        self.showWidgetWithID(2)

    def manualModeSelected(self):
        self.showWidgetWithID(3)









    '''

    Global functions

    '''

    #Make the Finish button actually close the dialog
    def accept(self):

        #Add shotgun widget overlay
        try :

            #Try thread
            self._bgthread = AThread()
            self._bgthread.finished.connect(self.threadFinished)
            self._bgthread.start()

            self._overlay = overlay.ShotgunOverlayWidget(self)
            self._overlay.resize( 600, 350 )
            self._overlay.start_spin()

        except Exception as e : 
            self.display_exception("Error", [str(e)])

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