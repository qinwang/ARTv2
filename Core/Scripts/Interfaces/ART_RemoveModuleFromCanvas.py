'''
Created on Aug 10, 2015

@author: jeremy
'''


#import statements
from ThirdParty.Qt import QtGui, QtCore, QtWidgets
import maya.cmds as cmds
import System.utils as utils
import System.interfaceUtils


class ART_RemoveModuleFromCanvas(object):
    def __init__(self, animPickerUI, modulesToAdd, parent = None):

        super(ART_RemoveModuleFromCanvas, self).__init__()

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")
        self.scriptPath = settings.value("scriptPath")
        self.projectPath = settings.value("projectPath")

        self.pickerUI = animPickerUI
        self.modules = []
        self.modulesToAdd = modulesToAdd

        #assign close event
        self.closeEvent = self.closeWin

        #build the UI
        self.buildUI()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildUI(self):


        if cmds.window("pyART_AddToCanvasWIN", exists = True):
            cmds.deleteUI("pyART_AddToCanvasWIN", wnd = True)

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


        self.mainWin.setMinimumSize(QtCore.QSize( 250, 400 ))
        self.mainWin.setMaximumSize(QtCore.QSize( 250, 400 ))
        self.mainWin.resize(250, 400)


        #set qt object name
        self.mainWin.setObjectName("pyART_AddToCanvasWIN")
        self.mainWin.setWindowTitle("Remove Module From Canvas")


        #label, listWidget, button
        label = QtWidgets.QLabel("Available Modules:")
        label.setProperty("boldFont", True)
        self.layout.addWidget(label)

        self.moduleList = QtWidgets.QListWidget()
        self.moduleList.setMaximumSize(230, 300)
        self.moduleList.setMinimumSize(230, 300)
        self.layout.addWidget(self.moduleList)

        #add modules to listWidget
        self.addModulesToList()

        #create remove button
        button = QtWidgets.QPushButton("Remove From Canvas")
        self.layout.addWidget(button)
        button.setObjectName("blueButton")
        button.clicked.connect(self.removeFromCanvas)


        #show ui
        self.mainWin.show()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addModulesToList(self):

        #get the current tab index and the widget
        index = self.pickerUI.characterTabs.currentIndex()
        character = self.pickerUI.characterTabs.tabToolTip(index)

        #find character nodes in the scene, and compare namespace to selected tab
        characterMods = utils.returnCharacterModules()
        nodeNamespace = ""

        for each in characterMods:
            if cmds.objExists(each + ".namespace"):
                namespace = cmds.getAttr(each + ".namespace")
                if namespace == character:
                    nodeNamespace = namespace + ":"


        for module in self.modulesToAdd:
            info = self.getCurrentCanvasTab(module)
            if info[1] != None:
                modName = cmds.getAttr(nodeNamespace + module + ".moduleName")

                #add to listWIdget
                item = QtWidgets.QListWidgetItem(modName)
                item.setData(QtCore.Qt.UserRole, module)
                self.moduleList.addItem(item)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def removeFromCanvas(self):

        selected = self.moduleList.currentItem()
        try:
            module =  selected.data(QtCore.Qt.UserRole)

            data = self.getCurrentCanvasTab(module)
            scene = data[0]
            item = data[1]
            scriptJob = item.data(5)
            scene.removeItem(item)
            cmds.scriptJob(kill = scriptJob)

            row = self.moduleList.row(selected)
            self.moduleList.takeItem(row)

        except:
            pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getCurrentCanvasTab(self, module):

        #get the current tab index and the widget
        index = self.pickerUI.characterTabs.currentIndex()
        widget = self.pickerUI.characterTabs.widget(index)
        pickerRoot = None

        children =  widget.children()
        for child in children:
            if type(child) == QtWidgets.QTabWidget:
                tab = child

                canvasIndex = tab.currentIndex()
                canvasWidget = tab.widget(canvasIndex)

                canvasChildren = canvasWidget.children()
                for canvasChild in canvasChildren:
                    if type(canvasChild) == QtWidgets.QGraphicsView:
                        view = canvasChild
                        scene = view.scene()

                        #get all items in the gfxScene
                        itemsInScene = scene.items()

                        for item in itemsInScene:
                            if type(item) == System.interfaceUtils.pickerBorderItem or item.type() == 3:
                                data = item.data(QtCore.Qt.UserRole)
                                if data == module:
                                    pickerRoot = item


        return [scene, pickerRoot]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def closeWin(self, event):


        cmds.deleteUI("pyART_AddToCanvasWIN", wnd = True)
