from functools import partial
import maya.cmds as cmds
import os, json
import maya.OpenMayaUI as mui
import maya.OpenMaya as openMaya
import System.utils as utils

from ThirdParty.Qt import QtGui, QtCore, QtWidgets
#maya 2016< maya2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken



class ART_Publish():
    #Original Author: Jeremy Ernst

    def __init__(self, mainUI):

        #super(ART_Publish, self).__init__(parent = None)

        #publish file info
        self.publishFileInfo = []
        self.currentModule = None

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.projectPath = settings.value("projectPath")
        self.iconsPath = settings.value("iconPath")
        self.mainUI = mainUI


        #images
        self.imageBkgrd =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/toolbar_background.png"))
        self.imageBtnBkrd =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/blue_field_background.png"))
        self.frameBackground =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/field_background.png"))


        #build the UI
        if cmds.window("ART_PublishWin", exists = True):
            cmds.deleteUI("ART_PublishWin", wnd = True)

        #create model poses
        for inst in self.mainUI.moduleInstances:
            if inst.name != "root":
                #call on the module's bakeOffsets method
                inst.aimMode_Setup(False)
                inst.getReferencePose("modelPose")

        self.buildPublishUI()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildPublishUI(self):
        #Original Author: Jeremy Ernst

        #create the main window
        self.mainWin = QtWidgets.QMainWindow(self.mainUI)
        self.mainWin.closeEvent = self.closeWin

        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.mainWin.setStyleSheet(self.style)

        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setStyleSheet(self.style)
        self.mainWin.setCentralWidget(self.mainWidget)

        #set qt object name
        self.mainWin.setObjectName("ART_PublishWin")
        self.mainWin.setWindowTitle("Publish")

        #font
        headerFont = QtGui.QFont()
        headerFont.setPointSize(8)
        headerFont.setBold(True)

        #set size policy
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the mainLayout for the rig creator UI
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        #create the menu bar
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setMaximumHeight(20)
        self.layout.addWidget(self.menuBar)

        #add items to menu bar
        helpMenu = self.menuBar.addMenu("Help")
        helpMenu.addAction("Help On Publish..", self.publishHelp)
        helpMenu.addAction("Help On Create Rig Pose..", self.rigPoseHelp)

        self.mainWin.resize(600, 400)
        self.mainWin.setSizePolicy(mainSizePolicy)
        self.mainWin.setMinimumSize(QtCore.QSize( 600, 400 ))
        self.mainWin.setMaximumSize(QtCore.QSize( 600, 400 ))

        #Create a stackedWidget
        self.stackWidget = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stackWidget)

        #build pages
        self.createInfoPage()
        self.createProjectPage()
        self.createRigPosePage()
        self.createMeshSlicerPage()
        self.createThumbnailCreatorPage()
        self.createSummaryPage()


        #show window
        self.mainWin.show()
        self.stackWidget.setCurrentIndex(0)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createInfoPage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.infoPage = QtWidgets.QFrame()
        self.stackWidget.addWidget(self.infoPage)
        self.infoPageMainLayout = QtWidgets.QVBoxLayout(self.infoPage)
        self.infoPage.setObjectName("epic")
        self.infoPage.setStyleSheet(self.style)

        #label
        infoLabel = QtWidgets.QLabel("Publish Your Rig")
        infoLabel.setStyleSheet("background: transparent;")
        self.infoPageMainLayout.addWidget(infoLabel)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        infoLabel.setFont(font)

        #image
        self.infoFrame = QtWidgets.QFrame()
        self.infoFrame.setMinimumSize(QtCore.QSize( 560, 250 ))
        self.infoFrame.setMaximumSize(QtCore.QSize( 560, 250 ))
        self.infoPageMainLayout.addWidget(self.infoFrame)


        #add the image showing the information to the user
        image =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/publishInfo.png"))
        self.infoFrame.setStyleSheet("background-image: url(" + image + ");")

        #buttons
        self.infoPageButtonlayout = QtWidgets.QHBoxLayout()
        self.infoPageMainLayout.addLayout(self.infoPageButtonlayout)
        self.cancelPublishBtn = QtWidgets.QPushButton("Cancel")
        self.cancelPublishBtn.setMinimumHeight(50)
        self.cancelPublishBtn.setFont(font)
        self.continuePublishBtn = QtWidgets.QPushButton("Continue")
        self.continuePublishBtn.setMinimumHeight(50)
        self.continuePublishBtn.setFont(font)
        self.infoPageButtonlayout.addWidget(self.cancelPublishBtn)
        self.infoPageButtonlayout.addWidget(self.continuePublishBtn)


        #button styling
        self.cancelPublishBtn.setObjectName("blueButton")
        self.continuePublishBtn.setObjectName("blueButton")

        #button hookups
        self.cancelPublishBtn.clicked.connect(partial(self.cancelPublish))
        self.continuePublishBtn.clicked.connect(partial(self.continueToProject))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createProjectPage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.projPage = QtWidgets.QFrame()
        self.stackWidget.addWidget(self.projPage)
        self.projPageMainLayout = QtWidgets.QHBoxLayout(self.projPage)
        self.projPage.setStyleSheet(self.style)
        self.projPage.setObjectName("dark")

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)



        #the HBoxLayout will have 2 VBoxLayouts
        self.projectPageLeftColumn = QtWidgets.QVBoxLayout()
        self.projectPageRightColumn = QtWidgets.QVBoxLayout()
        self.projPageMainLayout.addLayout(self.projectPageLeftColumn)
        self.projPageMainLayout.addLayout(self.projectPageRightColumn)

        # #Left Column # #
        #2 HBox children that contain comboBox + pushButton, listWidget that lists characters in that project/group

        #project
        self.projectCbLayout = QtWidgets.QHBoxLayout()
        self.projectPageLeftColumn.addLayout(self.projectCbLayout)

        self.projectComboBox = QtWidgets.QComboBox()
        self.projectCbLayout.addWidget(self.projectComboBox)
        self.projectComboBox.setMaximumWidth(200)
        self.projectComboBox.setMaximumHeight(30)
        self.projectComboBox.currentIndexChanged.connect(self.populateGroups)
        self.projectComboBox.setToolTip("Choose a project to build the rig to.")

        self.addProjectBtn = QtWidgets.QPushButton("+")
        self.addProjectBtn.setFont(font)
        self.addProjectBtn.setMaximumWidth(30)
        self.addProjectBtn.setMaximumHeight(30)
        self.addProjectBtn.setToolTip("Add a new project to the list.")
        self.projectCbLayout.addWidget(self.addProjectBtn)
        self.addProjectBtn.clicked.connect(partial(self.addNewProject, True))
        self.addProjectBtn.setToolTip("Create a new project.")
        self.addProjectBtn.setObjectName("blueButton")

        #group
        self.groupCbLayout = QtWidgets.QHBoxLayout()
        self.projectPageLeftColumn.addLayout(self.groupCbLayout)

        self.groupComboBox = QtWidgets.QComboBox()
        self.groupCbLayout.addWidget(self.groupComboBox)
        self.groupComboBox.setMaximumWidth(200)
        self.groupComboBox.setMaximumHeight(30)
        self.groupComboBox.currentIndexChanged.connect(self.populateCharacters)
        self.groupComboBox.setToolTip("Choose a group to build the rig to in the selected project. (optional)")

        self.addGroupBtn = QtWidgets.QPushButton("+")
        self.addGroupBtn.setFont(font)
        self.addGroupBtn.setMaximumWidth(30)
        self.addGroupBtn.setMaximumHeight(30)
        self.addGroupBtn.setToolTip("Add a new group to the list.")
        self.groupCbLayout.addWidget(self.addGroupBtn)
        self.addGroupBtn.clicked.connect(self.addNewGroup)
        self.addGroupBtn.setToolTip("Create a new group.")
        self.addGroupBtn.setObjectName("blueButton")



        #listWidget
        self.characterList = QtWidgets.QListWidget()
        self.characterList.setMaximumWidth(230)
        self.projectPageLeftColumn.addWidget(self.characterList)
        self.characterList.itemClicked.connect(self.setCharacterName)
        self.characterList.setToolTip("List of characters in the specified character and group.")
        self.characterList.setFont(font)
        self.characterList.setSpacing(3)

        # #Right Column # #
        #line edit for character name, 2 hboxLayouts for pre/post script path lineEdits + pushButtons, spacers, and continue button

        #character name
        style = """
        QLineEdit
        {
            border: 2px solid rgb(0,0,0);
            border-radius: 5px;
            background-color: rgb(80,80,80);
            font: bold 30px;
            selection-background-color: black;
        }

        QLineEdit::focus
        {
            border: 1px solid rgb(25,175,255);

        }
        """
        self.characterName = QtWidgets.QLineEdit()
        self.projectPageRightColumn.addWidget(self.characterName)
        self.characterName.setMinimumHeight(75)
        self.characterName.setMaximumHeight(75)
        self.characterName.setPlaceholderText("Asset Name")
        self.characterName.setStyleSheet(style)
        self.characterName.setAlignment(QtCore.Qt.AlignCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.projectPageRightColumn.addItem(spacerItem)
        self.characterName.setToolTip("Name the asset will be published with.")

        #character node
        characterNode = utils.returnCharacterModule()
        attrs = cmds.listAttr(characterNode, ud = True)

        #select character, if applicable
        version = 0
        for attr in attrs:
            if attr.find("version") == 0:
                version = cmds.getAttr(characterNode + ".version")

        if version > 0:
            #change type (for versioning)
            self.changeTypeLayout = QtWidgets.QHBoxLayout()
            self.projectPageRightColumn.addLayout(self.changeTypeLayout)

            label = QtWidgets.QLabel("Change Type:")
            label.setStyleSheet("background: transparent;")
            self.changeTypeLayout.addWidget(label)
            self.changeType = QtWidgets.QComboBox()
            self.changeTypeLayout.addWidget(self.changeType)

            self.changeType.addItem("Cosmetic Change")
            self.changeType.addItem("Minor Change")
            self.changeType.addItem("Major Change")
            self.changeType.setToolTip("The type of change that was done, leading to a republish.")

            #add note box for revision
            noteLabel = QtWidgets.QLabel("Revision Note (optional):")
            noteLabel.setStyleSheet("background: transparent;")
            self.projectPageRightColumn.addWidget(noteLabel)

            self.revisionNote = QtWidgets.QTextEdit()
            self.projectPageRightColumn.addWidget(self.revisionNote)
            self.revisionNote.setObjectName("light")

        spacerItem = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.projectPageRightColumn.addItem(spacerItem)


        #pre script
        self.preScriptLayout = QtWidgets.QHBoxLayout()
        self.projectPageRightColumn.addLayout(self.preScriptLayout)

        self.preScriptLineEdit = QtWidgets.QLineEdit()
        self.preScriptLineEdit.setMinimumHeight(30)
        self.preScriptLineEdit.setMaximumHeight(30)
        self.preScriptLineEdit.setPlaceholderText("Pre-Script (optional)")
        self.preScriptLayout.addWidget(self.preScriptLineEdit)
        self.preScriptLineEdit.setToolTip("If you want to run any custom code before the rig is built, load in a MEL or Python script here.")

        self.preScriptBrowse = QtWidgets.QPushButton()
        self.preScriptLayout.addWidget(self.preScriptBrowse)
        self.preScriptBrowse.setMinimumSize(35,35)
        self.preScriptBrowse.setMaximumSize(35, 35)
        self.preScriptBrowse.clicked.connect(partial(self.addCustomScripts, True, False))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/fileBrowse.png"))
        self.preScriptBrowse.setIconSize(QtCore.QSize(30,30))
        self.preScriptBrowse.setIcon(icon)

        #post script
        self.postScriptLayout = QtWidgets.QHBoxLayout()
        self.projectPageRightColumn.addLayout(self.postScriptLayout)

        self.postScriptLineEdit = QtWidgets.QLineEdit()
        self.postScriptLineEdit.setMinimumHeight(30)
        self.postScriptLineEdit.setMaximumHeight(30)
        self.postScriptLineEdit.setPlaceholderText("Post-Script (optional)")
        self.postScriptLayout.addWidget(self.postScriptLineEdit)
        self.postScriptLineEdit.setToolTip("If you want to run any custom code after the rig is built, load in a MEL or Python script here.")

        self.postScriptBrowse = QtWidgets.QPushButton()
        self.postScriptLayout.addWidget(self.postScriptBrowse)
        self.postScriptBrowse.setMinimumSize(35,35)
        self.postScriptBrowse.setMaximumSize(35, 35)
        self.postScriptBrowse.clicked.connect(partial(self.addCustomScripts, False, True))
        icon = QtGui.QIcon(os.path.join(self.iconsPath, "System/fileBrowse.png"))
        self.postScriptBrowse.setIconSize(QtCore.QSize(30,30))
        self.postScriptBrowse.setIcon(icon)


        spacerItem = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.projectPageRightColumn.addItem(spacerItem)


        #continue btn
        self.goToRigPoseBtn = QtWidgets.QPushButton("Continue")
        self.goToRigPoseBtn.setFont(font)
        self.goToRigPoseBtn.setMinimumHeight(50)
        self.goToRigPoseBtn.setMaximumHeight(50)
        self.projectPageRightColumn.addWidget(self.goToRigPoseBtn)
        self.goToRigPoseBtn.clicked.connect(self.createNewCharacter)
        self.goToRigPoseBtn.setObjectName("blueButton")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createRigPosePage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.rigPosePage = QtWidgets.QFrame()
        self.rigPosePage.setMinimumSize(560, 250)
        self.stackWidget.addWidget(self.rigPosePage)
        self.rpPageMainLayout = QtWidgets.QHBoxLayout(self.rigPosePage)
        self.rigPosePage.setStyleSheet(self.style)
        self.rigPosePage.setObjectName("dark")

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        #the HBoxLayout will have 2 VBoxLayouts
        self.rpPageLeftColumn = QtWidgets.QVBoxLayout()
        self.rpPageRightColumn = QtWidgets.QVBoxLayout()
        self.rpPageMainLayout.addLayout(self.rpPageLeftColumn)
        self.rpPageMainLayout.addLayout(self.rpPageRightColumn)


        #left column (list of modules, back button)
        self.rpPage_moduleList = QtWidgets.QListWidget()
        self.rpPage_moduleList.setMinimumSize(200, 280)
        self.rpPage_moduleList.setMaximumSize(200, 280)
        self.rpPageLeftColumn.addWidget(self.rpPage_moduleList)
        self.rpPage_moduleList.setToolTip("This list of modules make up your character.\nSelect a module from the list to alter the rig \npose for that module.\n\nA rig pose is the ideal pose for each\nmodule for rigging. For legs, this means that\nthe leg is coplanar for the IK solve and\nthe feet are aligned to the world.\n\nFor arms, the same. It's the T-Pose that's\nbest suited to building the rig, since models\nare not always built in that pose.")
        self.rpPage_moduleList.setFont(font)
        self.rpPage_moduleList.setSpacing(3)

        #populate list
        modules = utils.returnRigModules()
        for mod in modules:
            name = cmds.getAttr(mod + ".moduleName")
            if name != "root":
                self.rpPage_moduleList.addItem(name)

        self.rpPage_moduleList.itemClicked.connect(self.moduleSelected)

        #button layout
        self.rpPage_leftButtonLayout = QtWidgets.QHBoxLayout()
        self.rpPageLeftColumn.addLayout(self.rpPage_leftButtonLayout)
        self.rpPage_leftButtonLayout.setContentsMargins(0,0,100,0)

        #button/spacer
        self.rpPage_backButton = QtWidgets.QPushButton("Back")
        self.rpPage_leftButtonLayout.addWidget(self.rpPage_backButton)
        self.rpPage_backButton.setFont(font)
        self.rpPage_backButton.setMinimumHeight(50)
        self.rpPage_backButton.setMaximumHeight(50)
        self.rpPage_backButton.clicked.connect(self.backToProject)
        self.rpPage_backButton.setObjectName("blueButton")


        #right column (scrollArea for module settings)

        #scroll area contents
        self.rpPage_scrollContents = QtWidgets.QFrame()
        scrollSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.rpPage_scrollContents.setSizePolicy(scrollSizePolicy)
        self.rpPage_scrollContents.setObjectName("dark")


        #scroll area
        self.rpPage_Settings = QtWidgets.QScrollArea()
        self.rpPage_Settings.setMinimumSize(350, 280)
        self.rpPage_Settings.setMaximumSize(350, 280)
        self.rpPageRightColumn.addWidget(self.rpPage_Settings)
        self.rpPage_Settings.setWidgetResizable(True)
        self.rpPage_Settings.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.rpPage_Settings.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.rpPage_Settings.setWidget(self.rpPage_scrollContents)


        #layout for scroll area
        self.rpPage_layout = QtWidgets.QVBoxLayout(self.rpPage_scrollContents)

        #stacked widget
        self.rpPage_stackWidget = QtWidgets.QStackedWidget()
        self.rpPage_layout.addWidget(self.rpPage_stackWidget)


        #message
        self.message = QtWidgets.QLabel("Select a module from the list to adjust the rig pose for that module.")
        self.message.setStyleSheet("background: transparent;")
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.rpPage_stackWidget.addWidget(self.message)

        #button layout
        self.rpPage_righttButtonLayout = QtWidgets.QHBoxLayout()
        self.rpPageRightColumn.addLayout(self.rpPage_righttButtonLayout)
        self.rpPage_righttButtonLayout.setContentsMargins(100,0,0,0)

        #button/spacer
        self.rpPage_continueButton = QtWidgets.QPushButton("Continue")
        self.rpPage_righttButtonLayout.addWidget(self.rpPage_continueButton)
        self.rpPage_continueButton.setFont(font)
        self.rpPage_continueButton.setMinimumHeight(50)
        self.rpPage_continueButton.setMaximumHeight(50)
        self.rpPage_continueButton.clicked.connect(partial(self.continueToCreateAnimMesh))
        self.rpPage_continueButton.setObjectName("blueButton")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createMeshSlicerPage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.meshSlicerPage = QtWidgets.QFrame()
        self.meshSlicerPage.setMinimumSize(560, 250)
        self.stackWidget.addWidget(self.meshSlicerPage)
        self.msPageMainLayout = QtWidgets.QVBoxLayout(self.meshSlicerPage)

        #info page styling
        self.meshSlicerPage.setStyleSheet(self.style)
        self.meshSlicerPage.setObjectName("epic")

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        #create the label for the instructional gif
        self.movie_screen = QtWidgets.QLabel()

        # expand and center the label
        self.movie_screen.setAlignment(QtCore.Qt.AlignCenter)
        self.msPageMainLayout.addWidget(self.movie_screen)

        #set movie from file path
        gif = utils.returnFriendlyPath(os.path.join(self.iconsPath, "Help/meshSlicer.gif"))
        self.movie = QtGui.QMovie(gif, QtCore.QByteArray())
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)

        #button layout
        self.msPageButtonLayout = QtWidgets.QHBoxLayout()
        self.msPageMainLayout.addLayout(self.msPageButtonLayout)

        self.msPageBackBtn = QtWidgets.QPushButton("Back")
        self.msPageBackBtn.setMinimumHeight(50)
        self.msPageBackBtn.setFont(font)
        self.msPageBackBtn.clicked.connect(partial(self.backToRigPose))
        self.msPageBackBtn.setObjectName("blueButton")

        self.msPageSkipBtn = QtWidgets.QPushButton("Skip")
        self.msPageSkipBtn.setMinimumHeight(50)
        self.msPageSkipBtn.setFont(font)
        self.msPageSkipBtn.clicked.connect(partial(self.skipToCreateThumbnail))
        self.msPageSkipBtn.setObjectName("blueButton")

        self.mePageContBtn = QtWidgets.QPushButton("Continue")
        self.mePageContBtn.setMinimumHeight(50)
        self.mePageContBtn.setFont(font)
        self.mePageContBtn.clicked.connect(partial(self.continueToCreateThumbnail))
        self.mePageContBtn.setObjectName("blueButton")

        self.msPageButtonLayout.addWidget(self.msPageBackBtn)
        spacer = QtWidgets.QSpacerItem(200, 20)
        self.msPageButtonLayout.addSpacerItem(spacer)
        self.msPageButtonLayout.addWidget(self.msPageSkipBtn)
        self.msPageButtonLayout.addWidget(self.mePageContBtn)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createThumbnailCreatorPage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.thumbCreatorPage = QtWidgets.QFrame()
        self.thumbCreatorPage.setMinimumSize(560, 250)
        self.stackWidget.addWidget(self.thumbCreatorPage)
        self.tcPageMainLayout = QtWidgets.QVBoxLayout(self.thumbCreatorPage)

        #info page styling
        self.thumbCreatorPage.setStyleSheet(self.style)
        self.thumbCreatorPage.setObjectName("dark")

        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)

        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(12)
        buttonFont.setBold(True)


        #viewport and tabs layout
        self.tcPageViewportLayout = QtWidgets.QHBoxLayout()
        self.tcPageMainLayout.addLayout(self.tcPageViewportLayout)
        self.viewportToggle = QtWidgets.QStackedWidget()
        self.viewportToggle.setMinimumSize(200,200)
        self.viewportToggle.setMaximumSize(200,200)
        self.tcPageViewportLayout.addWidget(self.viewportToggle)

        #custom image loaded
        self.customImg = QtWidgets.QFrame()
        self.customImg.setMinimumSize(200,200)
        self.customImg.setMaximumSize(200,200)
        self.viewportToggle.addWidget(self.customImg)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #first element in this layout is our viewport

        #create the camera for the viewport
        self.thumbnailCamera = cmds.camera(name = "thumbnail_camera")[0]
        constraint = cmds.parentConstraint("persp", self.thumbnailCamera)
        cmds.setAttr(self.thumbnailCamera + ".v", 0)
        cmds.lockNode(self.thumbnailCamera, lock = True)

        #create light rig
        self.lightGrp = cmds.group(empty = True, name = "thumbnail_lights")

        #key light
        self.spot1 = cmds.spotLight(rgb = (.902, .785, .478), name = "thumbnail_spot1", ca = 100, do = 1)
        cmds.setAttr(self.spot1 + ".useDepthMapShadows", 1)
        self.spot1Parent = cmds.listRelatives(self.spot1, parent = True)[0]
        cmds.setAttr(self.spot1Parent + ".tx", 150)
        cmds.setAttr(self.spot1Parent + ".ty", -150)
        cmds.setAttr(self.spot1Parent + ".tz", 300)
        aim = cmds.aimConstraint("root", self.spot1Parent, aimVector = [0,0,-1], upVector = [0,1,0], worldUpType = "scene")[0]
        cmds.delete(aim)

        #bounce light
        self.spot2 = cmds.spotLight(rgb = (.629, .799, .949), name = "thumbnail_spot2", ca = 100, do = 1)
        cmds.setAttr(self.spot2 + ".useDepthMapShadows", 1)
        self.spot2Parent = cmds.listRelatives(self.spot2, parent = True)[0]
        cmds.setAttr(self.spot2Parent + ".tx", -150)
        cmds.setAttr(self.spot2Parent + ".ty", -150)
        cmds.setAttr(self.spot2Parent + ".tz", 300)
        aim = cmds.aimConstraint("root", self.spot2Parent, aimVector = [0,0,-1], upVector = [0,1,0], worldUpType = "scene")[0]
        cmds.delete(aim)

        #fill light
        self.spot3 = cmds.spotLight(rgb = (1, 1, 1), name = "thumbnail_spot3", ca = 100, do = 1)
        cmds.setAttr(self.spot3 + ".useDepthMapShadows", 1)
        self.spot3Parent = cmds.listRelatives(self.spot3, parent = True)[0]
        cmds.setAttr(self.spot3Parent + ".tx", 0)
        cmds.setAttr(self.spot3Parent + ".ty", 150)
        cmds.setAttr(self.spot3Parent + ".tz", 300)
        aim = cmds.aimConstraint("root", self.spot3Parent, aimVector = [0,0,-1], upVector = [0,1,0], worldUpType = "scene")[0]
        cmds.delete(aim)

        cmds.parent([self.spot1Parent, self.spot2Parent, self.spot3Parent], self.lightGrp)

        cmds.lockNode(self.spot1Parent, lock = True)
        cmds.lockNode(self.spot2Parent, lock = True)
        cmds.lockNode(self.spot3Parent, lock = True)
        cmds.lockNode(self.lightGrp, lock = True)


        #model editor
        self.tcViewport = cmds.modelEditor(camera = self.thumbnailCamera, dl = "all", da = "smoothShaded", hud = False, gr = False, dtx = True, sdw = True, j = False, ca = False, lt = False)
        pointer = mui.MQtUtil.findControl(self.tcViewport)
        self.tcViewWidget = shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)
        self.viewportToggle.addWidget(self.tcViewWidget)
        self.tcViewWidget.setMinimumSize(200,200)
        self.tcViewWidget.setMaximumSize(200,200)
        self.viewportToggle.setCurrentIndex(1)

        #add image plane with image
        imagePlanePath = utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/imagePlane.png"))
        self.imagePlane = cmds.imagePlane(fn = imagePlanePath, c = self.thumbnailCamera, lt = self.thumbnailCamera, sia = False )
        cmds.setAttr(self.imagePlane[1] + ".depth", 3000)
        cmds.setAttr(self.imagePlane[1] + ".sizeX", 2)
        cmds.setAttr(self.imagePlane[1] + ".sizeY", 2)

        #second element in this layout is a tabWidget

        #tab stylesheet (tab stylesheet via QSS doesn't seem to work for some reason
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


        self.tcPageTabs = QtWidgets.QTabWidget()
        self.tcPageTabs.setStyleSheet(stylesheet)
        self.tcPageViewportLayout.addWidget(self.tcPageTabs)
        self.tcPageTabs.setMinimumHeight(200)
        self.tcPageTabs.setMaximumHeight(200)



        # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # #
        #rendering tab
        self.renderTab = QtWidgets.QFrame()
        self.tcPageTabs.addTab(self.renderTab, "LIGHT OPTIONS")
        self.renderTab.setObjectName("epic")

        #rendering tab main layout
        self.renderTabLayout = QtWidgets.QHBoxLayout(self.renderTab)
        self.renderTabLayout.setSpacing(10)

        #left column of render tab options
        self.renderTabLeft = QtWidgets.QVBoxLayout()
        self.renderTabLayout.addLayout(self.renderTabLeft)

        icon = utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/spotLight.png"))


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #light 1
        self.light1Layout = QtWidgets.QHBoxLayout()
        self.renderTabLeft.addLayout(self.light1Layout)

        self.light1Img = QtWidgets.QPushButton("")
        self.light1Img.setFont(font)
        self.light1Img.setMinimumSize(40,40)
        self.light1Img.setMaximumSize(40,40)
        self.light1Img.setStyleSheet("background-image: url(" + icon + "); border: black solid 0px;")
        self.light1Layout.addWidget(self.light1Img)

        self.light1Dial = QtWidgets.QDial()
        self.light1Dial.setToolTip("Light Intensity")
        self.light1Layout.addWidget(self.light1Dial)
        self.light1Dial.setMinimumSize(50,50)
        self.light1Dial.setMaximumSize(50,50)
        self.light1Dial.setRange(0,100)
        self.light1Dial.setValue(50)
        shadow1 = QtWidgets.QGraphicsDropShadowEffect(self.light1Dial)
        shadow1.setBlurRadius(5)
        shadow1.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light1Dial.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.light1Dial.setGraphicsEffect(shadow1)
        self.light1Dial.valueChanged.connect(partial(self.changeLightIntensity, self.spot1, self.light1Dial))

        self.light1Swatch = QtWidgets.QPushButton("Color")
        self.light1Layout.addWidget(self.light1Swatch)
        self.light1Swatch.setMinimumSize(60,30)
        self.light1Swatch.setMaximumSize(60,30)
        self.light1Swatch.setFont(buttonFont)
        self.light1Swatch.setStyleSheet("color: rgb(230, 200, 122);")
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(self.light1Swatch)
        shadow2.setBlurRadius(5)
        shadow2.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light1Swatch.setGraphicsEffect(shadow2)
        self.light1Swatch.clicked.connect(partial(self.changeLightColor, self.spot1, self.light1Swatch))

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #light 2
        self.light2Layout = QtWidgets.QHBoxLayout()
        self.renderTabLeft.addLayout(self.light2Layout)

        self.light2Img = QtWidgets.QPushButton("")
        self.light2Img.setFont(font)
        self.light2Img.setMinimumSize(40,40)
        self.light2Img.setMaximumSize(40,40)
        self.light2Img.setStyleSheet("background-image: url(" + icon + "); border: black solid 0px;")
        self.light2Layout.addWidget(self.light2Img)

        self.light2Dial = QtWidgets.QDial()
        self.light2Dial.setToolTip("Light Intensity")
        self.light2Layout.addWidget(self.light2Dial)
        self.light2Dial.setMinimumSize(50,50)
        self.light2Dial.setMaximumSize(50,50)
        self.light2Dial.setRange(0,100)
        self.light2Dial.setValue(50)
        shadow1 = QtWidgets.QGraphicsDropShadowEffect(self.light2Dial)
        shadow1.setBlurRadius(5)
        shadow1.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light2Dial.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.light2Dial.setGraphicsEffect(shadow1)
        self.light2Dial.valueChanged.connect(partial(self.changeLightIntensity, self.spot2, self.light2Dial))

        self.light2Swatch = QtWidgets.QPushButton("Color")
        self.light2Layout.addWidget(self.light2Swatch)
        self.light2Swatch.setMinimumSize(60,30)
        self.light2Swatch.setMaximumSize(60,30)
        self.light2Swatch.setFont(buttonFont)
        self.light2Swatch.setStyleSheet("color: rgb(160, 204, 242);")
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(self.light2Swatch)
        shadow2.setBlurRadius(5)
        shadow2.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light2Swatch.setGraphicsEffect(shadow2)
        self.light2Swatch.clicked.connect(partial(self.changeLightColor, self.spot2, self.light2Swatch))

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #light 3
        self.light3Layout = QtWidgets.QHBoxLayout()
        self.renderTabLeft.addLayout(self.light3Layout)

        self.light3Img = QtWidgets.QPushButton("")
        self.light3Img.setFont(font)
        self.light3Img.setMinimumSize(40,40)
        self.light3Img.setMaximumSize(40,40)
        self.light3Img.setStyleSheet("background-image: url(" + icon + "); border: black solid 0px;")
        self.light3Layout.addWidget(self.light3Img)

        self.light3Dial = QtWidgets.QDial()
        self.light3Dial.setToolTip("Light Intensity")
        self.light3Layout.addWidget(self.light3Dial)
        self.light3Dial.setMinimumSize(50,50)
        self.light3Dial.setMaximumSize(50,50)
        self.light3Dial.setRange(0,100)
        self.light3Dial.setValue(50)
        shadow1 = QtWidgets.QGraphicsDropShadowEffect(self.light3Dial)
        shadow1.setBlurRadius(5)
        shadow1.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light3Dial.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.light3Dial.setGraphicsEffect(shadow1)
        self.light3Dial.valueChanged.connect(partial(self.changeLightIntensity, self.spot3, self.light3Dial))

        self.light3Swatch = QtWidgets.QPushButton("Color")
        self.light3Layout.addWidget(self.light3Swatch)
        self.light3Swatch.setMinimumSize(60,30)
        self.light3Swatch.setMaximumSize(60,30)
        self.light3Swatch.setFont(buttonFont)
        self.light3Swatch.setStyleSheet("color: rgb(255, 255, 255);")
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(self.light3Swatch)
        shadow2.setBlurRadius(5)
        shadow2.setColor(QtGui.QColor (0, 0, 0, 255))
        self.light3Swatch.setGraphicsEffect(shadow2)
        self.light3Swatch.clicked.connect(partial(self.changeLightColor, self.spot3, self.light3Swatch))


        #right column
        self.renderTabRight = QtWidgets.QVBoxLayout()
        self.renderTabLayout.addLayout(self.renderTabRight)


        #orbit layout
        self.orbitLayout = QtWidgets.QHBoxLayout()
        self.renderTabRight.addLayout(self.orbitLayout)


        label = QtWidgets.QLabel("Orbit: ")
        label.setStyleSheet("background: transparent;")
        label.setFont(buttonFont)
        label.setMinimumHeight(30)
        label.setMaximumHeight(30)
        self.orbitLayout.addWidget(label)

        self.orbitDial = QtWidgets.QDial()
        self.orbitDial.setToolTip("Light Rig Position")
        self.orbitLayout.addWidget(self.orbitDial)
        self.orbitDial.setMinimumSize(75,75)
        self.orbitDial.setMaximumSize(75,75)
        self.orbitDial.setRange(0,360)
        self.orbitDial.setValue(0)
        shadow = QtWidgets.QGraphicsDropShadowEffect(self.orbitDial)
        shadow.setBlurRadius(5)
        shadow.setColor(QtGui.QColor (0, 0, 0, 255))
        self.orbitDial.setGraphicsEffect(shadow)
        self.orbitDial.valueChanged.connect(partial(self.orbitLights, self.lightGrp, self.orbitDial))


        #pitch layout
        self.pitchLayout = QtWidgets.QHBoxLayout()
        self.renderTabRight.addLayout(self.pitchLayout)


        label = QtWidgets.QLabel("Pitch: ")
        label.setStyleSheet("background: transparent;")
        label.setFont(buttonFont)
        label.setMinimumHeight(30)
        label.setMaximumHeight(30)
        self.pitchLayout.addWidget(label)


        self.pitchSlider = QtWidgets.QSlider()
        self.pitchSlider.setOrientation(QtCore.Qt.Horizontal)
        self.pitchSlider.setToolTip("Light Aim Height")
        self.pitchSlider.setRange(-180, 180)
        self.pitchLayout.addWidget(self.pitchSlider)
        self.pitchSlider.valueChanged.connect(partial(self.pitchLights, [self.spot1Parent, self.spot2Parent, self.spot3Parent], self.pitchSlider))

        #options layout
        self.tcPageOptionsLayout = QtWidgets.QHBoxLayout()
        self.tcPageMainLayout.addLayout(self.tcPageOptionsLayout)

        self.hqRenderCB = QtWidgets.QCheckBox("High Quality")
        self.tcPageOptionsLayout.addWidget(self.hqRenderCB)
        self.hqRenderCB.clicked.connect(partial(self.highQualityToggle))
        self.hqRenderCB.setChecked(False)


        self.shadowsCB = QtWidgets.QCheckBox("Shadows")
        self.tcPageOptionsLayout.addWidget(self.shadowsCB)
        self.shadowsCB.setChecked(False)
        self.shadowsCB.clicked.connect(partial(self.shadowsToggle, [self.spot1, self.spot2, self.spot3]))

        self.customThumbnail = QtWidgets.QLineEdit()
        self.tcPageOptionsLayout.addWidget(self.customThumbnail)
        self.customThumbnail.setStyleSheet("background-image: url(" + self.frameBackground + ");")

        self.loadThumbBtn = QtWidgets.QPushButton("Load Custom")
        self.tcPageOptionsLayout.addWidget(self.loadThumbBtn)
        self.loadThumbBtn.clicked.connect(self.loadCustomImg)
        self.loadThumbBtn.setObjectName("blueButton")

        #button layout
        self.tcPageButtonLayout = QtWidgets.QHBoxLayout()
        self.tcPageMainLayout.addLayout(self.tcPageButtonLayout)

        self.tcPageBackBtn = QtWidgets.QPushButton("Back")
        self.tcPageBackBtn.setMinimumHeight(50)
        self.tcPageBackBtn.setFont(font)
        self.tcPageBackBtn.clicked.connect(partial(self.backToMeshSlicer))
        self.tcPageBackBtn.setObjectName("blueButton")

        self.tcPageContBtn = QtWidgets.QPushButton("Continue")
        self.tcPageContBtn.setMinimumHeight(50)
        self.tcPageContBtn.setFont(font)
        self.tcPageContBtn.clicked.connect(partial(self.continueToSummary, False))
        self.tcPageContBtn.setObjectName("blueButton")

        self.tcPageButtonLayout.addWidget(self.tcPageBackBtn)
        spacer = QtWidgets.QSpacerItem(200, 20)
        self.tcPageButtonLayout.addSpacerItem(spacer)
        self.tcPageButtonLayout.addWidget(self.tcPageContBtn)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createSummaryPage(self):
        #Original Author: Jeremy Ernst

        #create the QFrame for this page
        self.summaryPage = QtWidgets.QFrame()
        self.summaryPage.setMinimumSize(560, 250)
        self.stackWidget.addWidget(self.summaryPage)
        self.sumPageMainLayout = QtWidgets.QVBoxLayout(self.summaryPage)

        #info page styling
        self.summaryPage.setStyleSheet(self.style)
        self.summaryPage.setObjectName("epic")

        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)

        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(12)
        buttonFont.setBold(True)

        #top section of UI will contain Hbox layout with icon and character information
        self.sumPageTopLayout = QtWidgets.QHBoxLayout()
        self.sumPageMainLayout.addLayout(self.sumPageTopLayout)

        #left side of top layout
        self.sumPageIcon = QtWidgets.QFrame()
        self.sumPageIcon.setMinimumSize(200,200)
        self.sumPageIcon.setMaximumSize(200,200)
        self.sumPageTopLayout.addWidget(self.sumPageIcon)
        shadow = QtWidgets.QGraphicsDropShadowEffect(self.sumPageIcon)
        shadow.setBlurRadius(5)
        shadow.setColor(QtGui.QColor (0, 0, 0, 255))
        self.sumPageIcon.setGraphicsEffect(shadow)



        #right side of top layout (vbox with 5 hbox children)
        self.sumPageTopRight = QtWidgets.QVBoxLayout()
        self.sumPageTopLayout.addLayout(self.sumPageTopRight)


        #character name
        assetNameLayout = QtWidgets.QHBoxLayout()
        self.sumPageTopRight.addLayout(assetNameLayout)
        assetNameLayout.setContentsMargins(3,0,3,0)

        label = QtWidgets.QLabel("Asset Name: ")
        label.setStyleSheet("background: transparent;")
        assetNameLayout.addWidget(label)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setMinimumWidth(80)
        label.setMaximumWidth(80)

        self.sumPageAssetName = QtWidgets.QLineEdit()
        assetNameLayout.addWidget(self.sumPageAssetName)
        self.sumPageAssetName.setMinimumWidth(240)
        self.sumPageAssetName.setMaximumWidth(240)
        self.sumPageAssetName.setAlignment(QtCore.Qt.AlignRight)
        self.sumPageAssetName.setReadOnly(True)

        #project
        projLayout = QtWidgets.QHBoxLayout()
        self.sumPageTopRight.addLayout(projLayout)
        projLayout.setContentsMargins(3,0,3,0)

        label = QtWidgets.QLabel("Project: ")
        label.setStyleSheet("background: transparent;")
        projLayout.addWidget(label)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setMinimumWidth(80)
        label.setMaximumWidth(80)

        self.sumPageProj = QtWidgets.QLineEdit()
        projLayout.addWidget(self.sumPageProj)
        self.sumPageProj.setMinimumWidth(240)
        self.sumPageProj.setMaximumWidth(240)
        self.sumPageProj.setAlignment(QtCore.Qt.AlignRight)
        self.sumPageProj.setReadOnly(True)


        #group
        groupNameLayout = QtWidgets.QHBoxLayout()
        self.sumPageTopRight.addLayout(groupNameLayout)
        groupNameLayout.setContentsMargins(3,0,3,0)

        label = QtWidgets.QLabel("Group: ")
        label.setStyleSheet("background: transparent;")
        groupNameLayout.addWidget(label)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setMinimumWidth(80)
        label.setMaximumWidth(80)

        self.sumPageGroup = QtWidgets.QLineEdit()
        groupNameLayout.addWidget(self.sumPageGroup)
        self.sumPageGroup.setMinimumWidth(240)
        self.sumPageGroup.setMaximumWidth(240)
        self.sumPageGroup.setAlignment(QtCore.Qt.AlignRight)
        self.sumPageGroup.setReadOnly(True)


        #revision type
        revisionTypeLayout = QtWidgets.QHBoxLayout()
        self.sumPageTopRight.addLayout(revisionTypeLayout)
        revisionTypeLayout.setContentsMargins(3,0,3,0)

        label = QtWidgets.QLabel("Revision Type: ")
        label.setStyleSheet("background: transparent;")
        revisionTypeLayout.addWidget(label)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setMinimumWidth(80)
        label.setMaximumWidth(80)

        self.sumPageRevisionType = QtWidgets.QLineEdit()
        revisionTypeLayout.addWidget(self.sumPageRevisionType)
        self.sumPageRevisionType.setMinimumWidth(240)
        self.sumPageRevisionType.setMaximumWidth(240)
        self.sumPageRevisionType.setAlignment(QtCore.Qt.AlignRight)
        self.sumPageRevisionType.setReadOnly(True)


        #options
        optionsLayout = QtWidgets.QHBoxLayout()
        self.sumPageTopRight.addLayout(optionsLayout)
        optionsLayout.setContentsMargins(3,0,3,0)

        self.sp_preScriptCB = QtWidgets.QCheckBox("Pre-Script?")
        optionsLayout.addWidget(self.sp_preScriptCB)
        self.sp_preScriptCB.setEnabled(False)

        self.sp_postScriptCB = QtWidgets.QCheckBox("Post-Script?")
        optionsLayout.addWidget(self.sp_postScriptCB)
        self.sp_postScriptCB.setEnabled(False)

        self.sp_animMeshCB = QtWidgets.QCheckBox("Animation Mesh?")
        optionsLayout.addWidget(self.sp_animMeshCB)
        self.sp_animMeshCB.setEnabled(False)


        #button layout
        self.sp_PageButtonLayout = QtWidgets.QHBoxLayout()
        self.sumPageMainLayout.addLayout(self.sp_PageButtonLayout)

        self.sp_PageBackBtn = QtWidgets.QPushButton("Back")
        self.sp_PageBackBtn.setMinimumHeight(50)
        self.sp_PageBackBtn.setFont(font)
        self.sp_PageBackBtn.clicked.connect(partial(self.backToMeshIconCreation))
        self.sp_PageBackBtn.setObjectName("blueButton")


        self.sp_PageContBtn = QtWidgets.QPushButton("BUILD")
        self.sp_PageContBtn.setMinimumHeight(50)
        self.sp_PageContBtn.setFont(font)
        self.sp_PageContBtn.clicked.connect(partial(self.launchBuild))
        self.sp_PageContBtn.setObjectName("blueButton")

        self.sp_PageButtonLayout.addWidget(self.sp_PageBackBtn)
        spacer = QtWidgets.QSpacerItem(200, 20)
        self.sp_PageButtonLayout.addSpacerItem(spacer)
        self.sp_PageButtonLayout.addWidget(self.sp_PageContBtn)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def highQualityToggle(self):

        state = self.hqRenderCB.isChecked()

        if state:
            cmds.modelEditor(self.tcViewport, edit = True, rnm = "ogsRenderer")

        if not state:
            cmds.modelEditor(self.tcViewport, edit = True, rnm = "base_OpenGL_Renderer")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def shadowsToggle(self, lights):

        state = self.shadowsCB.isChecked()

        for light in lights:
            cmds.setAttr(light + ".useDepthMapShadows", state)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pitchLights(self, lights, slider, *args):

        value = slider.value()

        for light in lights:
            cmds.setAttr(light + ".rotateX", value)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeLightIntensity(self, light, dial, *args):

        #get dial value
        value = dial.value()
        value = float(value)/50.0

        cmds.setAttr(light + ".intensity", value)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeLightColor(self, light, button, *args):

        #launch color dialog
        self.qColorDialog = QtWidgets.QColorDialog.getColor()
        color = self.qColorDialog.getRgb()
        red = float(color[0])
        green = float(color[1])
        blue = float(color[2])

        cmds.setAttr(light + ".colorR", float(red/255))
        cmds.setAttr(light + ".colorG", float(green/255))
        cmds.setAttr(light + ".colorB", float(blue/255))

        button.setStyleSheet("color: rgb(" + str(red) + "," + str(green) + "," + str(blue) + ");")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def orbitLights(self, group, dial, *args):

        value = dial.value()
        cmds.setAttr(group + ".rotateZ", value)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def loadCustomImg(self):

        try:
            imgPath = cmds.fileDialog2(fm = 1, dir = self.iconsPath)[0]
            imgPath = utils.returnFriendlyPath(imgPath)

            #check to make sure image is valid
            extension = imgPath.rpartition(".")[2]
            if extension != "png":
                cmds.warning("Please upload only png files!")
            else:
                self.customImg.setStyleSheet("background-image: url(" + imgPath + ");")
                self.customThumbnail.setText(imgPath)
                self.viewportToggle.setCurrentIndex(0)

        except:
            cmds.warning("No File Chosen")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def moduleSelected(self):
        #Original Author: Jeremy Ernst

        currentSelection = cmds.ls(sl = True)

        #run toggleMoverVisibility
        self.mainUI.setMoverVisibility()

        #clean up current module
        if self.currentModule != None:
            self.currentModule.cleanUpRigPose()

        #find the currently selected module
        selected = self.rpPage_moduleList.selectedItems()
        module = selected[0].text()

        #find the network node this module belongs to
        networkNode = None
        modules = utils.returnRigModules()
        for mod in modules:
            modName = cmds.getAttr(mod + ".moduleName")
            if modName == module:
                networkNode = mod
                break

        #find the instance in memory of the selected module
        if networkNode != None:

            for inst in  self.mainUI.moduleInstances:

                if inst.returnNetworkNode == networkNode:

                    #call on module's method for unhiding and constraining joints
                    inst.setupForRigPose()

                    #call on the module's getRigPose method
                    inst.getReferencePose("rigPose")

                    #call on the module's rigPose_UI method
                    index = self.rpPage_stackWidget.indexOf(inst.rigPoseFrame)
                    self.rpPage_stackWidget.setCurrentIndex(index)

                    #set current module
                    self.currentModule = inst

        cmds.select(clear = True)
        if len(currentSelection) > 0:
            cmds.select(currentSelection)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateProjects(self):
        #Original Author: Jeremy Ernst

        #if the project path doesn't exist on disk, create it
        if not os.path.exists(self.projectPath):
            os.makedirs(self.projectPath)

        #get a list of the existing folders in projects
        existingProjects = os.listdir(self.projectPath)
        folders = []

        #find out which returned items are directories
        for each in existingProjects:
            if os.path.isdir(os.path.join(self.projectPath, each)):
                folders.append(each)

        #if there are no projects, bring up add project interface
        if len(folders) == 0:
            self.addNewProject(False)

        #otherwise, add each project to the combo box
        else:
            self.projectComboBox.clear()
            for each in folders:
                self.projectComboBox.addItem(each)


        #find selected project and populate groups
        self.populateGroups()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateGroups(self):
        #Original Author: Jeremy Ernst

        #get a list of the existing folders in projects
        selectedProject = self.projectComboBox.currentText()
        project = os.path.join(self.projectPath, selectedProject)
        existingGroups = os.listdir(project)
        folders = []

        #find out which returned items are directories
        for each in existingGroups:
            if os.path.isdir(os.path.join(project, each)):
                folders.append(each)

        #otherwise, add each project to the combo box
        self.groupComboBox.clear()
        self.groupComboBox.addItem(" ")
        for each in folders:
            self.groupComboBox.addItem(each)


        #populate characters
        self.populateCharacters()
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateCharacters(self):
        #Original Author: Jeremy Ernst

        #get a list of the existing folders in projects
        selectedProject = self.projectComboBox.currentText()
        fullPath = os.path.join(self.projectPath, selectedProject)
        selectedGroup = self.groupComboBox.currentText()
        if len(selectedGroup) > 1:
            fullPath = os.path.join(fullPath, selectedGroup)

        existingCharacters = os.listdir(fullPath)
        files = []

        #find out which returned items are directories
        for each in existingCharacters:
            if os.path.isfile(os.path.join(fullPath, each)):
                if each.rpartition(".")[2] == "ma":
                    files.append(each)

        #otherwise, add each project to the combo box
        self.characterList.clear()


        for each in files:
            item = QtWidgets.QListWidgetItem(each.partition(".ma")[0])
            self.characterList.addItem(item)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addNewProject(self, fromButton):
        #Original Author: Jeremy Ernst

        #simple UI for user to add new Project
        if cmds.window("ART_Publish_AddNewProjUI", exists = True):
            cmds.deleteUI("ART_Publish_AddNewProjUI", wnd = True)

        #launch a UI to get the name information
        self.addNewProjWindow = QtWidgets.QMainWindow(self.mainWin)

        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the main widget
        self.addNewProjWindow_mainWidget = QtWidgets.QWidget()
        self.addNewProjWindow.setCentralWidget(self.addNewProjWindow_mainWidget)

        #set qt object name
        self.addNewProjWindow.setObjectName("ART_Publish_AddNewProjUI")
        self.addNewProjWindow.setWindowTitle("Add New Project")

        #create the mainLayout for the rig creator UI
        self.addNewProjWindow_mainLayout = QtWidgets.QVBoxLayout(self.addNewProjWindow_mainWidget)
        self.addNewProjWindow_mainLayout.setContentsMargins(0, 0, 0, 0)

        self.addNewProjWindow.resize(300, 100)
        self.addNewProjWindow.setSizePolicy(mainSizePolicy)
        self.addNewProjWindow.setMinimumSize(QtCore.QSize( 300, 100 ))
        self.addNewProjWindow.setMaximumSize(QtCore.QSize( 300, 100 ))

        #add stackWidget for ability to swap between two different pages (page 1: No projects exist. page 2: add new project)
        self.addNewProjWindow_stackWidget = QtWidgets.QStackedWidget()
        self.addNewProjWindow_mainLayout.addWidget(self.addNewProjWindow_stackWidget)


        #NO PROJECT EXISTS PAGE

        #add background image/QFrame for first page
        page1Widget = QtWidgets.QWidget()
        self.addNewProjWindow_stackWidget.addWidget(page1Widget)

        self.addNewProjWindow_frame = QtWidgets.QFrame(page1Widget)
        self.addNewProjWindow_frame.setMinimumSize(QtCore.QSize( 300, 100 ))
        self.addNewProjWindow_frame.setMaximumSize(QtCore.QSize( 300, 100 ))
        self.addNewProjWindow_frame.setStyleSheet("background-image: url(" + self.imageBkgrd + ");")

        #Add simple VBoxLayout for page
        self.addNewProjWindow_page1Layout = QtWidgets.QVBoxLayout(self.addNewProjWindow_frame)

        #add label
        label = QtWidgets.QLabel("No projects exist in this directory. Would you like to add one now?")
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.addNewProjWindow_page1Layout.addWidget(label)

        #add buttons for Yes/Cancel
        self.addNewProjWinPage1_buttonLayout = QtWidgets.QHBoxLayout()
        self.addNewProjWindow_page1Layout.addLayout(self.addNewProjWinPage1_buttonLayout)

        self.addNewProjWinPage1_CancelButton = QtWidgets.QPushButton("Cancel")
        self.addNewProjWinPage1_buttonLayout.addWidget(self.addNewProjWinPage1_CancelButton)
        self.addNewProjWinPage1_CancelButton.setStyleSheet("background-image: url(" + self.imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.addNewProjWinPage1_CancelButton.clicked.connect(self.addNewProjWindow.close)


        self.addNewProjWinPage1_YesButton = QtWidgets.QPushButton("Yes")
        self.addNewProjWinPage1_buttonLayout.addWidget(self.addNewProjWinPage1_YesButton)
        self.addNewProjWinPage1_YesButton.setStyleSheet("background-image: url(" + self.imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.addNewProjWinPage1_YesButton.clicked.connect(partial(self.addNewProjWindow_stackWidget.setCurrentIndex,1))



        #ADD NEW PROJECT PAGE

        #add background image/QFrame for first page
        page2Widget = QtWidgets.QWidget()
        self.addNewProjWindow_stackWidget.addWidget(page2Widget)

        self.addNewProjWinPage2_frame = QtWidgets.QFrame(page2Widget)
        self.addNewProjWinPage2_frame.setMinimumSize(QtCore.QSize( 300, 100 ))
        self.addNewProjWinPage2_frame.setMaximumSize(QtCore.QSize( 300, 100 ))
        self.addNewProjWinPage2_frame.setStyleSheet("background-image: url(" + self.imageBkgrd + ");")

        #Add simple VBoxLayout for page
        self.addNewProjWindow_page2Layout = QtWidgets.QVBoxLayout(self.addNewProjWinPage2_frame)

        #line edit for writing project name
        self.addNewProjLineEdit = QtWidgets.QLineEdit()
        self.addNewProjLineEdit.setPlaceholderText("Project Name")
        self.addNewProjWindow_page2Layout.addWidget(self.addNewProjLineEdit)
        self.addNewProjLineEdit.setStyleSheet("background-image: url(" + self.frameBackground + ");")


        #add project button
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        self.addNewProj_AddButton = QtWidgets.QPushButton("Create New Project")
        self.addNewProjWindow_page2Layout.addWidget(self.addNewProj_AddButton)
        self.addNewProj_AddButton.setFont(font)
        self.addNewProj_AddButton.setStyleSheet("background-image: url(" + self.imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.addNewProj_AddButton.clicked.connect(self.createNewProject)

        #show the ui
        self.addNewProjWindow.show()

        if not fromButton:
            self.addNewProjWindow_stackWidget.setCurrentIndex(0)
        if fromButton:
            self.addNewProjWindow_stackWidget.setCurrentIndex(1)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addNewGroup(self):
        #Original Author: Jeremy Ernst

        #simple UI for user to add new Group
        if cmds.window("ART_Publish_AddNewGrpUI", exists = True):
            cmds.deleteUI("ART_Publish_AddNewGrpUI", wnd = True)

        #launch a UI to get the name information
        self.addNewGrpWin = QtWidgets.QMainWindow(self.mainWin)

        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the main widget
        self.addNewGrpWin_mainWidget = QtWidgets.QWidget()
        self.addNewGrpWin.setCentralWidget(self.addNewGrpWin_mainWidget)

        #set qt object name
        self.addNewGrpWin.setObjectName("ART_Publish_AddNewGrpUI")
        self.addNewGrpWin.setWindowTitle("Add New Group")

        #create the mainLayout for the rig creator UI
        self.addNewGrpWin_mainLayout = QtWidgets.QVBoxLayout(self.addNewGrpWin_mainWidget)
        self.addNewGrpWin_mainLayout.setContentsMargins(0, 0, 0, 0)

        self.addNewGrpWin.resize(300, 100)
        self.addNewGrpWin.setSizePolicy(mainSizePolicy)
        self.addNewGrpWin.setMinimumSize(QtCore.QSize( 300, 100 ))
        self.addNewGrpWin.setMaximumSize(QtCore.QSize( 300, 100 ))


        #add background image/QFrame for first page
        self.addNewGrpWin_frame = QtWidgets.QFrame()
        self.addNewGrpWin_mainLayout.addWidget(self.addNewGrpWin_frame)
        self.addNewGrpWin_frame.setMinimumSize(QtCore.QSize( 300, 100 ))
        self.addNewGrpWin_frame.setMaximumSize(QtCore.QSize( 300, 100 ))
        self.addNewGrpWin_frame.setStyleSheet("background-image: url(" + self.imageBkgrd + ");")

        #create vertical layout
        self.addNewGrpWin_vLayout = QtWidgets.QVBoxLayout(self.addNewGrpWin_frame)

        #line edit for writing group name
        self.addNewGrpWinLineEdit = QtWidgets.QLineEdit()
        self.addNewGrpWinLineEdit.setPlaceholderText("Group Name")
        self.addNewGrpWin_vLayout.addWidget(self.addNewGrpWinLineEdit)
        self.addNewGrpWinLineEdit.setStyleSheet("background-image: url(" + self.frameBackground + ");")


        #add group button
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)

        self.addNewGrpWin_AddButton = QtWidgets.QPushButton("Create New Group")
        self.addNewGrpWin_vLayout.addWidget(self.addNewGrpWin_AddButton)
        self.addNewGrpWin_AddButton.setFont(font)
        self.addNewGrpWin_AddButton.setStyleSheet("background-image: url(" + self.imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.addNewGrpWin_AddButton.clicked.connect(self.createNewGroup)

        #show the ui
        self.addNewGrpWin.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def setCharacterName(self):
        #Original Author: Jeremy Ernst

        selected = self.characterList.currentItem().text()
        self.characterName.setText(selected)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createNewProject(self):
        #Original Author: Jeremy Ernst

        #get name from lineEdit
        projectName = self.addNewProjLineEdit.text()
        if len(projectName) == 0:
            cmds.warning("No valid Project Name entered.")
            return

        #make sure there are no naming conflicts
        existingProjects = os.listdir(self.projectPath)
        if projectName in existingProjects:
            cmds.warning("Project with that name already exists. Aborting..")
            return

        #make the directory
        path = os.path.join(self.projectPath, projectName)
        os.makedirs(path)

        #close the ui
        self.addNewProjWindow.close()

        #repopulate
        self.populateProjects()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createNewGroup(self):
        #Original Author: Jeremy Ernst

        #get name from lineEdit
        groupName = self.addNewGrpWinLineEdit.text()
        if len(groupName) == 0:
            cmds.warning("No valid Group Name entered.")
            return

        #make sure there are no naming conflicts
        selectedProject = self.projectComboBox.currentText()
        project = os.path.join(self.projectPath, selectedProject)
        existingGroups = os.listdir(project)

        if groupName in existingGroups:
            cmds.warning("Group with that name already exists. Aborting..")
            return

        #make the directory
        path = os.path.join(project, groupName)
        os.makedirs(path)

        #close the ui
        self.addNewGrpWin.close()

        #repopulate
        self.populateGroups()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createNewCharacter(self):
        #Original Author: Jeremy Ernst

        #get character name from lineEdit
        characterName = self.characterName.text()
        toContinue = False

        #get existing names in characterList
        existingCharacters = []
        for i in range(self.characterList.count()):
            existingCharacters.append(self.characterList.item(i).text())

        #check if name is unique. If not, ask if user wants to overwrite
        if characterName not in existingCharacters:
            toContinue = True

        else:
            toContinue = self.overwriteCharacterUI()

        if toContinue:

            #if the name is not an empty string, proceed.
            if len(characterName) > 0:

                #check for attributes on ART_RIG_ROOT node
                characterNode = utils.returnCharacterModule()
                firstVersion = False

                if cmds.objExists(characterNode + ".project") == False:
                    cmds.addAttr(characterNode, ln = "project", dt = "string", keyable = True)

                if cmds.objExists(characterNode + ".group") == False:
                    cmds.addAttr(characterNode, ln = "group", dt = "string", keyable = True)

                if cmds.objExists(characterNode + ".name") == False:
                    cmds.addAttr(characterNode, ln = "name", dt = "string", keyable = True)

                if cmds.objExists(characterNode + ".version") == False:
                    cmds.addAttr(characterNode, ln = "version", keyable = True)
                    firstVersion = True

                if cmds.objExists(characterNode + ".versionNote") == False:
                    cmds.addAttr(characterNode, ln = "versionNote", dt = "string", keyable = True)

                if cmds.objExists(characterNode + ".publishedBy") == False:
                    cmds.addAttr(characterNode, ln = "publishedBy", dt = "string", keyable = True)


                #get data from UI
                projectName = self.projectComboBox.currentText()
                groupName = self.groupComboBox.currentText()
                charName = self.characterName.text()

                #get user
                for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
                    user = os.environ.get(name)
                cmds.setAttr(characterNode + ".publishedBy", user, type = "string")


                #version character
                if firstVersion:
                    cmds.setAttr(characterNode + ".version", 1)
                    cmds.setAttr(characterNode + ".versionNote", json.dumps([[1, "initial checkin", cmds.getAttr(characterNode + ".publishedBy")]]), type = "string")

                #if this is not the firstVersion, check to see if it's technically being saved as a new file
                if not firstVersion:
                    #get current data off node
                    currentProj = cmds.getAttr(characterNode + ".project")
                    currentGrp = cmds.getAttr(characterNode + ".group")
                    currentName = cmds.getAttr(characterNode + ".name")

                    if type(currentGrp) == type(None):
                        currentGrp = " "


                    #figure out if this is truly a new version, or if this is getting published as something else
                    doVersion = False
                    if projectName == currentProj:
                        if groupName == currentGrp:
                            if charName == currentName:
                                doVersion = True

                    if doVersion:
                        currentVersion = cmds.getAttr(characterNode + ".version")

                        #find type of revision
                        changeType = self.changeType.currentText()
                        if changeType == "Cosmetic Change":
                            value = .01
                        if changeType == "Minor Change":
                            value = .1
                        if changeType == "Major Change":
                            value = 1

                        cmds.setAttr(characterNode + ".version", currentVersion + value)

                    else:
                        cmds.setAttr(characterNode + ".version", 1)
                        cmds.setAttr(characterNode + ".versionNote", json.dumps([1, "initial checkin", cmds.getAttr(characterNode + ".publishedBy")]), type = "string")

                    #version note
                    string = self.revisionNote.toPlainText()
                    revisionHistory = json.loads(cmds.getAttr(characterNode + ".versionNote"))
                    revisionHistory.append([cmds.getAttr(characterNode + ".version"), string, cmds.getAttr(characterNode + ".publishedBy")])
                    cmds.setAttr(characterNode + ".versionNote", json.dumps(revisionHistory), type = "string")

                #set data on characterNode
                cmds.setAttr(characterNode + ".project", projectName, type = "string")
                cmds.setAttr(characterNode + ".group", groupName, type = "string")
                cmds.setAttr(characterNode + ".name", charName, type = "string")



                #save maya ascii file in path
                selectedProject = self.projectComboBox.currentText()
                fullPath = os.path.join(self.projectPath, selectedProject)
                selectedGroup = self.groupComboBox.currentText()
                if len(selectedGroup) > 1:
                    fullPath = os.path.join(fullPath, selectedGroup)
                else:
                    selectedGroup = None

                #save file
                fullPath = utils.returnFriendlyPath(os.path.join(fullPath, charName + ".ma"))
                cmds.file(rename = fullPath)
                cmds.file(save = True, type = "mayaAscii")


                #repopulate character list
                self.populateCharacters()

                #add info to publishFileInfo
                self.publishFileInfo.append([fullPath, selectedProject, selectedGroup, charName])


                #go to next page
                self.continueToRigPose()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def overwriteCharacterUI(self):
        #Original Author: Jeremy Ernst

        #message box for confirming if character should be overwritten or not
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("A character already exists with the given name!")
        msgBox.addButton("Overwrite", QtWidgets.QMessageBox.YesRole)
        msgBox.addButton("Cancel", QtWidgets.QMessageBox.NoRole)
        ret = msgBox.exec_()

        if ret == 1:
            return False
        else:
            return True

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def overwriteIconUI(self, path):
        #Original Author: Jeremy Ernst

        #message box for confirming if icon should be overwritten or not
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText("This asset already has an icon associated with it.")
        msgBox.addButton("Overwrite", QtWidgets.QMessageBox.YesRole)
        msgBox.addButton("Keep Current Icon", QtWidgets.QMessageBox.NoRole)
        msgBox.setDetailedText("Current Icon:\n\n" + path)
        ret = msgBox.exec_()

        if ret == 1:
            return False
        else:
            return True



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def cancelPublish(self):
        #Original Author: Jeremy Ernst

        cmds.deleteUI("ART_PublishWin", wnd = True)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def continueToProject(self):
        #Original Author: Jeremy Ernst

        self.stackWidget.setCurrentIndex(1)

        #populate projects
        self.populateProjects()

        #populate project page info if it exists on character node
        characterNode = utils.returnCharacterModule()

        attrs = cmds.listAttr(characterNode, ud = True)
        for attr in attrs:
            #set project if applicable
            if attr.find("project") == 0:
                project = cmds.getAttr(characterNode + ".project")
                for i in range(self.projectComboBox.count()):
                    item = self.projectComboBox.itemText(i)
                    if item == project:
                        self.projectComboBox.setCurrentIndex(i)

            #set group if applicable
            if attr.find("group") == 0:
                group = cmds.getAttr(characterNode + ".group")
                for i in range(self.groupComboBox.count()):
                    item = self.groupComboBox.itemText(i)
                    if item == group:
                        self.groupComboBox.setCurrentIndex(i)

            #select character, if applicable
            if attr.find("name") == 0:
                name = cmds.getAttr(characterNode + ".name")
                for i in range(self.characterList.count()):
                    item = self.characterList.item(i).text()
                    if item == name:
                        self.characterList.setCurrentRow(i)
                        self.setCharacterName()

            #set pre-script, if applicable
            if attr.find("preScriptPath") == 0:
                path = cmds.getAttr(characterNode + ".preScriptPath")
                self.preScriptLineEdit.setText(path)

            #set post-script, if applicable
            if attr.find("postScriptPath") == 0:
                path = cmds.getAttr(characterNode + ".postScriptPath")
                self.postScriptLineEdit.setText(path)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def continueToRigPose(self):
        #Original Author: Jeremy Ernst

        self.stackWidget.setCurrentIndex(2)

        self.mainWin.setWindowTitle("Create Rig Pose")

        #if pre/post script slots are empty, and the attrs exist, remove attrs
        characterModule = utils.returnCharacterModule()

        if self.preScriptLineEdit.text() == "":
            if cmds.objExists(characterModule + ".preScriptPath"):
                cmds.deleteAttr(characterModule, at = "preScriptPath")

        if self.postScriptLineEdit.text() == "":
            if cmds.objExists(characterModule + ".postScriptPath"):
                cmds.deleteAttr(characterModule, at = "postScriptPath")


        #setup the interfaces
        for inst in self.mainUI.moduleInstances:
            listItems = []
            for i in range(self.rpPage_moduleList.count()):

                text = self.rpPage_moduleList.item(i).text()
                listItems.append(text)

            if inst.name in listItems:
                inst.rigPose_UI(self.rpPage_stackWidget)

            #set slider states if attribute exists
            networkNode = inst.returnNetworkNode
            if cmds.objExists(networkNode + ".rigPoseState"):
                sliderData = json.loads(cmds.getAttr(networkNode + ".rigPoseState"))


                #create progress bar
                progBar = QtWidgets.QProgressDialog(self.mainWin)
                progBar.setCancelButton(None)
                progBar.setStyleSheet(self.style)
                progBar.setLabelText("Setting rig pose slider values for " + inst.name)
                progBar.setMinimum(0)

                #get the slider children, if there is a match between the name property and the name data in the list, set slider value
                sliders = inst.rigPoseFrame.findChildren(QtWidgets.QSlider)

                progBar.setMaximum(len(sliders))
                progBar.show()

                for slider in sliders:
                    name = slider.property("name")
                    progBar.setValue(progBar.value() + 1)

                    for data in sliderData:
                        sliderName = data.get("name")

                        if sliderName == name:
                            value = data.get("value")
                            inst.setupForRigPose()
                            slider.setValue(value)
                            if cmds.objExists(networkNode + ".rigPose"):
                                inst.setReferencePose("rigPose")
                            inst.cleanUpRigPose()

                progBar.deleteLater()


        self.rpPage_stackWidget.setCurrentIndex(0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def continueToCreateAnimMesh(self):
        #Original Author: Jeremy Ernst

        #save slider states and rig pose
        for inst in self.mainUI.moduleInstances:
            if inst.name != "root":
                networkNode = inst.returnNetworkNode
                inst.cleanUpRigPose()

                #add attr if it doesn't exist
                if not cmds.objExists(networkNode + ".rigPoseState"):
                    cmds.addAttr(networkNode, ln = "rigPoseState", dt = "string")

                #if rig pose doesn't exist, get and set it
                inst.getReferencePose("rigPose", False)


                #get the sliders from this widget (name and value)
                sliderList = []
                sliders = inst.rigPoseFrame.findChildren(QtWidgets.QSlider)
                for slider in sliders:
                    sliderData = {}
                    sliderData["name"] = slider.property("name")
                    sliderData["value"] = slider.value()

                    sliderList.append(sliderData)

                #set the rigPoseState attr
                jsonString = json.dumps(sliderList)
                cmds.setAttr(networkNode + ".rigPoseState", jsonString, type = "string")

        #get the character node
        characterNode = utils.returnCharacterModule()

        #go to next UI page
        self.mainWin.setWindowTitle("Create Animation Mesh")
        self.stackWidget.setCurrentIndex(3)
        self.movie.start()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skipToCreateThumbnail(self):
        #Original Author: Jeremy Ernst

        #get the character node
        characterNode = utils.returnCharacterModule()

        #get the icon path if present
        if cmds.objExists(characterNode + ".iconPath"):
            path = cmds.getAttr(characterNode + ".iconPath")
            if os.path.exists(utils.returnNicePath(self.projectPath,path)):
                toContinue = self.overwriteIconUI(path)

                # if the user wants to overwrite the existing icon
                if toContinue:

                    self.stackWidget.setCurrentIndex(4)
                    self.mainWin.setWindowTitle("Create Thumbnail")
                # if the user wants to keep the existing icon
                else:
                    self.continueToSummary(True)

            # if the icon path did not exist on disc
            else:
                self.stackWidget.setCurrentIndex(4)
                self.mainWin.setWindowTitle("Create Thumbnail")

        else:
            self.stackWidget.setCurrentIndex(4)
            self.mainWin.setWindowTitle("Create Thumbnail")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def continueToCreateThumbnail(self):
        #Original Author: Jeremy Ernst

        #get the character node
        characterNode = utils.returnCharacterModule()

        #get asset name
        name = cmds.getAttr(characterNode + ".name")

        #get LOD0 meshes
        if cmds.objExists(characterNode + ".LOD_0"):
            jsonData = json.loads(cmds.getAttr(characterNode + ".LOD_0"))
            meshes = jsonData.get("Meshes")
        else:
            meshes = utils.findAllSkinnableGeo()

        for mesh in meshes:
            newMesh = utils.splitMesh(mesh, name)
            cmds.select(newMesh)

            #select all new meshes and add to layer if layer doesn't exist
            if not cmds.objExists("Animation_Mesh_Geo"):
                cmds.createDisplayLayer(newMesh, name = "Animation_Mesh_Geo")

            else:
                cmds.editDisplayLayerMembers("Animation_Mesh_Geo", newMesh)


        #get the icon path if present
        cmds.select(clear = True)
        if cmds.objExists(characterNode + ".iconPath"):
            path = cmds.getAttr(characterNode + ".iconPath")
            if os.path.exists(utils.returnNicePath(self.projectPath, path)):
                toContinue = self.overwriteIconUI(path)
                if toContinue:

                    self.stackWidget.setCurrentIndex(5)
                    self.mainWin.setWindowTitle("Create Thumbnail")

                else:
                    self.continueToSummary(True)
        else:
            self.stackWidget.setCurrentIndex(5)
            self.mainWin.setWindowTitle("Create Thumbnail")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def continueToSummary(self, skip):


        #set window title
        self.mainWin.setWindowTitle("Summary")

        #get character attributes to build up the path
        characterNode = utils.returnCharacterModule()
        project = cmds.getAttr(characterNode + ".project")
        group = cmds.getAttr(characterNode + ".group")
        name = cmds.getAttr(characterNode + ".name")
        version = cmds.getAttr(characterNode + ".version")


        #create the path
        if len(group) > 1:
            path = utils.returnFriendlyPath(project + "/" + group + "/" + name + ".png")
        else:
            path = utils.returnFriendlyPath(project + "/" + name + ".png")

        #add icon attr to character node if needed
        if not cmds.objExists(characterNode + ".iconPath"):
            cmds.addAttr(characterNode, ln = "iconPath", dt = "string", keyable = True)

        cmds.setAttr(characterNode + ".iconPath", path, type = "string")

        #render our images if needed
        if not skip:
            if self.viewportToggle.currentIndex() == 1:

                #use API to grab image from view
                newView = mui.M3dView()
                view = mui.M3dView.getM3dViewFromModelEditor(self.tcViewport, newView)

                #read the color buffer from the view, and save the MImage to disk
                image = openMaya.MImage()
                newView.readColorBuffer(image, True)
                image.writeToFile(utils.returnNicePath(self.projectPath, path), 'png')


            #if user passed in an image, save it to the appropriate location with the correct extension
            else:
                customPath = self.customThumbnail.text()
                print customPath, path

                import shutil
                shutil.copyfile(customPath, utils.returnNicePath(self.projectPath, path))


        #switch to summary page
        self.stackWidget.setCurrentIndex(5)

        #find if pre/post script added
        preScript = False
        if cmds.objExists(characterNode + ".preScript"):
            preScript = True

        postScript = False
        if cmds.objExists(characterNode + ".postScript"):
            postScript = True

        #get latest icon
        self.sumPageIcon.setStyleSheet("background-image: url(" + utils.returnNicePath(self.projectPath, path) + ");")

        #set info
        self.sumPageAssetName.setText(name)
        self.sumPageProj.setText(project)
        self.sumPageGroup.setText(group)
        self.sumPageRevisionType.setText(str(version))
        self.sp_preScriptCB.setChecked(preScript)
        self.sp_postScriptCB.setChecked(postScript)

        if cmds.objExists(name + "_animMeshGrp"):
            self.sp_animMeshCB.setChecked(True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def backToMeshIconCreation(self):

        self.stackWidget.setCurrentIndex(4)
        self.mainWin.setWindowTitle("Create Thumbnail")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def backToMeshSlicer(self):

        self.stackWidget.setCurrentIndex(3)
        self.mainWin.setWindowTitle("Create Animation Mesh")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def backToProject(self):
        #Original Author: Jeremy Ernst

        self.stackWidget.setCurrentIndex(1)
        self.mainWin.setWindowTitle("Publish")


        #make sure we hide all joint movers when going back and put things in the proper state
        for inst in self.mainUI.moduleInstances:
            listItems = []
            for i in range(self.rpPage_moduleList.count()):

                text = self.rpPage_moduleList.item(i).text()
                listItems.append(text)

            if inst.name in listItems:
                inst.cleanUpRigPose()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def backToRigPose(self):
        #Original Author: Jeremy Ernst

        self.stackWidget.setCurrentIndex(2)
        self.mainWin.setWindowTitle("Create Rig Pose")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addCustomScripts(self, preScript, postScript):
        #Original Author: Jeremy Ernst

        #launch the file dialog window
        try:
            fileName = cmds.fileDialog2(startingDirectory = cmds.internalVar(usd = True), ff = "*.py;;*.mel", fm = 1, okCaption = "Load Script")[0]
            fileName = utils.returnFriendlyPath(fileName)

        except:
            return

        #add attributes if they don't exist to character node
        characterNode = utils.returnCharacterModule()

        #edit the lineEdit to have the path to the script
        if preScript:
            self.preScriptLineEdit.setText(fileName)

            if not cmds.objExists(characterNode + ".preScriptPath"):
                cmds.addAttr(characterNode, ln = "preScriptPath", dt = "string", keyable = True)

            #set attrs
            cmds.setAttr(characterNode + ".preScriptPath", fileName, type = "string")


        #edit the lineEdit to have the path to the script
        if postScript:
            self.postScriptLineEdit.setText(fileName)

            if not cmds.objExists(characterNode + ".postScriptPath"):
                cmds.addAttr(characterNode, ln = "postScriptPath", dt = "string", keyable = True)

            #set attrs
            cmds.setAttr(characterNode + ".postScriptPath", fileName, type = "string")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def publishHelp(self):
        #Original Author: Jeremy Ernst

        import ART_Help
        reload(ART_Help)

        helpMovie = utils.returnFriendlyPath(os.path.join(self.iconsPath, "Help/publish.gif"))
        helpInst = ART_Help.ART_HelpMovie(self.mainWin, helpMovie)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def rigPoseHelp(self):
        #Original Author: Jeremy Ernst

        import ART_Help
        reload(ART_Help)

        helpMovie = utils.returnFriendlyPath(os.path.join(self.iconsPath, "Help/rigPose.gif"))
        helpInst = ART_Help.ART_HelpMovie(self.mainWin, helpMovie)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def launchBuild(self):
        #Original Author: Jeremy Ernst

        if cmds.window("ART_PublishWin", exists = True):
            cmds.deleteUI("ART_PublishWin", wnd = True)

        #save the file
        cmds.file(save = True)

        #launch build progress UI
        import ART_BuildProgressUI
        reload(ART_BuildProgressUI)
        ART_BuildProgressUI.ART_BuildProgress_UI(self.mainUI)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def closeWin(self, event):
        #Original Author: Jeremy Ernst

        if cmds.window("ART_PublishWin", exists = True):
            self.mainWin.close()

        #override the close event for the window with a custom function that makes sure the scene is cleaned up
        #delete the light and camera rig for the icon creator
        try:
            for node in [self.thumbnailCamera, self.lightGrp]:
                children = cmds.listRelatives(node, children = True)
                if len(children) > 0:
                    for each in children:
                        cmds.lockNode(each, lock = False)
                cmds.lockNode(node, lock = False)
                cmds.delete(node)
        except:
            pass

        for inst in self.mainUI.moduleInstances:
            try:
                #call on the module's bakeOffsets method
                inst.setupForRigPose()
                inst.setReferencePose("modelPose")
                inst.cleanUpRigPose()
            except Exception, e:
                print e

        event.accept()

