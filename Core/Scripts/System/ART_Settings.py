from ThirdParty.Qt import QtGui, QtCore, QtWidgets

#maya 2016< maya2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken

from functools import partial
import maya.cmds as cmds
import os, json
import System.utils as utils




def getMainWindow():
    import maya.OpenMayaUI as mui
    pointer = mui.MQtUtil.mainWindow()
    #pyside QMainWindow takes in a QWidget rather than QObject
    return shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)



windowTitle = "ART_Settings"
windowObject = "pyArtSettingsWin"



class ART_Settings(QtWidgets.QMainWindow):

    def __init__(self, parent = None):

        super(ART_Settings, self).__init__(parent)
        
        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.scriptPath = settings.value("scriptPath")
        self.iconsPath = settings.value("iconPath")
        self.projPath = settings.value("projectPath")
        
        #build the UI
        self.buildSettingsUi()
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildSettingsUi(self):
        
        #fonts
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        
        fontSmall = QtGui.QFont()
        fontSmall.setPointSize(9)
        fontSmall.setBold(True)
        
        
        #images
        frameBackground =  os.path.normcase(os.path.join(self.iconsPath, "System/field_background.png"))
        if frameBackground.partition("\\")[2] != "":
            frameBackground = frameBackground.replace("\\", "/")
        
        imageBkgrd =  os.path.normcase(os.path.join(self.iconsPath, "System/toolbar_background.png"))
        if imageBkgrd.partition("\\")[2] != "":
            imageBkgrd = imageBkgrd.replace("\\", "/")
            
        imageBtnBkrd =  os.path.normcase(os.path.join(self.iconsPath, "System/blue_field_background.png"))
        if imageBtnBkrd.partition("\\")[2] != "":
            imageBtnBkrd = imageBtnBkrd.replace("\\", "/")
        
        
        
        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setStyleSheet("background-color: rgb(0, 0, 0);, color: rgb(0,0,0);")
        self.setCentralWidget(self.mainWidget)

        #set qt object name
        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        #create the mainLayout for the rig creator UI
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.resize(600, 260)
        self.setSizePolicy(mainSizePolicy)
        self.setMinimumSize(QtCore.QSize( 600, 260 ))
        self.setMaximumSize(QtCore.QSize( 600, 260 ))
        
        #create the QFrame
        self.frame = QtWidgets.QFrame()
        self.layout.addWidget(self.frame)
        self.widgetLayout = QtWidgets.QVBoxLayout(self.frame)
        
        #info page styling
        self.frame.setStyleSheet("background-image: url(" + imageBkgrd + ");")
        
        
        #MayaTools/Core : Sccipts, icons, jointmover, etc
        #MayaTools/Projects: actual project files (animation rigs, thumbnails, poses, etc)
        
        #location
        self.locationLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addLayout(self.locationLayout)
        
        #location -> label
        label = QtWidgets.QLabel("Tools Location:  ")
        self.locationLayout.addWidget(label)
        label.setFont(font)
        label.setMinimumWidth(150)
        
        #location -> line edit
        path = utils.returnFriendlyPath(self.toolsPath)
        self.locationPath = QtWidgets.QLineEdit(path)
        self.locationLayout.addWidget(self.locationPath)
        
        
        
        self.locationPath.setStyleSheet("background-image: url(" + frameBackground + "); background-color: rgb(25,175,255);")
        self.locationPath.setMinimumHeight(35)
        
        #location -> browse button
        self.locationBrowse = QtWidgets.QPushButton()
        self.locationLayout.addWidget(self.locationBrowse)
        
        self.locationBrowse.setMinimumSize(35,35)
        self.locationBrowse.setMaximumSize(35, 35)
        btnBackground =  utils.returnNicePath(self.iconsPath, "System/fileBrowse.png")
        self.locationBrowse.setStyleSheet("background-image: url(" + btnBackground + ");")
        self.locationBrowse.clicked.connect(partial(self.browse, self.locationPath))
        
        
        #scripts folder
        self.scriptsLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addLayout(self.scriptsLayout)
        
        #scripts -> label
        label = QtWidgets.QLabel("Scripts:  ")
        self.scriptsLayout.addWidget(label)
        label.setFont(fontSmall)
        label.setMinimumWidth(150)
        
        #scripts -> line edit
        path = utils.returnFriendlyPath(self.scriptPath)
        self.scriptsPath = QtWidgets.QLineEdit(path)
        self.scriptsLayout.addWidget(self.scriptsPath)
        
        self.scriptsPath.setStyleSheet("background-image: url(" + frameBackground + "); background-color: rgb(25,175,255);")
        self.scriptsPath.setMinimumHeight(35)
        
        #scripts -> browse button
        self.scriptsBrowse = QtWidgets.QPushButton()
        self.scriptsLayout.addWidget(self.scriptsBrowse)
        
        self.scriptsBrowse.setMinimumSize(35,35)
        self.scriptsBrowse.setMaximumSize(35, 35)
        self.scriptsBrowse.setStyleSheet("background-image: url(" + btnBackground + ");")
        self.scriptsBrowse.clicked.connect(partial(self.browse, self.scriptsPath))
        
        #icons folder
        self.iconsLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addLayout(self.iconsLayout)
        
        #icons -> label
        label = QtWidgets.QLabel("Icons:  ")
        self.iconsLayout.addWidget(label)
        label.setFont(fontSmall)
        label.setMinimumWidth(150)
        
        #icons -> line edit
        path = utils.returnFriendlyPath(self.iconsPath)
        self.iconPath = QtWidgets.QLineEdit(path)
        self.iconsLayout.addWidget(self.iconPath)
        
        self.iconPath.setStyleSheet("background-image: url(" + frameBackground + "); background-color: rgb(25,175,255);")
        self.iconPath.setMinimumHeight(35)
        
        #icons -> browse button
        self.iconsBrowse = QtWidgets.QPushButton()
        self.iconsLayout.addWidget(self.iconsBrowse)
        
        self.iconsBrowse.setMinimumSize(35,35)
        self.iconsBrowse.setMaximumSize(35, 35)
        self.iconsBrowse.setStyleSheet("background-image: url(" + btnBackground + ");")
        self.iconsBrowse.clicked.connect(partial(self.browse, self.iconsPath))
        
        #projects folder
        self.projectsLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addLayout(self.projectsLayout)
        
        #projects -> label
        label = QtWidgets.QLabel("Projects:  ")
        self.projectsLayout.addWidget(label)
        label.setFont(fontSmall)
        label.setMinimumWidth(150)
        
        #projects -> line edit
        path = utils.returnFriendlyPath(self.projPath)
        self.projectsPath = QtWidgets.QLineEdit(path)
        self.projectsLayout.addWidget(self.projectsPath)
        
        self.projectsPath.setStyleSheet("background-image: url(" + frameBackground + "); background-color: rgb(25,175,255);")
        self.projectsPath.setMinimumHeight(35)
        
        #projects -> browse button
        self.projectsBrowse = QtWidgets.QPushButton()
        self.projectsLayout.addWidget(self.projectsBrowse)
        
        self.projectsBrowse.setMinimumSize(35,35)
        self.projectsBrowse.setMaximumSize(35, 35)
        self.projectsBrowse.setStyleSheet("background-image: url(" + btnBackground + ");")
        self.projectsBrowse.clicked.connect(partial(self.browse, self.projectsPath))
        
        #Save button
        self.saveChangesBtn = QtWidgets.QPushButton("Save Changes")
        self.widgetLayout.addWidget(self.saveChangesBtn)
        self.saveChangesBtn.setFont(font)
        self.saveChangesBtn.setMinimumHeight(35)
        self.saveChangesBtn.setStyleSheet("background-image: url(" + imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.saveChangesBtn.clicked.connect(partial(self.saveSettings))
        
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def browse(self, lineEdit):
        
        try:
            newPath = cmds.fileDialog2(dir = self.toolsPath, fm = 3)[0]
            newPath = utils.returnFriendlyPath(newPath)
            lineEdit.setText(newPath)
            
        except:
            pass #in case user cancels on Maya's browse dialog
        
        
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def saveSettings(self):
        

        #get data from ui
        mayaToolsDir = self.locationPath.text()
        scriptDir = self.scriptsPath.text()
        iconsDir = self.iconPath.text()
        projectsDir = self.projectsPath.text()

        #save data

        settings = QtCore.QSettings("Epic Games", "ARTv2")
        settings.setValue("toolsPath", mayaToolsDir)
        settings.setValue("scriptPath", scriptDir)
        settings.setValue("iconPath", iconsDir)
        settings.setValue("projectPath", projectsDir)


        #Give message regarding data being saved, but it won't take effect until Maya is restarted.
        cmds.confirmDialog(title = "Settings Saved", message = "Please close Maya and reopen in order to have these settings take effect.")
        
        #close UI
        if cmds.window("pyArtSettingsWin", exists = True):
            cmds.deleteUI("pyArtSettingsWin", wnd = True)
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def run():
    
    if cmds.window("pyArtSettingsWin", exists = True):
        cmds.deleteUI("pyArtSettingsWin", wnd = True)
        
    gui = ART_Settings(getMainWindow())
    gui.show()

