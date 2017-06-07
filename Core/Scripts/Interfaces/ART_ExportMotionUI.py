"""
Author: Jeremy Ernst
"""

# import statements
import json
import os
import subprocess
import tempfile
from functools import partial

import System.interfaceUtils as interfaceUtils
import System.utils as utils
import maya.cmds as cmds
from ThirdParty.Qt import QtGui, QtCore, QtWidgets


class ART_ExportMotion(object):
    """
    This class is used to export FBX animation from the rig to Unreal Engine. It supports morph targets,
    custom attribute curves, and pre/post scripts.

    It can be found on the animation sidebar with this icon:
        .. image:: /images/exportMotionButton.png

    .. todo:: Add the ability to export alembic and animation curve data.

    """

    def __init__(self, animPickerUI, parent=None):
        """
        Instantiates the class, getting the QSettings and calling on the function to build the interface.

        :param animPickerUI: Instance of the Animation UI from which this class was called.

        """

        super(ART_ExportMotion, self).__init__()

        # get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")
        self.scriptPath = settings.value("scriptPath")
        self.projectPath = settings.value("projectPath")

        self.pickerUI = animPickerUI

        # write out qss based on user settings
        stylesheetDir = utils.returnNicePath(self.scriptPath, "Interfaces/StyleSheets/")
        stylesheets = os.listdir(stylesheetDir)

        for sheet in stylesheets:
            interfaceUtils.writeQSS(os.path.join(stylesheetDir, sheet))

        # build the UI
        self.buildUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildUI(self):

        if cmds.window("pyART_ExportMotionWIN", exists=True):
            cmds.deleteUI("pyART_ExportMotionWIN", wnd=True)

        # create the main window
        self.mainWin = QtWidgets.QMainWindow(self.pickerUI)
        self.mainWin.resizeEvent = self.windowResized

        # create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWin.setCentralWidget(self.mainWidget)

        # create the mainLayout
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/animPicker.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.mainWin.setStyleSheet(self.style)

        self.mainWin.setMinimumSize(QtCore.QSize(470, 500))
        self.mainWin.setMaximumSize(QtCore.QSize(470, 900))
        self.mainWin.resize(470, 500)

        # set qt object name
        self.mainWin.setObjectName("pyART_ExportMotionWIN")
        self.mainWin.setWindowTitle("Export Motion")

        # tabs
        self.exportTabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.exportTabs)

        # style sheet
        stylesheet = """
        QTabBar::tab
        {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(19,132,183), stop:1 rgb(30,30,30));
            width: 100px;
            padding-left: -10px;
        }
        QTabBar::tab:selected
        {
            background-color: rgb(14,100,143);
            border: 2px solid black;
        }
        QTabBar::tab:hover
        {
            background: rgb(19,132,183);
        }
        QTabBar::tab:!selected
        {
            margin-top: 5px;
            border: 2px solid black;
        }
        QTabWidget::pane
        {
            border-top: 2px solid rgb(19,132,183);
            border-left: 2px solid rgb(19,132,183);
            border-right: 2px solid rgb(19,132,183);
            border-bottom: 2px solid rgb(19,132,183);
        }
        """

        stylesheet2 = """
        QTabBar::tab
        {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(19,132,183), stop:1 rgb(30,30,30));
            width: 140px;
            padding-left: -10px;
        }
        QTabBar::tab:selected
        {
            background-color: rgb(14,100,143);
            border: 2px solid black;
        }
        QTabBar::tab:hover
        {
            background: rgb(19,132,183);
        }
        QTabBar::tab:!selected
        {
            margin-top: 5px;
        }
        QTabWidget::pane
        {
            border-top: 2px solid rgb(255,175,25);
            border-left: 0px solid rgb(19,132,183);
            border-right: 0px solid rgb(19,132,183);
            border-bottom: 2px solid rgb(255,175,25);
        }
        """

        self.exportTabs.setStyleSheet(stylesheet)

        # FBX Tab
        self.fbxExportTab = QtWidgets.QWidget()
        self.exportTabs.addTab(self.fbxExportTab, "FBX")

        # ABC Tab
        self.abcExportTab = QtWidgets.QWidget()
        self.exportTabs.addTab(self.abcExportTab, "ABC")

        # Anim Curve Tab
        self.animExportTab = QtWidgets.QWidget()
        self.exportTabs.addTab(self.animExportTab, "Animation")

        # =======================================================================
        # =======================================================================
        # =======================================================================
        # =======================================================================
        # #FBX TAB
        # =======================================================================
        # =======================================================================
        # =======================================================================
        # =======================================================================
        self.fbxTabLayoutFrame = QtWidgets.QFrame(self.fbxExportTab)
        self.fbxTabLayoutFrame.setObjectName("dark")
        self.fbxTabLayoutFrame.setMinimumSize(450, 410)
        self.fbxTabLayoutFrame.setMaximumSize(450, 900)
        self.fbxTabLayoutFrame.setStyleSheet(self.style)

        self.fbxTabLayout = QtWidgets.QVBoxLayout(self.fbxTabLayoutFrame)

        # FBX Export Tabs
        self.fbxTabs = QtWidgets.QTabWidget()
        self.fbxTabLayout.addWidget(self.fbxTabs)

        self.fbxTabs.setStyleSheet(stylesheet2)

        # Settings Tab
        self.exportSettings = QtWidgets.QWidget()
        self.fbxTabs.addTab(self.exportSettings, "Export Settings")
        self.settingsTabLayout = QtWidgets.QVBoxLayout(self.exportSettings)

        # Anim Curve Tab
        self.sequencesTab = QtWidgets.QWidget()
        self.fbxTabs.addTab(self.sequencesTab, "Sequences")
        self.sequenceTabLayout = QtWidgets.QVBoxLayout(self.sequencesTab)

        # =======================================================================
        # =======================================================================
        # =======================================================================
        # # Export Settings
        # =======================================================================
        # =======================================================================
        # =======================================================================
        self.exportSettings = QtWidgets.QFrame()
        self.exportSettings.setObjectName("dark")
        self.exportSettings.setMinimumSize(QtCore.QSize(415, 330))
        self.exportSettings.setMaximumSize(QtCore.QSize(415, 900))
        self.settingsTabLayout.addWidget(self.exportSettings)

        self.settingsLayout = QtWidgets.QVBoxLayout(self.exportSettings)

        # export meshes checkbox
        self.exportMeshCB = QtWidgets.QCheckBox("Export Meshes")
        self.settingsLayout.addWidget(self.exportMeshCB)
        self.exportMeshCB.setChecked(True)

        # horizontal layout for morphs and custom attr curves
        self.settings_cb_layout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addLayout(self.settings_cb_layout)

        # export morphs and custom attr curves checkboxes
        self.exportMorphsCB = QtWidgets.QCheckBox("Export Morph Targets")
        self.settings_cb_layout.addWidget(self.exportMorphsCB)
        self.exportMorphsCB.setChecked(True)

        self.exportCustomAttrsCB = QtWidgets.QCheckBox("Export Custom Attribute Curves")
        self.settings_cb_layout.addWidget(self.exportCustomAttrsCB)
        self.exportCustomAttrsCB.setChecked(True)

        # horizontal layout for list widgets (morphs and custom attrs)
        self.settings_list_layout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addLayout(self.settings_list_layout)

        # list widgets for listing morphs and custom attr curves
        self.exportMorphList = QtWidgets.QListWidget()
        self.exportMorphList.setMinimumSize(QtCore.QSize(185, 150))
        self.exportMorphList.setMaximumSize(QtCore.QSize(185, 150))
        self.settings_list_layout.addWidget(self.exportMorphList)
        self.exportMorphList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.exportCurveList = QtWidgets.QListWidget()
        self.exportCurveList.setMinimumSize(QtCore.QSize(185, 150))
        self.exportCurveList.setMaximumSize(QtCore.QSize(185, 150))
        self.settings_list_layout.addWidget(self.exportCurveList)
        self.exportCurveList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # signal slots for checkboxes and lists
        self.exportMorphsCB.stateChanged.connect(partial(self.disableWidget, self.exportMorphList, self.exportMorphsCB))
        self.exportCustomAttrsCB.stateChanged.connect(
            partial(self.disableWidget, self.exportCurveList, self.exportCustomAttrsCB))
        self.exportMorphsCB.stateChanged.connect(self.exportMeshCB.setChecked)
        self.exportMeshCB.stateChanged.connect(self.exportMorphsCB.setChecked)

        # horizontal layout for pre-script
        self.preScript_layout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addLayout(self.preScript_layout)

        # pre-script checkbox, lineEdit, and button
        self.preScriptCB = QtWidgets.QCheckBox("Pre-Script: ")
        self.preScript_layout.addWidget(self.preScriptCB)

        self.preScript_path = QtWidgets.QLineEdit()
        self.preScript_layout.addWidget(self.preScript_path)

        ps_browseBtn = QtWidgets.QPushButton()
        ps_browseBtn.setMinimumSize(25, 25)
        ps_browseBtn.setMaximumSize(25, 25)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/fileBrowse.png"))
        ps_browseBtn.setIconSize(QtCore.QSize(25, 25))
        ps_browseBtn.setIcon(icon)
        ps_browseBtn.clicked.connect(partial(self.fileBrowse_script, self.preScript_path, self.preScriptCB))
        self.preScript_layout.addWidget(ps_browseBtn)

        # horizontal layout for post-script
        self.postScript_layout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addLayout(self.postScript_layout)

        # pre-script checkbox, lineEdit, and button
        self.postScriptCB = QtWidgets.QCheckBox("Post-Script: ")
        self.postScript_layout.addWidget(self.postScriptCB)

        self.postScript_path = QtWidgets.QLineEdit()
        self.postScript_layout.addWidget(self.postScript_path)

        pps_browseBtn = QtWidgets.QPushButton()
        pps_browseBtn.setMinimumSize(25, 25)
        pps_browseBtn.setMaximumSize(25, 25)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/fileBrowse.png"))
        pps_browseBtn.setIconSize(QtCore.QSize(25, 25))
        pps_browseBtn.setIcon(icon)
        pps_browseBtn.clicked.connect(partial(self.fileBrowse_script, self.postScript_path, self.postScriptCB))
        self.postScript_layout.addWidget(pps_browseBtn)

        # save settings button
        button = QtWidgets.QPushButton("Save Export Settings")
        self.settingsLayout.addWidget(button)
        button.clicked.connect(self.fbx_saveExportData)

        # spacer
        self.settingsLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        # =======================================================================
        # =======================================================================
        # =======================================================================
        # # FBX Sequences
        # =======================================================================
        # =======================================================================
        # =======================================================================

        # # Add Sequence
        self.addFbxAnimSequence = QtWidgets.QPushButton("Add Sequence")
        self.addFbxAnimSequence.setMinimumSize(QtCore.QSize(415, 50))
        self.addFbxAnimSequence.setMaximumSize(QtCore.QSize(415, 50))
        self.addFbxAnimSequence.setObjectName("blueButton")
        self.addFbxAnimSequence.clicked.connect(partial(self.fbx_addSequence))
        self.sequenceTabLayout.addWidget(self.addFbxAnimSequence)

        # #Main Export Section
        self.fbxAnimSequenceFrame = QtWidgets.QFrame()
        self.fbxAnimSequenceFrame.setMinimumWidth(415)
        self.fbxAnimSequenceFrame.setMaximumWidth(415)
        scrollSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.fbxAnimSequenceFrame.setSizePolicy(scrollSizePolicy)
        self.fbxAnimSequenceFrame.setObjectName("dark")

        self.fbxMainScroll = QtWidgets.QScrollArea()
        self.sequenceTabLayout.addWidget(self.fbxMainScroll)
        self.fbxMainScroll.setMinimumSize(QtCore.QSize(415, 280))
        self.fbxMainScroll.setMaximumSize(QtCore.QSize(415, 900))
        self.fbxMainScroll.setWidgetResizable(True)
        self.fbxMainScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.fbxMainScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.fbxMainScroll.setWidget(self.fbxAnimSequenceFrame)

        self.fbxSequenceLayout = QtWidgets.QVBoxLayout(self.fbxAnimSequenceFrame)
        self.fbxSequenceLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        # spacer
        self.sequenceTabLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        # =======================================================================
        # #export button
        # =======================================================================
        self.doFbxExportBtn = QtWidgets.QPushButton("Export")
        self.fbxTabLayout.addWidget(self.doFbxExportBtn)
        self.doFbxExportBtn.setObjectName("blueButton")
        self.doFbxExportBtn.setMinimumSize(QtCore.QSize(430, 40))
        self.doFbxExportBtn.setMaximumSize(QtCore.QSize(430, 40))
        self.doFbxExportBtn.clicked.connect(self.fbx_export)

        # show window
        self.mainWin.show()
        self.fbxTabs.setCurrentIndex(1)

        # find morphs
        self.findMorphs()

        # find custom curves
        self.findCustomCurves()

        # populate UI
        self.fbx_populateUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_checkExportMesh(self):

        if self.exportMorphsCB.isChecked():
            if not self.exportMeshCB.isChecked():
                self.exportMeshCB.setChecked(True)
                self.exportMeshCB.setEnabled(False)

        else:
            self.exportMeshCB.setEnabled(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_populateUI(self, refresh=False, *args):

        # remove existing animation sequences
        widgetsToRemove = []

        for i in range(self.fbxSequenceLayout.count()):
            child = self.fbxSequenceLayout.itemAt(i)
            if child is not None:
                if type(child.widget()) == QtWidgets.QGroupBox:
                    widgetsToRemove.append(child.widget())

        for widget in widgetsToRemove:
            self.fbx_removeAnimSequence(widget)

        # get characters in scene
        characters = []
        characterInfo = self.findCharacters()
        for info in characterInfo:
            characters.append(info[0])

        # check character nodes for fbxAnimData
        for currentChar in characters:
            # loop through data, adding sequences and setting settings
            if cmds.objExists(currentChar + ":ART_RIG_ROOT.fbxAnimData"):
                fbxData = json.loads(cmds.getAttr(currentChar + ":ART_RIG_ROOT.fbxAnimData"))

                # each entry in the fbxData list is a sequence with all the needed information
                for data in fbxData:

                    # first, set export settings
                    self.exportMeshCB.setChecked(data[0])
                    self.exportMorphsCB.setChecked(data[1])
                    self.exportCustomAttrsCB.setChecked(data[2])

                    # select morphs and curves to export in the lists if they exist
                    for i in range(self.exportMorphList.count()):
                        bShape = self.exportMorphList.item(i)
                        text = bShape.text()
                        if text in data[3]:
                            bShape.setSelected(True)

                    for i in range(self.exportCurveList.count()):
                        cCurve = self.exportCurveList.item(i)
                        text = cCurve.text()
                        if text in data[4]:
                            cCurve.setSelected(True)

                    # set pre/post script info
                    self.preScriptCB.setChecked(data[5][0])
                    self.preScript_path.setText(data[5][1])

                    self.postScriptCB.setChecked(data[6][0])
                    self.postScript_path.setText(data[6][1])

                    # add anim sequence
                    self.fbx_addSequence(data[7])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_addSequence(self, data=None):

        # get number of children of fbxSequenceLayout
        children = self.fbxSequenceLayout.count()
        index = children - 1

        # contained groupBox for each sequence
        groupBox = QtWidgets.QGroupBox()
        groupBox.setCheckable(True)
        groupBox.setMaximumHeight(260)
        groupBox.setMaximumWidth(380)
        self.fbxSequenceLayout.insertWidget(index, groupBox)

        # set context menu policy on groupbox
        groupBox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        groupBox.customContextMenuRequested.connect(partial(self.fbx_createContextMenu, groupBox))

        # add frame layout to groupbox
        frameLayout = QtWidgets.QVBoxLayout(groupBox)

        # add frame to groupbox
        frame = QtWidgets.QFrame()
        frame.setObjectName("light")
        frameLayout.addWidget(frame)

        vLayout = QtWidgets.QVBoxLayout(frame)
        vLayout.setObjectName("vLayout")

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(groupBox, QtCore.SIGNAL("toggled(bool)"), frame.setVisible)
        groupBox.setChecked(True)

        # =======================================================================
        # #portrait and character combo box
        # =======================================================================
        characterLayout = QtWidgets.QHBoxLayout()
        characterLayout.setObjectName("charLayout")
        vLayout.addLayout(characterLayout)

        portrait = QtWidgets.QLabel()
        portrait.setObjectName("charPortrait")
        portrait.setMinimumSize(QtCore.QSize(30, 30))
        portrait.setMaximumSize(QtCore.QSize(30, 30))
        characterLayout.addWidget(portrait)

        characterComboBox = QtWidgets.QComboBox()
        characterComboBox.setObjectName("charComboBox")
        characterComboBox.setMinimumHeight(30)
        characterComboBox.setMaximumHeight(30)
        characterLayout.addWidget(characterComboBox)

        # populate combo box
        characters = self.findCharacters()
        for character in characters:
            characterName = character[0]
            characterComboBox.addItem(characterName)
        self.updateIcon(characterComboBox, portrait, characters)
        characterComboBox.currentIndexChanged.connect(partial(self.updateIcon, characterComboBox, portrait, characters))

        # =======================================================================
        # #Checkbox, path, and browse button
        # =======================================================================
        pathLayout = QtWidgets.QHBoxLayout()
        pathLayout.setObjectName("pathLayout")
        vLayout.addLayout(pathLayout)

        checkBox = QtWidgets.QCheckBox()
        checkBox.setObjectName("exportCheckBox")
        checkBox.setChecked(True)
        pathLayout.addWidget(checkBox)

        pathField = QtWidgets.QLineEdit()
        pathField.setObjectName("exportPath")
        pathLayout.addWidget(pathField)
        pathField.setMinimumWidth(200)

        browseBtn = QtWidgets.QPushButton()
        browseBtn.setMinimumSize(25, 25)
        browseBtn.setMaximumSize(25, 25)
        pathLayout.addWidget(browseBtn)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/fileBrowse.png"))
        browseBtn.setIconSize(QtCore.QSize(25, 25))
        browseBtn.setIcon(icon)
        browseBtn.clicked.connect(partial(self.fileBrowse_export, pathField))

        # =======================================================================
        # #frame range, and frame rate
        # =======================================================================
        optionLayout = QtWidgets.QHBoxLayout()
        vLayout.addLayout(optionLayout)
        optionLayout.setObjectName("optionLayout")

        label1 = QtWidgets.QLabel("Start Frame: ")
        optionLayout.addWidget(label1)
        label1.setStyleSheet("background: transparent;")

        startFrame = QtWidgets.QSpinBox()
        startFrame.setObjectName("startFrame")
        optionLayout.addWidget(startFrame)
        startFrame.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        startFrame.setRange(-1000, 10000)

        label2 = QtWidgets.QLabel(" End Frame: ")
        optionLayout.addWidget(label2)
        label2.setStyleSheet("background: transparent;")
        label2.setAlignment(QtCore.Qt.AlignCenter)

        endFrame = QtWidgets.QSpinBox()
        endFrame.setObjectName("endFrame")
        optionLayout.addWidget(endFrame)
        endFrame.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        endFrame.setRange(-1000, 10000)

        # set frame range by default based on current timeline
        start = cmds.playbackOptions(q=True, ast=True)
        end = cmds.playbackOptions(q=True, aet=True)
        startFrame.setValue(start)
        endFrame.setValue(end)

        frameRate = QtWidgets.QComboBox()
        frameRate.setObjectName("frameRate")
        optionLayout.addWidget(frameRate)
        frameRate.hide()

        # add items to frame rate
        frameRate.addItem("ntsc")
        frameRate.addItem("ntscf")
        frameRate.addItem("film")

        # set the FPS to the current scene setting
        fps = cmds.currentUnit(q=True, time=True)
        if fps == "film":
            frameRate.setCurrentIndex(2)
        if fps == "ntsc":
            frameRate.setCurrentIndex(0)
        if fps == "ntscf":
            frameRate.setCurrentIndex(1)

        # =======================================================================
        # #advanced options
        # =======================================================================
        advancedGroup = QtWidgets.QGroupBox("Advanced Settings")
        vLayout.addWidget(advancedGroup)
        advancedGroup.setCheckable(True)

        advancedLayout = QtWidgets.QVBoxLayout(advancedGroup)
        advancedFrame = QtWidgets.QFrame()
        advancedLayout.addWidget(advancedFrame)
        advancedFrameLayout = QtWidgets.QVBoxLayout(advancedFrame)

        # =======================================================================
        # #rotation interpolation
        # =======================================================================
        interpLayout = QtWidgets.QHBoxLayout()
        advancedFrameLayout.addLayout(interpLayout)

        label3 = QtWidgets.QLabel("Rotation Interpolation: ")
        interpLayout.addWidget(label3)
        label3.setStyleSheet("background: transparent;")

        interpCombo = QtWidgets.QComboBox()
        interpLayout.addWidget(interpCombo)
        interpCombo.setObjectName("rotInterp")
        interpCombo.setMinimumWidth(150)

        interpCombo.addItem("Quaternion Slerp")
        interpCombo.addItem("Independent Euler-Angle")

        # =======================================================================
        # #sample rate and root options
        # =======================================================================
        rateRootLayout = QtWidgets.QHBoxLayout()
        advancedFrameLayout.addLayout(rateRootLayout)

        label4 = QtWidgets.QLabel("Sample Rate: ")
        rateRootLayout.addWidget(label4)

        sampleRate = QtWidgets.QDoubleSpinBox()
        sampleRate.setObjectName("sampleRate")
        rateRootLayout.addWidget(sampleRate)
        sampleRate.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        sampleRate.setRange(0, 1)
        sampleRate.setSingleStep(0.1)
        sampleRate.setValue(1.00)

        rootComboBox = QtWidgets.QComboBox()
        rootComboBox.setObjectName("rootExportOptions")
        rootComboBox.addItem("Export Root Animation")
        rootComboBox.addItem("Zero Root")
        rootComboBox.addItem("Zero Root, Keep World Space")
        rateRootLayout.addWidget(rootComboBox)

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(advancedGroup, QtCore.SIGNAL("toggled(bool)"), advancedFrame.setVisible)
        advancedGroup.setChecked(False)

        # signal slot for groupbox title
        characterComboBox.currentIndexChanged.connect(partial(self.fbx_updateTitle, groupBox))
        pathField.textChanged.connect(partial(self.fbx_updateTitle, groupBox))
        startFrame.valueChanged.connect(partial(self.fbx_updateTitle, groupBox))
        endFrame.valueChanged.connect(partial(self.fbx_updateTitle, groupBox))
        checkBox.stateChanged.connect(partial(self.fbx_updateTitle, groupBox))

        # create groupbox title
        self.fbx_updateTitle(groupBox)

        # set data if coming from duplicate call
        if data:

            # set character combo box
            for i in range(characterComboBox.count()):
                text = characterComboBox.itemText(i)
                if text == data[0]:
                    characterComboBox.setCurrentIndex(i)

            # set export checkbox
            checkBox.setChecked(data[1])

            # set export path
            pathField.setText(data[2])

            # set start frame
            startFrame.setValue(data[3])

            # set end frame
            endFrame.setValue(data[4])

            # set FPS
            for i in range(frameRate.count()):
                text = frameRate.itemText(i)
                if text == data[5]:
                    frameRate.setCurrentIndex(i)

            # set rotation interpolation
            for i in range(interpCombo.count()):
                text = interpCombo.itemText(i)
                if text == data[6]:
                    interpCombo.setCurrentIndex(i)

            # set sample rate
            sampleRate.setValue(data[7])

            # set root export
            for i in range(rootComboBox.count()):
                text = rootComboBox.itemText(i)
                if text == data[8]:
                    rootComboBox.setCurrentIndex(i)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_createContextMenu(self, widget, point):

        # icons
        icon_delete = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/delete.png"))
        icon_duplicate = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/duplicate.png"))
        icon_collapse = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/upArrow.png"))
        icon_expand = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/downArrow.png"))

        # create the context menu
        contextMenu = QtWidgets.QMenu()
        contextMenu.addAction(icon_delete, "Remove Sequence", partial(self.fbx_removeAnimSequence, widget))
        contextMenu.addAction(icon_duplicate, "Duplicate Sequence", partial(self.fbx_duplicateSequence, widget))
        contextMenu.addAction(icon_expand, "Expand All Sequences", partial(self.fbx_expandAllSequences, True))
        contextMenu.addAction(icon_collapse, "Collapse All Sequences", partial(self.fbx_expandAllSequences, False))
        contextMenu.exec_(widget.mapToGlobal(point))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_removeAnimSequence(self, widget):

        widget.setParent(None)
        widget.close()
        self.fbx_saveExportData()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_duplicateSequence(self, widget):

        sequenceData = self.fbx_getSequenceInfo(widget)
        self.fbx_addSequence(sequenceData)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fileBrowse_export(self, widget):

        try:
            path = cmds.fileDialog2(fm=0, okc="Export", dir=self.projectPath, ff="*.fbx")
            nicePath = utils.returnFriendlyPath(path[0])
            widget.setText(nicePath)
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fileBrowse_script(self, widget, checkbox=None):

        try:
            path = cmds.fileDialog2(fm=1, okc="Accept", dir=self.projectPath, ff="*.py;;*.mel")
            nicePath = utils.returnFriendlyPath(path[0])
            widget.setText(nicePath)

            if checkbox is not None:
                checkbox.setChecked(True)
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_export(self):

        # save settings
        characterData = self.fbx_saveExportData()

        # find mayapy interpreter location
        mayapy = utils.getMayaPyLoc()

        # message box for confirming save action
        msgBax = QtWidgets.QMessageBox()
        msgBax.setText("Please make sure any changes to the current file are saved before continuing.\
        This process will be creating a temporary file to do all of the exporting from.")
        msgBax.setIcon(QtWidgets.QMessageBox.Warning)
        msgBax.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBax.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBax.exec_()

        if ret == QtWidgets.QMessageBox.Ok:

            # save copy of scene to temp location
            sourceFile = cmds.file(q=True, sceneName=True)
            filePath = os.path.dirname(sourceFile)
            tempFile = os.path.join(filePath, "export_TEMP.ma")

            cmds.file(rename=tempFile)
            cmds.file(save=True, type="mayaAscii", force=True)

            # pass tempFile and characterData to mayapy instance for processing
            if os.path.exists(mayapy):
                script = utils.returnFriendlyPath(os.path.join(self.toolsPath, "Core\Scripts\System\ART_FbxExport.py"))

                # create a temp file with the json data
                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    json.dump(characterData, temp)
                    temp.close()

                # create a log file
                stdoutFile = os.path.join(filePath, "export_log.txt")
                out = file(stdoutFile, 'w')

                # open mayapy, passing in export file and character data
                subprocess.Popen(mayapy + ' ' + "\"" + script + "\"" + ' ' + "\"" + tempFile + "\"" + ' ' +
                                 "\"" + temp.name + "\"", stdout=out, stderr=out)

                # close the output file (for logging)
                out.close()

            else:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText("mayapy executable not found. Currently not implemented for mac and linux.")
                msgBox.setIcon(QtWidgets.QMessageBox.Error)
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
                msgBox.exec_()

            # reopen the original file
            cmds.file(sourceFile, open=True, force=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findMorphs(self):

        # clear list
        self.exportMorphList.clear()
        characterMeshes = []

        # get all characters
        characters = self.findCharacters()

        for character in characters:
            currentCharacter = character[0]

            # get meshes off of character node
            if cmds.objExists(currentCharacter + ":ART_RIG_ROOT"):
                if cmds.objExists(currentCharacter + ":ART_RIG_ROOT.LOD_0_Meshes"):
                    characterMeshes = cmds.listConnections(currentCharacter + ":ART_RIG_ROOT.LOD_0_Meshes")

            # get skinClusters in scene and query their connections
            skins = cmds.ls(type="skinCluster")

            for skin in skins:
                shapeInfo = cmds.listConnections(skin, c=True, type="blendShape", et=True)
                mesh = cmds.listConnections(skin, type="mesh")

                if mesh is not None:
                    # confirm that the blendshape found belongs to one of our character meshes. Then add to list
                    if mesh[0] in characterMeshes:
                        if shapeInfo is not None:
                            for info in shapeInfo:
                                if cmds.nodeType(info) == "blendShape":
                                    item = QtWidgets.QListWidgetItem(info)
                                    self.exportMorphList.addItem(item)
                                    item.setSelected(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCustomCurves(self):

        # get all characters
        characters = self.findCharacters()

        for character in characters:
            currentCharacter = character[0]
            rootBone = currentCharacter + ":root"
            attrs = cmds.listAttr(rootBone, keyable=True)

            standardAttrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ",
                             "scaleX", "scaleY", "scaleZ", "visibility"]

            for attr in attrs:
                if attr not in standardAttrs:
                    item = QtWidgets.QListWidgetItem(currentCharacter + ":" + attr)
                    self.exportCurveList.addItem(item)
                    item.setSelected(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCharacters(self):

        characterInfo = []

        allNodes = cmds.ls(type="network")
        characterNodes = []
        for node in allNodes:
            attrs = cmds.listAttr(node)
            if "rigModules" in attrs:
                characterNodes.append(node)

        # go through each node, find the character name, the namespace on the node, and the picker attribute
        for node in characterNodes:
            try:
                namespace = cmds.getAttr(node + ".namespace")
            except:
                namespace = cmds.getAttr(node + ".name")

            # add the icon found on the node's icon path attribute to the tab
            iconPath = cmds.getAttr(node + ".iconPath")
            iconPath = utils.returnNicePath(self.projectPath, iconPath)

            characterInfo.append([namespace, iconPath])

        return characterInfo

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateIcon(self, comboBox, label, characterInfo, *args):

        # get current selection of combo box
        characterName = comboBox.currentText()

        # loop through characterInfo, find matching characterName, and get icon path
        for each in characterInfo:
            if characterName == each[0]:
                iconPath = each[1]
                img = QtGui.QImage(iconPath)
                pixmap = QtGui.QPixmap(img.scaledToWidth(30))
                label.setPixmap(pixmap)
                label.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def windowResized(self, event):

        currentSize = self.mainWin.size()
        height = currentSize.height()

        self.fbxTabLayoutFrame.resize(450, height - 50)

        width = self.fbxTabs.size()
        width = width.width()
        self.fbxTabs.resize(width, height - 50)
        self.fbxMainScroll.setMinimumSize(415, height - 220)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def disableWidget(self, widget, checkbox, *args):

        state = checkbox.isChecked()
        if state:
            widget.setEnabled(True)
            for i in range(widget.count()):
                item = widget.item(i)
                item.setHidden(False)
        else:
            widget.setEnabled(False)
            for i in range(widget.count()):
                item = widget.item(i)
                item.setHidden(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_updateTitle(self, groupBox, *args):

        # get info from interface
        data = []
        children = groupBox.children()
        for each in children:
            if type(each) == QtWidgets.QFrame:
                contents = each.children()

                for child in contents:
                    objectName = child.objectName()

                    if objectName == "charComboBox":
                        char = child.currentText()
                        data.append(char)

                    if objectName == "exportCheckBox":
                        value = child.isChecked()
                        data.append(value)

                    if objectName == "exportPath":
                        path = child.text()
                        filename = os.path.basename(path)
                        data.append(filename.partition(".")[0])

                    if objectName == "startFrame":
                        startFrame = child.value()
                        data.append(startFrame)

                    if objectName == "endFrame":
                        endFrame = child.value()
                        data.append(endFrame)

        titleString = ""
        if data[1]:
            titleString += data[0] + ", "
            titleString += data[2] + ", "
            titleString += "["
            titleString += str(data[3]) + ": "
            titleString += str(data[4]) + "]"
        else:
            titleString += "Not Exporting.."
        groupBox.setTitle(titleString)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_saveExportData(self):

        exportData = []

        # get main export settings
        exportMesh = self.exportMeshCB.isChecked()
        exportMorph = self.exportMorphsCB.isChecked()
        exportCurve = self.exportCustomAttrsCB.isChecked()

        exportData.append(exportMesh)
        exportData.append(exportMorph)
        exportData.append(exportCurve)

        # get selected morphs
        morphs = []
        for i in range(self.exportMorphList.count()):
            item = self.exportMorphList.item(i)
            if item.isSelected():
                morphs.append(item.text())

        # get selected curves
        curves = []
        for i in range(self.exportCurveList.count()):
            item = self.exportCurveList.item(i)
            if item.isSelected():
                curves.append(item.text())

        # pre and post script
        preScript = self.preScriptCB.isChecked()
        preScript_path = self.preScript_path.text()

        postScript = self.postScriptCB.isChecked()
        postScript_path = self.postScript_path.text()

        exportData.append(morphs)
        exportData.append(curves)
        exportData.append([preScript, preScript_path])
        exportData.append([postScript, postScript_path])

        # get fbx sequences and settings
        characterData = {}
        for i in range(self.fbxSequenceLayout.count()):
            child = self.fbxSequenceLayout.itemAt(i)
            if type(child.widget()) == QtWidgets.QGroupBox:
                data = []
                sequenceData = self.fbx_getSequenceInfo(child.widget())
                data.extend(exportData)
                data.append(sequenceData)

                if sequenceData[0] not in characterData:
                    characterData[sequenceData[0]] = [data]
                else:
                    currentData = characterData.get(sequenceData[0])
                    currentData.append(data)
                    characterData[sequenceData[0]] = currentData

        # loop through each key (character) in the dictionary, and write its data to the network node
        for each in characterData:
            data = characterData.get(each)

            # Add that data to the character node
            networkNode = each + ":ART_RIG_ROOT"
            if not cmds.objExists(networkNode + ".fbxAnimData"):
                cmds.addAttr(networkNode, ln="fbxAnimData", dt="string")

            cmds.setAttr(networkNode + ".fbxAnimData", json.dumps(data), type="string")

        return characterData

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_getSequenceInfo(self, groupBox, *args):

        # get info from interface
        data = []

        children = groupBox.children()
        for each in children:
            if type(each) == QtWidgets.QFrame:
                contents = each.children()

                for child in contents:
                    objectName = child.objectName()

                    if objectName == "charComboBox":
                        char = child.currentText()
                        data.append(char)

                    if objectName == "exportCheckBox":
                        value = child.isChecked()
                        data.append(value)

                    if objectName == "exportPath":
                        path = child.text()
                        data.append(path)

                    if objectName == "startFrame":
                        startFrame = child.value()
                        data.append(startFrame)

                    if objectName == "endFrame":
                        endFrame = child.value()
                        data.append(endFrame)

                    if objectName == "frameRate":
                        fps = child.currentText()
                        data.append(fps)

                    if type(child) == QtWidgets.QGroupBox:
                        subChildren = child.children()

                        for sub in subChildren:
                            if type(sub) == QtWidgets.QFrame:
                                advancedChildren = sub.children()
                                for advancedChild in advancedChildren:
                                    advancedObj = advancedChild.objectName()

                                    if advancedObj == "sampleRate":
                                        rate = advancedChild.value()
                                        data.append(rate)

                                    if advancedObj == "rotInterp":
                                        interp = advancedChild.currentText()
                                        data.append(interp)

                                    if advancedObj == "rootExportOptions":
                                        root = advancedChild.currentText()
                                        data.append(root)

        return data

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbx_expandAllSequences(self, state):

        # get info from interface
        for i in range(self.fbxSequenceLayout.count()):
            data = []
            child = self.fbxSequenceLayout.itemAt(i)
            if type(child.widget()) == QtWidgets.QGroupBox:
                child.widget().setChecked(state)
