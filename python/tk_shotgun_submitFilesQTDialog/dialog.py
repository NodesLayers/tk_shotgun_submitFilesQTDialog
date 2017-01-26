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
import urlparse
import re
import logging
import logging.handlers

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

#Dialog
from .ui.dialog import Ui_Dialog


def show_dialog(app_instance, entity_type=None, entity_ids=None):
    """
    Shows the main dialog window.
    
    :param entity_type: A Shotgun entity type, e.g. "Shot"
    :param entity_ids: A list of Shotgun entity ids, possibly empty
    """
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Submit Files to Shotgun", app_instance, AppDialog)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    # Our own threadpool instance shared between app instances in the same engine
    __thread_pool = QtCore.QThreadPool()

    def __init__(self):
        """
        Build the app main window.
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        #Load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        # self.display_exception("Context", [str(self._app.context)])

        # Close the dialog when asked to do it
        # self.ui.button_box.rejected.connect(self.close_dialog)

        #Set the entity label
        context = self._app.context
        self.ui.entityLabel.setText("You clicked on %s %s" % (context.entity['type'], context.entity['name']))

        #Set ok 
        # buttons = self.ui.button_box.buttons()
        # self._ok_button = buttons[0]
        # self._ok_button.setText("OK")
        # self._ok_button.clicked.connect(self.okPressed)

        #Set custom style
        self.set_custom_style()

    @QtCore.Slot()
    def okPressed(self):
        self.close()
        self.display_exception("That worked!", ["You don't need to do anything.", "It worked!"])

    @QtCore.Slot(str, list)
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
        # Fall back to base class implementation
        super(AppDialog, self).keyPressEvent(evt)


    @QtCore.Slot()
    def close_dialog(self):
        """
        Shutdown the dialog
        """
        self.close()


    # CSS

    def set_custom_style(self):
        """
        Append our custom style to the inherited style sheet
        """
        self._css_watcher=None
        this_folder = self._app.disk_location #os.path.abspath(os.path.dirname(__file__))
        css_file = os.path.join(this_folder, "style.qss")
        if os.path.exists(css_file):
            self._load_css(css_file)

    def _load_css(self, css_file):
        """
        Load the given css file

        If css file watching was enabled, ensure the file is still in watched
        files list

        :param css_file: Full path to a css file
        """
        self.setStyleSheet("")
        if os.path.exists(css_file):
            # Re-attach a watcher everytime the file is changed, otherwise it
            # seems the watcher is run only once ? Might be that some editors
            # rename the edited file so the watcher thinks it went away
            if self._css_watcher and css_file not in self._css_watcher.files():
                self._css_watcher.addPath(css_file)
            try:
                # Read css file
                f = open(css_file)
                css_data = f.read()
                # Append our add ons to current sytle sheet at the top widget
                # level, children will inherit from it, without us affecting
                # other apps for this engine
                self.setStyleSheet(css_data)
            except Exception,e:
                self._app.log_warning( "Unable to read style sheet %s" % css_file )
            finally:
                f.close()