from ThirdParty.Qt import QtGui, QtCore, QtWidgets
from functools import partial
import maya.cmds as cmds
import System.utils as utils
import System.riggingUtils as riggingUtils


class ART_FinalizeSetup():
    def __init__(self, mainUI, skinToolsInst):

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")

        self.mainUI = mainUI
        self.skinToolsInst = skinToolsInst

        #build the UI
        self.finalizeSetup_UI()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def finalizeSetup_UI(self):

        if cmds.window("ART_finalizeSetupWin", exists = True):
            cmds.deleteUI("ART_finalizeSetupWin", wnd = True)

        #launch a UI to get the name information
        self.finalizeSetupWin = QtWidgets.QMainWindow(self.mainUI)

        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #load toolbar stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.finalizeSetupWin.setStyleSheet(self.style)


        #create the main widget
        self.finalizeSetupWin_mainWidget = QtWidgets.QWidget()
        self.finalizeSetupWin.setCentralWidget(self.finalizeSetupWin_mainWidget)

        #set qt object name
        self.finalizeSetupWin.setObjectName("ART_finalizeSetupWin")
        self.finalizeSetupWin.setWindowTitle("Finalize Setup")

        #create the mainLayout for the rig creator UI
        self.finalizeSetupWin_mainLayout = QtWidgets.QVBoxLayout(self.finalizeSetupWin_mainWidget)
        self.finalizeSetupWin_mainLayout.setContentsMargins(0, 0, 0, 0)

        self.finalizeSetupWin.resize(450, 300)
        self.finalizeSetupWin.setSizePolicy(mainSizePolicy)
        self.finalizeSetupWin.setMinimumSize(QtCore.QSize( 450, 300 ))
        self.finalizeSetupWin.setMaximumSize(QtCore.QSize( 450, 300 ))

        #create the background image
        self.finalizeSetupWin_frame = QtWidgets.QFrame()
        self.finalizeSetupWin_mainLayout.addWidget(self.finalizeSetupWin_frame)


        #create the main vertical layout inside the frame
        self.finalizeSetupWin_mainVLayout = QtWidgets.QVBoxLayout(self.finalizeSetupWin_frame)

        # # # # TEXT EDIT # # # #
        self.finalizeSetupWin_Text = QtWidgets.QTextEdit()
        self.finalizeSetupWin_Text.setMinimumSize(QtCore.QSize( 440, 230 ))
        self.finalizeSetupWin_Text.setMaximumSize(QtCore.QSize( 440, 230 ))
        self.finalizeSetupWin_mainVLayout.addWidget(self.finalizeSetupWin_Text)
        self.finalizeSetupWin_Text.setReadOnly(True)
        self.finalizeSetupWin_Text.setAcceptRichText(True)

        #text
        text = "Finalizing the setup will create the skeleton that will be used for skin binding."
        cursor = self.finalizeSetupWin_Text.textCursor()
        cursor.insertText(text)

        text = "\nIt is recommended that offsets are baked before continuing.  "
        self.finalizeSetupWin_Text.setTextColor(QtGui.QColor(236,217,0))
        self.finalizeSetupWin_Text.setFontPointSize(10)
        self.finalizeSetupWin_Text.append(text)

        #image
        image2 =  utils.returnNicePath(self.iconsPath, "System/bakeOffsets.png")
        icon = QtGui.QPixmap(image2)
        image = icon.toImage()
        cursor.insertImage(image)


        text = "\n(You will still be able to edit your setup by coming back to this step using the 'Edit Setup' button seen in the deformation tools interface):\n\n"
        self.finalizeSetupWin_Text.setTextColor(QtGui.QColor(255,255,255))
        self.finalizeSetupWin_Text.setFontPointSize(8)
        self.finalizeSetupWin_Text.append(text)

        #image
        image2 =  utils.returnNicePath(self.iconsPath, "System/finalizeSetup.png")
        icon = QtGui.QPixmap(image2)
        image = icon.toImage()
        cursor.insertImage(image)

        self.finalizeSetupWin_Text.setTextCursor(cursor)
        end = "<br>"
        fragment = QtGui.QTextDocumentFragment.fromHtml(end)
        cursor.insertFragment(fragment)
        # # # # END TEXT EDIT # # # #




        # # # # BUTTON LAYOUT # # # #
        self.finalizeSetupWin_buttonLayout = QtWidgets.QHBoxLayout()
        self.finalizeSetupWin_mainVLayout.addLayout(self.finalizeSetupWin_buttonLayout)

        self.finalizeSetupWin_ContinueBtn = QtWidgets.QPushButton("Continue")
        self.finalizeSetupWin_CancelBtn = QtWidgets.QPushButton("Cancel")
        self.finalizeSetupWin_HelpBtn = QtWidgets.QPushButton("?")
        self.finalizeSetupWin_HelpBtn.setMinimumSize(QtCore.QSize( 25, 25 ))
        self.finalizeSetupWin_HelpBtn.setMaximumSize(QtCore.QSize( 25, 25 ))
        self.finalizeSetupWin_buttonLayout.addWidget(self.finalizeSetupWin_ContinueBtn)
        self.finalizeSetupWin_buttonLayout.addWidget(self.finalizeSetupWin_CancelBtn)
        self.finalizeSetupWin_buttonLayout.addWidget(self.finalizeSetupWin_HelpBtn)

        self.finalizeSetupWin_ContinueBtn.clicked.connect(partial(self.finalizeSetup_Continue))
        self.finalizeSetupWin_CancelBtn.clicked.connect(partial(self.finalizeSetup_Cancel))
        self.finalizeSetupWin_HelpBtn.clicked.connect(partial(self.finalizeSetup_Help))

        self.finalizeSetupWin_ContinueBtn.setObjectName("blueButton")
        self.finalizeSetupWin_CancelBtn.setObjectName("blueButton")
        self.finalizeSetupWin_HelpBtn.setObjectName("blueButton")
        # # # # END BUTTON LAYOUT # # # #


        #show window
        self.finalizeSetupWin_Text.moveCursor(QtGui.QTextCursor.Start)
        self.finalizeSetupWin.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def finalizeSetup_Continue(self):

        #delete UI
        self.finalizeSetup_Cancel()

        #toggle tab visibility
        self.mainUI.toolModeStack.setCurrentIndex(1)

        #update network node with state change
        if not cmds.objExists("ART_RIG_ROOT.state"):
            cmds.addAttr("ART_RIG_ROOT", ln = "state", keyable = False)
        cmds.setAttr("ART_RIG_ROOT.state", 1)

        #build bind skeleton
        riggingUtils.buildSkeleton()

        #hide joint mover and lock
        lockNodes = cmds.listRelatives("JointMover", children = True)
        for node in lockNodes:
            cmds.setAttr(node + ".v", 0, lock = True)

        #lock nodes
        cmds.select("JointMover", hi = True)
        jmNodes = cmds.ls(sl = True)
        for node in jmNodes:
            cmds.lockNode(node, lock = True)

        #clear selection
        cmds.select(clear = True)

        #launch weight wizard
        import ART_WeightWizard as aww
        reload(aww)
        aww.run(self.mainUI)

        #remove outliner scriptJobs
        for job in self.mainUI.scriptJobs:
            try:
                cmds.scriptJob(kill = job, force = True)
                print "killed job :" + str(job)
            except:
                pass

        #weight table scriptJob
        self.mainUI.scriptJobs.append(self.skinToolsInst.weightTable_scriptJob())

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def finalizeSetup_Cancel(self):

        if cmds.window("ART_finalizeSetupWin", exists = True):
            cmds.deleteUI("ART_finalizeSetupWin", wnd = True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def finalizeSetup_Help(self):
        print "Not implemented yet. This will need to link to documentation online."
