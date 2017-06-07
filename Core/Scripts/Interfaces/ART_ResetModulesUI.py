__author__ = 'jeremy.ernst'

from ThirdParty.Qt import QtGui, QtCore, QtWidgets
from functools import partial
import maya.cmds as cmds
import os
import System.utils as utils
import System.interfaceUtils as interfaceUtils






class ART_ResetModules(object):
    def __init__(self, animPickerUI, parent = None):

        super(ART_ResetModules, self).__init__()


        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")
        self.scriptPath = settings.value("scriptPath")
        self.projectPath = settings.value("projectPath")

        self.pickerUI = animPickerUI

        #write out qss based on user settings
        stylesheetDir = utils.returnNicePath(self.scriptPath, "Interfaces/StyleSheets/")
        stylesheets = os.listdir(stylesheetDir)

        for sheet in stylesheets:
            interfaceUtils.writeQSS(os.path.join(stylesheetDir,sheet))

        #build the UI
        self.buildUI()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildUI(self):


        if cmds.window("pyART_ResetModulesWIN", exists = True):
            cmds.deleteUI("pyART_ResetModulesWIN", wnd = True)

        #create the main window
        self.mainWin = QtWidgets.QMainWindow(self.pickerUI)

        #create the main widget
        self.mainWidget = QtWidgets.QFrame()
        self.mainWidget.setObjectName("dark")
        self.mainWin.setCentralWidget(self.mainWidget)

        #create the mainLayout
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainWidget)

        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/animPicker.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()


        self.mainWin.setStyleSheet(self.style)


        self.mainWin.setMinimumSize(QtCore.QSize( 400, 250 ))
        self.mainWin.setMaximumSize(QtCore.QSize( 400, 250 ))
        self.mainWin.resize(400, 250)


        #set qt object name
        self.mainWin.setObjectName("pyART_ResetModulesWIN")
        self.mainWin.setWindowTitle("Reset Rig Controls")


        self.layout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.layout)

        #LEFT SIDE
        #list of modules
        self.moduleList = QtWidgets.QListWidget()
        self.moduleList.setMinimumSize(QtCore.QSize(180, 230))
        self.moduleList.setMaximumSize(QtCore.QSize(180, 230))
        self.layout.addWidget(self.moduleList)
        self.moduleList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        #RIGHT SIDE
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.rightLayout)


        #character combo
        self.characterCombo = QtWidgets.QComboBox()
        self.rightLayout.addWidget(self.characterCombo)
        self.characterCombo.setMinimumSize(QtCore.QSize(180, 60))
        self.characterCombo.setMaximumSize(QtCore.QSize(180, 60))
        self.characterCombo.setIconSize(QtCore.QSize(50,50))
        self.characterCombo.currentIndexChanged.connect(partial(self.findCharacterModules))

        #buttons
        self.selAllBtn = QtWidgets.QPushButton("Select All")
        self.selAllBtn.setMinimumWidth(180)
        self.selAllBtn.setMaximumWidth(180)
        self.rightLayout.addWidget(self.selAllBtn)
        self.selAllBtn.setObjectName("blueButton")
        self.selAllBtn.clicked.connect(partial(self.selectAllModules))

        self.clearSelBtn = QtWidgets.QPushButton("Clear Selection")
        self.clearSelBtn.setMinimumWidth(180)
        self.clearSelBtn.setMaximumWidth(180)
        self.rightLayout.addWidget(self.clearSelBtn)
        self.clearSelBtn.setObjectName("blueButton")
        self.clearSelBtn.clicked.connect(partial(self.clearModuleSelection))

        self.rightLayout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        #reset transforms button
        self.resetXformsBtn = QtWidgets.QPushButton("Reset Transformations")
        self.resetXformsBtn.setMinimumWidth(180)
        self.resetXformsBtn.setMaximumWidth(180)
        self.rightLayout.addWidget(self.resetXformsBtn)
        self.resetXformsBtn.setObjectName("blueButton")
        self.resetXformsBtn.clicked.connect(partial(self.reset))



        #show window
        self.mainWin.show()

        #populate UI
        self.findCharacters()
        self.findCharacterModules()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCharacters(self):

        allNodes= cmds.ls(type = "network")
        characterNodes = []
        for node in allNodes:
            attrs = cmds.listAttr(node)
            if "rigModules" in attrs:
                characterNodes.append(node)

        #go through each node, find the character name, the namespace on the node, and the picker attribute
        for node in characterNodes:
            try:
                namespace = cmds.getAttr(node + ".namespace")
            except:
                namespace = cmds.getAttr(node + ".name")


            #add the icon found on the node's icon path attribute to the tab
            iconPath = cmds.getAttr(node + ".iconPath")
            iconPath = utils.returnNicePath(self.projectPath, iconPath)
            icon = QtGui.QIcon(iconPath)


            self.characterCombo.addItem(icon, namespace)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCharacterModules(self, *args):

        self.moduleList.clear()

        #current character
        selectedChar = self.characterCombo.currentText()

        #get rig modules
        if cmds.objExists(selectedChar + ":" + "ART_RIG_ROOT"):
            modules = cmds.listConnections(selectedChar + ":" + "ART_RIG_ROOT.rigModules")

            for module in modules:
                modName = cmds.getAttr(module + ".moduleName")
                item = QtWidgets.QListWidgetItem(modName)
                item.setData(QtCore.Qt.UserRole, module)
                self.moduleList.addItem(item)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectAllModules(self, *args):

        self.moduleList.selectAll()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def clearModuleSelection(self, *args):

        self.moduleList.clearSelection()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def reset(self, *args):

        selected = self.moduleList.selectedItems()
        selectedChar = self.characterCombo.currentText()


        for each in selected:
            module =  each.data(QtCore.Qt.UserRole)

            #get inst
            modType = cmds.getAttr(module + ".moduleType")
            modName = cmds.getAttr(module + ".moduleName")
            mod = __import__("RigModules." + modType, {}, {}, [modType])
            reload(mod)

            #get the class name from that module file (returns Modules.ART_Root.ART_Root for example)
            moduleClass = getattr(mod, mod.className)

            #find the instance of that module
            moduleInst = moduleClass(self, modName)

            #set namespace for instance
            moduleInst.namespace = selectedChar + ":"

            moduleInst.resetRigControls(True)