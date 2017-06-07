# standard imports
import json
import os
from functools import partial

import maya.OpenMayaUI as mui
import maya.cmds as cmds

from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# maya 2016< maya2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken

# external imports
import System.utils as utils
import System.riggingUtils as riggingUtils
from System.ART_RigModule import ART_RigModule
from RigModules.ART_Root import ART_Root
import System.interfaceUtils as interfaceUtils

windowTitle = "Rig_Creator"
windowObject = "pyArtRigCreatorUi"


class ART_RigCreator_UI(QtWidgets.QMainWindow):
    # Original Author: Jeremy Ernst

    def __init__(self, parent=None):

        super(ART_RigCreator_UI, self).__init__(parent)

        # clean up script jobs
        jobs = cmds.scriptJob(lj=True)
        for job in jobs:
            if job.find("ART_") != -1:
                jobNum = int(job.partition(":")[0])
                cmds.scriptJob(kill=jobNum, force=True)

        # get settings
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.scriptPath = settings.value("scriptPath")
        self.iconsPath = settings.value("iconPath")

        # create a few lists/dicts to store info
        self.outlinerWidgets = {}
        self.outlinerControls = []

        # this list will store module instances created by this UI or by any sub-UIs (like addModuleUI)
        self.moduleInstances = []
        self.scriptJobs = []
        self.boneCounterInst = None

        # build the UI
        self.buildUI()

        # tooltip style sheet
        # write out qss based on user settings
        stylesheetDir = utils.returnNicePath(self.scriptPath, "Interfaces/StyleSheets/")
        stylesheets = os.listdir(stylesheetDir)

        for sheet in stylesheets:
            interfaceUtils.writeQSS(os.path.join(stylesheetDir, sheet))

        # check to see if the root of our rig network exists
        exists = False
        networkNodes = cmds.ls(type="network")
        for node in networkNodes:
            attrs = cmds.listAttr(node)

            if "rigModules" in attrs:
                exists = True

        # if the root of the rig network did not exist, create it now as well as our root module

        if exists == False:

            self.rigRootMod = ART_RigModule("ART_RIG_ROOT", None, None)
            self.rigRootMod.buildNetwork()

            # create a root module
            self.rootMod = ART_Root(self, "root")
            self.rootMod.buildNetwork()
            self.rootMod.skeletonSettings_UI("Root")
            self.rootMod.jointMover_Build("Core/JointMover/ART_Root.ma")
            self.rootMod.addJointMoverToOutliner()
            self.moduleInstances.append(self.rootMod)



        # if module node network existed, create UI elements and do not create any new network nodes
        else:
            modules = utils.returnRigModules()

            for module in modules:
                modType = cmds.getAttr(module + ".moduleType")
                modName = cmds.getAttr(module + ".moduleName")
                mod = __import__("RigModules." + modType, {}, {}, [modType])
                reload(mod)

                # get the class name from that module file (returns Modules.ART_Root.ART_Root for example)
                moduleClass = getattr(mod, mod.className)

                # find the instance of that module and call on the skeletonSettings_UI function
                moduleInst = moduleClass(self, modName)
                moduleInst.skeletonSettings_UI(modName)
                moduleInst.addJointMoverToOutliner()

                self.moduleInstances.append(moduleInst)

        # run toggleMoverVisibility
        self.setMoverVisibility()

        # clear selection
        cmds.select(clear=True)

        # unisolate selection if needed
        try:
            isoPnl = cmds.getPanel(wf=True)
            isoCrnt = cmds.isolateSelect(isoPnl, q=True, s=True)
            if isoCrnt:
                cmds.isolateSelect(isoPnl, s=False)
        except:
            pass

        utils.fitViewAndShade()

        # set the UI to the correct state
        if cmds.objExists("ART_RIG_ROOT.state"):
            state = cmds.getAttr("ART_RIG_ROOT.state")
            if state == 1:
                self.toolModeStack.setCurrentIndex(1)

                # remove outliner scriptJobs
                for job in self.scriptJobs:
                    cmds.scriptJob(kill=job, force=True)

                # build the scriptJob for the weight table
                self.scriptJobs.append(self.skinToolsInst.weightTable_scriptJob())

            if state == 2:
                self.toolModeStack.setCurrentIndex(2)

                # remove outliner scriptJobs
                for job in self.scriptJobs:
                    cmds.scriptJob(kill=job, force=True)

        self.populateNetworkList()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateNetworkList(self):

        self.nodeNetworkList.clear()

        # get network nodes and add to list widget
        modules = cmds.ls(type="network")
        returnMods = []
        for module in modules:
            attrs = cmds.listAttr(module)
            if "parent" in attrs:
                returnMods.append(module)

        mainNode = cmds.listConnections(returnMods[0] + ".parent")[0]
        self.nodeNetworkList.addItem(mainNode)

        for mod in returnMods:
            self.nodeNetworkList.addItem(mod)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def buildUI(self):
        # Original Author: Jeremy Ernst

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.setStyleSheet(self.style)

        # size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        scrollSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

        # create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setObjectName("darkImg")
        self.setCentralWidget(self.mainWidget)

        # set qt object name
        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # create the mainLayout for the rig creator UI
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.setMinimumSize(QtCore.QSize(580, 400))
        self.setMaximumSize(QtCore.QSize(580, 900))

        self.resize(600, 450)

        # Create a stackedWidget
        self.toolModeStack = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.toolModeStack)
        self.rigMode = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout(self.rigMode)
        self.toolModeStack.addWidget(self.rigMode)

        # create the menu bar
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setMaximumHeight(25)
        self.mainLayout.addWidget(self.menuBar)

        # create the toolbar layout
        self.toolFrame = QtWidgets.QFrame()
        self.toolFrame.setMinimumHeight(60)
        self.toolFrame.setMaximumHeight(60)
        self.toolFrame.setObjectName("dark2")
        self.mainLayout.addWidget(self.toolFrame)
        self.toolbarLayout = QtWidgets.QHBoxLayout(self.toolFrame)
        self.toolbarLayout.setDirection(QtWidgets.QBoxLayout.RightToLeft)
        self.toolbarLayout.addStretch(0)
        self.toolbarLayout.setSpacing(10)

        # toolbar buttons

        self.pinModulesBtn = QtWidgets.QPushButton()
        self.pinModulesBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.pinModulesBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/pin.png"))
        self.pinModulesBtn.setIconSize(QtCore.QSize(30, 30))
        self.pinModulesBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.pinModulesBtn)
        self.pinModulesBtn.setToolTip("Pin a module in place so that moving a parent does not effect the module.")
        self.pinModulesBtn.clicked.connect(self.pinModulesUI)
        self.pinModulesBtn.setObjectName("toolbar")

        self.bakeOffsetsBtn = QtWidgets.QPushButton()
        self.bakeOffsetsBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.bakeOffsetsBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/bakeOffsets.png"))
        self.bakeOffsetsBtn.setIconSize(QtCore.QSize(30, 30))
        self.bakeOffsetsBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.bakeOffsetsBtn)
        self.bakeOffsetsBtn.setToolTip("Bake the offset mover values up to the global movers.")
        self.bakeOffsetsBtn.clicked.connect(self.bakeOffsetsUI)
        self.bakeOffsetsBtn.setObjectName("toolbar")

        self.aimModeBtn = QtWidgets.QPushButton()
        self.aimModeBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.aimModeBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/aim.png"))
        self.aimModeBtn.setIconSize(QtCore.QSize(30, 30))
        self.aimModeBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.aimModeBtn)
        self.aimModeBtn.setToolTip("Toggle Aim mode for modules.")
        self.aimModeBtn.clicked.connect(self.aimModeUI)
        self.aimModeBtn.setObjectName("toolbar")

        self.boneCountBtn = QtWidgets.QPushButton()
        self.boneCountBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.boneCountBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/count.png"))
        self.boneCountBtn.setIconSize(QtCore.QSize(30, 30))
        self.boneCountBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.boneCountBtn)
        self.boneCountBtn.setToolTip("Bring up a bone counter utility")
        self.boneCountBtn.setCheckable(True)
        self.boneCountBtn.clicked.connect(self.boneCounterUI)
        self.boneCountBtn.setObjectName("toolbar")

        self.resetBtn = QtWidgets.QPushButton()
        self.resetBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.resetBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/reset.png"))
        self.resetBtn.setIconSize(QtCore.QSize(30, 30))
        self.resetBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.resetBtn)
        self.resetBtn.setToolTip("Reset Joint Mover Modules Position and Rotation")
        self.resetBtn.setCheckable(True)
        self.resetBtn.clicked.connect(self.resetModeUI)
        self.resetBtn.setObjectName("toolbar")

        self.symmetryModeBtn = QtWidgets.QPushButton()
        self.symmetryModeBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.symmetryModeBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/symmetryMode.png"))
        self.symmetryModeBtn.setIconSize(QtCore.QSize(30, 30))
        self.symmetryModeBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.symmetryModeBtn)
        self.symmetryModeBtn.setToolTip("Brings up a new window to apply symmetry to the selected modules in the list.")
        self.symmetryModeBtn.clicked.connect(self.symmetryModeUI)
        self.symmetryModeBtn.setObjectName("toolbar")

        self.geoDisplayBtn = QtWidgets.QPushButton()
        self.geoDisplayBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.geoDisplayBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/geoDisplay_on.png"))
        self.geoDisplayBtn.setIconSize(QtCore.QSize(30, 30))
        self.geoDisplayBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.geoDisplayBtn)
        self.geoDisplayBtn.setToolTip("Toggle the visibility of the proxy geometry")
        self.geoDisplayBtn.setCheckable(True)
        self.geoDisplayBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_proxy_geo", self.geoDisplayBtn))
        self.geoDisplayBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.geoDisplayBtn, "System/geoDisplay_on.png", "System/geoDisplay.png"))
        self.geoDisplayBtn.setChecked(True)
        self.geoDisplayBtn.setObjectName("toolbar")

        self.lraDisplayBtn = QtWidgets.QPushButton()
        self.lraDisplayBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.lraDisplayBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/lra_on.png"))
        self.lraDisplayBtn.setIconSize(QtCore.QSize(30, 30))
        self.lraDisplayBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.lraDisplayBtn)
        self.lraDisplayBtn.setToolTip("Toggle the visibility of the local rotation axis display")
        self.lraDisplayBtn.setCheckable(True)
        self.lraDisplayBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_lra", self.lraDisplayBtn))
        self.lraDisplayBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.lraDisplayBtn, "System/lra_on.png", "System/lra.png"))
        self.lraDisplayBtn.setChecked(True)
        self.lraDisplayBtn.setObjectName("toolbar")

        self.boneDisplayBtn = QtWidgets.QPushButton()
        self.boneDisplayBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.boneDisplayBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/boneDisplay.png"))
        self.boneDisplayBtn.setIconSize(QtCore.QSize(30, 30))
        self.boneDisplayBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.boneDisplayBtn)
        self.boneDisplayBtn.setToolTip("Toggle the visibility of the bone representations")
        self.boneDisplayBtn.setCheckable(True)
        self.boneDisplayBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_bone_geo", self.boneDisplayBtn))
        self.boneDisplayBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.boneDisplayBtn, "System/boneDisplay_on.png", "System/boneDisplay.png"))
        self.boneDisplayBtn.setChecked(False)
        self.boneDisplayBtn.setObjectName("toolbar")

        self.meshMoverBtn = QtWidgets.QPushButton()
        self.meshMoverBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.meshMoverBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/meshMover.png"))
        self.meshMoverBtn.setIconSize(QtCore.QSize(30, 30))
        self.meshMoverBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.meshMoverBtn)
        self.meshMoverBtn.setToolTip("Toggle the visibility of the mesh mover controls")
        self.meshMoverBtn.setCheckable(True)
        self.meshMoverBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_mover_geo", self.meshMoverBtn))
        self.meshMoverBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.meshMoverBtn, "System/meshMover_on.png", "System/meshMover.png"))
        self.meshMoverBtn.setChecked(False)
        self.meshMoverBtn.setObjectName("toolbar")

        self.offsetMoverBtn = QtWidgets.QPushButton()
        self.offsetMoverBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.offsetMoverBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/offsetMover.png"))
        self.offsetMoverBtn.setIconSize(QtCore.QSize(30, 30))
        self.offsetMoverBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.offsetMoverBtn)
        self.offsetMoverBtn.setToolTip("Toggle the visibility of the offset mover controls")
        self.offsetMoverBtn.setCheckable(True)
        self.offsetMoverBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_mover_offset", self.offsetMoverBtn))
        self.offsetMoverBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.offsetMoverBtn, "System/offsetMover_on.png", "System/offsetMover.png"))
        self.offsetMoverBtn.setChecked(False)
        self.offsetMoverBtn.setObjectName("toolbar")

        self.globalMoverBtn = QtWidgets.QPushButton()
        self.globalMoverBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.globalMoverBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/globalMover_on.png"))
        self.globalMoverBtn.setIconSize(QtCore.QSize(30, 30))
        self.globalMoverBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.globalMoverBtn)
        self.globalMoverBtn.setToolTip("Toggle the visibility of the global mover controls")
        self.globalMoverBtn.setCheckable(True)
        self.globalMoverBtn.clicked.connect(partial(self.toggleMoverVisibility, "*_mover", self.globalMoverBtn))
        self.globalMoverBtn.clicked.connect(
            partial(self.toggleButtonIcon, self.globalMoverBtn, "System/globalMover_on.png", "System/globalMover.png"))
        self.globalMoverBtn.setChecked(True)
        self.globalMoverBtn.setObjectName("toolbar")

        self.saveTemplateBtn = QtWidgets.QPushButton()
        self.saveTemplateBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.saveTemplateBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/save.png"))
        self.saveTemplateBtn.setIconSize(QtCore.QSize(30, 30))
        self.saveTemplateBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.saveTemplateBtn)
        self.saveTemplateBtn.setToolTip("Save current setup as template")
        self.saveTemplateBtn.clicked.connect(self.saveTemplate)
        self.saveTemplateBtn.setObjectName("toolbar")

        self.loadTemplateBtn = QtWidgets.QPushButton()
        self.loadTemplateBtn.setMinimumSize(QtCore.QSize(30, 30))
        self.loadTemplateBtn.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/load.png"))
        self.loadTemplateBtn.setIconSize(QtCore.QSize(30, 30))
        self.loadTemplateBtn.setIcon(icon)
        self.toolbarLayout.addWidget(self.loadTemplateBtn)
        self.loadTemplateBtn.setToolTip("Load an existing template file")
        self.loadTemplateBtn.clicked.connect(self.loadTemplate)
        self.loadTemplateBtn.setObjectName("toolbar")

        # Add Items to the Menu Bar
        # icons
        icon_saveTemplate = QtGui.QIcon(os.path.join(self.iconsPath, "System/save.png"))
        icon_loadTemplate = QtGui.QIcon(os.path.join(self.iconsPath, "System/load.png"))
        icon_exit = QtGui.QIcon(os.path.join(self.iconsPath, "System/exit.png"))
        icon_viewToolbar = QtGui.QIcon(os.path.join(self.iconsPath, "System/toggleVis.png"))
        icon_globalMover = QtGui.QIcon(os.path.join(self.iconsPath, "System/globalMover.png"))
        icon_offsetMover = QtGui.QIcon(os.path.join(self.iconsPath, "System/offsetMover.png"))
        icon_meshMover = QtGui.QIcon(os.path.join(self.iconsPath, "System/meshMover.png"))
        icon_boneDisplay = QtGui.QIcon(os.path.join(self.iconsPath, "System/boneDisplay.png"))
        icon_lraDisplay = QtGui.QIcon(os.path.join(self.iconsPath, "System/lra.png"))
        icon_proxyGeo = QtGui.QIcon(os.path.join(self.iconsPath, "System/geoDisplay.png"))
        icon_massMirrorMode = QtGui.QIcon(os.path.join(self.iconsPath, "System/symmetryMode.png"))
        icon_resetModules = QtGui.QIcon(os.path.join(self.iconsPath, "System/reset.png"))
        icon_boneCount = QtGui.QIcon(os.path.join(self.iconsPath, "System/count.png"))

        # file
        fileMenu = self.menuBar.addMenu("File")
        fileMenu.addAction(icon_saveTemplate, "Save Template", self.saveTemplate)
        fileMenu.addAction(icon_loadTemplate, "Load Template", self.loadTemplate)
        fileMenu.addAction(icon_exit, "Exit")

        # view
        viewMenu = self.menuBar.addMenu("View")
        viewMenu.addAction(icon_viewToolbar, "Toggle Toolbar Visibility", self.setToolbarVisibility)
        viewMenu.addAction(icon_viewToolbar, "View Module Stats", self.moduleStatusUI)

        # display
        displayMenu = self.menuBar.addMenu("Display")
        displayMenu.addAction(icon_globalMover, "Toggle Global Movers",
                              partial(self.toggleMoverVisibility_FromMenu, "*_mover", self.globalMoverBtn,
                                      "System/globalMover_on.png", "System/globalMover.png"))
        displayMenu.addAction(icon_offsetMover, "Toggle Offset Movers",
                              partial(self.toggleMoverVisibility_FromMenu, "*_mover_offset", self.offsetMoverBtn,
                                      "System/offsetMover_on.png", "System/offsetMover.png"))
        displayMenu.addAction(icon_meshMover, "Toggle Mesh Movers",
                              partial(self.toggleMoverVisibility_FromMenu, "*_mover_geo", self.meshMoverBtn,
                                      "System/meshMover_on.png", "System/meshMover.png"))
        displayMenu.addAction(icon_boneDisplay, "Toggle Joint Display",
                              partial(self.toggleMoverVisibility_FromMenu, "*_bone_geo", self.boneDisplayBtn,
                                      "System/boneDisplay_on.png", "System/boneDisplay.png"))
        displayMenu.addAction(icon_lraDisplay, "Toggle LRA Display",
                              partial(self.toggleMoverVisibility_FromMenu, "*_lra", self.lraDisplayBtn,
                                      "System/lra_on.png", "System/lra.png"))
        displayMenu.addAction(icon_proxyGeo, "Toggle Proxy Geo Display",
                              partial(self.toggleMoverVisibility_FromMenu, "*_proxy_geo", self.geoDisplayBtn,
                                      "System/geoDisplay_on.png", "System/geoDisplay.png"))

        # tools
        toolsMenu = self.menuBar.addMenu("Tools")
        toolsMenu.addAction(icon_massMirrorMode, "Mass Mirror Mode Tool", self.symmetryModeUI)
        toolsMenu.addAction(icon_resetModules, "Reset Modules Tool", self.resetModeUI)
        toolsMenu.addAction(icon_boneCount, "Bone Counter Tool", self.boneCounterUI)

        # help
        helpMenu = self.menuBar.addMenu("Help")
        helpMenu.addAction("Documentation")
        helpMenu.addAction("About")

        # create the tabLayout (Skeleton Creation and Settings/Outliner)

        # tab stylesheet (tab stylesheet via QSS doesn't seem to work for some reason
        stylesheet = """
        QTabBar::tab
        {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(90,90,90), stop:1 rgb(30,30,30));
            border: 2px solid black;
            width: 180px;
            padding-left: -10px;
            font: 8pt;
        }
        QTabBar::tab:selected
        {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(255,174,0), stop:1 rgb(30,30,30));
            border: 2px solid black;
            font: bold 10pt;
        }
        QTabBar::tab:hover
        {
            background: rgb(132,95,16);
            font: bold 10pt;
        }
        QTabBar::tab:!selected
        {
            margin-top: 5px;
        }
        QTabWidget::pane
        {
            border: 2px solid rgb(0,0,0);
        }
        """

        self.tabWidget = QtWidgets.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(545, 400))
        self.tabWidget.setMaximumSize(QtCore.QSize(545, 900))
        self.tabWidget.setSizePolicy(scrollSizePolicy)
        self.tabWidget.setStyleSheet(stylesheet)

        # Create our first tab
        self.tab1 = QtWidgets.QFrame()
        self.tab1.setObjectName("dark")
        self.topLevelLayout = QtWidgets.QVBoxLayout(self.tab1)
        self.tabWidget.addTab(self.tab1, "Creation/Settings")

        # create the label layout
        self.labelLayout = QtWidgets.QHBoxLayout()
        self.topLevelLayout.addLayout(self.labelLayout)

        # create a label for  Modules and Installed Modules
        self.modLabel = QtWidgets.QLabel("Rig Modules:")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.modLabel.setFont(font)
        self.modLabel.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.modLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modLabel.setSizePolicy(mainSizePolicy)
        self.modLabel.setMinimumSize(QtCore.QSize(150, 30))
        self.modLabel.setMaximumSize(QtCore.QSize(150, 30))
        self.modLabel.setStyleSheet(
            'color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(25, 175, 255, 255), stop:1 rgba(25, 175, 255, 255));background-color: rgb(60,60,60);')
        self.labelLayout.addWidget(self.modLabel)

        # create the installed modules label
        self.installedModLabel = QtWidgets.QLabel("Installed Modules:")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.installedModLabel.setFont(font)
        self.installedModLabel.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.installedModLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.installedModLabel.setSizePolicy(mainSizePolicy)
        self.installedModLabel.setMinimumSize(QtCore.QSize(360, 30))
        self.installedModLabel.setMaximumSize(QtCore.QSize(360, 30))
        self.installedModLabel.setStyleSheet(
            'color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(25, 175, 255, 255), stop:1 rgba(25, 175, 255, 255));background-color: rgb(60,60,60);')
        self.labelLayout.addWidget(self.installedModLabel)

        # create the search layout
        self.searchLayout = QtWidgets.QHBoxLayout()
        self.topLevelLayout.addLayout(self.searchLayout)

        # create the search bars for both sides
        self.moduleSearch = QtWidgets.QLineEdit()
        self.moduleSearch.setPlaceholderText("Search...")
        self.moduleSearch.setMinimumSize(QtCore.QSize(150, 20))
        self.moduleSearch.setMaximumSize(QtCore.QSize(150, 20))
        self.moduleSearch.setSizePolicy(mainSizePolicy)
        self.searchLayout.addWidget(self.moduleSearch)
        self.moduleSearch.textChanged.connect(self.searchModules)

        self.installedSearch = QtWidgets.QLineEdit()
        self.installedSearch.setPlaceholderText("Search...")
        self.installedSearch.setMinimumSize(QtCore.QSize(150, 20))
        self.installedSearch.setMaximumSize(QtCore.QSize(150, 20))
        self.installedSearch.setSizePolicy(mainSizePolicy)
        self.searchLayout.addWidget(self.installedSearch)
        self.installedSearch.textChanged.connect(self.searchInstalled)

        # add buttons (expand all, collapse all, sort by type, sort by ABC)
        self.installed_ExpandAll = QtWidgets.QPushButton()
        self.installed_ExpandAll.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.installed_ExpandAll.setMinimumSize(QtCore.QSize(40, 20))
        self.installed_ExpandAll.setMaximumSize(QtCore.QSize(40, 20))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/expand_all.png"))
        self.installed_ExpandAll.setIcon(icon)
        self.installed_ExpandAll.setIconSize(QtCore.QSize(40, 20))
        self.installed_ExpandAll.setToolTip("Expand all module settings")
        self.searchLayout.addWidget(self.installed_ExpandAll)
        self.installed_ExpandAll.clicked.connect(partial(self.expandAllSettings, True))
        self.installed_ExpandAll.setObjectName("toolbar")

        self.installed_CollapseAll = QtWidgets.QPushButton()
        self.installed_CollapseAll.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.installed_CollapseAll.setMinimumSize(QtCore.QSize(40, 20))
        self.installed_CollapseAll.setMaximumSize(QtCore.QSize(40, 20))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/collapse_all.png"))
        self.installed_CollapseAll.setIcon(icon)
        self.installed_CollapseAll.setIconSize(QtCore.QSize(40, 20))
        self.installed_CollapseAll.setToolTip("Collapse all module settings")
        self.searchLayout.addWidget(self.installed_CollapseAll)
        self.installed_CollapseAll.clicked.connect(partial(self.expandAllSettings, False))
        self.installed_CollapseAll.setObjectName("toolbar")

        self.installed_sortByType = QtWidgets.QPushButton()
        self.installed_sortByType.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.installed_sortByType.setMinimumSize(QtCore.QSize(40, 20))
        self.installed_sortByType.setMaximumSize(QtCore.QSize(40, 20))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/sortByType.png"))
        self.installed_sortByType.setIcon(icon)
        self.installed_sortByType.setIconSize(QtCore.QSize(40, 20))
        self.installed_sortByType.setToolTip("Sort modules by module type")
        self.searchLayout.addWidget(self.installed_sortByType)
        self.installed_sortByType.clicked.connect(partial(self.sortModules, "type"))
        self.installed_sortByType.setObjectName("toolbar")

        self.installed_sortByAlphabet = QtWidgets.QPushButton()
        self.installed_sortByAlphabet.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.installed_sortByAlphabet.setMinimumSize(QtCore.QSize(40, 20))
        self.installed_sortByAlphabet.setMaximumSize(QtCore.QSize(40, 20))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/sortByAlphabet.png"))
        self.installed_sortByAlphabet.setIcon(icon)
        self.installed_sortByAlphabet.setIconSize(QtCore.QSize(40, 20))
        self.installed_sortByAlphabet.setToolTip("Sort modules by module alphabetical order")
        self.searchLayout.addWidget(self.installed_sortByAlphabet)
        self.installed_sortByAlphabet.clicked.connect(partial(self.sortModules, "abc"))
        self.installed_sortByAlphabet.setObjectName("toolbar")

        # create the layout for the main part of our UI
        self.main = QtWidgets.QHBoxLayout()
        self.topLevelLayout.addLayout(self.main)

        # create the module scroll area and add it to the main layout
        self.scrollAreaMods = QtWidgets.QScrollArea()
        self.scrollAreaMods.setObjectName("epic")
        self.main.addWidget(self.scrollAreaMods)
        self.scrollAreaMods.setSizePolicy(mainSizePolicy)
        self.scrollAreaMods.setMinimumSize(QtCore.QSize(150, 400))
        self.scrollAreaMods.setMaximumSize(QtCore.QSize(150, 60000))
        self.scrollAreaMods.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Module scroll area contents
        self.modScrollAreaContents = QtWidgets.QFrame()
        self.modScrollAreaContents.setObjectName("epic")
        self.modScrollAreaContents.setSizePolicy(scrollSizePolicy)
        self.modScrollAreaContents.setMinimumSize(QtCore.QSize(150, 800))
        self.modScrollAreaContents.setMaximumSize(QtCore.QSize(150, 60000))
        self.scrollAreaMods.setWidget(self.modScrollAreaContents)

        # add the vertical box layout for the module scroll area
        self.moduleLayout = QtWidgets.QVBoxLayout(self.modScrollAreaContents)
        self.moduleLayout.setDirection(QtWidgets.QBoxLayout.BottomToTop)
        self.moduleLayout.setContentsMargins(5, 5, 0, 5)
        self.moduleLayout.addStretch(2)
        self.moduleLayout.setSpacing(5)

        # create the scroll area for the module settings
        self.scrollAreaSettings = QtWidgets.QScrollArea()
        self.scrollAreaSettings.setObjectName("epic")
        self.scrollAreaSettings.setWidgetResizable(True)
        self.main.addWidget(self.scrollAreaSettings)
        self.scrollAreaSettings.setSizePolicy(scrollSizePolicy)
        self.scrollAreaSettings.setMinimumSize(QtCore.QSize(360, 400))
        self.scrollAreaSettings.setMaximumSize(QtCore.QSize(360, 600000))
        self.scrollAreaSettings.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # create the module settings scroll area contents widget
        self.settingsScrollAreaContents = QtWidgets.QFrame()
        self.settingsScrollAreaContents.setObjectName("dark")
        self.settingsScrollAreaContents.setMinimumWidth(360)
        self.settingsScrollAreaContents.setMaximumWidth(360)
        self.settingsScrollAreaContents.setSizePolicy(scrollSizePolicy)
        self.scrollAreaSettings.setWidget(self.settingsScrollAreaContents)

        # add the vertical box layout for the module scroll area
        self.moduleSettingsLayout = QtWidgets.QVBoxLayout(self.settingsScrollAreaContents)
        self.moduleSettingsLayout.setDirection(QtWidgets.QBoxLayout.BottomToTop)
        self.moduleSettingsLayout.setContentsMargins(0, 5, 0, 5)
        self.moduleSettingsLayout.addStretch(2)
        self.moduleSettingsLayout.setSpacing(10)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # SECOND TAB #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Create the 2nd tab
        self.tab2 = QtWidgets.QFrame(self.tabWidget)
        self.tab2.setObjectName("mid")
        self.tab2Layout = QtWidgets.QHBoxLayout(self.tab2)
        self.tabWidget.addTab(self.tab2, "Outliner")

        # create the treeView representing the outliner
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setIndentation(10)
        self.treeWidget.expandAll()

        self.tab2Layout.addWidget(self.treeWidget)
        self.treeWidget.setSizePolicy(mainSizePolicy)
        self.treeWidget.setMinimumSize(QtCore.QSize(320, 500))
        self.treeWidget.setMaximumSize(QtCore.QSize(320, 800))

        # create columns
        self.treeWidget.headerItem().setText(0, "Modules")
        self.treeWidget.headerItem().setText(1, "G")
        self.treeWidget.headerItem().setText(2, "O")
        self.treeWidget.headerItem().setText(3, "M")

        # set column widths
        self.treeWidget.setColumnWidth(0, 240)
        self.treeWidget.setColumnWidth(1, 20)
        self.treeWidget.setColumnWidth(2, 20)
        self.treeWidget.setColumnWidth(3, 20)
        self.treeWidget.setObjectName("light")
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # CHANNEL BOX #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # add the channel box layout
        self.channelBoxLayout = QtWidgets.QFrame()
        self.channelBoxLayout.setObjectName("mid")

        # set dimensions
        self.channelBoxLayout.setSizePolicy(scrollSizePolicy)
        self.channelBoxLayout.setGeometry(0, 0, 250, 500)
        self.channelBoxLayout.setMinimumSize(QtCore.QSize(220, 500))
        self.channelBoxLayout.setMaximumSize(QtCore.QSize(220, 800))
        self.tab2Layout.addWidget(self.channelBoxLayout)

        # create a VBoxLayout for the channelBox Layout
        self.channelBoxVLayout = QtWidgets.QVBoxLayout(self.channelBoxLayout)

        # create the QWidget to house the channelBox
        self.channelBoxWidget = QtWidgets.QFrame()
        self.channelBoxWidget.setObjectName("mid")

        # set dimensions
        self.channelBoxWidget.setSizePolicy(mainSizePolicy)
        self.channelBoxWidget.setMinimumSize(QtCore.QSize(220, 470))
        self.channelBoxWidget.setMaximumSize(QtCore.QSize(220, 770))

        # add the channel box widget to the VBoxLayout
        self.channelBoxVLayout.addWidget(self.channelBoxWidget)

        # add the channel box VBoxLayout to the QFrame
        self.channelBox_mainLayout = QtWidgets.QVBoxLayout(self.channelBoxWidget)

        # add the channel box from Maya to the UI
        channelBoxWidget = cmds.channelBox()
        pointer = mui.MQtUtil.findControl(channelBoxWidget)
        self.channelBox = shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)
        self.channelBox_mainLayout.addWidget(self.channelBox)
        self.channelBox.setObjectName("dark")
        self.channelBox.show()

        # add network node info
        self.nodeNetworkList = QtWidgets.QListWidget()
        self.channelBox_mainLayout.addWidget(self.nodeNetworkList)
        self.nodeNetworkList.setMinimumHeight(200)
        self.nodeNetworkList.setMaximumHeight(200)
        self.nodeNetworkList.itemClicked.connect(self.selectNetworkNode)

        # add the "Finalize Setup" button
        self.createSkeletonLayout = QtWidgets.QHBoxLayout()
        self.createSkeletonLayout.setContentsMargins(25, 0, 0, 0)
        self.createSkeletonBtn = QtWidgets.QPushButton("FINALIZE SETUP")
        self.createSkeletonBtn.setObjectName("blueButtonSpecial")
        self.createSkeletonBtn.setMinimumHeight(50)
        self.createSkeletonBtn.setMaximumHeight(50)

        self.createSkeletonBtn.clicked.connect(self.finalizeSetup_UI)
        self.createSkeletonLayout.addWidget(self.createSkeletonBtn)
        self.mainLayout.addLayout(self.createSkeletonLayout)

        # build deformation UI
        self.buildDeformation_UI()

        # set the layout
        self.setLayout(self.mainLayout)

        # find and populate modules list
        self.findRigModules()

        # build lock page
        self.rigLockedPage = QtWidgets.QFrame()
        self.toolModeStack.addWidget(self.rigLockedPage)

        self.rigLockedPage.setMinimumSize(QtCore.QSize(550, 500))
        self.rigLockedPage.setMaximumSize(QtCore.QSize(550, 800))
        image = utils.returnNicePath(self.iconsPath, "System/rigLockPage.png")
        self.rigLockedPage.setStyleSheet("background-image: url(" + image + ");")

        # add the layout to the lock page
        self.lockLayout = QtWidgets.QVBoxLayout(self.rigLockedPage)
        self.lockLayout.setContentsMargins(70, 500, 70, 160)

        buttonLayout1 = QtWidgets.QHBoxLayout()
        self.lockLayout.addLayout(buttonLayout1)

        buttonLayout2 = QtWidgets.QHBoxLayout()
        self.lockLayout.addLayout(buttonLayout2)

        # add spacer and button
        self.unlockBtn = QtWidgets.QPushButton("Remove Rig")
        self.unlockBtn.clicked.connect(partial(self.removeRigging))
        buttonLayout1.addWidget(self.unlockBtn)
        self.unlockBtn.setMinimumSize(200, 40)
        self.unlockBtn.setMaximumSize(200, 40)
        self.unlockBtn.setFont(font)
        self.unlockBtn.setStyleSheet(self.style)
        self.unlockBtn.setObjectName("blueButton")

        self.skinToolsBtn = QtWidgets.QPushButton("Deformation Toolkit")
        self.skinToolsBtn.clicked.connect(partial(self.deformationTools))
        buttonLayout2.addWidget(self.skinToolsBtn)
        self.skinToolsBtn.setMinimumSize(200, 40)
        self.skinToolsBtn.setMaximumSize(200, 40)
        self.skinToolsBtn.setStyleSheet(self.style)
        self.skinToolsBtn.setObjectName("blueButton")

        self.exportMeshesBtn = QtWidgets.QPushButton("Export Skeletal Meshes")
        self.exportMeshesBtn.clicked.connect(partial(self.exportMeshes))
        buttonLayout2.addWidget(self.exportMeshesBtn)
        self.exportMeshesBtn.setMinimumSize(200, 40)
        self.exportMeshesBtn.setMaximumSize(200, 40)
        self.exportMeshesBtn.setStyleSheet(self.style)
        self.exportMeshesBtn.setObjectName("blueButton")

        self.rigHistBtn = QtWidgets.QPushButton("Rig History")
        self.rigHistBtn.clicked.connect(partial(self.rigHistoryUI))
        buttonLayout1.addWidget(self.rigHistBtn)
        self.rigHistBtn.setMinimumSize(200, 40)
        self.rigHistBtn.setMaximumSize(200, 40)
        self.rigHistBtn.setStyleSheet(self.style)
        self.rigHistBtn.setObjectName("blueButton")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def setToolbarVisibility(self):
        # Original Author: Jeremy Ernst
        state = self.toolFrame.isVisible()
        if state == True:
            self.toolFrame.setVisible(False)
        if state == False:
            self.toolFrame.setVisible(True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def setMoverVisibility(self):
        # Original Author: Jeremy Ernst

        movers = [["*_proxy_geo", self.geoDisplayBtn], ["*_lra", self.lraDisplayBtn],
                  ["*_bone_geo", self.boneDisplayBtn], ["*_mover_geo", self.meshMoverBtn],
                  ["*_mover_offset", self.offsetMoverBtn], ["*_mover", self.globalMoverBtn]]
        for mover in movers:
            self.toggleMoverVisibility(mover[0], mover[1])


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def sortModules(self, sortMethod):
        # Original Author: Jeremy Ernst

        modules = utils.returnRigModules()
        modTypes = []
        modNames = []
        # get the module's type and name
        for module in modules:
            modType = cmds.getAttr(module + ".moduleType")
            modName = cmds.getAttr(module + ".moduleName")
            modTypes.append([modName, modType])
            modNames.append(str(modName))

        if sortMethod == "abc":
            # create a sorted list of that info
            modNames = sorted(modNames, key=str.lower)

            # create a list of the groupbox widgets sorted by alphabetical order
            groupBoxes = []
            for i in range(self.moduleSettingsLayout.count()):
                try:
                    groupBoxes.append([self.moduleSettingsLayout.itemAt(i).widget().title(),
                                       self.moduleSettingsLayout.itemAt(i).widget()])
                except:
                    pass

            # re-sort the groupboxes in the layout
            for each in modNames:
                for box in groupBoxes:
                    if box[0] == each:
                        self.moduleSettingsLayout.insertWidget(1, box[1])
                        self.moduleSettingsLayout.setDirection(QtWidgets.QBoxLayout.BottomToTop)

        if sortMethod == "type":
            # create a sorted list of that info
            sortedList = sorted(modTypes, key=lambda name: name[1])

            # create a list of the groupbox widgets sorted by module type
            groupBoxes = []
            for i in range(self.moduleSettingsLayout.count()):
                try:
                    groupBoxes.append([self.moduleSettingsLayout.itemAt(i).widget().title(),
                                       self.moduleSettingsLayout.itemAt(i).widget()])
                except:
                    pass
            # compare the sorted list to the list of groupboxes and make a new list that has those groupboxes in the same order as the sorted list
            newList = []
            for item in sortedList:
                name = item[0]
                for box in groupBoxes:
                    title = box[0]
                    if title == name:
                        newList.append(box)

            # re-sort the groupboxes in the layout
            for i in range(len(newList)):
                self.moduleSettingsLayout.insertWidget(1, newList[i][1])


            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def expandAllSettings(self, doExpand):
        # Original Author: Jeremy Ernst

        modules = utils.returnRigModules()

        for module in modules:
            modType = cmds.getAttr(module + ".moduleType")
            modName = cmds.getAttr(module + ".moduleName")
            mod = __import__("RigModules." + modType, {}, {}, [modType])

            # get the class name from that module file (returns Modules.ART_Root.ART_Root for example)
            moduleClass = getattr(mod, mod.className)

            # find the instance of that module and call on the skeletonSettings_UI function
            moduleInst = moduleClass(self, modName)

            if modType != "ART_Root":
                for i in range(self.moduleSettingsLayout.count()):
                    if type(self.moduleSettingsLayout.itemAt(i).widget()) == QtWidgets.QGroupBox:
                        if self.moduleSettingsLayout.itemAt(i).widget().title() == modName:
                            self.moduleSettingsLayout.itemAt(i).widget().setChecked(doExpand)

                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addModule(self, baseName, className):
        # Original Author: Jeremy Ernst

        # This function gets called when a module button is pushed. It will grab some information from the user and then add the network node, jointMover, and skelSettingsUI

        # delete the UI if it already exists
        mayaWindow = interfaceUtils.getMainWindow()
        mayaWindow = mayaWindow.objectName()
        if cmds.window(mayaWindow + "|pyArtAddModuleUi", q=True, exists=True):
            cmds.deleteUI(mayaWindow + "|pyArtAddModuleUi")

        # run the user interface to gather information
        import ART_AddModuleUI as ART_AddModuleUI
        reload(ART_AddModuleUI)
        inst = ART_AddModuleUI.ART_AddModule_UI(baseName, className, self, interfaceUtils.getMainWindow())
        inst.show()

        return True

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleButtonIcon(self, button, onIcon, offIcon):
        # Original Author: Jeremy Ernst

        state = button.isChecked()

        if state:
            icon = QtGui.QIcon(os.path.join(self.iconsPath, onIcon))
        else:
            icon = QtGui.QIcon(os.path.join(self.iconsPath, offIcon))

        button.setIcon(icon)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleMoverVisibility_FromMenu(self, searchKey, button, onIcon, offIcon):
        # Original Author: Jeremy Ernst

        state = button.isChecked()
        if state:
            button.setChecked(False)
            icon = QtGui.QIcon(os.path.join(self.iconsPath, offIcon))
            button.setIcon(icon)

        else:
            button.setChecked(True)
            icon = QtGui.QIcon(os.path.join(self.iconsPath, onIcon))
            button.setIcon(icon)

        self.toggleMoverVisibility(searchKey, button)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleMoverVisibility(self, searchKey, button):
        # Original Author: Jeremy Ernst

        try:
            currentSelection = cmds.ls(sl=True)
            # get current checkbox state
            state = button.isChecked()

            # get the list of movers
            cmds.select(searchKey)
            movers = cmds.ls(sl=True)

            # find the mover shapes and set their visibility
            shapes = []
            for mover in movers:
                child = cmds.listRelatives(mover, children=True, shapes=True)
                if len(child) > 0:
                    shapes.append(mover + "|" + child[0])

            for shape in shapes:
                cmds.setAttr(shape + ".v", lock=False)
                cmds.setAttr(shape + ".v", state, lock=True)

            try:
                cmds.select(currentSelection)
            except:
                pass

        except:
            pass


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def saveTemplate(self):
        # Original Author: Jeremy Ernst

        # find all modules in the scene
        if cmds.objExists("ART_RIG_ROOT"):
            modules = cmds.listConnections("ART_RIG_ROOT.rigModules")

            # start creating the data list
            data = []

            # loop through each module, getting the required information
            for module in modules:
                moduleData = [str(module)]

                # get the module attributes and their values
                attrData = []
                attrs = cmds.listAttr(module, ud=True, hd=True)
                for attr in attrs:
                    value = cmds.getAttr(module + "." + attr)
                    attrData.append([str(attr), value])

                # add the attrData to the moduleData
                moduleData.append(attrData)

                # get all movers and thier keyable values
                moduleName = cmds.getAttr(module + ".moduleName")
                moverTypes = ["_mover", "_mover_offset", "_mover_geo"]
                allMoverData = []

                for moverType in moverTypes:
                    try:
                        cmds.select(moduleName + "*" + moverType)
                        movers = cmds.ls(sl=True)
                        validMovers = []

                        # validate selection
                        for mover in movers:
                            moverGrp = moduleName + "_mover_grp"
                            validMovers.append(moverGrp)
                            children = cmds.listRelatives(moverGrp, ad=True)
                            if mover in children:
                                validMovers.append(str(mover))

                        # get mover values
                        for mover in validMovers:
                            moverData = []
                            attrs = cmds.listAttr(mover, keyable=True)

                            for attr in attrs:
                                value = cmds.getAttr(mover + "." + attr)
                                moverData.append([str(mover + "." + attr), value])
                            allMoverData.append(moverData)

                    except:
                        pass

                # add all of the mover data to the moduleData list
                moduleData.append(allMoverData)

                # add the moduleData to data
                data.append(moduleData)

            # ask for the file name to give the template
            startingDir = os.path.normcase(os.path.join(self.toolsPath, "Core/JointMover/Templates"))
            if not os.path.exists(startingDir):
                os.makedirs(startingDir)

            filename = cmds.fileDialog2(fm=0, okc="Save Template", dir=startingDir, ff="*.template")[0]

            # create the template file
            f = open(filename, 'w')

            # dump the data with json
            json.dump(data, f)
            f.close()

            # print out confirmation
            print "Template has been saved"
            # inViewMessage only available in 2014 and up
            try:
                cmds.inViewMessage(amg=' <hl>Template has been saved.</hl>', pos='topCenter', fade=True)
            except:
                print "inViewMessage not supported"
                pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def loadTemplate(self):
        # Original Author: Jeremy Ernst

        # make sure scene is new, and refresh UI
        if self.moduleSettingsLayout.count() > 2:
            self.unsavedChanges()
            return

        # prompt for the file to load
        startingDir = os.path.normcase(os.path.join(self.toolsPath, "Core/JointMover/Templates"))
        if not os.path.exists:
            startingDir = self.toolsPath
        try:
            filename = cmds.fileDialog2(fm=1, okc="Load Template", dir=startingDir, ff="*.template")[0]
        except:
            return

        if filename is not None:

            self.moduleInstances = []

            # load the data
            json_file = open(filename)
            data = json.load(json_file)
            json_file.close()

            # clear out the scene of any network nodes, joint movers and relaunch the UI
            modules = cmds.listConnections("ART_RIG_ROOT.rigModules")
            modules.append("ART_RIG_ROOT")
            cmds.delete(modules)

            if cmds.objExists("JointMover"):
                cmds.delete("JointMover")

            for material in ["blue_m", "green_m", "red_m", "white_m"]:
                if cmds.objExists(material):
                    cmds.delete(material)

            # relaunch the UI
            newUI = createUI()

            # create a progress window
            progWindow = cmds.progressWindow(title='Loading Template', progress=0)
            amount = (100 / len(data)) / 5

            # go through the template data, adding the modules, the settings UI, and the joint mover
            solveLast = []
            for each in data:
                currentAmount = cmds.progressWindow(query=True, progress=True)
                cmds.progressWindow(edit=True, progress=currentAmount + amount, status="Working on " + each[0])

                module = each[0]
                if module is not None:
                    moduleAttrData = each[1]
                    for attr in moduleAttrData:
                        if attr[0] == "moduleName":
                            moduleName = attr[1]
                        if attr[0] == "moduleType":
                            moduleClass = str(attr[1])
                            moduleType = str(attr[1])

                    # build the network node for the module
                    if module != "ART_Root_Module":
                        mod = __import__("RigModules." + moduleClass, {}, {}, [moduleClass])
                        moduleClass = getattr(mod, mod.className)
                        jmPath = mod.jointMover
                        moduleInst = moduleClass(newUI, moduleName)
                        networkNode = moduleInst.buildNetwork()

                        # set the attributes on the network node
                        for moduleAttr in moduleAttrData:
                            attr = moduleAttr[0]
                            value = moduleAttr[1]

                            try:
                                attrType = str(cmds.getAttr(networkNode + "." + attr, type=True))
                                cmds.setAttr(networkNode + "." + attr, lock=False)
                                if attrType == "string":
                                    cmds.setAttr(networkNode + "." + attr, value, type=attrType, lock=True)
                                else:
                                    cmds.setAttr(networkNode + "." + attr, value, lock=True)

                            except:
                                print attr, value, attrType

                        # arm/leg exceptions
                        specialCaseModules = ["ART_Leg_Standard", "ART_Arm_Standard"]
                        if moduleType in specialCaseModules:
                            side = cmds.getAttr(networkNode + ".side")
                            jmPath = jmPath.partition(".ma")[0] + "_" + side + ".ma"

                        # torso exception
                        if moduleType == "ART_Torso":
                            numSpine = int(cmds.getAttr(networkNode + ".spineJoints"))
                            jmPath = jmPath.partition(".ma")[0].rpartition("_")[0] + "_" + str(numSpine) + "Spine.ma"

                        # head exception
                        if moduleType == "ART_Head":
                            numNeck = int(cmds.getAttr(networkNode + ".neckJoints"))
                            jmPath = jmPath.partition(".ma")[0].rpartition("_")[0] + "_" + str(numNeck) + "Neck.ma"

                        # build settings UI/build JM/Add to Outliner
                        currentAmount = cmds.progressWindow(query=True, progress=True)
                        cmds.progressWindow(edit=True, progress=currentAmount + amount)

                        moduleInst.skeletonSettings_UI(moduleName)
                        moduleInst.jointMover_Build(jmPath)
                        moduleInst.addJointMoverToOutliner()
                        moduleInst.applyModuleChanges(moduleInst)

                        # copy, reset, and paste settings to update the UI/scene one last time
                        # this was initially put in to get leaf module proxy shape/control shape to actually load in
                        # properly without this, the settings would be correct, but the scene would not update, since
                        # the combo boxes had not been hooked up yet
                        skipModules = ["ART_Torso", "ART_Head"]
                        if moduleType not in skipModules:
                            moduleInst.copySettings()
                            moduleInst.resetSettings()
                            moduleInst.pasteSettings()
                        self.moduleInstances.append(moduleInst)

                        # position the movers according to the template
                        currentAmount = cmds.progressWindow(query=True, progress=True)
                        cmds.progressWindow(edit=True, progress=currentAmount + amount)

                        # Apply the positional data
                        movers = each[2]
                        for mover in movers:
                            for each in mover:

                                moduleAttr = each[0]
                                attrValue = each[1]

                                try:
                                    cmds.setAttr(moduleAttr, attrValue)
                                except:
                                    pass

                        # bake offsets
                        moduleInst.bakeOffsets()

                        # hook up mover to parent
                        currentAmount = cmds.progressWindow(query=True, progress=True)
                        cmds.progressWindow(edit=True, progress=currentAmount + amount)

                        parent = ""
                        for attr in moduleAttrData:
                            if attr[0] == "parentModuleBone":
                                parent = attr[1]

                        mover = ""
                        if parent == "root":
                            mover = "root_mover"
                            offsetMover = "root_mover"

                        else:
                            # find the parent mover name to parent to
                            networkNodes = utils.returnRigModules()
                            mover = utils.findMoverNodeFromJointName(networkNodes, parent, False, True)
                            offsetMover = utils.findMoverNodeFromJointName(networkNodes, parent)

                        if mover is not None:
                            cmds.parentConstraint(mover, moduleName + "_mover_grp", mo = True)
                            cmds.scaleConstraint(mover, moduleName + "_mover_grp", mo = True)

                        # create the connection geo between the two
                        currentAmount = cmds.progressWindow(query=True, progress=True)
                        cmds.progressWindow(edit=True, progress=currentAmount + amount)

                        childMover = utils.findOffsetMoverFromName(moduleName)
                        riggingUtils.createBoneConnection(offsetMover, childMover, moduleName)

                        globalMover = utils.findGlobalMoverFromName(moduleName)
                        cmds.select(globalMover)
                        cmds.setToolTo("moveSuperContext")

                        utils.fitViewAndShade()

                    else:
                        solveLast.append(each)

            # solve root mover last
            for each in solveLast:
                # position the movers according to the template
                currentAmount = cmds.progressWindow(query=True, progress=True)
                cmds.progressWindow(edit=True, progress=currentAmount + amount)

                movers = each[2]
                for mover in movers:
                    for eachMover in mover:

                        moduleAttr = eachMover[0]
                        attrValue = eachMover[1]

                        try:
                            cmds.setAttr(moduleAttr, attrValue)
                        except:
                            pass

            cmds.progressWindow(endProgress=1)
            createUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findRigModules(self):
        # Original Author: Jeremy Ernst

        # get rig module files
        modulesLocation = os.path.normcase(os.path.join(self.toolsPath, "Core/Scripts/RigModules"))
        files = os.listdir(modulesLocation)
        modules = []

        for f in files:
            if f.rpartition(".")[2] == "py":
                modules.append(f)

        for mod in modules:
            niceName = mod.rpartition(".")[0]
            if niceName != "__init__" and niceName != "ART_Root":
                # create the push button for the module and set the size
                button = QtWidgets.QPushButton()
                button.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
                button.setMinimumSize(QtCore.QSize(125, 75))
                button.setMaximumSize(QtCore.QSize(125, 75))

                # get the icon path from the module and add the icon to the push button
                module = __import__("RigModules." + niceName, {}, {}, [niceName])
                reload(module)
                icon = module.icon
                hoverIcon = module.hoverIcon

                searchTerm = module.search
                className = module.className
                baseName = module.baseName
                iconFile = utils.returnFriendlyPath(os.path.join(self.iconsPath, icon))
                hoverIcon = utils.returnFriendlyPath(os.path.join(self.iconsPath, hoverIcon))

                # create stylesheet
                style = """

                QPushButton
                {
                    background-image: url(iconfilepath);
                }


                QPushButton:hover
                {
                    background-image: url(hoverfilepath);
                    margin-top: -2px;
                }

                """

                buttonStyle = style.replace("iconfilepath", iconFile)
                buttonStyle = buttonStyle.replace("hoverfilepath", hoverIcon)

                # set properties for filtering later
                button.setObjectName(searchTerm)
                button.setProperty("name", searchTerm)
                button.setStyleSheet(buttonStyle)
                self.moduleLayout.addWidget(button)

                # setup signal
                button.clicked.connect(partial(self.addModule, baseName, className))

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def searchModules(self):
        # Original Author: Jeremy Ernst

        searchText = self.moduleSearch.text()

        for i in range(self.moduleLayout.count()):
            if type(self.moduleLayout.itemAt(i).widget()) == QtWidgets.QPushButton:
                self.moduleLayout.itemAt(i).widget().setVisible(False)
                moduleType = self.moduleLayout.itemAt(i).widget().property("name")
                searchKeys = moduleType.split(":")

                for key in searchKeys:
                    if key.find(searchText) != -1:
                        self.moduleLayout.itemAt(i).widget().setVisible(True)

                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def searchInstalled(self):
        # Original Author: Jeremy Ernst

        searchText = self.installedSearch.text()

        for i in range(self.moduleSettingsLayout.count()):
            if type(self.moduleSettingsLayout.itemAt(i).widget()) == QtWidgets.QGroupBox:
                self.moduleSettingsLayout.itemAt(i).widget().setVisible(False)
                title = self.moduleSettingsLayout.itemAt(i).widget().title()

                if title.find(searchText) != -1:
                    self.moduleSettingsLayout.itemAt(i).widget().setVisible(True)


                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def editSetup(self):
        # Original Author: Jeremy Ernst

        # set model pose if exists
        for inst in self.moduleInstances:
            networkNode = inst.returnNetworkNode
            if cmds.objExists(networkNode + ".modelPose"):
                inst.setReferencePose("modelPose")

        # remove weight table script job
        cmds.scriptJob(kill=self.skinToolsInst.wtScriptJob)

        # show index 0 of stacked widget
        self.toolModeStack.setCurrentIndex(0)

        # change state in network node
        cmds.setAttr("ART_RIG_ROOT.state", 0)

        # find meshes that are weighted
        weightedMeshes = []
        skinClusters = cmds.ls(type='skinCluster')

        for cluster in skinClusters:
            geometry = cmds.skinCluster(cluster, q=True, g=True)[0]
            geoTransform = cmds.listRelatives(geometry, parent=True)[0]
            if geoTransform.find("proxy_geo") == -1:
                weightedMeshes.append([geoTransform, cluster])

        # save out weights of meshes
        for mesh in weightedMeshes:
            filePath = utils.returnFriendlyPath(os.path.join(cmds.internalVar(utd=True), mesh[0] + ".WEIGHTS"))
            print "saving out skin weights for " + mesh[0] + " at: " + filePath

            # export skin weights
            skin = riggingUtils.export_skin_weights(filePath, mesh[0])

            # delete history of meshes
            cmds.delete(mesh[0], ch=True)

        # delete skeleton
        cmds.delete("root")

        # delete proxy geo grp if it exists
        if cmds.objExists("skinned_proxy_geo"):
            cmds.delete("skinned_proxy_geo")

        # unhide/lock joint mover
        cmds.select("JointMover", hi=True)
        jmNodes = cmds.ls(sl=True)
        for node in jmNodes:
            cmds.lockNode(node, lock=False)

        lockNodes = cmds.listRelatives("JointMover", children=True)
        for node in lockNodes:
            cmds.setAttr(node + ".v", lock=False)
            cmds.setAttr(node + ".v", 1)

        # clear selection
        cmds.select(clear=True)

        # recreate outliner scriptjobs
        self.scriptJobs = []
        for module in self.moduleInstances:
            module.createScriptJob()


        ##############################################################################################################
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # EXTERNAL FILE CALLS
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        ##############################################################################################################


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def buildDeformation_UI(self):
        # Original Author: Jeremy Ernst

        import ART_SkinTools
        reload(ART_SkinTools)
        self.skinToolsInst = ART_SkinTools.ART_SkinTools(self, True, self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def deformationTools(self):
        # Original Author: Jeremy Ernst

        import ART_SkinTools
        reload(ART_SkinTools)
        self.skinToolsInst = ART_SkinTools.ART_SkinTools(self, False, interfaceUtils.getMainWindow())

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def aimModeUI(self):
        # Original Author: Jeremy Ernst

        import ART_AimModeUI
        reload(ART_AimModeUI)
        ART_AimModeUI.ART_AimMode(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pinModulesUI(self):
        # Original Author: Jeremy Ernst
        import ART_PinModules
        reload(ART_PinModules)
        ART_PinModules.ART_PinModules(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def bakeOffsetsUI(self):
        # Original Author: Jeremy Ernst

        import ART_BakeOffsetsUI
        reload(ART_BakeOffsetsUI)
        ART_BakeOffsetsUI.ART_BakeOffsets(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def boneCounterUI(self):
        # Original Author: Jeremy Ernst

        import ART_BoneCounter
        reload(ART_BoneCounter)
        inst = ART_BoneCounter.ART_BoneCounter(self)
        self.boneCounterInst = inst

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetModeUI(self):

        import ART_ResetModeUI
        reload(ART_ResetModeUI)
        ART_ResetModeUI.ART_ResetMode(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def symmetryModeUI(self):
        # Original Author: Jeremy Ernst

        import ART_SymmetryModeUI
        reload(ART_SymmetryModeUI)
        ART_SymmetryModeUI.ART_SymmetryMode(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def finalizeSetup_UI(self):
        # Original Author: Jeremy Ernst

        import ART_FinalizeSetup
        reload(ART_FinalizeSetup)
        ART_FinalizeSetup.ART_FinalizeSetup(self, self.skinToolsInst)
        # need to also pass in deformation ui instance

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildRig(self):
        # Original Author: Jeremy Ernst

        # run publish process
        import ART_Publish
        reload(ART_Publish)
        ART_Publish.ART_Publish(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def removeRigging(self):
        # Original Author: Jeremy Ernst

        # reset scale if needed
        if cmds.objExists("master_anim.globalScale"):
            cmds.setAttr("master_anim.globalScale", 1)
        cmds.refresh()

        # disconnect main deformation hiearchy
        cmds.select("root", hi=True)
        joints = cmds.ls(sl=True, type="joint")

        for joint in joints:
            attrs = ["translate", "rotate", "scale"]
            for attr in attrs:
                try:
                    cmds.disconnectAttr("driver_" + joint + "." + attr, joint + "." + attr)
                except Exception, e:
                    print str(e)

        # unlock nodes
        cmds.select("rig_grp", hi=True)
        rigNodes = cmds.ls(sl=True)
        for node in rigNodes:
            cmds.lockNode(node, lock=False)

        # go through each rig and delete that module's rigging
        for module in self.moduleInstances:
            module.deleteRig()

        # set the state of the character
        self.toolModeStack.setCurrentIndex(1)
        if cmds.objExists("ART_RIG_ROOT.state"):
            cmds.setAttr("ART_RIG_ROOT.state", 1)

        # remove outliner scriptJobs
        for job in self.scriptJobs:
            cmds.scriptJob(kill=job, force=True)

        # build the scriptJob for the weight table
        self.scriptJobs.append(self.skinToolsInst.weightTable_scriptJob())

        # delete driver skeleton
        if cmds.objExists("driver_root"):
            cmds.delete("driver_root")

        # set model pose
        for inst in self.moduleInstances:
            networkNode = inst.returnNetworkNode
            if cmds.objExists(networkNode + ".modelPose"):
                inst.setSkeletonPose("modelPose")

        # remove the skeletal constraints
        for inst in self.moduleInstances:
            networkNode = inst.returnNetworkNode
            if cmds.objExists(networkNode + ".modelPose"):
                inst.removeSkeletalConstraints()


            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def rigHistoryUI(self):

        import ART_RigHistoryUI as arh
        reload(arh)
        arh.ART_RigHistoryUI(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def moduleStatusUI(self):

        import ART_ModuleStatus as ART_ModuleStatus
        reload(ART_ModuleStatus)
        ART_ModuleStatus.run(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def unsavedChanges(self):
        # Original Author: Jeremy Ernst

        # message box for letting user know current file has unsaved changes
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("Current File Has Unsaved Changes!")
        msgBox.setDetailedText("To load a template, please create a new file and re-launch the tool.")
        ret = msgBox.exec_()

        return ret

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def exportMeshes(self):
        # Original Author: Jeremy Ernst

        # run publish process
        import ART_ExportMeshes
        reload(ART_ExportMeshes)
        inst = ART_ExportMeshes.ART_ExportMeshes(self, parent=interfaceUtils.getMainWindow())

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectNetworkNode(self):

        selection = self.nodeNetworkList.currentItem()
        cmds.select(selection.text())


##############################################################################################################
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# NON-CLASS FUNCTIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##############################################################################################################


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def createUI():
    # Original Author: Jeremy Ernst

    global parent
    global gui

    try:

        gui.close()
        gui.deleteLater()

    except:
        pass

    # if the rigCreatorUI exists delete UI
    if cmds.dockControl("pyArtRigCreatorDock", q=True, exists=True):
        cmds.deleteUI(windowObject)
        cmds.deleteUI("pyArtRigCreatorDock", control=True)

    # create an instance of the UI and add it to a Maya dock
    gui = ART_RigCreator_UI(interfaceUtils.getMainWindow())
    allowedAreas = ["left", "right"]
    dockControl = cmds.dockControl("pyArtRigCreatorDock", area="right", content=windowObject, allowedArea=allowedAreas,
                                   label=windowTitle, w=450, h=500)
    cmds.refresh(force=True)
    cmds.dockControl("pyArtRigCreatorDock", e=True, r=True)
    return gui
