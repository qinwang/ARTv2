
import os
from functools import partial

import maya.cmds as cmds

import System.interfaceUtils as interfaceUtils
import System.utils as utils
from ThirdParty.Qt import QtGui, QtCore, QtWidgets


class ART_MatchOverRange(object):
    def __init__(self, animPickerUI, parent=None):

        super(ART_MatchOverRange, self).__init__()

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

        if cmds.window("pyART_MatchOverRangeWIN", exists=True):
            cmds.deleteUI("pyART_MatchOverRangeWIN", wnd=True)

        # create the main window
        self.mainWin = QtWidgets.QMainWindow(self.pickerUI)

        # create the main widget
        self.mainWidget = QtWidgets.QFrame()
        self.mainWidget.setObjectName("dark")
        self.mainWin.setCentralWidget(self.mainWidget)

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/animPicker.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()
        self.mainWin.setStyleSheet(self.style)

        # set window size
        self.mainWin.setMinimumSize(QtCore.QSize(600, 350))
        self.mainWin.setMaximumSize(QtCore.QSize(600, 350))
        self.mainWin.resize(600, 350)

        # set qt object name
        self.mainWin.setObjectName("pyART_MatchOverRangeWIN")
        self.mainWin.setWindowTitle("Match Over Frame Range")

        # horizontal layout
        self.mainLayout = QtWidgets.QHBoxLayout(self.mainWidget)

        # LEFT SIDE
        # module list widget
        self.moduleList = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.moduleList)
        # self.moduleList.setMinimumSize(QtCore.QSize(300, 280))
        # self.moduleList.setMaximumSize(QtCore.QSize(300, 280))
        self.moduleList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.moduleList.setSpacing(20)

        # RIGHT SIDE
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.rightLayout)

        self.rightLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 25, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.characterCombo = QtWidgets.QComboBox()
        self.rightLayout.addWidget(self.characterCombo)
        self.characterCombo.setMinimumHeight(50)
        self.characterCombo.setMaximumHeight(50)
        self.characterCombo.setIconSize(QtCore.QSize(50, 50))
        self.characterCombo.currentIndexChanged.connect(partial(self.findCharacterModules))

        # frame ranges

        # SPACER!
        self.rightLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.rangeLayout = QtWidgets.QHBoxLayout()
        self.rightLayout.addLayout(self.rangeLayout)

        label1 = QtWidgets.QLabel("Start:")
        label1.setStyleSheet("background: transparent;")
        self.rangeLayout.addWidget(label1)

        self.startFrame = QtWidgets.QSpinBox()
        self.startFrame.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.rangeLayout.addWidget(self.startFrame)
        self.startFrame.setRange(-10000, 10000)

        label2 = QtWidgets.QLabel("End:")
        label2.setStyleSheet("background: transparent;")
        self.rangeLayout.addWidget(label2)

        self.endFrame = QtWidgets.QSpinBox()
        self.endFrame.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.rangeLayout.addWidget(self.endFrame)
        self.endFrame.setRange(-10000, 10000)

        # SPACER!
        self.rightLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        # Button
        self.matchButton = QtWidgets.QPushButton("Match")
        self.rightLayout.addWidget(self.matchButton)
        self.matchButton.setObjectName("blueButton")
        self.matchButton.setMinimumHeight(50)
        self.matchButton.clicked.connect(self.match)

        # SPACER!
        self.rightLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 25, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # show the window
        self.mainWin.show()

        # populate UI
        self.findCharacters()
        self.findCharacterModules()

        startFrame = cmds.playbackOptions(q=True, min=True)
        endFrame = cmds.playbackOptions(q=True, max=True)

        self.startFrame.setValue(startFrame)
        self.endFrame.setValue(endFrame)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCharacters(self):

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

        # current character
        selectedChar = self.characterCombo.currentText()

        # get rig modules
        if cmds.objExists(selectedChar + ":" + "ART_RIG_ROOT"):
            modules = cmds.listConnections(selectedChar + ":" + "ART_RIG_ROOT.rigModules")

            for module in modules:
                niceName = cmds.getAttr(module + ".moduleName")
                moduleType = cmds.getAttr(module + ".moduleType")

                # create widget
                item = QtWidgets.QListWidgetItem()

                widgetItem = QtWidgets.QGroupBox()
                widgetItem.setMinimumHeight(50)
                widgetItem.setProperty("module", module)
                widgetItem.setObjectName("light")

                layout = QtWidgets.QHBoxLayout(widgetItem)

                checkBox = QtWidgets.QCheckBox(niceName)
                checkBox.setChecked(False)
                layout.addWidget(checkBox)

                comboBox = QtWidgets.QComboBox()
                layout.addWidget(comboBox)

                # add items to combo box bases on module class var
                mod = __import__("RigModules." + moduleType, {}, {}, [moduleType])
                matchData = mod.matchData

                if matchData[0] is True:
                    for each in matchData[1]:
                        comboBox.addItem(each)

                    comboBox.setCurrentIndex(1)

                    self.moduleList.addItem(item)
                    self.moduleList.setItemWidget(item, widgetItem)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def match(self):

        # get the current character
        character = self.characterCombo.currentText()

        # go through each module in list, find import method, and setup constraints accordingly
        moduleItems = []
        for i in range(self.moduleList.count()):
            item = self.moduleList.item(i)
            itemWidget = self.moduleList.itemWidget(item)
            itemModule = itemWidget.property("module")

            children = itemWidget.children()
            for child in children:

                if type(child) == QtWidgets.QCheckBox:
                    value = child.isChecked()
                    if value == False:
                        break

                if type(child) == QtWidgets.QComboBox:
                    matchMethod = child.currentText()
                    moduleItems.append([itemModule, matchMethod])

        # get frame range
        start = self.startFrame.value()
        end = self.endFrame.value()

        # loop through frame range, calling each module's match function given the match method
        if len(moduleItems) > 0:
            for i in range(start, end + 1):
                cmds.currentTime(i)
                for each in moduleItems:
                    # get inst
                    modType = cmds.getAttr(each[0] + ".moduleType")
                    modName = cmds.getAttr(each[0] + ".moduleName")
                    mod = __import__("RigModules." + modType, {}, {}, [modType])
                    reload(mod)

                    # get the class name from that module file (returns Modules.ART_Root.ART_Root for example)
                    moduleClass = getattr(mod, mod.className)

                    # find the instance of that module
                    moduleInst = moduleClass(self, modName)

                    # set namespace for instance
                    moduleInst.namespace = character + ":"

                    # call on module's match function (method, checkbox, match over range)
                    moduleInst.switchMode(each[1], None, True)
