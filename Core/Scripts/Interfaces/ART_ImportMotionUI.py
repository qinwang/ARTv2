'''
Created on Aug 27, 2015

@author: jeremy.ernst
'''


#import statements
from ThirdParty.Qt import QtGui, QtCore, QtWidgets
from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import os, subprocess, sys, json
import System.utils as utils
import System.interfaceUtils as interfaceUtils





class ART_ImportMotion(object):
    def __init__(self, animPickerUI, parent = None):

        super(ART_ImportMotion, self).__init__()


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


        if cmds.window("pyART_ImportMotionWIN", exists = True):
            cmds.deleteUI("pyART_ImportMotionWIN", wnd = True)

        #create the main window
        self.mainWin = QtWidgets.QMainWindow(self.pickerUI)

        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWin.setCentralWidget(self.mainWidget)

        #create the mainLayout
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/animPicker.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()


        self.mainWin.setStyleSheet(self.style)


        self.mainWin.setMinimumSize(QtCore.QSize( 600, 350 ))
        self.mainWin.setMaximumSize(QtCore.QSize( 600, 350 ))
        self.mainWin.resize(600, 350)


        #set qt object name
        self.mainWin.setObjectName("pyART_ImportMotionWIN")
        self.mainWin.setWindowTitle("Import Motion")


        #tabs
        self.importTabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.importTabs)

        #style sheet
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
        }
        QTabWidget::pane
        {
            border-top: 2px solid rgb(19,132,183);
            border-left: 2px solid rgb(19,132,183);
            border-right: 2px solid rgb(19,132,183);
            border-bottom: 2px solid rgb(19,132,183);
        }
        """

        self.importTabs.setStyleSheet(stylesheet)

        #FBX Tab
        self.fbxImportTab = QtWidgets.QWidget()
        self.importTabs.addTab(self.fbxImportTab, "FBX")

        #Anim Curve Tab
        self.animImportTab = QtWidgets.QWidget()
        self.importTabs.addTab(self.animImportTab, "Animation")



        #=======================================================================
        #=======================================================================
        #=======================================================================
        #=======================================================================
        # #FBX TAB
        #=======================================================================
        #=======================================================================
        #=======================================================================
        #=======================================================================

        #horizontal layout
        self.fbxMainLayout = QtWidgets.QHBoxLayout(self.fbxImportTab)

        #LEFT SIDE

        #module list widget
        self.fbxModuleList = QtWidgets.QListWidget()
        self.fbxMainLayout.addWidget(self.fbxModuleList)
        self.fbxModuleList.setMinimumSize(QtCore.QSize(300, 280))
        self.fbxModuleList.setMaximumSize(QtCore.QSize(300,280))
        self.fbxModuleList.setSpacing(15)
        self.fbxModuleList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)



        #RIGHT SIDE

        self.fbxRightLayout = QtWidgets.QVBoxLayout()
        self.fbxMainLayout.addLayout(self.fbxRightLayout)

        self.fbxCharacterCombo = QtWidgets.QComboBox()
        self.fbxRightLayout.addWidget(self.fbxCharacterCombo)
        self.fbxCharacterCombo.setMinimumSize(QtCore.QSize(250, 50))
        self.fbxCharacterCombo.setMaximumSize(QtCore.QSize(250, 50))
        self.fbxCharacterCombo.setIconSize(QtCore.QSize(45,45))
        self.fbxCharacterCombo.currentIndexChanged.connect(partial(self.findCharacterModules))


        self.fbxPathLayout = QtWidgets.QHBoxLayout()
        self.fbxRightLayout.addLayout(self.fbxPathLayout)

        self.fbxFilePath = QtWidgets.QLineEdit()
        self.fbxFilePath.setMinimumWidth(210)
        self.fbxFilePath.setMaximumWidth(210)
        self.fbxPathLayout.addWidget(self.fbxFilePath)
        self.fbxFilePath.setPlaceholderText("fbx file..")

        browseBtn = QtWidgets.QPushButton()
        browseBtn.setMinimumSize(25,25)
        browseBtn.setMaximumSize(25,25)
        self.fbxPathLayout.addWidget(browseBtn)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/fileBrowse.png"))
        browseBtn.setIconSize(QtCore.QSize(25,25))
        browseBtn.setIcon(icon)
        browseBtn.clicked.connect(self.fbxFileBrowse)


        self.frameOffsetLayout = QtWidgets.QHBoxLayout()
        self.fbxRightLayout.addLayout(self.frameOffsetLayout)

        frameOffset = QtWidgets.QLabel("Frame Offset:")
        frameOffset.setStyleSheet("background: transparent; font: bold;")
        self.frameOffsetLayout.addWidget(frameOffset)


        self.frameOffsetField = QtWidgets.QSpinBox()
        self.frameOffsetField.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.frameOffsetField.setRange(-1000, 10000)
        self.frameOffsetLayout.addWidget(self.frameOffsetField)


        #option to strip namespace
        self.stripNamespace = QtWidgets.QCheckBox("Strip Incoming Namespace")
        self.stripNamespace.setToolTip("If the incoming FBX has a namespace, checking this\noption will strip that namespace upon import")
        self.stripNamespace.setChecked(True)
        self.fbxRightLayout.addWidget(self.stripNamespace)


        #Save/Load Settings
        saveLoadLayout = QtWidgets.QHBoxLayout()
        self.fbxRightLayout.addLayout(saveLoadLayout)

        saveSettingsBtn = QtWidgets.QPushButton("Save Settings")
        saveSettingsBtn.setMinimumSize(120, 30)
        saveSettingsBtn.setMaximumSize(120, 30)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/save.png"))
        saveSettingsBtn.setIconSize(QtCore.QSize(25,25))
        saveSettingsBtn.setIcon(icon)
        saveLoadLayout.addWidget(saveSettingsBtn)
        saveSettingsBtn.setObjectName("blueButton")
        saveSettingsBtn.setToolTip("Save out module import settings")
        saveSettingsBtn.clicked.connect(self.saveSettings)


        loadSettingsBtn = QtWidgets.QPushButton("Load Settings")
        loadSettingsBtn.setMinimumSize(120, 30)
        loadSettingsBtn.setMaximumSize(120, 30)
        icon = QtGui.QIcon(utils.returnNicePath(self.iconsPath, "System/load.png"))
        loadSettingsBtn.setIconSize(QtCore.QSize(25,25))
        loadSettingsBtn.setIcon(icon)
        saveLoadLayout.addWidget(loadSettingsBtn)
        loadSettingsBtn.setObjectName("blueButton")
        loadSettingsBtn.setToolTip("Load and set module import settings")
        loadSettingsBtn.clicked.connect(self.loadSettings)

        #SPACER!
        self.fbxRightLayout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))


        #Button
        self.importFBXbutton = QtWidgets.QPushButton("Import")
        self.fbxRightLayout.addWidget(self.importFBXbutton)
        self.importFBXbutton.setObjectName("blueButton")
        self.importFBXbutton.setMinimumHeight(50)
        self.importFBXbutton.clicked.connect(self.fbxImport)


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

        self.characterInfo = []

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


            self.fbxCharacterCombo.addItem(icon, namespace)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findCharacterModules(self, *args):

        self.fbxModuleList.clear()

        #current character
        selectedChar = self.fbxCharacterCombo.currentText()

        #get rig modules
        if cmds.objExists(selectedChar + ":" + "ART_RIG_ROOT"):
            modules = cmds.listConnections(selectedChar + ":" + "ART_RIG_ROOT.rigModules")

            for module in modules:
                niceName = cmds.getAttr(module + ".moduleName")
                moduleType = cmds.getAttr(module + ".moduleType")


                #create widget
                item = QtWidgets.QListWidgetItem()

                widgetItem = QtWidgets.QGroupBox()
                widgetItem.setMinimumHeight(40)
                widgetItem.setProperty("module", module)
                widgetItem.setObjectName("light")

                layout = QtWidgets.QHBoxLayout(widgetItem)
                label = QtWidgets.QLabel(niceName)
                label.setStyleSheet("background: transparent; font: bold;")
                layout.addWidget(label)

                comboBox = QtWidgets.QComboBox()
                layout.addWidget(comboBox)

                #add items to combo box bases on module class var
                mod = __import__("RigModules." + moduleType, {}, {}, [moduleType])
                fbxOptions = mod.fbxImport

                for each in fbxOptions:
                    comboBox.addItem(each)

                comboBox.setCurrentIndex(1)

                self.fbxModuleList.addItem(item)
                self.fbxModuleList.setItemWidget(item, widgetItem)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbxFileBrowse(self):

        settings = QtCore.QSettings("Epic Games", "ARTv2")
        path = settings.value("ImportPath")
        if path == None:
            path = self.projectPath

        #see if export node exists, and if it does, see if there is an existing export path
        try:
            path = cmds.fileDialog2(fm = 1, okc = "Import FBX", dir = path, ff = "*.fbx")
            nicePath = utils.returnFriendlyPath(path[0])

            self.fbxFilePath.setText(nicePath)
            settings.setValue("ImportPath", nicePath)

        except:
            pass


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def fbxImport(self):


        try:
            #Maya 2015 has one click dependency on FBX. super annoying
            cmds.loadPlugin("OneClick.mll")
        except:
            pass


        #get the file path from the UI
        filePath = self.fbxFilePath.text()

        if not os.path.exists(filePath):
            cmds.warning("No such file exists")
            return


        #stripping namespace
        if self.stripNamespace.isChecked():
            #open maya standalone
            mayaPath = None
            for path in sys.path:
                if path.find("bin") != -1:
                    if path.find("bin" + os.sep) == -1:
                        mayaPath =  utils.returnFriendlyPath(os.path.join(path, "mayapy.exe"))

            #error checking
            if mayaPath == None:
                try:
                    msg = interfaceUtils.DialogMessage("Error", "Unable to locate mayapy.exe", [], 0)
                    msg.show()
                except:
                    cmds.warning("Unable to locate mayapy.exe.")
                return

            scriptPath = utils.returnNicePath(self.scriptPath, "System/ART_StripFbxNamespace.py")

            #run a subprocess, opening mayapy/mayastandlone, running our stripNameSpace script
            maya = subprocess.Popen(mayaPath + ' ' + scriptPath + ' ' + filePath, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out = maya.stdout.read()
            err = maya.stderr.read()

            print out



        #get the current character
        character = self.fbxCharacterCombo.currentText()

        #duplicate the character's root
        if cmds.objExists("root"):
            cmds.warning("There is already a skeleton in the scene with the name \"root\". Aborting")
            return

        newSkeleton = cmds.duplicate(character + ":root")
        cmds.select(newSkeleton)
        cmds.delete(constraints = True)

        #go through each module in list, find import method, and setup constraints accordingly
        moduleItems = []
        for i in range(self.fbxModuleList.count()):
            item = self.fbxModuleList.item(i)
            itemWidget = self.fbxModuleList.itemWidget(item)
            itemModule = itemWidget.property("module")

            children = itemWidget.children()
            for child in children:
                if type(child) == QtWidgets.QComboBox:
                    importMethod = child.currentText()
                    moduleItems.append([itemModule, importMethod])

        controls = []
        postModules = []

        #setup the constraints
        for each in moduleItems:
            #get inst
            modType = cmds.getAttr(each[0] + ".moduleType")
            modName = cmds.getAttr(each[0] + ".moduleName")
            mod = __import__("RigModules." + modType, {}, {}, [modType])
            reload(mod)

            #list of modules that have post bake operations needed
            specialModules = ["ART_Leg_Standard"]



            #get the class name from that module file (returns Modules.ART_Root.ART_Root for example)
            moduleClass = getattr(mod, mod.className)

            #find the instance of that module
            moduleInst = moduleClass(self, modName)

            #set namespace for instance
            moduleInst.namespace = character + ":"

            #run the module's pre import function
            moduleInst.importFBX_pre(each[1], character)

            if modType in specialModules:
                postModules.append([each[1], character,moduleInst])

            returnControls = moduleInst.importFBX(each[1], character)
            if returnControls != None:
                controls.extend(returnControls)


        #ensure that the scene is in 30fps
        cmds.currentUnit(time = 'ntsc')
        cmds.playbackOptions(min = 0, max = 100, animationStartTime = 0, animationEndTime = 100)
        cmds.currentTime(0)

        #import the FBX file
        string = "FBXImportMode -v \"exmerge\";"
        string += "FBXImport -file \"" + filePath + "\""
        string += "FBXImportFillTimeline -v true"
        mel.eval(string)


        #ensure we're on the base layer
        animLayers = cmds.ls(type = "animLayer")
        if animLayers != []:
            for layer in animLayers:
                cmds.animLayer(layer, edit = True, selected = False)
            cmds.animLayer("BaseAnimation", edit = True, selected = True, preferred = True)


        #snap timeline to length of imported animation
        cmds.select("root", hi = True)
        firstFrame = cmds.findKeyframe(cmds.ls(sl = True), which = 'first')
        lastFrame = cmds.findKeyframe(cmds.ls(sl = True),which = 'last')
        if lastFrame == firstFrame:
            lastFrame = lastFrame + 1

        cmds.playbackOptions(min = firstFrame, max = lastFrame, animationStartTime = firstFrame, animationEndTime = lastFrame)

        #BAKE!
        cmds.select(controls)
        cmds.bakeResults(simulation = True, t = (firstFrame, lastFrame))


        #Post Modules: Modules that have post-bake operations needing to be done
        for each in postModules:
            method = each[0]
            character = each[1]
            inst = each[2]

            inst.importFBX_post(method, character)


        #Clean up (delete duplicate skeleton)
        cmds.delete("root")


        #Look at frame offset, and offset animation based on that
        frameOffset = self.frameOffsetField.value()

        cmds.select(controls)
        cmds.keyframe(timeChange = frameOffset, r = True)

        firstFrame = cmds.findKeyframe( which = 'first')
        lastFrame = cmds.findKeyframe(which = 'last')
        cmds.playbackOptions(min = firstFrame, max = lastFrame, animationStartTime = firstFrame, animationEndTime = lastFrame)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def saveSettings(self):

        #loop through each of the modules and read the qComboBox value
        moduleItems = []
        for i in range(self.fbxModuleList.count()):
            item = self.fbxModuleList.item(i)
            itemWidget = self.fbxModuleList.itemWidget(item)
            itemModule = itemWidget.property("module")

            children = itemWidget.children()
            for child in children:
                if type(child) == QtWidgets.QComboBox:
                    importMethod = child.currentIndex()
                    moduleItems.append([itemModule, importMethod])

        #save import settings in the settings folder
        if not os.path.exists(os.path.join(self.toolsPath, "settings")):
            os.makedirs(os.path.join(self.toolsPath, "settings"))

        if not os.path.exists(os.path.join(self.toolsPath, "settings" + os.sep + "importSettings")):
            os.makedirs(os.path.join(self.toolsPath, "settings" + os.sep + "importSettings"))


        #open a file browser dialog for user to name file
        dialog = QtWidgets.QFileDialog(None, "Save", os.path.join(self.toolsPath, "settings" + os.sep + "importSettings"))
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setDefaultSuffix("json")
        dialog.exec_()
        fileName = dialog.selectedFiles()

        #write file
        f = open(fileName[0], 'w')
        json.dump(moduleItems, f)
        f.close()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def loadSettings(self):

        #open a file browser dialog for user to name file
        dialog = QtWidgets.QFileDialog(None, "Open", os.path.join(self.toolsPath, "settings" + os.sep + "importSettings"))
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setDefaultSuffix("json")
        dialog.exec_()
        fileName = dialog.selectedFiles()

        #open and read the file
        f = open(fileName[0], 'r')
        data = json.load(f)
        f.close()

        #find items in UI
        modules = {}
        for i in range(self.fbxModuleList.count()):
            item = self.fbxModuleList.item(i)
            itemWidget = self.fbxModuleList.itemWidget(item)
            itemModule = itemWidget.property("module")

            children = itemWidget.children()
            for child in children:
                if type(child) == QtWidgets.QComboBox:
                    modules[itemModule] = child

        #loop through data
        keys = modules.keys()
        for each in data:
            if each[0] in keys:
                comboBox = modules.get(each[0])
                comboBox.setCurrentIndex(each[1])
