# coding=utf-8
"""
Author: Jeremy Ernst
"""

import os
from functools import partial

import System.interfaceUtils as interfaceUtils
import System.utils as utils
import maya.cmds as cmds
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# maya 2016< maya2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken


def getMainWindow():

    """
    Get Maya’s window as a QWidget and return the item in memory.

    :return: a QWidget of Maya’s window

    """

    import maya.OpenMayaUI as mui
    pointer = mui.MQtUtil.mainWindow()
    # pyside QMainWindow takes in a QWidget rather than QObject
    return shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)


windowTitle = "Edit Rig"
windowObject = "pyArtEditRigWin"


class ART_EditRigUI(QtWidgets.QMainWindow):
    """
    This class builds a tool that allows a user to Edit a Rig or Add Character for Animation. Both functions use the
    same interface. The title and button text get swapped out depending on which situation has been called for by
    the A.R.T.2.0 menu.

        .. image:: /images/editRig.png

    """

    def __init__(self, edit, add, parent=None):
        """
        Instantiates the class, getting the QSettings and building the interface.

        :param edit: Whether or not the operation is to edit the rig.
        :param add: Whether or not the operation is to add the character for animation.

        """

        super(ART_EditRigUI, self).__init__(parent)
        self.edit = edit
        self.add = add

        # get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")
        self.scriptPath = settings.value("scriptPath")
        self.projectPath = settings.value("projectPath")

        # build the UI
        self.createUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createUI(self):
        """
        Builds the UI, listing options for choosing a project and showing all assets belonging to that project for
        edit or add.

        """

        # fonts
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        fontSmall = QtGui.QFont()
        fontSmall.setPointSize(9)
        fontSmall.setBold(True)

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.setStyleSheet(self.style)
        # size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # =======================================================================
        # #create the main widget
        # =======================================================================
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        # set qt object name
        self.setObjectName(windowObject)
        if self.edit:
            self.setWindowTitle(windowTitle)
        if self.add:
            self.setWindowTitle("Add Rig For Animation")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # create the mainLayout
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.resize(400, 400)
        self.setSizePolicy(mainSizePolicy)
        self.setMinimumSize(QtCore.QSize(400, 400))
        self.setMaximumSize(QtCore.QSize(400, 400))

        # create the QFrame
        self.frame = QtWidgets.QFrame()
        self.layout.addWidget(self.frame)
        self.widgetLayout = QtWidgets.QHBoxLayout(self.frame)
        self.frame.setObjectName("mid")

        # =======================================================================
        # #create two VBox Layouts to create 2 columns
        # =======================================================================
        self.leftColumn = QtWidgets.QVBoxLayout()
        self.widgetLayout.addLayout(self.leftColumn)

        self.rightColumn = QtWidgets.QVBoxLayout()
        self.widgetLayout.addLayout(self.rightColumn)

        # =======================================================================
        # #left column : project comboBox, group comboBox, listWidget of characters
        # =======================================================================

        self.projectMenu = QtWidgets.QComboBox()
        self.leftColumn.addWidget(self.projectMenu)
        self.projectMenu.setMinimumSize(150, 30)
        self.projectMenu.setMaximumSize(150, 30)
        self.projectMenu.currentIndexChanged.connect(self.populateGroups)

        self.groupMenu = QtWidgets.QComboBox()
        self.leftColumn.addWidget(self.groupMenu)
        self.groupMenu.setMinimumSize(150, 30)
        self.groupMenu.setMaximumSize(150, 30)
        self.groupMenu.currentIndexChanged.connect(self.populateCharacters)

        self.characterList = QtWidgets.QListWidget()
        self.leftColumn.addWidget(self.characterList)
        self.characterList.setMinimumSize(150, 200)
        self.characterList.setMaximumSize(150, 200)
        self.characterList.itemClicked.connect(partial(self.populateIcon))
        self.populateProjects()
        # =======================================================================
        # #right column: icon frame, edit button/add button, close button
        # =======================================================================

        self.characterIcon = QtWidgets.QLabel()
        self.characterIcon.setMinimumSize(200, 200)
        self.characterIcon.setMaximumSize(200, 200)
        self.rightColumn.addWidget(self.characterIcon)

        # default image
        self.defaultPixMap = QtGui.QPixmap(utils.returnNicePath(self.iconsPath, "System/noCharacter.png"))
        self.characterIcon.setPixmap(self.defaultPixMap)

        # if edit:
        if self.edit:
            self.editButton = QtWidgets.QPushButton("Edit Selected")
            self.editButton.setFont(font)
            self.rightColumn.addWidget(self.editButton)
            self.editButton.setMinimumSize(200, 40)
            self.editButton.setMaximumSize(200, 40)
            self.editButton.clicked.connect(partial(self.editSelected))
            self.editButton.setObjectName("blueButton")

        # if add:
        if self.add:
            self.addButton = QtWidgets.QPushButton("Add Selected")
            self.addButton.setFont(font)
            self.rightColumn.addWidget(self.addButton)
            self.addButton.setMinimumSize(200, 40)
            self.addButton.setMaximumSize(200, 40)
            self.addButton.clicked.connect(partial(self.addSelected))
            self.addButton.setObjectName("blueButton")

        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.setFont(font)
        self.rightColumn.addWidget(self.closeButton)
        self.closeButton.setMinimumSize(200, 40)
        self.closeButton.setMaximumSize(200, 40)
        self.closeButton.clicked.connect(partial(self.closeUI))
        self.closeButton.setObjectName("blueButton")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateProjects(self):
        """
        Find all projects on disk (using the project path setting) and add each project to the QComboBox. Then,
        call on populateGroups.

        .. seealso:: ART_EditRigUI.populateGroups()

        """

        # if the project path doesn't exist on disk, create it
        if not os.path.exists(self.projectPath):
            os.makedirs(self.projectPath)

        # get a list of the existing folders in projects
        existingProjects = os.listdir(self.projectPath)
        folders = []

        # find out which returned items are directories
        for each in existingProjects:
            if os.path.isdir(os.path.join(self.projectPath, each)):
                folders.append(each)

        # add each project to the combo box
        self.projectMenu.clear()
        for each in folders:
            self.projectMenu.addItem(each)

        # find selected project and populate groups
        self.populateGroups()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateGroups(self):
        """
        Given the selected project, populate any groups for that project (using the project path from QSettings) and
        add them to the groups QComboBox.

        Then, call on populateCharacters.

        .. seealso:: ART_EditRigUI.populateCharacters()

        """

        # get a list of the existing folders in projects
        selectedProject = self.projectMenu.currentText()
        project = os.path.join(self.projectPath, selectedProject)
        existingGroups = os.listdir(project)
        folders = []

        # find out which returned items are directories
        for each in existingGroups:
            if os.path.isdir(os.path.join(project, each)):
                folders.append(each)

        # otherwise, add each project to the combo box
        self.groupMenu.clear()
        self.groupMenu.addItem(" ")
        for each in folders:
            self.groupMenu.addItem(each)

        # populate characters
        self.populateCharacters()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateCharacters(self):
        """
        Given the selected project and group, populate the QListWidget with any assets found using that information.
        The project path comes from the QSettings, the group is a subfolder of the project.

        """

        # add project button
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        # get a list of the existing folders in projects
        selectedProject = self.projectMenu.currentText()
        fullPath = os.path.join(self.projectPath, selectedProject)
        selectedGroup = self.groupMenu.currentText()
        if len(selectedGroup) > 1:
            fullPath = os.path.join(fullPath, selectedGroup)

        existingCharacters = os.listdir(fullPath)
        files = []

        # find out which returned items are directories
        for each in existingCharacters:
            if os.path.isfile(os.path.join(fullPath, each)):
                if each.rpartition(".")[2] == "ma":
                    files.append(each)

        # otherwise, add each project to the combo box
        self.characterList.clear()

        for each in files:
            item = QtWidgets.QListWidgetItem(each.partition(".ma")[0])
            item.setFont(font)
            self.characterList.addItem(item)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateIcon(self, *args):
        """
        Given the selected character, display the correct icon for that character in the UI.

        """

        # default
        self.characterIcon.setPixmap(self.defaultPixMap)

        # get a list of the existing folders in projects
        selectedProject = self.projectMenu.currentText()
        fullPath = utils.returnNicePath(self.projectPath, selectedProject)
        selectedGroup = self.groupMenu.currentText()
        if len(selectedGroup) > 1:
            fullPath = utils.returnNicePath(fullPath, selectedGroup)

        selectedCharacter = self.characterList.currentItem().text()
        fullPath = utils.returnNicePath(fullPath, selectedCharacter + ".png")

        if os.path.exists(fullPath):
            pixmap = QtGui.QPixmap(fullPath)
            self.characterIcon.setPixmap(pixmap)

        else:
            self.characterIcon.setPixmap(self.defaultPixMap)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editSelected(self, *args):
        """
        Find the selected character, and open that file for edit. The path is constructed using the QSettings info,
        with any group as a subfolder, and lastly the selected asset/character as the last part of the path.

        """

        # get a list of the existing folders in projects
        selectedProject = self.projectMenu.currentText()
        fullPath = utils.returnNicePath(self.projectPath, selectedProject)
        selectedGroup = self.groupMenu.currentText()
        if len(selectedGroup) > 1:
            fullPath = utils.returnNicePath(fullPath, selectedGroup)

        selectedCharacter = self.characterList.currentItem().text()
        mayaFile = utils.returnNicePath(fullPath, selectedCharacter + ".ma")
        iconFile = utils.returnNicePath(fullPath, selectedCharacter + ".png")

        if os.path.exists(mayaFile):
            if os.path.exists(iconFile):
                launchUI = False

                # get current file
                currentFile = cmds.file(q=True, sceneName=True)
                if cmds.file(currentFile, q=True, modified=True) == True:
                    proceed = self.unsavedChanges(currentFile)

                    if proceed == 0:
                        cmds.file(save=True, force=True)
                        cmds.file(mayaFile, open=True, prompt=True, options="v=0", ignoreVersion=True, typ="mayaAscii",
                                  f=True)
                        launchUI = True

                    if proceed == 1:
                        cmds.file(mayaFile, open=True, prompt=True, options="v=0", ignoreVersion=True, typ="mayaAscii",
                                  f=True)
                        launchUI = True

                    if proceed == 2:
                        return
                else:
                    cmds.file(mayaFile, open=True, prompt=True, options="v=0", ignoreVersion=True, typ="mayaAscii",
                              f=True)
                    launchUI = True

        if launchUI:
            import Interfaces.ART_RigCreatorUI as ART_RigCreatorUI
            reload(ART_RigCreatorUI)
            ART_RigCreatorUI.createUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addSelected(self, *args):
        """
        Finds the selected character, and references that file into the currently opened scene. The path is
        constructed using the QSettings info, with any group as a subfolder, and lastly the selected asset/character
        as the last part of the path.

        Also handles namespaces, adding the new namespace to the network node of the added asset, and launches the
        animationUI.

        """

        # get a list of the existing folders in projects
        selectedProject = self.projectMenu.currentText()
        fullPath = utils.returnNicePath(self.projectPath, selectedProject)
        selectedGroup = self.groupMenu.currentText()
        if len(selectedGroup) > 1:
            fullPath = utils.returnNicePath(fullPath, selectedGroup)

        selectedCharacter = self.characterList.currentItem().text()
        mayaFile = utils.returnNicePath(fullPath, selectedCharacter + ".ma")
        iconFile = utils.returnNicePath(fullPath, selectedCharacter + ".png")

        # reference in the selected character if the file exists on drive
        if os.path.exists(mayaFile):
            if os.path.exists(iconFile):

                # find existing namespaces in scene
                namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)

                # reference the rig file
                cmds.file(mayaFile, r=True, type="mayaAscii", loadReferenceDepth="all", namespace=selectedCharacter,
                          options="v=0")

                # clear selection and fit view
                cmds.select(clear=True)
                cmds.viewFit()
                panels = cmds.getPanel(type='modelPanel')

                # turn on smooth shading
                for panel in panels:
                    editor = cmds.modelPanel(panel, q=True, modelEditor=True)
                    cmds.modelEditor(editor, edit=True, displayAppearance="smoothShaded", displayTextures=True,
                                     textures=True)

                # find new namespaces in scene to figure out the namespace that was created upon referencing the
                # character
                newCharacterName = selectedCharacter
                newNamespaces = cmds.namespaceInfo(listOnlyNamespaces=True)

                for name in newNamespaces:
                    if name not in namespaces:
                        newCharacterName = name

                # add an attribute to the rig root (if needed) and set the namespace attr to the newCharacterName
                if cmds.objExists(newCharacterName + ":ART_RIG_ROOT"):
                    if not cmds.objExists(newCharacterName + ":ART_RIG_ROOT.namespace"):
                        cmds.addAttr(newCharacterName + ":ART_RIG_ROOT", ln="namespace", dt="string", keyable=False)

                    cmds.setAttr(newCharacterName + ":ART_RIG_ROOT.namespace", newCharacterName, type="string")

                # delete any interfaces that may be up
                self.closeUI()

                if cmds.dockControl("pyArtRigCreatorDock", q=True, exists=True):
                    if cmds.window("pyArtRigCreatorUi", exists=True):
                        cmds.deleteUI("pyArtRigCreatorUi", wnd=True)
                    cmds.deleteUI("pyArtRigCreatorDock", control=True)

        # launch anim UI
        cmds.refresh(force=True)

        stylesheetDir = utils.returnNicePath(self.scriptPath, "Interfaces/StyleSheets/")
        stylesheets = os.listdir(stylesheetDir)
        for sheet in stylesheets:
            interfaceUtils.writeQSS(os.path.join(stylesheetDir, sheet))

        import Interfaces.ART_AnimationUI as ART_AnimationUI
        ART_AnimationUI.run()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def unsavedChanges(self, path):
        """
        Displays a message box that warns the user of unsaved file changed and returns their response.

        :return: Returns the user response (Save, Don't Save, Cancel)

        """

        # message box for letting user know current file has unsaved changes
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("Current File Has Unsaved Changes!")
        msgBox.addButton("Save Changes", QtWidgets.QMessageBox.YesRole)
        msgBox.addButton("Don't Save", QtWidgets.QMessageBox.NoRole)
        msgBox.addButton("Cancel", QtWidgets.QMessageBox.NoRole)
        ret = msgBox.exec_()

        return ret

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def closeUI(self):
        """
        Closes and deletes the interface for the class.

        """

        if cmds.window("pyArtEditRigWin", exists=True):
            cmds.deleteUI("pyArtEditRigWin", wnd=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def run():
    """
    Creates an instance of the class for Editing a rig. The ARTv2 menu calls on this function.

    """

    if cmds.window("pyArtEditRigWin", exists=True):
        cmds.deleteUI("pyArtEditRigWin", wnd=True)

    gui = ART_EditRigUI(True, False, getMainWindow())
    gui.show()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def runAdd():
    """
    Creates an instance of the class for adding a rig for animation. The artv2 menu calls this function.

    """

    if cmds.window("pyArtEditRigWin", exists=True):
        cmds.deleteUI("pyArtEditRigWin", wnd=True)

    gui = ART_EditRigUI(False, True, getMainWindow())
    gui.show()
