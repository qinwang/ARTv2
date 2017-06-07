import maya.cmds as cmds
import os, time, json, weakref
from functools import partial


from System.ART_RigModule import ART_RigModule
from System import mathUtils
from System import utils
from System import riggingUtils
import System.interfaceUtils as interfaceUtils


from ThirdParty.Qt import QtGui, QtCore, QtWidgets


#file attributes
icon = "Modules/legStandard.png"
hoverIcon = "Modules/hover_legStandard.png"
search = "biped:leg"
className = "ART_Leg_Standard"
jointMover = "Core/JointMover/ART_Leg_Standard.ma"
baseName = "leg"
rigs = ["FK::IK"]
fbxImport = ["None", "FK", "IK", "Both"]
matchData = [True, ["Match FK to IK", "Match IK to FK"]]
controlTypes = [["fkControls", "FK"], ["ikV1Controls", "IK"], ["thighTwistControls", "FK"], ["calfTwistControls", "FK"], ["toeControls", "FK"]]

#begin class
class ART_Leg_Standard(ART_RigModule):

    _instances = set()

    def __init__(self, rigUiInst, moduleUserName):

        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}


        self.__class__._instances.add(weakref.ref(self))


        ART_RigModule.__init__(self, "ART_Leg_Standard_Module", "ART_Leg_Standard", moduleUserName)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addAttributes(self):
        #call the base class method first to hook up our connections to the master module
        ART_RigModule.addAttributes(self)

        #add custom attributes for this specific module
        cmds.addAttr(self.networkNode, sn = "Created_Bones", dt = "string", keyable = False)
        cmds.setAttr(self.networkNode + ".Created_Bones", "thigh::calf::foot::ball::", type = "string", lock = True)

        cmds.addAttr(self.networkNode, sn = "baseName", dt = "string", keyable = False)
        cmds.setAttr(self.networkNode + ".baseName", baseName , type = "string", lock = True)

        cmds.addAttr(self.networkNode, sn = "canAim", at = "bool", keyable = False)
        cmds.setAttr(self.networkNode + ".canAim", True, lock = True)

        cmds.addAttr(self.networkNode, sn = "aimMode", at = "bool", keyable = False)
        cmds.setAttr(self.networkNode + ".aimMode", False, lock = True)

        #joint mover settings
        cmds.addAttr(self.networkNode, sn = "thighTwists", keyable = False)
        cmds.setAttr(self.networkNode + ".thighTwists", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "calfTwists", keyable = False)
        cmds.setAttr(self.networkNode + ".calfTwists", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "bigToeJoints", keyable = False)
        cmds.setAttr(self.networkNode + ".bigToeJoints", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "bigToeMeta", keyable = False, at = "bool")
        cmds.setAttr(self.networkNode + ".bigToeMeta", False, lock = True)

        cmds.addAttr(self.networkNode, sn = "indexToeJoints", keyable = False)
        cmds.setAttr(self.networkNode + ".indexToeJoints", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "indexToeMeta", keyable = False, at = "bool")
        cmds.setAttr(self.networkNode + ".indexToeMeta", False, lock = True)

        cmds.addAttr(self.networkNode, sn = "middleToeJoints", keyable = False)
        cmds.setAttr(self.networkNode + ".middleToeJoints", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "middleToeMeta", keyable = False, at = "bool")
        cmds.setAttr(self.networkNode + ".middleToeMeta", False, lock = True)

        cmds.addAttr(self.networkNode, sn = "ringToeJoints", keyable = False)
        cmds.setAttr(self.networkNode + ".ringToeJoints", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "ringToeMeta", keyable = False, at = "bool")
        cmds.setAttr(self.networkNode + ".ringToeMeta", False, lock = True)

        cmds.addAttr(self.networkNode, sn = "pinkyToeJoints", keyable = False)
        cmds.setAttr(self.networkNode + ".pinkyToeJoints", 0, lock = True)

        cmds.addAttr(self.networkNode, sn = "pinkyToeMeta", keyable = False, at = "bool")
        cmds.setAttr(self.networkNode + ".pinkyToeMeta", False, lock = True)

        cmds.addAttr(self.networkNode, sn = "includeBall", at = "bool", keyable = False)
        cmds.setAttr(self.networkNode + ".includeBall", True, lock = True)

        cmds.addAttr(self.networkNode, sn = "side", dt = "string", keyable = False)
        cmds.setAttr(self.networkNode + ".side", "Left", type = "string", lock = True)

        #rig creation settings
        cmds.addAttr(self.networkNode, sn = "buildFK", at = "bool", keyable = False)
        cmds.setAttr(self.networkNode + ".buildFK", True, lock = True)

        cmds.addAttr(self.networkNode, sn = "buildIK_V1", at = "bool", keyable = False)
        cmds.setAttr(self.networkNode + ".buildIK_V1", True, lock = True)




    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):
        networkNode = self.returnNetworkNode

        #groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 480, True)

        font = QtGui.QFont()
        font.setPointSize(8)

        headerFont = QtGui.QFont()
        headerFont.setPointSize(8)
        headerFont.setBold(True)


        #create a VBoxLayout to add to our Groupbox and then add a QFrame for our signal/slot
        self.layout = QtWidgets.QVBoxLayout(self.groupBox)
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.layout.addWidget(self.frame)

        self.frame.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.frame.setMinimumSize(QtCore.QSize(320, 445))
        self.frame.setMaximumSize(QtCore.QSize(320, 445))


        #add layout for custom settings
        self.customSettingsLayout = QtWidgets.QVBoxLayout(self.frame)

        #mirror module
        self.mirrorModLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.mirrorModLayout)
        self.mirrorModuleLabel = QtWidgets.QLabel("Mirror Module: ")
        self.mirrorModuleLabel.setFont(font)
        self.mirrorModLayout.addWidget(self.mirrorModuleLabel)

        mirror = cmds.getAttr(networkNode +".mirrorModule")
        if mirror == "":
            mirror = "None"
        self.mirrorMod = QtWidgets.QLabel(mirror)
        self.mirrorMod.setFont(font)
        self.mirrorMod.setAlignment(QtCore.Qt.AlignHCenter)
        self.mirrorModLayout.addWidget(self.mirrorMod)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.customSettingsLayout.addItem(spacerItem)

        #current parent
        self.currentParentMod = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.currentParentMod)
        self.currentParentLabel = QtWidgets.QLabel("Current Parent: ")
        self.currentParentLabel.setFont(font)
        self.currentParentMod.addWidget(self.currentParentLabel)

        parent = cmds.getAttr(networkNode +".parentModuleBone")
        self.currentParent = QtWidgets.QLabel(parent)
        self.currentParent.setFont(font)
        self.currentParent.setAlignment(QtCore.Qt.AlignHCenter)
        self.currentParentMod.addWidget(self.currentParent)


        #button layout for name/parent
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.buttonLayout)
        self.changeNameBtn = QtWidgets.QPushButton("Change Name")
        self.changeParentBtn = QtWidgets.QPushButton("Change Parent")
        self.mirrorModuleBtn = QtWidgets.QPushButton("Mirror Module")
        self.buttonLayout.addWidget(self.changeNameBtn)
        self.buttonLayout.addWidget(self.changeParentBtn)
        self.buttonLayout.addWidget(self.mirrorModuleBtn)
        self.changeNameBtn.setObjectName("blueButton")
        self.changeParentBtn.setObjectName("blueButton")
        self.mirrorModuleBtn.setObjectName("blueButton")

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.customSettingsLayout.addItem(spacerItem)

        #add side settings
        self.sideLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.sideLayout)
        self.sideLabel = QtWidgets.QLabel("Side:    ")
        self.sideLabel.setFont(font)
        self.leftSideBtn = QtWidgets.QRadioButton("Left Side")
        self.rightSideBtn = QtWidgets.QRadioButton("Right Side")
        self.sideLayout.addWidget(self.sideLabel)
        self.sideLayout.addWidget(self.leftSideBtn)
        self.sideLayout.addWidget(self.rightSideBtn)

        #get current side
        if cmds.getAttr(networkNode + ".side") == "Left":
            self.leftSideBtn.setChecked(True)
        if cmds.getAttr(networkNode + ".side") == "Right":
            self.rightSideBtn.setChecked(True)

        self.leftSideBtn.clicked.connect(self.changeSide)
        self.rightSideBtn.clicked.connect(self.changeSide)

        spacerItem = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.customSettingsLayout.addItem(spacerItem)


        #coplanar mode and bake offsets layout
        self.legToolsLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.legToolsLayout)

        #Coplanar mode
        self.coplanarBtn = QtWidgets.QPushButton("Coplanar Mode")
        self.coplanarBtn.setFont(headerFont)
        self.legToolsLayout.addWidget(self.coplanarBtn)
        self.coplanarBtn.setCheckable(True)
        self.coplanarBtn.clicked.connect(self.coplanarMode)
        self.coplanarBtn.setToolTip("[EXPERIMENTAL] Forces leg joints to always be planar for best IK setup")

        #Bake OFfsets
        self.bakeOffsetsBtn = QtWidgets.QPushButton("Bake Offsets")
        self.bakeOffsetsBtn.setFont(headerFont)
        self.legToolsLayout.addWidget(self.bakeOffsetsBtn)
        self.bakeOffsetsBtn.clicked.connect(self.bakeOffsets)
        self.bakeOffsetsBtn.setToolTip("Bake the offset mover values up to the global movers to get them in sync")

        self.coplanarBtn.setObjectName("blueButton")
        self.bakeOffsetsBtn.setObjectName("blueButton")

        #Twist Bones Section
        self.twistSettingsLabel = QtWidgets.QLabel("Twist Bone Settings: ")
        self.twistSettingsLabel.setFont(headerFont)
        self.twistSettingsLabel.setStyleSheet("color: rgb(25, 175, 255);")
        self.customSettingsLayout.addWidget(self.twistSettingsLabel)

        self.separatorA = QtWidgets.QFrame()
        self.separatorA.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorA.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.customSettingsLayout.addWidget(self.separatorA)

        #twist bones HBoxLayout
        self.twistBonesLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.twistBonesLayout)

        self.twistForm = QtWidgets.QFormLayout()
        self.thighTwistLabel = QtWidgets.QLabel("Thigh Twists: ")
        self.thighTwistLabel.setFont(font)
        self.twistForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.thighTwistLabel)
        self.thighTwistNum = QtWidgets.QSpinBox()
        self.thighTwistNum.setMaximum(3)
        self.twistForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.thighTwistNum)
        self.twistBonesLayout.addLayout(self.twistForm)


        self.calfForm = QtWidgets.QFormLayout()
        self.calfTwistLabel = QtWidgets.QLabel("Calf Twists: ")
        self.calfTwistLabel.setFont(font)
        self.calfForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.calfTwistLabel)
        self.calfTwistNum = QtWidgets.QSpinBox()
        self.calfTwistNum.setMaximum(3)
        self.calfForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.calfTwistNum)
        self.twistBonesLayout.addLayout(self.calfForm)


        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.customSettingsLayout.addItem(spacerItem)

        #Feet Settings Section
        self.feetSettingsLabel = QtWidgets.QLabel("Foot Settings: ")
        self.feetSettingsLabel.setFont(headerFont)
        self.feetSettingsLabel.setStyleSheet("color: rgb(25, 175, 255);")
        self.customSettingsLayout.addWidget(self.feetSettingsLabel)

        self.separatorB = QtWidgets.QFrame()
        self.separatorB.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorB.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.customSettingsLayout.addWidget(self.separatorB)


        self.ballJoint = QtWidgets.QCheckBox("Include Ball Joint?")
        self.ballJoint.setChecked(True)
        self.customSettingsLayout.addWidget(self.ballJoint)


        #Toe Settings: add VBoxLayout
        self.toeVBoxLayout = QtWidgets.QVBoxLayout()
        self.customSettingsLayout.addLayout(self.toeVBoxLayout)

        #BIG TOE
        self.bigToeLayout = QtWidgets.QHBoxLayout()

        self.bigToeLabel = QtWidgets.QLabel("Big Toe Joints: ")
        self.bigToeLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.bigToeLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.bigToeLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.bigToeLayout.addWidget((self.bigToeLabel))


        self.bigToeNum = QtWidgets.QSpinBox()
        self.bigToeNum.setMaximum(2)
        self.bigToeNum.setMinimumSize(QtCore.QSize(50, 20))
        self.bigToeNum.setMaximumSize(QtCore.QSize(50, 20))
        self.bigToeNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.bigToeLayout.addWidget(self.bigToeNum)

        self.bigToeMeta = QtWidgets.QCheckBox("Include Metatarsal")
        self.bigToeLayout.addWidget(self.bigToeMeta)
        self.toeVBoxLayout.addLayout(self.bigToeLayout)



        #INDEX TOE
        self.indexToeLayout = QtWidgets.QHBoxLayout()

        self.indexToeLabel = QtWidgets.QLabel("Index Toe Joints: ")
        self.indexToeLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.indexToeLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.indexToeLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.indexToeLayout.addWidget((self.indexToeLabel))

        self.indexToeNum = QtWidgets.QSpinBox()
        self.indexToeNum.setMaximum(3)
        self.indexToeNum.setMinimumSize(QtCore.QSize(50, 20))
        self.indexToeNum.setMaximumSize(QtCore.QSize(50, 20))
        self.indexToeNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.indexToeLayout.addWidget((self.indexToeNum))

        self.indexToeMeta = QtWidgets.QCheckBox("Include Metatarsal")
        self.indexToeLayout.addWidget(self.indexToeMeta)
        self.toeVBoxLayout.addLayout(self.indexToeLayout)

        #MIDDLE TOE
        self.middleToeLayout = QtWidgets.QHBoxLayout()

        self.middleToeLabel = QtWidgets.QLabel("Middle Toe Joints: ")
        self.middleToeLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.middleToeLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.middleToeLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.middleToeLayout.addWidget(self.middleToeLabel)

        self.middleToeNum = QtWidgets.QSpinBox()
        self.middleToeNum.setMaximum(3)
        self.middleToeNum.setMinimumSize(QtCore.QSize(50, 20))
        self.middleToeNum.setMaximumSize(QtCore.QSize(50, 20))
        self.middleToeNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.middleToeLayout.addWidget(self.middleToeNum)

        self.middleToeMeta = QtWidgets.QCheckBox("Include Metatarsal")
        self.middleToeLayout.addWidget(self.middleToeMeta)
        self.toeVBoxLayout.addLayout(self.middleToeLayout)

        #RING TOE
        self.ringToeLayout = QtWidgets.QHBoxLayout()

        self.ringToeLabel = QtWidgets.QLabel("Ring Toe Joints: ")
        self.ringToeLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.ringToeLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.ringToeLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.ringToeLayout.addWidget(self.ringToeLabel)

        self.ringToeNum = QtWidgets.QSpinBox()
        self.ringToeNum.setMaximum(3)
        self.ringToeNum.setMinimumSize(QtCore.QSize(50, 20))
        self.ringToeNum.setMaximumSize(QtCore.QSize(50, 20))
        self.ringToeNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.ringToeLayout.addWidget(self.ringToeNum)

        self.ringToeMeta = QtWidgets.QCheckBox("Include Metatarsal")
        self.ringToeLayout.addWidget(self.ringToeMeta)
        self.toeVBoxLayout.addLayout(self.ringToeLayout)


        #PINKY TOE
        self.pinkyToeLayout = QtWidgets.QHBoxLayout()

        self.pinkyToeLabel = QtWidgets.QLabel("Pinky Toe Joints: ")
        self.pinkyToeLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.pinkyToeLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.pinkyToeLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.pinkyToeLayout.addWidget(self.pinkyToeLabel)

        self.pinkyToeNum = QtWidgets.QSpinBox()
        self.pinkyToeNum.setMaximum(3)
        self.pinkyToeNum.setMinimumSize(QtCore.QSize(50, 20))
        self.pinkyToeNum.setMaximumSize(QtCore.QSize(50, 20))
        self.pinkyToeNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.pinkyToeLayout.addWidget(self.pinkyToeNum)

        self.pinkyToeMeta = QtWidgets.QCheckBox("Include Metatarsal")
        self.pinkyToeLayout.addWidget(self.pinkyToeMeta)
        self.toeVBoxLayout.addLayout(self.pinkyToeLayout)


        #rebuild button
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.customSettingsLayout.addItem(spacerItem)

        self.applyButton = QtWidgets.QPushButton("Apply Changes")
        self.customSettingsLayout.addWidget(self.applyButton)
        self.applyButton.setFont(headerFont)
        self.applyButton.setMinimumSize(QtCore.QSize(300, 40))
        self.applyButton.setMaximumSize(QtCore.QSize(300, 40))
        self.applyButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.applyButton.setEnabled(False)



        #SIGNALS/SLOTS

        #signal slot for groupbox checkbox
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.frame.setVisible)
        self.groupBox.setChecked(False)

        #button signal/slots
        self.changeNameBtn.clicked.connect(partial(self.changeModuleName, baseName, self, self.rigUiInst))
        self.changeParentBtn.clicked.connect(partial(self.changeModuleParent, self, self.rigUiInst))
        self.mirrorModuleBtn.clicked.connect(partial(self.setMirrorModule, self, self.rigUiInst))
        self.applyButton.clicked.connect(partial(self.applyModuleChanges, self))

        #spinBox & checkbox signal/slots
        self.thighTwistNum.valueChanged.connect(self.toggleButtonState)
        self.calfTwistNum.valueChanged.connect(self.toggleButtonState)
        self.bigToeNum.valueChanged.connect(self.toggleButtonState)
        self.indexToeNum.valueChanged.connect(self.toggleButtonState)
        self.middleToeNum.valueChanged.connect(self.toggleButtonState)
        self.ringToeNum.valueChanged.connect(self.toggleButtonState)
        self.pinkyToeNum.valueChanged.connect(self.toggleButtonState)
        self.ballJoint.stateChanged.connect(self.toggleButtonState)
        self.ballJoint.stateChanged.connect(partial(self.includeBallJoint, True))

        self.pinkyToeMeta.stateChanged.connect(self.toggleButtonState)
        self.ringToeMeta.stateChanged.connect(self.toggleButtonState)
        self.middleToeMeta.stateChanged.connect(self.toggleButtonState)
        self.indexToeMeta.stateChanged.connect(self.toggleButtonState)
        self.bigToeMeta.stateChanged.connect(self.toggleButtonState)

        #add custom skeletonUI settings  name, parent, rig types to install, mirror module, thigh twist, calf twists, ball joint, toes,
        #add to the rig cretor UI's module settings layout VBoxLayout
        self.rigUiInst.moduleSettingsLayout.addWidget(self.groupBox)

        #Populate the settings UI based on the network node attributes
        self.updateSettingsUI()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pickerUI(self, center, animUI, networkNode, namespace):

        self.namespace = namespace

        #create qBrushes
        yellowBrush = QtCore.Qt.yellow
        blueBrush = QtGui.QColor(100,220,255)
        purpleBrush = QtGui.QColor(111,48,161)
        greenBrush = QtGui.QColor(0,255,30)
        clearBrush = QtGui.QBrush(QtCore.Qt.black)
        clearBrush.setStyle(QtCore.Qt.NoBrush)
        side = cmds.getAttr(networkNode + ".side")

        #create the picker border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode

        borderItem = interfaceUtils.pickerBorderItem(center.x() - 75, center.y() - 130, 150, 260, clearBrush, moduleNode)

        #get controls
        ikControls = json.loads(cmds.getAttr(networkNode + ".ikV1Controls")) #["ik_foot_anim", "leg_heel_ctrl", "leg_toe_tip_ctrl", "leg_toe_wiggle_ctrl"]
        fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls")) #["fk_thigh_anim", "fk_calf_anim", "fk_foot_anim", "fk_ball_anim"]
        thighTwistControls = json.loads(cmds.getAttr(networkNode + ".thighTwistControls"))
        calfTwistControls = json.loads(cmds.getAttr(networkNode + ".calfTwistControls"))

        buttonData = []
        controls = []

        #ik buttons
        ikFootBtn = interfaceUtils.pickerButton(30, 30, [30,225], namespace + ikControls[0], yellowBrush, borderItem)
        buttonData.append([ikFootBtn, namespace + ikControls[0], yellowBrush])
        controls.append(namespace + ikControls[0])



        ikHeelBtn = interfaceUtils.pickerButton(20, 20, [5,235], namespace + ikControls[1], yellowBrush, borderItem)
        buttonData.append([ikHeelBtn, namespace + ikControls[1], yellowBrush])
        controls.append(namespace + ikControls[1])

        ikToeTipBtn = interfaceUtils.pickerButton(20, 20, [135,235], namespace + ikControls[2], yellowBrush, borderItem)
        buttonData.append([ikToeTipBtn, namespace + ikControls[2], yellowBrush])
        controls.append(namespace + ikControls[2])

        ikToeWiggleBtn = interfaceUtils.pickerButton(20, 20, [97,200], namespace + ikControls[3], yellowBrush, borderItem)
        buttonData.append([ikToeWiggleBtn, namespace + ikControls[3], yellowBrush])
        controls.append(namespace + ikControls[3])

        #fk buttons
        fkThighBtn = interfaceUtils.pickerButton(30, 100, [30,10], namespace + fkControls[0], blueBrush, borderItem)
        buttonData.append([fkThighBtn, namespace + fkControls[0], blueBrush])
        controls.append(namespace + fkControls[0])

        fkCalfBtn = interfaceUtils.pickerButton(30, 90, [30,122], namespace + fkControls[1], blueBrush, borderItem)
        buttonData.append([fkCalfBtn, namespace + fkControls[1], blueBrush])
        controls.append(namespace + fkControls[1])

        fkFootBtn = interfaceUtils.pickerButton(30, 30, [62,225], namespace + fkControls[2], blueBrush, borderItem)
        buttonData.append([fkFootBtn, namespace + fkControls[2], blueBrush])
        controls.append(namespace + fkControls[2])

        if len(fkControls) == 4:
            fkBallBtn = interfaceUtils.pickerButton(30, 30, [97,225], namespace + fkControls[3], blueBrush, borderItem)
            buttonData.append([fkBallBtn, namespace + fkControls[3], blueBrush])
            controls.append(namespace + fkControls[3])

        #thigh twists
        if thighTwistControls != None:
            if len(thighTwistControls) > 0:
                y = 20
                for i in range(len(thighTwistControls)):
                    button = interfaceUtils.pickerButton(20, 20, [5, y], namespace + thighTwistControls[i], purpleBrush, borderItem)
                    buttonData.append([button, namespace + thighTwistControls[i], purpleBrush])
                    controls.append(namespace + thighTwistControls[i])
                    y = y + 30


        if calfTwistControls != None:
            if len(calfTwistControls) > 0:
                y = 192
                for i in range(len(calfTwistControls)):
                    button = interfaceUtils.pickerButton(20, 20, [5, y], namespace + calfTwistControls[i], purpleBrush, borderItem)
                    buttonData.append([button, namespace + calfTwistControls[i], purpleBrush])
                    controls.append(namespace + calfTwistControls[i])
                    y = y - 30




        #=======================================================================
        # #TOES !!!! THIS IS A SUB-PICKER !!!!
        #=======================================================================

        #if there are toes, create a toe picker
        toeControls = json.loads(cmds.getAttr(networkNode + ".toeControls"))
        if len(toeControls) > 0:

            name = cmds.getAttr(networkNode + ".moduleName")
            toeBorder = interfaceUtils.pickerBorderItem(center.x() + 35, center.y() - 75, 100, 100, clearBrush, moduleNode, name + "_toes")
            toeBorder.setParentItem(borderItem)
            interfaceUtils.addTextToButton(side[0] + "_Toes", toeBorder, False, True, False)


            #create selection set lists
            bigToes = []
            indexToes = []
            middleToes = []
            ringToes = []
            pinkyToes = []

            metaTarsals = []
            distalKnuckles = []
            middleKnuckles = []
            proximalKnuckles = []

            #BIG TOE
            for toe in toeControls:
                if toe.find("bigtoe_metatarsal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20,75], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    bigToes.append(namespace + toe)
                    metaTarsals.append(namespace + toe)

                if toe.find("bigtoe_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20,40], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    bigToes.append(namespace + toe)
                    proximalKnuckles.append(namespace + toe)

                if toe.find("bigtoe_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20,25], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    bigToes.append(namespace + toe)
                    distalKnuckles.append(namespace + toe)


                #INDEX TOE
                if toe.find("index_metatarsal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35,75], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    indexToes.append(namespace + toe)
                    metaTarsals.append(namespace + toe)

                if toe.find("index_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35,55], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    indexToes.append(namespace + toe)
                    proximalKnuckles.append(namespace + toe)

                if toe.find("index_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35,40], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    indexToes.append(namespace + toe)
                    middleKnuckles.append(namespace + toe)

                if toe.find("index_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35,25], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    indexToes.append(namespace + toe)
                    distalKnuckles.append(namespace + toe)


                #MIDDLE TOE
                if toe.find("middle_metatarsal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50,75], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    middleToes.append(namespace + toe)
                    metaTarsals.append(namespace + toe)

                if toe.find("middle_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50,55], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    middleToes.append(namespace + toe)
                    proximalKnuckles.append(namespace + toe)

                if toe.find("middle_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50,40], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    middleToes.append(namespace + toe)
                    middleKnuckles.append(namespace + toe)

                if toe.find("middle_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50,25], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    middleToes.append(namespace + toe)
                    distalKnuckles.append(namespace + toe)


                #RING TOE
                if toe.find("ring_metatarsal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65,75], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    ringToes.append(namespace + toe)
                    metaTarsals.append(namespace + toe)

                if toe.find("ring_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65,55], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    ringToes.append(namespace + toe)
                    proximalKnuckles.append(namespace + toe)

                if toe.find("ring_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65,40], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    ringToes.append(namespace + toe)
                    middleKnuckles.append(namespace + toe)

                if toe.find("ring_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65,25], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    ringToes.append(namespace + toe)
                    distalKnuckles.append(namespace + toe)


                #PINKY TOE
                if toe.find("pinky_metatarsal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80,75], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    pinkyToes.append(namespace + toe)
                    metaTarsals.append(namespace + toe)

                if toe.find("pinky_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80,55], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    pinkyToes.append(namespace + toe)
                    proximalKnuckles.append(namespace + toe)

                if toe.find("pinky_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80,40], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    pinkyToes.append(namespace + toe)
                    middleKnuckles.append(namespace + toe)

                if toe.find("pinky_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80,25], namespace + toe, blueBrush, toeBorder)
                    buttonData.append([button, namespace + toe, blueBrush])
                    controls.append(namespace + toe)
                    pinkyToes.append(namespace + toe)
                    distalKnuckles.append(namespace + toe)


            #TOE MASS SELECT BUTTONS
            interfaceUtils.pickerButtonAll(10, 10, [5,75], metaTarsals, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [5,55], proximalKnuckles, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [5,40], middleKnuckles, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [5,25], distalKnuckles, greenBrush, toeBorder)

            interfaceUtils.pickerButtonAll(10, 10, [20,5], bigToes, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [35,5], indexToes, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [50,5], middleToes, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [65,5], ringToes, greenBrush, toeBorder)
            interfaceUtils.pickerButtonAll(10, 10, [80,5], pinkyToes, greenBrush, toeBorder)






        #settings button
        settingsBtn = interfaceUtils.pickerButton(20, 20, [65,40], namespace + self.name + "_settings", greenBrush, borderItem)
        buttonData.append([settingsBtn, namespace + ":" + self.name + "_settings", greenBrush])
        controls.append(namespace + ":" + self.name + "_settings")
        interfaceUtils.addTextToButton("S", settingsBtn)


        #go through button data, adding menu items
        for each in buttonData:
            button = each[0]

            fkIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/jointFilter.png"))))
            ikIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/ikMode.png"))))
            zeroIcon1 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroAll.png"))))
            zeroIcon2 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroSel.png"))))
            selectIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/select.png"))))

            switchAction = QtWidgets.QAction('Match when Switching', button.menu)
            switchAction.setCheckable(True)
            switchAction.setChecked(True)

            button.menu.addAction(selectIcon, "Select All Leg Controls", partial(self.selectRigControls, "all"))
            button.menu.addAction(selectIcon, "Select FK Leg Controls", partial(self.selectRigControls, "fk"))
            button.menu.addAction(selectIcon, "Select IK Leg Controls", partial(self.selectRigControls, "ik"))
            button.menu.addSeparator()

            button.menu.addAction(fkIcon, "FK Mode", partial(self.switchMode, "FK", switchAction))
            button.menu.addAction(ikIcon, "IK Mode", partial(self.switchMode, "IK", switchAction))
            button.menu.addAction(switchAction)

            button.menu.addSeparator()
            button.menu.addAction(zeroIcon1, "Zero Out Attrs (All)", partial(self.resetRigControls, True))
            button.menu.addAction(zeroIcon2, "Zero Out Attrs (Sel)", partial(self.resetRigControls, False))


        #select all button
        interfaceUtils.pickerButtonAll(20, 20, [65,10], controls, greenBrush, borderItem)


        #=======================================================================
        # #Create scriptJob for selection. Set scriptJob number to borderItem.data(5)
        #=======================================================================
        scriptJob = cmds.scriptJob(event = ["SelectionChanged", partial(self.selectionScriptJob_animUI, buttonData)], kws = True)
        borderItem.setData(5, scriptJob)
        animUI.selectionScriptJobs.append(scriptJob)

        #return data and set to mirror if side is right
        if side == "Right":
            return [borderItem, True, scriptJob]
        else:
            return [borderItem, False, scriptJob]


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildRigCustom(self, textEdit, uiInst):

        """
        The base class gets a buildRig function called from the buildProgressUI. This function has some pre/post functionality that labels new nodes created by the buildRigCustom
        method. Each derived class will need to have a buildRigCustom implemented. This method should call on any rig building functions for that module.

        -each module should have its own settings group : self.name + "_settings"
        -each module should have something similar to the builtRigs list, which is a list that holds what rigs have been built (NOT, which are going to BE built, but the ones that already have)
            -this list looks something like this: [["FK", [nodesToHide]],["IK", [nodesToHide]]]
            -this is used when it's time to setup the mode switching
        -each module should also, at the very least, write to an attribute, what controls have been created for that module.
            -right now, I have it as 2 attrs on the leg. This should probably just be changed to 1 controls attr, or keep what I have and add the controls attr which combines the previous?
            -This would made looking up controls per module consistent, but may not be necessary?
        """
        #TO DO: investigate if controls attrs should be made consistent across all modules


        #get the network node and find out which rigs to build
        networkNode = self.returnNetworkNode
        buildFK = True
        buildIK_V1 = True

        #have it build all rigs by default, unless there is an attr stating otherwise (backwards- compatability)
        numRigs = 0
        if cmds.objExists(networkNode + ".buildFK"):
            buildFK = cmds.getAttr(networkNode + ".buildFK")
            if buildFK:
                numRigs += 1
        if cmds.objExists(networkNode + ".buildIK_V1"):
            buildIK_V1 = cmds.getAttr(networkNode + ".buildIK_V1")
            if buildIK_V1:
                numRigs += 1


        #find the joints in the leg module that need rigging
        joints = self.getMainLegJoints()

        builtRigs = []

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #create groups and settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        #create the leg group
        legJoints = self.getMainLegJoints()
        self.legGroup = cmds.group(empty = True, name = self.name + "_group")
        constraint = cmds.parentConstraint(legJoints[0], self.legGroup)[0]
        cmds.delete(constraint)

        #create the leg settings group
        self.legSettings = cmds.group(empty = True, name = self.name + "_settings")
        cmds.parent(self.legSettings, self.legGroup)
        for attr in(cmds.listAttr(self.legSettings, keyable = True)):
            cmds.setAttr(self.legSettings + "." + attr, lock = True, keyable = False)

        #add mode attribute to settings
        if numRigs > 1:
            cmds.addAttr(self.legSettings, ln = "mode", min = 0, max = numRigs - 1, dv = 0, keyable = True)

        #create the ctrl group (what will get the constraint to the parent)
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        self.legCtrlGrp = cmds.group(empty = True, name = self.name + "_leg_ctrl_grp")
        constraint = cmds.parentConstraint(parentBone, self.legCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.legCtrlGrp, self.legGroup)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #build the rigs
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       FK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #if build FK was true, build the FK rig now
        if buildFK:

            #update progress
            if textEdit != None:
                textEdit.append("        Starting FK Rig Build..")

            #build the rig
            slot = len(builtRigs)
            fkRigData = riggingUtils.createFkRig(joints, networkNode, numRigs, slot)
            self.topNode = fkRigData[0]

            builtRigs.append(["FK", [self.topNode]])

            #parent top node into leg group
            if self.topNode != None:
                cmds.parent(self.topNode, self.legCtrlGrp)

            #lock attrs
            for each in fkRigData[1]:
                for attr in [".scaleX", ".scaleY",".scaleZ", ".visibility"]:
                    cmds.setAttr(each + attr, lock = True, keyable = False)

            #add created control info to module
            if not cmds.objExists(networkNode + ".fkControls"):
                cmds.addAttr(networkNode, ln = "fkControls", dt = "string")
            jsonString = json.dumps(fkRigData[1])
            cmds.setAttr(networkNode + ".fkControls", jsonString, type = "string")

            #update progress
            if textEdit != None:
                textEdit.setTextColor(QtGui.QColor(0,255,18))
                textEdit.append("        SUCCESS: FK Build Complete!")
                textEdit.setTextColor(QtGui.QColor(255,255,255))


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       IK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #if build IK was true, build the IK rig now
        if buildIK_V1:

            #update progress
            if textEdit != None:
                textEdit.append("        Starting IK (version 1) Rig Build..")

            #build the rig
            slot = len(builtRigs)
            ikInfo = self.buildIkRig(numRigs, slot)
            builtRigs.append(["IK", [self.ikFootCtrl + "_grp", ikInfo[1]]])


            #lock attributes on controls
            for each in ikInfo[0]:
                for attr in [".visibility", ".scaleX", ".scaleY", ".scaleZ"]:
                    cmds.setAttr(each + attr, lock = True, keyable = False)

                if each != self.ikFootCtrl:
                    for attr in [".translateX", ".translateY", ".translateZ"]:
                        cmds.setAttr(each + attr, lock = True, keyable = False)

            #add created control info to module
            if not cmds.objExists(networkNode + ".ikV1Controls"):
                cmds.addAttr(networkNode, ln = "ikV1Controls", dt = "string")
            jsonString = json.dumps(ikInfo[0])
            cmds.setAttr(networkNode + ".ikV1Controls", jsonString, type = "string")

            #update progress
            if textEdit != None:
                textEdit.setTextColor(QtGui.QColor(0,255,18))
                textEdit.append("        SUCCESS: IK Build Complete!")
                textEdit.setTextColor(QtGui.QColor(255,255,255))



        #===================================================================
        # #create thigh twist rig
        #===================================================================
        twistJoints = self.getLegTwistJoints(True, False)
        twistCtrls = riggingUtils.createCounterTwistRig(twistJoints, self.name, networkNode, legJoints[0], legJoints[1], self.name + "_group")

        if not cmds.objExists(networkNode + ".thighTwistControls"):
            cmds.addAttr(networkNode, ln =  "thighTwistControls", dt = "string" )
        jsonString = json.dumps(twistCtrls)
        cmds.setAttr(networkNode + ".thighTwistControls", jsonString, type = "string")

        #create calf twist rig
        twistJoints = self.getLegTwistJoints(False, True)
        twistCtrls = riggingUtils.createTwistRig(twistJoints, self.name, networkNode, legJoints[1], legJoints[2], self.name + "_group")

        if not cmds.objExists(networkNode + ".calfTwistControls"):
            cmds.addAttr(networkNode, ln =  "calfTwistControls", dt = "string" )
        jsonString = json.dumps(twistCtrls)
        cmds.setAttr(networkNode + ".calfTwistControls", jsonString, type = "string")

        #=======================================================================
        # # #build toe rigs (if needed)
        #=======================================================================
        prefix = self.name.partition(baseName)[0]
        suffix = self.name.partition(baseName)[2]

        #lists of toe joints
        bigToeJoints = ["proximal_phalange", "distal_phalange"]
        toeJoints = ["proximal_phalange", "middle_phalange", "distal_phalange"]


        #loop through our toe attrs, building the toe rig as we go
        for attr in [[".bigToeJoints", "bigtoe", ".bigToeMeta"], [".indexToeJoints", "index", ".indexToeMeta"], [".middleToeJoints", "middle", ".middleToeMeta"], [".ringToeJoints", "ring", ".ringToeMeta"], [".pinkyToeJoints", "pinky", ".pinkyToeMeta"]]:
            metaValue = cmds.getAttr(networkNode + attr[2])

            value = cmds.getAttr(networkNode + attr[0])
            toes = []

            if metaValue:
                    toes.append(prefix + attr[1] + "_metatarsal" + suffix)

            if attr[0] != ".bigToeJoints":
                for i in range(int(value)):
                    toes.append(prefix + attr[1] + "_" + toeJoints[i] + suffix)

                #build toe rigs
                self.buildToeRigs(toes)

            else:
                for i in range(int(value)):
                    toes.append(prefix + attr[1] + "_" + bigToeJoints[i] + suffix)
                #build toe rigs
                self.buildToeRigs(toes)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #hook up settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        #mode
        if numRigs > 1:
            attrData = []
            rampData = []

            """ CONSTRAINTS """
            #get the constraint connections on the driver joints for the legs
            connections = []
            for joint in legJoints:
                connections.extend(list(set(cmds.listConnections("driver_" + joint, type = "constraint"))))
                ramps = (list(set(cmds.listConnections("driver_" + joint, type = "ramp"))))
                for ramp in ramps:
                    connections.append(ramp + ".uCoord")


                for connection in connections:
                    driveAttrs = []

                    if cmds.nodeType(connection) in ["pointConstraint", "orientConstraint"]:

                        #get those constraint target attributes for each constraint connection
                        targets = cmds.getAttr(connection + ".target", mi = True)
                        if len(targets) > 1:
                            for each in targets:
                                driveAttrs.append(cmds.listConnections(connection + ".target[" + str(each) + "].targetWeight", p = True))

                            #add this data to our master list of constraint attribute data
                            attrData.append(driveAttrs)
                    else:
                        if cmds.nodeType(connection) == "ramp":
                            rampData.append(connection)

            rampData = list(set(rampData))


            #setup set driven keys on our moder attr and those target attributes
            for i in range(numRigs):

                cmds.setAttr(self.legSettings + ".mode", i)

                #go through attr data and zero out anything but the first element in the list
                for data in attrData:
                    for each in data:
                        cmds.setAttr(each[0], 0)

                    cmds.setAttr(data[i][0], 1)

                #set driven keys
                for data in attrData:
                    for each in data:
                        cmds.setDrivenKeyframe(each[0], cd = self.legSettings + ".mode", itt = "linear", ott = "linear")

            """ RAMPS """
            #direct connect mode to uCoord value (only works if there are 2 rigs...) <- not sure if that is the case still
            for data in rampData:
                #create a multiply node that takes first input of 1/numRigs and 2nd of mode direct connection
                multNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_" + data.partition(".uCoord")[0] + "_mult")
                cmds.setAttr(multNode + ".input1X", float(float(1)/float(numRigs - 1)))
                cmds.connectAttr(self.legSettings + ".mode", multNode + ".input2X")
                cmds.connectAttr(multNode + ".outputX", data)


            """
            builtRigs is a list of the rigs that have been built, but each element has the label of what rig was built, and nodes to hide as the second element,
            like so: ["FK", [topNode]]
                    -the second element is a list of nodes. for FK, there is only 1 item in this list.

            each element in the builtRigs list should coincide with the mode #, so if FK is element 0 in built rigs, mode 0 should be FK.
            """
            #hook up control visibility
            for i in range(len(builtRigs)):
                cmds.setAttr(self.legSettings + ".mode", i)
                for rig in builtRigs:
                    visNodes = rig[1]
                    for node in visNodes:
                        if node != None:
                            cmds.setAttr(node + ".v", 0)

                    if builtRigs.index(rig) == i:
                        visNodes = rig[1]
                        for node in visNodes:
                            if node != None:
                                cmds.setAttr(node + ".v", 1)


                    cmds.setDrivenKeyframe(visNodes, at = "visibility", cd = self.legSettings + ".mode", itt = "linear", ott = "linear")




            #parent under offset_anim if it exists(it always should)
            if cmds.objExists("offset_anim"):
                cmds.parent(self.legGroup, "offset_anim")

        #return data
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        try:
            uiInst.rigData.append([self.legCtrlGrp, "driver_" + parentBone, numRigs])
        except:
            pass



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildIkRig(self, numRigs, slot):

        networkNode = self.returnNetworkNode

        #get main leg joints to duplicate for IK leg rig
        legJoints = self.getMainLegJoints()

        self.ikThigh = cmds.duplicate(legJoints[0], po = True, name = "ikV1_" + legJoints[0] + "_joint")[0]
        self.ikCalf = cmds.duplicate(legJoints[1], po = True, name = "ikV1_" + legJoints[1] + "_joint")[0]
        self.ikFoot = cmds.duplicate(legJoints[2], po = True, name = "ikV1_" + legJoints[2] + "_joint")[0]


        for joint in [self.ikThigh, self.ikCalf, self.ikFoot]:
            parent = cmds.listRelatives(joint, parent = True)
            if parent != None:
                cmds.parent(joint, world = True)

        #create heirarchy
        cmds.parent(self.ikFoot, self.ikCalf)
        cmds.parent(self.ikCalf, self.ikThigh)

        #freeze rotates
        cmds.makeIdentity(self.ikThigh, t = 0, r = 1, s = 0, apply = True)

        #hook up driver joints to these ik joints
        i = 0
        for joint in [self.ikThigh, self.ikCalf, self.ikFoot]:
            cmds.pointConstraint(joint, "driver_" + legJoints[i])
            cmds.orientConstraint(joint, "driver_" + legJoints[i])


            #plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into input 2, and plugs that into driver joint
            if cmds.objExists("master_anim"):
                globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = legJoints[i] + "_globalScale")
                cmds.connectAttr("master_anim.scale",  globalScaleMult + ".input1")
                cmds.connectAttr(joint + ".scale", globalScaleMult + ".input2")
                riggingUtils.createConstraint(globalScaleMult, "driver_" + legJoints[i], "scale", False, numRigs, slot, "output")
            else:
                riggingUtils.createConstraint(joint, "driver_" + legJoints[i], "scale", False, numRigs, slot)


            cmds.setAttr(joint + ".v", 0, lock = True)
            i += 1


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                          create the no-flip setup                                 #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # 1.) Create the No-Flip Bone Chain
        noFlipBegin = cmds.createNode("joint", name = self.name + "_noFlip_begin_joint")
        noFlipEnd = cmds.createNode("joint", name = self.name + "_noFlip_end_joint")
        noFlipGrp = cmds.group(empty = True, name = self.name + "_noFlip_joints_grp")

        cmds.setAttr(noFlipBegin + ".v", 0, lock = True)
        cmds.setAttr(noFlipEnd + ".v", 0, lock = True)
        cmds.parent(noFlipEnd, noFlipBegin)


        constraint = cmds.parentConstraint(self.ikThigh, noFlipGrp)[0]
        cmds.delete(constraint)
        constraint = cmds.parentConstraint(self.ikThigh, noFlipBegin)[0]
        cmds.delete(constraint)
        constraint = cmds.parentConstraint(self.ikFoot, noFlipEnd)[0]
        cmds.delete(constraint)

        #zero out all but tx on noFlipEnd
        cmds.setAttr(noFlipEnd + ".ty", 0)
        cmds.setAttr(noFlipEnd + ".tz", 0)


        cmds.parent(noFlipBegin, noFlipGrp)
        cmds.makeIdentity(noFlipBegin, t = 0, r = 1, s = 0, apply = True)

        #set the preferred angle
        cmds.setAttr(noFlipBegin + ".preferredAngleZ", 90)


        # 2.) create target loc/grp
        targetGrp = cmds.group(empty = True, name = self.name + "_noFlip_target_grp")
        targetLoc = cmds.spaceLocator(name = self.name + "_noFlip_target_loc")[0]
        cmds.setAttr(targetLoc + ".v", 0, lock = True)

        cmds.parent(targetLoc, targetGrp)

        constraint = cmds.pointConstraint(noFlipBegin, targetGrp)[0]
        cmds.delete(constraint)
        constraint = cmds.pointConstraint(noFlipEnd, targetLoc)[0]
        cmds.delete(constraint)

        # 3.) create the aim loc/grp
        aimNodes = cmds.duplicate(targetGrp, name = self.name + "_noFlip_aim_grp", rc = True)
        aimGrp = aimNodes[0]
        aimLoc = aimNodes[1]
        aimLoc = cmds.rename(aimLoc, self.name + "_noFlip_aim_loc")

        #find the world position of the aimGrp
        worldPos = cmds.xform(aimGrp, q = True, ws = True, t = True)

        #find the bone length of the noFlip chain
        length = cmds.getAttr(noFlipEnd + ".tx")

        #now create the world position of where the aim locator needs to be
        if worldPos[0] >= 0:
            aimLocPos = [worldPos[0] + abs(length), worldPos[1], worldPos[2]]
        if worldPos[0] < 0:
            aimLocPos = [(abs(worldPos[0]) + abs(length)) * -1, worldPos[1], worldPos[2]]

        #rotate the aim grp in 90 in every axis until the world position of the aim locator matches the passed in aimLocPos
        self.rotateAimGrp(int(aimLocPos[0]), aimGrp, aimLoc)

        # 4.) Connect TX and TZ of aimLoc to targetLoc
        cmds.connectAttr(targetLoc + ".tx", aimLoc + ".tx")
        cmds.connectAttr(targetLoc + ".tz", aimLoc + ".tz")

        # 5.) set limits on aimLoc translateZ
        currentValue = cmds.getAttr(aimLoc + ".tz")
        cmds.transformLimits(aimLoc, etz = [1, 1], tz = [currentValue, -10])

        # 6.) Create RP IK for noFlip bone chain
        ikNodes = cmds.ikHandle(name = self.name + "_noFlip_ikHandle", solver = "ikRPsolver", sj = noFlipBegin, ee = noFlipEnd)
        cmds.setAttr(ikNodes[0] + ".v", 0, lock = True)

        # 7.) pointConstraint IKHandle to targetLoc
        cmds.pointConstraint(targetLoc, ikNodes[0])

        # 8.) snap target loc to ankle
        constraint = cmds.pointConstraint(self.ikFoot, targetLoc)[0]
        cmds.delete(constraint)

        # 9.) pole vector constraint between ikHandle and aimLoc
        cmds.poleVectorConstraint(aimLoc, ikNodes[0])


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                          create the foot control                                  #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        footControlInfo = riggingUtils.createControlFromMover(legJoints[2], networkNode, False, True)

        cmds.parent(footControlInfo[0], world = True)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", footControlInfo[3])[0]
        cmds.delete(constraint)
        cmds.makeIdentity(footControlInfo[2], t = 1, r= 1, s = 1, apply = True)
        cmds.parent(footControlInfo[0], footControlInfo[1])
        cmds.makeIdentity(footControlInfo[0], t = 1, r= 1, s = 1, apply = True)

        #rename the control info
        self.ikFootCtrl = cmds.rename(footControlInfo[0], "ik_" + legJoints[2] + "_anim")
        cmds.rename(footControlInfo[1], self.ikFootCtrl + "_grp")
        cmds.rename(footControlInfo[2], self.ikFootCtrl + "_space_switcher")
        spaceSwitcherFollow = cmds.rename(footControlInfo[3], self.ikFootCtrl + "_space_switcher_follow")

        #Create leg RP IK
        legIkNodes = cmds.ikHandle(name = self.name + "_noFlip_ikHandle", solver = "ikRPsolver", sj = self.ikThigh, ee = self.ikFoot)
        cmds.setAttr(legIkNodes[0] + ".v", 0, lock = True)

        #parent ik under the foot control
        cmds.parent(legIkNodes[0], self.ikFootCtrl)

        #create a FK matcher node
        fkMatchGrp = cmds.group(empty = True, name = "ik_" + legJoints[2] + "_anim_fkMatchGrp")
        constr = cmds.parentConstraint(self.ikFoot, fkMatchGrp)[0]
        cmds.delete(constr)
        cmds.parent(fkMatchGrp, self.ikFootCtrl)

        fkMatch = cmds.group(empty = True, name = "ik_" + legJoints[2] + "_anim_fkMatch")
        constr = cmds.parentConstraint(self.ikFoot, fkMatch)[0]
        cmds.delete(constr)
        cmds.parent(fkMatch, fkMatchGrp)

        #point constraint target loc to foot ctrl
        cmds.pointConstraint(self.ikFootCtrl, targetLoc)

        #color the foot control
        riggingUtils.colorControl(self.ikFootCtrl)


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                          create the leg chain PV                                  #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        noFlipVectorLoc = cmds.spaceLocator(name = self.name + "_noFlip_pv_loc")[0]
        noFlipVectorGrp = cmds.group(empty = True, name = self.name + "_noFlip_pv_grp")
        cmds.setAttr(noFlipVectorLoc + ".v", 0, lock = True)

        constraint = cmds.pointConstraint([noFlipBegin, noFlipEnd], noFlipVectorLoc)[0]
        cmds.delete(constraint)
        constraint = cmds.pointConstraint(targetLoc, noFlipVectorGrp)[0]
        cmds.delete(constraint)

        #get the length of the leg
        legLength = abs(cmds.getAttr(noFlipEnd + ".tx"))

        #use that length to push out the noFlipVectorLoc in front
        cmds.parent(noFlipVectorLoc, self.ikCalf)
        cmds.setAttr(noFlipVectorLoc + ".translate", 0,0,0, type = "double3")
        cmds.setAttr(noFlipVectorLoc + ".rotate", 0,0,0, type = "double3")

        #get the forward vector for the knee and set the length of the leg on the noFlipVectorLoc translateY
        forwardVector = cmds.xform(self.ikThigh, q = True, ws = True, ro = True)[1]
        if forwardVector < 0:
            cmds.setAttr(noFlipVectorLoc + ".ty", (legLength * -1))
        else:
            cmds.setAttr(noFlipVectorLoc + ".ty", legLength)

        #parent noFlipVectorLoc and constrain the grp to the no flip end joint
        cmds.parent(noFlipVectorLoc, noFlipVectorGrp)
        cmds.makeIdentity(noFlipVectorLoc, t = 1, r = 1, s = 1, apply = True)
        cmds.parentConstraint(noFlipEnd, noFlipVectorGrp, mo = True)

        #pole vector constrain the ikHandle for the leg to the vectorLoc
        cmds.poleVectorConstraint(noFlipVectorLoc, legIkNodes[0])


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                        create the knee vector display                             #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        kneeControl = riggingUtils.createControl("arrow", 1.25, self.name + "_ik_knee_anim")
        constraint = cmds.pointConstraint(self.ikCalf, kneeControl)[0]
        cmds.delete(constraint)

        kneeGrp = cmds.group(empty = True, name = self.name + "_ik_knee_anim_grp")
        constraint = cmds.pointConstraint(self.ikCalf, kneeGrp)[0]
        cmds.delete(constraint)

        cmds.parent(kneeControl, kneeGrp)
        cmds.makeIdentity(kneeControl, t = 1, r = 1, s = 1, apply = True)

        cmds.pointConstraint(self.ikCalf, kneeGrp, mo = True)
        cmds.setAttr(kneeControl + ".overrideEnabled", 1)
        cmds.setAttr(kneeControl + ".overrideDisplayType", 2)

        cmds.aimConstraint(noFlipVectorLoc, kneeGrp, aim = [0, -1, 0], u = [0, 0, 1], wut = "vector", wu = [0, 0, 1])
        cmds.orientConstraint(self.ikCalf, kneeControl, mo = True)

        #color the control
        riggingUtils.colorControl(kneeControl)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                              create the foot rig                                  #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        ballExists = False

        #create ball and toe joints
        if len(legJoints) == 4:
            if cmds.objExists(legJoints[3]):
                ballExists = True


        cmds.select(clear = True)

        #select vertices influenced by foot and ball joint
        selection = []
        skinClusters = cmds.ls(type = "skinCluster")
        for skin in skinClusters:
            infs = cmds.skinCluster(skin, q = True, wi = True)
            if legJoints[2] in infs:
                cmds.skinCluster(skin, edit = True, siv = legJoints[2])
                selection.extend(cmds.ls(sl = True, flatten = True))

            if len(legJoints) == 4:
                if legJoints[3] in infs:
                    cmds.skinCluster(skin, edit = True, siv = legJoints[3])
                    selection.extend(cmds.ls(sl = True, flatten = True))

        #get the bounds of the foot to find the foot length
        cmds.select(selection)
        try:
            bounds = cmds.exactWorldBoundingBox(cmds.ls(sl = True), ce = True, ii = True)
            length = abs(bounds[1] - bounds[4])
        except:
            pass

        cmds.select(clear = True)

        # # #
        #create ball and toe joint
        # # #

        #ball joint creation
        if ballExists:
            self.ikBallJoint = cmds.createNode("joint", name = "ikV1_" + legJoints[3] + "_joint")
            constraint = cmds.parentConstraint(legJoints[3], self.ikBallJoint)[0]
            cmds.delete(constraint)
            cmds.move(0, moveZ = True, ws = True)


        #if there is no ball joint, we need to create one and place it approx. where it should go
        else:
            baseName = cmds.getAttr(networkNode + ".baseName")
            nameData = self.name.split(baseName)

            self.ikBallJoint = cmds.createNode("joint", name = "ikV1_" + nameData[0] + "ball" + nameData[1] + "_joint")
            constraint = cmds.pointConstraint(self.name + "_toe_pivot_mover", self.ikBallJoint)[0]
            cmds.delete(constraint)
            constraint = cmds.orientConstraint(self.name + "_inside_pivot_mover_orient", self.ikBallJoint)[0]
            cmds.delete(constraint)

        cmds.setAttr(self.ikBallJoint + ".v", 0, lock = True)

        #toe joint creation
        baseName = cmds.getAttr(networkNode + ".baseName")
        nameData = self.name.split(baseName)

        self.ikToeJoint = cmds.createNode("joint", name = "ikV1_" + nameData[0] + "toe" + nameData[1] + "_joint")
        constraint = cmds.pointConstraint(self.name + "_toe_pivot_mover", self.ikToeJoint)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ball_mover", self.ikToeJoint)[0]
        cmds.delete(constraint)

        cmds.setAttr(self.ikToeJoint + ".v", 0, lock = True)

        #parent ball and toe joints into ik joint hierarchy
        cmds.parent(self.ikToeJoint, self.ikBallJoint)
        cmds.parent(self.ikBallJoint, self.ikFoot)
        cmds.makeIdentity(self.ikBallJoint, t = 0, r = 1, s = 0, apply = True)

        #constrain driver ball joint to ik ball joint
        if ballExists:

            cmds.pointConstraint(self.ikBallJoint, "driver_" + legJoints[3])
            cmds.orientConstraint(self.ikBallJoint, "driver_" + legJoints[3])
            #plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into input 2, and plugs that into driver joint
            if cmds.objExists("master_anim"):
                globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = legJoints[i] + "_globalScale")
                cmds.connectAttr("master_anim.scale",  globalScaleMult + ".input1")
                cmds.connectAttr(joint + ".scale", globalScaleMult + ".input2")
                riggingUtils.createConstraint(globalScaleMult, "driver_" + legJoints[i], "scale", False, numRigs, slot, "output")
            else:
                riggingUtils.createConstraint(joint, "driver_" + legJoints[i], "scale", False, numRigs, slot)


        #create the SC IK for the ball -> toe
        ballIKNodes = cmds.ikHandle(name = self.name + "_ikHandle_ball", solver = "ikSCsolver", sj = self.ikFoot, ee = self.ikBallJoint)
        toeIKNodes = cmds.ikHandle(name = self.name + "_ikHandle_toe", solver = "ikSCsolver", sj = self.ikBallJoint, ee = self.ikToeJoint)
        cmds.setAttr(ballIKNodes[0] + ".v", 0, lock = True)
        cmds.setAttr(toeIKNodes[0] + ".v", 0, lock = True)

        #create the locators we need for the foot rig
        toeTipPivot = cmds.spaceLocator(name = self.name + "_ik_foot_toe_tip_pivot")[0]
        insidePivot = cmds.spaceLocator(name = self.name + "_ik_foot_inside_pivot")[0]
        outsidePivot = cmds.spaceLocator(name = self.name + "_ik_foot_outside_pivot")[0]
        heelPivot = cmds.spaceLocator(name = self.name + "_ik_foot_heel_pivot")[0]
        toePivot = cmds.spaceLocator(name = self.name + "_ik_foot_toe_pivot")[0]
        ballPivot = cmds.spaceLocator(name = self.name + "_ik_foot_ball_pivot")[0]
        masterBallPivot = cmds.spaceLocator(name = self.name + "_master_foot_ball_pivot")[0]


        #create the controls
        heelControl = riggingUtils.createControl("arrowOnBall", 1, self.name + "_heel_ctrl")
        toeWiggleControl = riggingUtils.createControl("arrowOnBall", 1.5, self.name + "_toe_wiggle_ctrl")
        toeControl = riggingUtils.createControl("arrowOnBall", 1, self.name + "_toe_tip_ctrl")

        #orient controls in worldspace correctly
        cmds.setAttr(heelControl + ".rx", -90)
        cmds.setAttr(toeControl + ".rx", 90)
        cmds.makeIdentity(heelControl, t = 0, r = 1, s = 0, apply = True)
        cmds.makeIdentity(toeControl, t = 0, r = 1, s = 0, apply = True)

        #position controls
        constraint = cmds.parentConstraint(self.name + "_heel_pivot_orient", heelControl)[0]
        cmds.delete(constraint)

        constraint = cmds.pointConstraint(self.name + "_toe_pivot_mover", toeControl)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_toe_pivot_orient", toeControl)[0]
        cmds.delete(constraint)


        constraint = cmds.pointConstraint(self.ikBallJoint, toeWiggleControl)[0]
        cmds.delete(constraint)

        constraint = cmds.orientConstraint(self.name + "_toe_pivot_orient", toeWiggleControl)[0]
        cmds.delete(constraint)

        #create control groups and orient controls properly

        #heelControl
        heelCtrlGrp = cmds.group(empty = True, name = self.name + "_heel_ctrl_grp")
        constraint = cmds.parentConstraint(heelControl, heelCtrlGrp)[0]
        cmds.delete(constraint)
        cmds.parent(heelControl, heelCtrlGrp)
        cmds.makeIdentity(heelControl, t = 1, r = 1, s = 1, apply = True)

        #toeControl
        toeCtrlGrp = cmds.group(empty = True, name = self.name + "_toe_tip_ctrl_grp")
        constraint = cmds.pointConstraint(toeControl, toeCtrlGrp)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.ikToeJoint, toeCtrlGrp)[0]
        cmds.delete(constraint)
        cmds.makeIdentity(toeControl, t = 0, r = 1, s = 0, apply = True)
        cmds.setAttr(toeControl + ".rx", -90)
        cmds.parent(toeControl, toeCtrlGrp)
        cmds.makeIdentity(toeControl, t = 1, r = 1, s = 1, apply = True)

        #toeWiggleControl
        toeWiggleCtrlGrp = cmds.group(empty = True, name = self.name + "_toe_wiggle_ctrl_grp")
        constraint = cmds.pointConstraint(self.ikBallJoint, toeWiggleCtrlGrp)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.ikBallJoint, toeWiggleCtrlGrp)[0]
        cmds.delete(constraint)
        cmds.parent(toeWiggleControl, toeWiggleCtrlGrp)
        cmds.setAttr(toeWiggleControl + ".rx", -90)
        cmds.makeIdentity(toeWiggleControl, t = 1, r = 1, s = 1, apply = True)

        if not ballExists:
            cmds.setAttr(toeWiggleControl + ".v", 0, lock = True)

        #place the pivot locators
        constraint = cmds.pointConstraint(heelControl, heelPivot)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", heelPivot)[0]
        cmds.delete(constraint)

        constraint = cmds.pointConstraint(toeWiggleControl, ballPivot)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", ballPivot)[0]
        cmds.delete(constraint)

        constraint = cmds.pointConstraint(toeWiggleControl, masterBallPivot)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", masterBallPivot)[0]
        cmds.delete(constraint)

        constraint = cmds.pointConstraint(toeControl, toeTipPivot)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", toeTipPivot)[0]
        cmds.delete(constraint)

        constraint = cmds.pointConstraint(toeControl, toePivot)[0]
        cmds.delete(constraint)
        constraint = cmds.orientConstraint(self.name + "_ik_foot_ctrl_orient", toePivot)[0]
        cmds.delete(constraint)

        constraint = cmds.parentConstraint(self.name + "_inside_pivot_mover_orient", insidePivot)[0]
        cmds.delete(constraint)

        constraint = cmds.parentConstraint(self.name + "_outside_pivot_mover_orient", outsidePivot)[0]
        cmds.delete(constraint)


        #create groups for each pivot and parent the pivot to the corresponding group
        for piv in [heelPivot, ballPivot, toeTipPivot, toePivot, insidePivot, outsidePivot, masterBallPivot]:
            pivGrp = cmds.group(empty = True, name = piv + "_grp")
            constraint = cmds.parentConstraint(piv, pivGrp)[0]
            cmds.delete(constraint)
            cmds.parent(piv, pivGrp)
            shape = cmds.listRelatives(piv, shapes = True)[0]
            cmds.setAttr(shape + ".v", 0)


        #setup pivot hierarchy
        cmds.parent(toeWiggleCtrlGrp, toePivot)
        cmds.parent(ballPivot + "_grp", toePivot)
        cmds.parent(toePivot + "_grp", heelPivot)
        cmds.parent(heelPivot + "_grp", outsidePivot)
        cmds.parent(outsidePivot + "_grp", insidePivot)
        cmds.parent(insidePivot + "_grp", toeTipPivot)


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                          create the set driven keys                               #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        #get the side attribute
        side = cmds.getAttr(networkNode + ".side")

        # # # FOOT ROLL # # #
        cmds.setAttr(heelControl + ".rz", 0)
        cmds.setAttr(heelPivot + ".rx", 0)
        cmds.setAttr(toePivot + ".rx", 0)
        cmds.setAttr(ballPivot + ".rx", 0)
        cmds.setDrivenKeyframe([heelPivot + ".rx", toePivot + ".rx", ballPivot + ".rx"], cd = heelControl + ".rz", itt = "linear", ott = "linear")

        cmds.setAttr(heelControl + ".rz", -90)
        cmds.setAttr(heelPivot + ".rx", 0)
        cmds.setAttr(toePivot + ".rx", 0)
        cmds.setAttr(ballPivot + ".rx", 90)
        cmds.setDrivenKeyframe([heelPivot + ".rx", toePivot + ".rx", ballPivot + ".rx"], cd = heelControl + ".rz", itt = "linear", ott = "linear")

        cmds.setAttr(heelControl + ".rz", 90)
        cmds.setAttr(heelPivot + ".rx", -90)
        cmds.setAttr(toePivot + ".rx", 0)
        cmds.setAttr(ballPivot + ".rx", 0)
        cmds.setDrivenKeyframe([heelPivot + ".rx", toePivot + ".rx", ballPivot + ".rx"], cd = heelControl + ".rz", itt = "linear", ott = "linear")

        cmds.setAttr(heelControl + ".rz", 0)
        cmds.setAttr(heelPivot + ".rx", 0)
        cmds.setAttr(toePivot + ".rx", 0)
        cmds.setAttr(ballPivot + ".rx", 0)

        # # # HEEL CONTROL RX & RY # # #
        cmds.connectAttr(heelControl + ".rx", ballPivot + ".rz")
        cmds.connectAttr(heelControl + ".ry", ballPivot + ".ry")

        # # # TOE CONTROL RY & RZ # # #
        if side == "Left":
            cmds.connectAttr(toeControl + ".ry", toeTipPivot + ".rz")

        else:
            toeRzMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_toeTipPivot_RZ_mult")
            cmds.setAttr(toeRzMult + ".input2X", -1)
            cmds.connectAttr(toeControl + ".ry", toeRzMult + ".input1X")
            cmds.connectAttr(toeRzMult + ".outputX", toeTipPivot + ".rz")

        toeRxMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_toeTipPivot_RX_mult")
        cmds.setAttr(toeRxMult + ".input2X", -1)
        cmds.connectAttr(toeControl + ".rz", toeRxMult + ".input1X")
        cmds.connectAttr(toeRxMult + ".outputX", toeTipPivot + ".rx")

        # # # FOOT SIDE TO SIDE # # #
        cmds.setAttr(toeControl + ".rx", 0)
        cmds.setAttr(insidePivot + ".rx", 0)
        cmds.setAttr(outsidePivot + ".rx", 0)
        cmds.setDrivenKeyframe([insidePivot + ".rx", outsidePivot + ".rx"], cd = toeControl + ".rx", itt = "linear", ott = "linear")

        cmds.setAttr(toeControl + ".rx", -90)
        cmds.setAttr(insidePivot + ".rx", 0)
        cmds.setAttr(outsidePivot + ".rx", -90)
        cmds.setDrivenKeyframe([insidePivot + ".rx", outsidePivot + ".rx"], cd = toeControl + ".rx", itt = "linear", ott = "linear")

        cmds.setAttr(toeControl + ".rx", 90)
        cmds.setAttr(insidePivot + ".rx", 90)
        cmds.setAttr(outsidePivot + ".rx", 0)
        cmds.setDrivenKeyframe([insidePivot + ".rx", outsidePivot + ".rx"], cd = toeControl + ".rx", itt = "linear", ott = "linear")

        cmds.setAttr(toeControl + ".rx", 0)
        cmds.setAttr(insidePivot + ".rx", 0)
        cmds.setAttr(outsidePivot + ".rx", 0)

        #parent the IK nodes into the foot rig setup
        cmds.parent(legIkNodes[0], ballPivot)
        cmds.parent(ballIKNodes[0], ballPivot)
        cmds.parent(toeIKNodes[0], toeWiggleControl)

        cmds.parent([toeTipPivot + "_grp", heelControl + "_grp", toeControl + "_grp"], masterBallPivot)
        cmds.parent(masterBallPivot + "_grp", self.ikFootCtrl)

        #add the heel pivot and ball pivot attrs to the foot control
        cmds.addAttr(heelControl, longName= ( "heelPivot" ), defaultValue=0,  keyable = True)
        cmds.addAttr(heelControl, longName= ( "ballPivot" ), defaultValue=0,  keyable = True)

        #setup heel and ball pivot
        if side == "Left":
            cmds.connectAttr(heelControl + ".heelPivot", heelPivot + ".rz")
            cmds.connectAttr(heelControl + ".ballPivot", masterBallPivot + ".rz")

        else:
            heelPivotMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_heelPivotMult")
            cmds.setAttr(heelPivotMult + ".input2X", -1)
            cmds.connectAttr(heelControl + ".heelPivot", heelPivotMult + ".input1X")
            cmds.connectAttr(heelPivotMult + ".outputX", heelPivot + ".rz")

            ballPivotMult = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_ballPivotMult")
            cmds.setAttr(ballPivotMult + ".input2X", -1)
            cmds.connectAttr(heelControl + ".ballPivot", ballPivotMult + ".input1X")
            cmds.connectAttr(ballPivotMult + ".outputX", masterBallPivot + ".rz")


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                connect ik twist attr to custom attr on foot ctrl                  #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        cmds.addAttr(self.ikFootCtrl, longName=("knee_twist"), at = 'double', keyable = True)

        if side == "Right":
            cmds.connectAttr(self.ikFootCtrl + ".knee_twist", legIkNodes[0] + ".twist")
        else:
            twistMultNode = cmds.shadingNode("multiplyDivide", name = self.name + "ik_knee_twistMultNode", asUtility = True)
            cmds.connectAttr(self.ikFootCtrl + ".knee_twist", twistMultNode + ".input1X")
            cmds.setAttr(twistMultNode + ".input2X", -1)
            cmds.connectAttr(twistMultNode + ".outputX", legIkNodes[0] + ".twist")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                          setup ik squash and stretch                              #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


        """
        Note about stretch bias, since this part is really confusing:

            the math goes like this:
                if the current leg length > original leg length, then the leg needs to stretch (if attr is on)
                1.) take the stretch bias attr from the foot control and divide by 5.
                    -Why 5? It's just an arbitrary number. The point of stretch bias is to essentially add onto the original length,
                    so that when we divide current by original, we get a slightly smaller number than we normally would. If stretch bias is 0, this returns 0. If 1, then .2
                2.) Take that result and add 1.
                    -Why? So that we aren't dividing the current length by 0 (original length * that result). At most, we would divide it by current length/(original * 1.2)
                    -At least would be current length /(original * 1)
                3.) Take the add node result (1 + stretch bias output) and multiply it by original length
                4.) Take the current length and put that into input1 of a new mult node
                5.) Take the result of step 3 and put it into input 2. Set operation to divide
                6.) This gets us current/(original * stretch bias output)
                7.) Lastly, create a blendColors node passing in color 1r as 1.0, and 2r as the scale factor
                8.) Pass in the stretch attr into blender. if stretch is .5, given 1 and 1.3, result is 1.15. That is the scale to be applied to joints.
        """



        #add attrs to the foot ctrl
        cmds.addAttr(self.ikFootCtrl, longName=("stretch"), at = 'double',min = 0, max = 1, dv = 0, keyable = True)
        cmds.addAttr(self.ikFootCtrl, longName=("squash"), at = 'double',min = 0, max = 1, dv = 0, keyable = True)
        cmds.addAttr(self.ikFootCtrl, longName=("toeCtrlVis"), at = 'bool', dv = 0, keyable = True)

        #need to get the total length of the leg chain
        totalDist = abs(cmds.getAttr(self.ikCalf + ".tx" ) + cmds.getAttr(self.ikFoot + ".tx"))

        #create a distanceBetween node
        distBetween = cmds.shadingNode("distanceBetween", asUtility = True, name = self.name + "_ik_leg_distBetween")

        #get world positions of thigh and ik
        baseGrp = cmds.group(empty = True, name = self.name + "_ik_leg_base_grp")
        endGrp = cmds.group(empty = True, name = self.name + "_ik_leg_end_grp")
        cmds.pointConstraint(self.ikThigh, baseGrp)
        cmds.pointConstraint(self.ikFootCtrl, endGrp)

        #hook in group translates into distanceBetween node inputs
        cmds.connectAttr(baseGrp + ".translate", distBetween + ".point1")
        cmds.connectAttr(endGrp + ".translate", distBetween + ".point2")


        #create a condition node that will compare original length to current length
        #if second term is greater than, or equal to the first term, the chain needs to stretch
        ikLegCondition = cmds.shadingNode("condition", asUtility = True, name = self.name + "_ik_leg_stretch_condition")
        cmds.setAttr(ikLegCondition + ".operation", 3)
        cmds.connectAttr(distBetween + ".distance", ikLegCondition + ".secondTerm")
        cmds.setAttr(ikLegCondition + ".firstTerm", totalDist)


        #hook up the condition node's return colors
        cmds.setAttr(ikLegCondition + ".colorIfTrueR", totalDist)
        cmds.connectAttr(distBetween + ".distance", ikLegCondition + ".colorIfFalseR")

        #add attr to foot control for stretch bias
        cmds.addAttr(self.ikFootCtrl, ln = "stretchBias", minValue = -1.0, maxValue = 1.0, defaultValue = 0.0, keyable = True)

        #add divide node so that instead of driving 0-1, we're actually only driving 0 - 0.2
        divNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_stretchBias_Div")
        cmds.connectAttr(self.ikFootCtrl + ".stretchBias", divNode + ".input1X")
        cmds.setAttr(divNode + ".operation", 2)
        cmds.setAttr(divNode + ".input2X", 5)

        #create the add node and connect the stretchBias into it, adding 1
        addNode = cmds.shadingNode("plusMinusAverage", asUtility = True, name = self.name + "_stretchBias_Add")
        cmds.connectAttr(divNode + ".outputX", addNode + ".input1D[0]")
        cmds.setAttr(addNode + ".input1D[1]", 1.0)

        #connect output of addNode to new mult node input1x
        stretchBiasMultNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_stretchBias_multNode")
        cmds.connectAttr(addNode + ".output1D", stretchBiasMultNode + ".input1X")

        #create the mult/divide node(set to divide) that will take the original creation length as a static value in input2x, and the connected length into 1x. This will get the scale factor
        legDistMultNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_leg_dist_multNode")
        cmds.setAttr(legDistMultNode + ".operation", 2) #divide
        cmds.connectAttr(ikLegCondition + ".outColorR", legDistMultNode + ".input1X")

        #set input2x to totalDist
        cmds.setAttr(stretchBiasMultNode + ".input2X", totalDist)
        cmds.connectAttr(stretchBiasMultNode + ".outputX", legDistMultNode + ".input2X")


        """ This differs from the original code. Instead of using a condition, I will use a blendColors node so that stretch % has an effect """

        #create a blendColors node for stretch
        blendResult = cmds.shadingNode("blendColors", asUtility = True, name = self.name + "_leg_stretch_scaleFactor")
        cmds.setAttr(blendResult + ".color2R", 1)
        cmds.connectAttr(legDistMultNode + ".outputX", blendResult + ".color1R")
        cmds.connectAttr(self.ikFootCtrl + ".stretch", blendResult + ".blender")

        #create a blendColors node for squash
        blendResultSquash = cmds.shadingNode("blendColors", asUtility = True, name = self.name + "_leg_squash_scaleFactor")
        cmds.setAttr(blendResultSquash + ".color2R", 1)
        cmds.connectAttr(legDistMultNode + ".outputX", blendResultSquash + ".color1R")
        cmds.connectAttr(self.ikFootCtrl + ".squash", blendResultSquash + ".blender")

        #get the sqrt of the scale factor by creating a multiply node and setting it to power operation
        powerNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_sqrt_scaleFactor")
        cmds.setAttr(powerNode + ".operation", 3)
        cmds.connectAttr(blendResultSquash + ".outputR", powerNode + ".input1X")
        cmds.setAttr(powerNode + ".input2X", .5)

        #now divide 1 by that result
        squashDivNode = cmds.shadingNode("multiplyDivide", asUtility = True, name = self.name + "_squash_Value")
        cmds.setAttr(squashDivNode + ".operation", 2)
        cmds.setAttr(squashDivNode + ".input1X", 1)
        cmds.connectAttr(powerNode + ".outputX", squashDivNode + ".input2X")


        #connect to leg joint scale attributes
        cmds.connectAttr(blendResult + ".outputR", self.ikThigh + ".sx")
        cmds.connectAttr(blendResult + ".outputR", self.ikCalf + ".sx")

        cmds.connectAttr(squashDivNode + ".outputX", self.ikCalf + ".sy")
        cmds.connectAttr(squashDivNode + ".outputX", self.ikCalf + ".sz")

        cmds.connectAttr(squashDivNode + ".outputX", self.ikThigh + ".sy")
        cmds.connectAttr(squashDivNode + ".outputX", self.ikThigh + ".sz")


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                                   clean up                                        #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        cmds.parent([targetGrp, aimGrp, noFlipVectorGrp], noFlipGrp)
        cmds.parent([self.ikThigh, noFlipGrp], self.legCtrlGrp)

        ikGrp = cmds.group(name = self.name + "_ik_group", empty = True)
        cmds.parent([spaceSwitcherFollow, ikNodes[0], kneeGrp], ikGrp)

        cmds.parent([spaceSwitcherFollow, ikGrp, baseGrp, endGrp], self.legGroup)

        return [[self.ikFootCtrl, heelControl, toeControl, toeWiggleControl], kneeGrp]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildToeRigs(self, joints):

        networkNode = self.returnNetworkNode

        #number of rigs. Might need to be pulled from a setting in the future
        buildFK = True
        buildIK = False  #later feature? Skip for now.
        numRigs = 0

        if buildFK:
            numRigs += 1
        if buildIK:
            numRigs += 1

        if numRigs > 1:
            cmds.addAttr(self.legSettings, ln = "toeRigMode", min = 0, max = numRigs - 1, dv = 0, keyable = True)

        if numRigs >= 1:
            #setup visibility to leg settings toe mode (will need to add attribute first)
            if not cmds.objExists(self.legSettings + ".toeCtrlVis"):
                cmds.addAttr(self.legSettings, ln = "toeCtrlVis", min = 0, max = 1, dv = 0, keyable = True)

        #build the fk rig if needed
        if buildFK:

            if not cmds.objExists(self.name + "_toe_rig_grp"):
                toeRigGrp = cmds.group(empty = True, name = self.name + "_toe_rig_grp")
                cmds.parent(toeRigGrp, self.legGroup)

            #create the control from the mover
            fkToeNodes = riggingUtils.createFkRig(joints, networkNode, numRigs, 0)

            if not cmds.objExists(networkNode + ".toeControls"):
                cmds.addAttr(networkNode, ln = "toeControls", dt = "string")
                jsonString = json.dumps(fkToeNodes[1])
                cmds.setAttr(networkNode + ".toeControls", jsonString, type = "string")

            else:
                currentData = json.loads(cmds.getAttr(networkNode + ".toeControls"))
                currentData.extend(fkToeNodes[1])
                jsonString = json.dumps(currentData)
                cmds.setAttr(networkNode + ".toeControls", jsonString, type = "string")

            for toe in fkToeNodes[1]:


                #default color
                color = 18

                #first, let's color controls
                currentColor = cmds.getAttr(toe + ".overrideColor")
                if currentColor == 13:
                    color = 4

                cmds.setAttr(toe + ".overrideColor", color)

                #next, duplicate the toe group for each toe, parent under the toe grp, freeze transforms, and parent the toe control under it
                drivenGrp = cmds.duplicate(toe + "_grp", po = True, name = toe + "_driven_grp")
                cmds.parent(drivenGrp, toe + "_grp")
                cmds.makeIdentity(drivenGrp, t = 1, r = 1, s = 1, apply = True)
                cmds.parent(toe, drivenGrp)

                #need to find the top most group node's parent, and unparent the top most group node from it
                #parent under the toe rig grp and parentConstraint to original parent's driver joint
                parent = cmds.listRelatives(toe + "_grp", parent = True)

                if parent == None:
                    cmds.parent(toe + "_grp", self.name + "_toe_rig_grp")

                    #get the joint the parent is driving
                    joint = toe.partition("fk_")[2].partition("_anim")[0]
                    parent = cmds.listRelatives(joint, parent = True)[0]
                    driverJnt = "driver_" + parent
                    cmds.parentConstraint(driverJnt, toe + "_grp", mo = True)


                #setup set connections on toes for toe ctrl vis
                cmds.connectAttr(self.legSettings + ".toeCtrlVis", toe + "_grp.v")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def rotateAimGrp(self, aimLocPos, aimGrp, aimLoc):

        for attr in [".rotateX", ".rotateY", ".rotateZ"]:
            cmds.setAttr(aimGrp + attr, 90)
            currentVal = int(cmds.xform(aimLoc, q = True, ws = True, t = True)[0])
            if currentVal == aimLocPos:
                return
            else:
                cmds.setAttr(aimGrp + attr, -90)
                currentVal = int(cmds.xform(aimLoc, q = True, ws = True, t = True)[0])
                if currentVal == aimLocPos:
                    return
                else:
                    cmds.setAttr(aimGrp + attr, 0)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getMainLegJoints(self):

        thighJoint = None
        calfJoint = None
        footJoint = None
        ballJoint = None

        returnData = []

        #thigh
        joints = self.returnCreatedJoints
        for joint in joints:
            if joint.find("thigh") != -1:
                if joint.find("twist") == -1:
                    thighJoint = joint
                    returnData.append(thighJoint)

        #calf
        for joint in joints:
            if joint.find("calf") != -1:
                if joint.find("twist") == -1:
                    calfJoint = joint
                    returnData.append(calfJoint)

        #foot
        for joint in joints:
            if joint.find("foot") != -1:
                footJoint = joint
                returnData.append(footJoint)

        #ball
        for joint in joints:
            if joint.find("ball") != -1:
                ballJoint = joint
                returnData.append(ballJoint)

        return returnData


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getLegTwistJoints(self, thighTwists, calfTwists):

        thighTwistBones = []
        calfTwistBones = []

        joints = self.returnCreatedJoints


        #thigh
        for joint in joints:
            if joint.find("thigh") != -1:
                if joint.find("twist") != -1:
                    thighTwistBones.append(joint)

        #calf
        for joint in joints:
            if joint.find("calf") != -1:
                if joint.find("twist") != -1:
                    calfTwistBones.append(joint)


        if thighTwists:
            return thighTwistBones
        if calfTwists:
            return calfTwistBones



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def setAttrViaInterface(self, attr, checkbox):

        networkNode = self.returnNetworkNode

        state = checkbox.isChecked()

        cmds.setAttr(networkNode + "." + attr, lock = False)
        cmds.setAttr(networkNode + "." + attr, state, lock = True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mirrorTransformations_Custom(self):

        networkNode = self.returnNetworkNode
        mirrorModule = cmds.getAttr(networkNode + ".mirrorModule")
        moduleName = cmds.getAttr(networkNode + ".moduleName")

        for mover in [self.name + "_toe_pivot_mover", self.name + "_heel_pivot_mover"]:
            for attr in [".rotateY", ".rotateZ"]:
                value = cmds.getAttr(mover + attr)
                mirrorMover = mover.replace(moduleName, mirrorModule)
                cmds.setAttr(mirrorMover + attr, value * -1)

            for attr in [".translateY", ".translateZ"]:
                value = cmds.getAttr(mover + attr)
                mirrorMover = mover.replace(moduleName, mirrorModule)
                cmds.setAttr(mirrorMover + attr, value)

        for mover in [self.name + "_outside_pivot_mover", self.name + "_inside_pivot_mover"]:
            for attr in [".rotateX", ".rotateZ"]:
                value = cmds.getAttr(mover + attr)
                mirrorMover = mover.replace(moduleName, mirrorModule)
                cmds.setAttr(mirrorMover + attr, value * -1)

        #outside translates
        value = cmds.getAttr(self.name + "_outside_pivot_mover.tz")
        mirrorMover = (self.name + "_outside_pivot_mover").replace(moduleName, mirrorModule)
        cmds.setAttr(mirrorMover + ".tz", value)

        value = cmds.getAttr(self.name + "_outside_pivot_mover.ty")
        mirrorMover = (self.name + "_outside_pivot_mover").replace(moduleName, mirrorModule)
        cmds.setAttr(mirrorMover + ".ty", value)

        #inside translates
        value = cmds.getAttr(self.name + "_inside_pivot_mover.tz")
        mirrorMover = (self.name + "_inside_pivot_mover").replace(moduleName, mirrorModule)
        cmds.setAttr(mirrorMover + ".tz", value)

        value = cmds.getAttr(self.name + "_inside_pivot_mover.tx")
        mirrorMover = (self.name + "_inside_pivot_mover").replace(moduleName, mirrorModule)
        cmds.setAttr(mirrorMover + ".tx", value)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def includeBallJoint(self, apply, *args):
        state = self.ballJoint.isChecked()

        self.bigToeNum.setEnabled(state)
        self.indexToeNum.setEnabled(state)
        self.middleToeNum.setEnabled(state)
        self.ringToeNum.setEnabled(state)
        self.pinkyToeNum.setEnabled(state)

        if state == False:
            #set values back to 0
            self.bigToeNum.setValue(0)
            self.indexToeNum.setValue(0)
            self.middleToeNum.setValue(0)
            self.ringToeNum.setValue(0)
            self.pinkyToeNum.setValue(0)

            #show ball to toe bone geo
            cmds.setAttr(self.name + "_noToes_bone_geo.v", lock = False)
            cmds.setAttr(self.name + "_noToes_bone_geo.v", 1, lock = True)

            #hide ball mover controls
            cmds.setAttr(self.name + "_ball_mover_grp.v", lock = False)
            cmds.setAttr(self.name + "_ball_mover_grp.v", 0, lock = True)


        if state == True:
            #show ball mover controls
            cmds.setAttr(self.name + "_ball_mover_grp.v", lock = False)
            cmds.setAttr(self.name + "_ball_mover_grp.v", 1, lock = True)

        #apply changes
        if apply:
            self.applyModuleChanges(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleButtonState(self):

        state = self.applyButton.isEnabled()
        if state == False:
            self.applyButton.setEnabled(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editMetaTarsals(self, uiWidget,  searchKey, *args):

        #uiWidget is the spinBox
        #isBigToe will be the special case, since there are only the three joints instead of the 4
        #searchKey is the basname (bigToe, middle, ring, etc)

        #unlock bone representations
        cmds.select(self.name + "_bone_representations", hi = True)
        selection = cmds.ls(sl = True, type = "transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock = False)


        #toggle visibility
        if uiWidget.isChecked():
            try:
                cmds.parent(self.name + "_" + searchKey + "_proximal_phalange_mover_grp", self.name + "_" + searchKey + "_metatarsal_mover")
            except Exception, e:
                print e

            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_mover_grp.v", lock = False)
            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_mover_grp.v", 1, lock = True)
            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_bone_geo.v", 1)


        if not uiWidget.isChecked():
            try:
                cmds.parent(self.name + "_" + searchKey + "_proximal_phalange_mover_grp", self.name + "_ball_mover")
            except Exception, e:
                print e

            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_mover_grp.v", lock = False)
            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_mover_grp.v", 0, lock = True)
            cmds.setAttr(self.name + "_" + searchKey + "_metatarsal_bone_geo.v", 0)

        #relock bone representations
        cmds.select(self.name + "_bone_representations", hi = True)
        selection = cmds.ls(sl = True, type = "transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock = True)

        #toggle mover vis
        self.rigUiInst.setMoverVisibility()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editJointMoverViaSpinBox(self, uiWidget, searchKey, isBigToe, *args):

        #uiWidget is the spinBox
        #isBigToe will be the special case, since there are only the three joints instead of the 4
        #searchKey is the basname (bigToe, middle, ring, etc)

        #unlock bone representations
        cmds.select(self.name + "_bone_representations", hi = True)
        selection = cmds.ls(sl = True, type = "transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock = False)

        #check number in spinBox
        num = uiWidget.value()

        #set visibility on movers and geo depending on the value of num
        for i in range(num + 1):
            #purely for fanciness
            time.sleep(.05)
            cmds.refresh(force = True)

            if isBigToe == False:

                moverList = ["_proximal_phalange", "_middle_phalange", "_distal_phalange"]
                for mover in moverList:
                    if moverList.index(mover) <= i -1:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock = False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 1, lock = True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 1)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 1)

                    if i == 0:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock = False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 0, lock = True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 0)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 0)

            if isBigToe == True:

                moverList = ["_proximal_phalange", "_distal_phalange"]
                for mover in moverList:
                    if moverList.index(mover) <= i -1:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock = False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 1, lock = True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 1)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 1)

                    if i == 0:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock = False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 0, lock = True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 0)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 0)


        #relock bone representations
        cmds.select(self.name + "_bone_representations", hi = True)
        selection = cmds.ls(sl = True, type = "transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock = True)

        #toggle mover vis
        self.rigUiInst.setMoverVisibility()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editJointMoverTwistBones(self, uiWidget, searchKey, *args):

        #check number in spinBox
        num = uiWidget.value()

        for i in range(num + 1):

            if i == 0:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 0, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 0, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock = True)

            if i == 1:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 0, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock = True)

            if i == 2:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 1, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock = True)

            if i == 3:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 1, lock = True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock = False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 1, lock = True)





    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addJointMoverToOutliner(self):

        index = self.rigUiInst.treeWidget.topLevelItemCount()

        #Add the module to the tree widget in the outliner tab of the rig creator UI
        self.outlinerWidgets[self.name + "_treeModule"] = QtWidgets.QTreeWidgetItem(self.rigUiInst.treeWidget)
        self.rigUiInst.treeWidget.topLevelItem(index).setText(0, self.name)
        foreground = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.outlinerWidgets[self.name + "_treeModule"].setForeground(0, foreground)

        #add the thigh
        self.outlinerWidgets[self.name + "_thigh"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_thigh"].setText(0, self.name + "_thigh")
        self.createGlobalMoverButton(self.name + "_thigh", self.outlinerWidgets[self.name + "_thigh"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thigh", self.outlinerWidgets[self.name + "_thigh"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_thigh", self.outlinerWidgets[self.name + "_thigh"], self.rigUiInst)

        #add the thigh twists
        self.outlinerWidgets[self.name + "_thigh_twist_01"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_thigh"])
        self.outlinerWidgets[self.name + "_thigh_twist_01"].setText(0, self.name + "_thigh_twist_01")
        #self.createGlobalMoverButton(self.name + "_thigh_twist_01", self.outlinerWidgets[self.name + "_thigh_twist_01"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thigh_twist_01", self.outlinerWidgets[self.name + "_thigh_twist_01"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_thigh_twist_01", self.outlinerWidgets[self.name + "_thigh_twist_01"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_thigh_twist_01"].setHidden(True)

        self.outlinerWidgets[self.name + "_thigh_twist_02"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_thigh"])
        self.outlinerWidgets[self.name + "_thigh_twist_02"].setText(0, self.name + "_thigh_twist_02")
        #self.createGlobalMoverButton(self.name + "_thigh_twist_02", self.outlinerWidgets[self.name + "_thigh_twist_02"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thigh_twist_02", self.outlinerWidgets[self.name + "_thigh_twist_02"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_thigh_twist_02", self.outlinerWidgets[self.name + "_thigh_twist_02"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_thigh_twist_02"].setHidden(True)

        self.outlinerWidgets[self.name + "_thigh_twist_03"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_thigh"])
        self.outlinerWidgets[self.name + "_thigh_twist_03"].setText(0, self.name + "_thigh_twist_03")
        #self.createGlobalMoverButton(self.name + "_thigh_twist_03", self.outlinerWidgets[self.name + "_thigh_twist_03"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thigh_twist_03", self.outlinerWidgets[self.name + "_thigh_twist_03"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_thigh_twist_03", self.outlinerWidgets[self.name + "_thigh_twist_03"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_thigh_twist_03"].setHidden(True)

        #add the calf
        self.outlinerWidgets[self.name + "_calf"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_thigh"] )
        self.outlinerWidgets[self.name + "_calf"].setText(0, self.name + "_calf")
        self.createGlobalMoverButton(self.name + "_calf", self.outlinerWidgets[self.name + "_calf"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_calf", self.outlinerWidgets[self.name + "_calf"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_calf", self.outlinerWidgets[self.name + "_calf"], self.rigUiInst)

        #add the calf twists
        self.outlinerWidgets[self.name + "_calf_twist_01"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_calf"] )
        self.outlinerWidgets[self.name + "_calf_twist_01"].setText(0, self.name + "_calf_twist_01")
        #self.createGlobalMoverButton(self.name + "_calf_twist_01", self.outlinerWidgets[self.name + "_calf_twist_01"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_calf_twist_01", self.outlinerWidgets[self.name + "_calf_twist_01"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_calf_twist_01", self.outlinerWidgets[self.name + "_calf_twist_01"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_calf_twist_01"].setHidden(True)

        self.outlinerWidgets[self.name + "_calf_twist_02"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_calf"] )
        self.outlinerWidgets[self.name + "_calf_twist_02"].setText(0, self.name + "_calf_twist_02")
        #self.createGlobalMoverButton(self.name + "_calf_twist_02", self.outlinerWidgets[self.name + "_calf_twist_02"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_calf_twist_02", self.outlinerWidgets[self.name + "_calf_twist_02"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_calf_twist_02", self.outlinerWidgets[self.name + "_calf_twist_02"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_calf_twist_02"].setHidden(True)

        self.outlinerWidgets[self.name + "_calf_twist_03"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_calf"] )
        self.outlinerWidgets[self.name + "_calf_twist_03"].setText(0, self.name + "_calf_twist_03")
        #self.createGlobalMoverButton(self.name + "_calf_twist_03", self.outlinerWidgets[self.name + "_calf_twist_03"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_calf_twist_03", self.outlinerWidgets[self.name + "_calf_twist_03"], self.rigUiInst)
        #self.createMeshMoverButton(self.name + "_calf_twist_03", self.outlinerWidgets[self.name + "_calf_twist_03"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_calf_twist_03"].setHidden(True)

        #add the foot
        self.outlinerWidgets[self.name + "_foot"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_calf"] )
        self.outlinerWidgets[self.name + "_foot"].setText(0, self.name + "_foot")
        self.createGlobalMoverButton(self.name + "_foot", self.outlinerWidgets[self.name + "_foot"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_foot", self.outlinerWidgets[self.name + "_foot"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_foot", self.outlinerWidgets[self.name + "_foot"], self.rigUiInst)

        #add the ball
        self.outlinerWidgets[self.name + "_ball"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_foot"] )
        self.outlinerWidgets[self.name + "_ball"].setText(0, self.name + "_ball")
        self.createGlobalMoverButton(self.name + "_ball", self.outlinerWidgets[self.name + "_ball"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ball", self.outlinerWidgets[self.name + "_ball"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ball", self.outlinerWidgets[self.name + "_ball"], self.rigUiInst)

        #add the big toes
        self.outlinerWidgets[self.name + "_bigtoe_metatarsal"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_bigtoe_metatarsal"].setText(0, self.name + "_bigtoe_metatarsal")
        self.createGlobalMoverButton(self.name + "_bigtoe_metatarsal", self.outlinerWidgets[self.name + "_bigtoe_metatarsal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_bigtoe_metatarsal", self.outlinerWidgets[self.name + "_bigtoe_metatarsal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_bigtoe_metatarsal"].setHidden(True)

        self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"].setText(0, self.name + "_bigtoe_proximal_phalange")
        self.createGlobalMoverButton(self.name + "_bigtoe_proximal_phalange", self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_bigtoe_proximal_phalange", self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_bigtoe_proximal_phalange", self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_bigtoe_proximal_phalange"] )
        self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"].setText(0, self.name + "_bigtoe_distal_phalange")
        self.createGlobalMoverButton(self.name + "_bigtoe_distal_phalange", self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_bigtoe_distal_phalange", self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_bigtoe_distal_phalange", self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_bigtoe_distal_phalange"].setHidden(True)

        #add the index toes
        self.outlinerWidgets[self.name + "_index_metatarsal"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_index_metatarsal"].setText(0, self.name + "_index_metatarsal")
        self.createGlobalMoverButton(self.name + "_index_metatarsal", self.outlinerWidgets[self.name + "_index_metatarsal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_metatarsal", self.outlinerWidgets[self.name + "_index_metatarsal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_index_metatarsal"].setHidden(True)

        self.outlinerWidgets[self.name + "_index_proximal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_index_proximal_phalange"].setText(0, self.name + "_index_proximal_phalange")
        self.createGlobalMoverButton(self.name + "_index_proximal_phalange", self.outlinerWidgets[self.name + "_index_proximal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_proximal_phalange", self.outlinerWidgets[self.name + "_index_proximal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_proximal_phalange", self.outlinerWidgets[self.name + "_index_proximal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_index_proximal_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_index_middle_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_index_proximal_phalange"] )
        self.outlinerWidgets[self.name + "_index_middle_phalange"].setText(0, self.name + "_index_middle_phalange")
        self.createGlobalMoverButton(self.name + "_index_middle_phalange", self.outlinerWidgets[self.name + "_index_middle_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_middle_phalange", self.outlinerWidgets[self.name + "_index_middle_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_middle_phalange", self.outlinerWidgets[self.name + "_index_middle_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_index_middle_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_index_distal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_index_middle_phalange"] )
        self.outlinerWidgets[self.name + "_index_distal_phalange"].setText(0, self.name + "_index_distal_phalange")
        self.createGlobalMoverButton(self.name + "_index_distal_phalange", self.outlinerWidgets[self.name + "_index_distal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_distal_phalange", self.outlinerWidgets[self.name + "_index_distal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_distal_phalange", self.outlinerWidgets[self.name + "_index_distal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_index_distal_phalange"].setHidden(True)


        #add the middle toes
        self.outlinerWidgets[self.name + "_middle_metatarsal"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_middle_metatarsal"].setText(0, self.name + "_middle_metatarsal")
        self.createGlobalMoverButton(self.name + "_middle_metatarsal", self.outlinerWidgets[self.name + "_middle_metatarsal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_metatarsal", self.outlinerWidgets[self.name + "_middle_metatarsal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_middle_metatarsal"].setHidden(True)

        self.outlinerWidgets[self.name + "_middle_proximal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_middle_proximal_phalange"].setText(0, self.name + "_middle_proximal_phalange")
        self.createGlobalMoverButton(self.name + "_middle_proximal_phalange", self.outlinerWidgets[self.name + "_middle_proximal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_proximal_phalange", self.outlinerWidgets[self.name + "_middle_proximal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_proximal_phalange", self.outlinerWidgets[self.name + "_middle_proximal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_middle_proximal_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_middle_middle_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_middle_proximal_phalange"] )
        self.outlinerWidgets[self.name + "_middle_middle_phalange"].setText(0, self.name + "_middle_middle_phalange")
        self.createGlobalMoverButton(self.name + "_middle_middle_phalange", self.outlinerWidgets[self.name + "_middle_middle_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_middle_phalange", self.outlinerWidgets[self.name + "_middle_middle_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_middle_phalange", self.outlinerWidgets[self.name + "_middle_middle_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_middle_middle_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_middle_distal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_middle_middle_phalange"] )
        self.outlinerWidgets[self.name + "_middle_distal_phalange"].setText(0, self.name + "_middle_distal_phalange")
        self.createGlobalMoverButton(self.name + "_middle_distal_phalange", self.outlinerWidgets[self.name + "_middle_distal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_distal_phalange", self.outlinerWidgets[self.name + "_middle_distal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_distal_phalange", self.outlinerWidgets[self.name + "_middle_distal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_middle_distal_phalange"].setHidden(True)


        #add the ring toes
        self.outlinerWidgets[self.name + "_ring_metatarsal"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_ring_metatarsal"].setText(0, self.name + "_ring_metatarsal")
        self.createGlobalMoverButton(self.name + "_ring_metatarsal", self.outlinerWidgets[self.name + "_ring_metatarsal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_metatarsal", self.outlinerWidgets[self.name + "_ring_metatarsal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_ring_metatarsal"].setHidden(True)

        self.outlinerWidgets[self.name + "_ring_proximal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_ring_proximal_phalange"].setText(0, self.name + "_ring_proximal_phalange")
        self.createGlobalMoverButton(self.name + "_ring_proximal_phalange", self.outlinerWidgets[self.name + "_ring_proximal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_proximal_phalange", self.outlinerWidgets[self.name + "_ring_proximal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_proximal_phalange", self.outlinerWidgets[self.name + "_ring_proximal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_ring_proximal_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_ring_middle_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ring_proximal_phalange"] )
        self.outlinerWidgets[self.name + "_ring_middle_phalange"].setText(0, self.name + "_ring_middle_phalange")
        self.createGlobalMoverButton(self.name + "_ring_middle_phalange", self.outlinerWidgets[self.name + "_ring_middle_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_middle_phalange", self.outlinerWidgets[self.name + "_ring_middle_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_middle_phalange", self.outlinerWidgets[self.name + "_ring_middle_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_ring_middle_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_ring_distal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ring_middle_phalange"] )
        self.outlinerWidgets[self.name + "_ring_distal_phalange"].setText(0, self.name + "_ring_distal_phalange")
        self.createGlobalMoverButton(self.name + "_ring_distal_phalange", self.outlinerWidgets[self.name + "_ring_distal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_distal_phalange", self.outlinerWidgets[self.name + "_ring_distal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_distal_phalange", self.outlinerWidgets[self.name + "_ring_distal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_ring_distal_phalange"].setHidden(True)


        #add the pinky toes
        self.outlinerWidgets[self.name + "_pinky_metatarsal"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_pinky_metatarsal"].setText(0, self.name + "_pinky_metatarsal")
        self.createGlobalMoverButton(self.name + "_pinky_metatarsal", self.outlinerWidgets[self.name + "_pinky_metatarsal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_metatarsal", self.outlinerWidgets[self.name + "_pinky_metatarsal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_pinky_metatarsal"].setHidden(True)

        self.outlinerWidgets[self.name + "_pinky_proximal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_ball"] )
        self.outlinerWidgets[self.name + "_pinky_proximal_phalange"].setText(0, self.name + "_pinky_proximal_phalange")
        self.createGlobalMoverButton(self.name + "_pinky_proximal_phalange", self.outlinerWidgets[self.name + "_pinky_proximal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_proximal_phalange", self.outlinerWidgets[self.name + "_pinky_proximal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_proximal_phalange", self.outlinerWidgets[self.name + "_pinky_proximal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_pinky_proximal_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_pinky_middle_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_pinky_proximal_phalange"] )
        self.outlinerWidgets[self.name + "_pinky_middle_phalange"].setText(0, self.name + "_pinky_middle_phalange")
        self.createGlobalMoverButton(self.name + "_pinky_middle_phalange", self.outlinerWidgets[self.name + "_pinky_middle_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_middle_phalange", self.outlinerWidgets[self.name + "_pinky_middle_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_middle_phalange", self.outlinerWidgets[self.name + "_pinky_middle_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_pinky_middle_phalange"].setHidden(True)

        self.outlinerWidgets[self.name + "_pinky_distal_phalange"] = QtWidgets.QTreeWidgetItem(self.outlinerWidgets[self.name + "_pinky_middle_phalange"] )
        self.outlinerWidgets[self.name + "_pinky_distal_phalange"].setText(0, self.name + "_pinky_distal_phalange")
        self.createGlobalMoverButton(self.name + "_pinky_distal_phalange", self.outlinerWidgets[self.name + "_pinky_distal_phalange"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_distal_phalange", self.outlinerWidgets[self.name + "_pinky_distal_phalange"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_distal_phalange", self.outlinerWidgets[self.name + "_pinky_distal_phalange"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_pinky_distal_phalange"].setHidden(True)


        #create selection script job for module
        self.createScriptJob()

        #update based on spinBox values
        self.updateOutliner()
        self.updateBoneCount()
        self.rigUiInst.treeWidget.expandAll()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateSettingsUI(self):

        #this function will update the settings UI when the UI is launched based on the network node settings in the scene
        networkNode = self.returnNetworkNode

        thighTwists = cmds.getAttr(networkNode + ".thighTwists")
        calfTwists = cmds.getAttr(networkNode + ".calfTwists")
        bigToes = cmds.getAttr(networkNode + ".bigToeJoints")
        indexToes = cmds.getAttr(networkNode + ".indexToeJoints")
        middleToes = cmds.getAttr(networkNode + ".middleToeJoints")
        ringToes = cmds.getAttr(networkNode + ".ringToeJoints")
        pinkyToes = cmds.getAttr(networkNode + ".pinkyToeJoints")
        includeBall = cmds.getAttr(networkNode + ".includeBall")
        bigToeMeta = cmds.getAttr(networkNode + ".bigToeMeta")
        indexToeMeta = cmds.getAttr(networkNode + ".indexToeMeta")
        middleToeMeta = cmds.getAttr(networkNode + ".middleToeMeta")
        ringToeMeta = cmds.getAttr(networkNode + ".ringToeMeta")
        pinkyToeMeta = cmds.getAttr(networkNode + ".pinkyToeMeta")

        #update UI elements
        self.thighTwistNum.setValue(thighTwists)
        self.calfTwistNum.setValue(calfTwists)
        self.ballJoint.setChecked(includeBall)

        self.bigToeNum.setValue(bigToes)
        self.indexToeNum.setValue(indexToes)
        self.middleToeNum.setValue(middleToes)
        self.ringToeNum.setValue(ringToes)
        self.pinkyToeNum.setValue(pinkyToes)

        self.bigToeMeta.setChecked(bigToeMeta)
        self.indexToeMeta.setChecked(indexToeMeta)
        self.middleToeMeta.setChecked(middleToeMeta)
        self.ringToeMeta.setChecked(ringToeMeta)
        self.pinkyToeMeta.setChecked(pinkyToeMeta)

        #apply changes
        self.applyButton.setEnabled(False)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateOutliner(self):

        #whenever changes are made to the module settings, update the outliner to show the new or removed movers

        #THIGH TWISTS
        thighTwists = self.thighTwistNum.value()
        if thighTwists == 0:
            self.outlinerWidgets[self.originalName + "_thigh_twist_01"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_thigh_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_thigh_twist_03"].setHidden(True)
        if thighTwists == 1:
            self.outlinerWidgets[self.originalName + "_thigh_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thigh_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_thigh_twist_03"].setHidden(True)
        if thighTwists == 2:
            self.outlinerWidgets[self.originalName + "_thigh_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thigh_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thigh_twist_03"].setHidden(True)
        if thighTwists == 3:
            self.outlinerWidgets[self.originalName + "_thigh_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thigh_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thigh_twist_03"].setHidden(False)

        #CALF TWISTS
        calfTwists = self.calfTwistNum.value()
        if calfTwists == 0:
            self.outlinerWidgets[self.originalName + "_calf_twist_01"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_calf_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_calf_twist_03"].setHidden(True)
        if calfTwists == 1:
            self.outlinerWidgets[self.originalName + "_calf_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_calf_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_calf_twist_03"].setHidden(True)
        if calfTwists == 2:
            self.outlinerWidgets[self.originalName + "_calf_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_calf_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_calf_twist_03"].setHidden(True)
        if calfTwists == 3:
            self.outlinerWidgets[self.originalName + "_calf_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_calf_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_calf_twist_03"].setHidden(False)

        #BALL JOINT
        ballJoint = self.ballJoint.isChecked()
        if ballJoint:
            self.outlinerWidgets[self.originalName + "_ball"].setHidden(False)
        else:
            self.outlinerWidgets[self.originalName + "_ball"].setHidden(True)


        #BIG TOES
        bigToes = self.bigToeNum.value()
        bigToeMeta = self.bigToeMeta.isChecked()

        if bigToes == 0:
            self.outlinerWidgets[self.originalName + "_bigtoe_proximal_phalange"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_bigtoe_distal_phalange"].setHidden(True)
        if bigToes == 1:
            self.outlinerWidgets[self.originalName + "_bigtoe_proximal_phalange"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_bigtoe_distal_phalange"].setHidden(True)
        if bigToes == 2:
            self.outlinerWidgets[self.originalName + "_bigtoe_proximal_phalange"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_bigtoe_distal_phalange"].setHidden(False)

        if bigToeMeta:
            self.outlinerWidgets[self.originalName + "_bigtoe_metatarsal"].setHidden(False)
        if not bigToeMeta:
            self.outlinerWidgets[self.originalName + "_bigtoe_metatarsal"].setHidden(True)

        toes = [[self.indexToeNum, "index", self.indexToeMeta],[self.middleToeNum, "middle", self.middleToeMeta],[self.ringToeNum, "ring", self.ringToeMeta],[self.pinkyToeNum, "pinky", self.pinkyToeMeta]]

        #OTHER TOES
        for toe in toes:
            value = toe[0].value()
            meta = toe[2].isChecked()

            if value == 0:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_proximal_phalange"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_middle_phalange"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_distal_phalange"].setHidden(True)
            if value == 1:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_proximal_phalange"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_middle_phalange"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_distal_phalange"].setHidden(True)
            if value == 2:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_proximal_phalange"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_middle_phalange"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_distal_phalange"].setHidden(True)
            if value == 3:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_proximal_phalange"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_middle_phalange"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_distal_phalange"].setHidden(False)

            if meta:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_metatarsal"].setHidden(False)
            if not meta:
                self.outlinerWidgets[self.originalName + "_" + toe[1] + "_metatarsal"].setHidden(True)





    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetSettings(self):

        networkNode = self.returnNetworkNode
        attrs = cmds.listAttr(networkNode, ud = True, hd = True)

        for attr in attrs:
            attrType = str(cmds.getAttr(networkNode + "." + attr, type = True))

            if attrType == "double":
                cmds.setAttr(networkNode + "." + attr, lock = False)
                cmds.setAttr(networkNode + "." + attr, 0, lock = True)

            if attrType == "bool":
                if attr.find("Meta") != -1:
                    cmds.setAttr(networkNode + "." + attr, lock = False)
                    cmds.setAttr(networkNode + "." + attr, False, lock = True)
                if attr.find("Meta") == -1:
                    cmds.setAttr(networkNode + "." + attr, lock = False)
                    cmds.setAttr(networkNode + "." + attr, True, lock = True)


        #relaunch the UI
        self.updateSettingsUI()
        self.applyModuleChanges(self)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def applyModuleChanges(self, moduleInst):

        #create an array of the created bones that fit a format [thighName, thighTwistA, thighTwistB, thighTwistC, calfName, etc]
        createdBones = self.returnCreatedJoints
        #list all base names of spinBox/checkBox joints
        removeBones = ["ball", "thigh_twist_0", "calf_twist_0", "pinky", "index", "bigtoe", "ring", "middle"]

        removeList = []
        for bone in createdBones:
            for removeBone in removeBones:
                if bone.find(removeBone) != -1:
                    removeList.append(bone)


        keepBones = []
        for bone in createdBones:
            if bone not in removeList:
                keepBones.append(bone)

        #get prefix/suffix
        name = self.groupBox.title()
        prefix = name.partition(baseName)[0]
        suffix = name.partition(baseName)[2]

        if len(prefix) > 0:
            if prefix.find("_") == -1:
                prefix = prefix + "_"
        if len(suffix) > 0:
            if suffix.find("_") == -1:
                suffix = "_" + suffix

        legJoints = [keepBones[0]]

        #get thigh twists, calf twists, and toes
        thighTwists = self.thighTwistNum.value()
        for i in range(thighTwists):
            legJoints.append(prefix + "thigh_twist_0" + str(i + 1) + suffix)
        legJoints.append(keepBones[1])

        calfTwists = self.calfTwistNum.value()
        for i in range(calfTwists):
            legJoints.append(prefix + "calf_twist_0" + str(i + 1) + suffix)
        legJoints.append(keepBones[2])

        ballJoint = self.ballJoint.isChecked()
        if ballJoint:
            legJoints.append(prefix + "ball" + suffix)

        #toes
        bigToes = self.bigToeNum.value()
        bigToeJoints = ["proximal_phalange", "distal_phalange"]
        toeJoints = ["proximal_phalange", "middle_phalange", "distal_phalange"]
        for i in range(bigToes):
            legJoints.append(prefix + "bigtoe_" + bigToeJoints[i] + suffix)

        indexToes = self.indexToeNum.value()
        for i in range(indexToes):
            legJoints.append(prefix + "index_" + toeJoints[i] + suffix)

        middleToes = self.middleToeNum.value()
        for i in range(middleToes):
            legJoints.append(prefix + "middle_" + toeJoints[i] + suffix)

        ringToes = self.ringToeNum.value()
        for i in range(ringToes):
            legJoints.append(prefix + "ring_" + toeJoints[i] + suffix)

        pinkyToes = self.pinkyToeNum.value()
        for i in range(pinkyToes):
            legJoints.append(prefix + "pinky_" + toeJoints[i] + suffix)

        #metatarsals
        if self.bigToeMeta.isChecked():
            legJoints.append(prefix + "bigtoe_metatarsal" + suffix)
        if self.indexToeMeta.isChecked():
            legJoints.append(prefix + "index_metatarsal" + suffix)
        if self.middleToeMeta.isChecked():
            legJoints.append(prefix + "middle_metatarsal" + suffix)
        if self.ringToeMeta.isChecked():
            legJoints.append(prefix + "ring_metatarsal" + suffix)
        if self.pinkyToeMeta.isChecked():
            legJoints.append(prefix + "pinky_metatarsal" + suffix)


        #build attrString
        attrString = ""
        for bone in legJoints:
            attrString += bone + "::"

        networkNode = self.returnNetworkNode
        cmds.setAttr(networkNode + ".Created_Bones", lock = False)
        cmds.setAttr(networkNode + ".Created_Bones", attrString, type = "string", lock = True)

        #reset button
        self.applyButton.setEnabled(False)

        #hide/show noToes geo based on numToes
        numToes = 0
        for each in [self.bigToeNum, self.indexToeNum, self.middleToeNum, self.ringToeNum, self.pinkyToeNum]:
            value = each.value()
            if value > 0:
                numToes += 1
        cmds.setAttr(self.name + "_noToes_bone_geo.v", lock = False)
        if numToes > 0:
            cmds.setAttr(self.name + "_noToes_bone_geo.v", 0, lock = True)
        else:
            cmds.setAttr(self.name + "_noToes_bone_geo.v", 1, lock = True)

        #update joint mover
        self.editJointMoverViaSpinBox(self.bigToeNum, "bigtoe", True)
        self.editJointMoverViaSpinBox(self.indexToeNum, "index", False)
        self.editJointMoverViaSpinBox(self.middleToeNum, "middle", False)
        self.editJointMoverViaSpinBox(self.ringToeNum, "ring", False)
        self.editJointMoverViaSpinBox(self.pinkyToeNum, "pinky", False)

        self.editJointMoverTwistBones(self.thighTwistNum, "thigh")
        self.editJointMoverTwistBones(self.calfTwistNum, "calf")

        self.includeBallJoint(False)

        self.editMetaTarsals(self.bigToeMeta, "bigtoe")
        self.editMetaTarsals(self.indexToeMeta, "index")
        self.editMetaTarsals(self.middleToeMeta, "middle")
        self.editMetaTarsals(self.ringToeMeta, "ring")
        self.editMetaTarsals(self.pinkyToeMeta, "pinky")


        #set network node attributes
        cmds.setAttr(networkNode + ".thighTwists", lock = False)
        cmds.setAttr(networkNode + ".thighTwists", thighTwists, lock = True)

        cmds.setAttr(networkNode + ".calfTwists", lock = False)
        cmds.setAttr(networkNode + ".calfTwists", calfTwists, lock = True)

        cmds.setAttr(networkNode + ".bigToeJoints", lock = False)
        cmds.setAttr(networkNode + ".bigToeJoints", bigToes, lock = True)

        cmds.setAttr(networkNode + ".indexToeJoints", lock = False)
        cmds.setAttr(networkNode + ".indexToeJoints", indexToes, lock = True)

        cmds.setAttr(networkNode + ".middleToeJoints", lock = False)
        cmds.setAttr(networkNode + ".middleToeJoints", middleToes, lock = True)

        cmds.setAttr(networkNode + ".ringToeJoints", lock = False)
        cmds.setAttr(networkNode + ".ringToeJoints", ringToes, lock = True)

        cmds.setAttr(networkNode + ".pinkyToeJoints", lock = False)
        cmds.setAttr(networkNode + ".pinkyToeJoints", pinkyToes, lock = True)

        cmds.setAttr(networkNode + ".includeBall", lock = False)
        cmds.setAttr(networkNode + ".includeBall", ballJoint, lock = True)

        cmds.setAttr(networkNode + ".bigToeMeta", lock = False)
        cmds.setAttr(networkNode + ".bigToeMeta", self.bigToeMeta.isChecked(), lock = True)

        cmds.setAttr(networkNode + ".indexToeMeta", lock = False)
        cmds.setAttr(networkNode + ".indexToeMeta", self.indexToeMeta.isChecked(), lock = True)

        cmds.setAttr(networkNode + ".ringToeMeta", lock = False)
        cmds.setAttr(networkNode + ".ringToeMeta", self.ringToeMeta.isChecked(), lock = True)

        cmds.setAttr(networkNode + ".middleToeMeta", lock = False)
        cmds.setAttr(networkNode + ".middleToeMeta", self.middleToeMeta.isChecked(), lock = True)

        cmds.setAttr(networkNode + ".pinkyToeMeta", lock = False)
        cmds.setAttr(networkNode + ".pinkyToeMeta", self.pinkyToeMeta.isChecked(), lock = True)

        #update outliner
        self.updateOutliner()
        self.updateBoneCount()

        #clear selection
        cmds.select(clear = True)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pinModule(self, state):

        networkNode = self.returnNetworkNode

        if state:
            topLevelMover = self.name + "_thigh_mover_grp"
            loc = cmds.spaceLocator()[0]
            cmds.setAttr(loc + ".v", False, lock = True)
            constraint = cmds.parentConstraint(topLevelMover, loc)[0]
            cmds.delete(constraint)
            const = cmds.parentConstraint(loc, topLevelMover)[0]


            if not cmds.objExists(networkNode + ".pinConstraint"):
                cmds.addAttr(networkNode, ln = "pinConstraint", keyable = True, at = "message")

            cmds.connectAttr(const + ".message", networkNode + ".pinConstraint")

        if not state:
            connections = cmds.listConnections(networkNode + ".pinConstraint")
            if len(connections) > 0:
                constraint = connections[0]
                cmds.delete(constraint)

        cmds.select(clear = True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skinProxyGeo(self):

        #get the network node
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        baseName = cmds.getAttr(networkNode + ".baseName")
        prefix = name.partition(baseName)[0]
        suffix = name.partition(baseName)[2]

        #get this module's proxy geo meshes
        cmds.select(name + "_mover_grp", hi = True)
        proxyGeoMeshes = []
        selection = cmds.ls(sl = True)
        for each in selection:
            if each.find("proxy_geo") != -1:
                parent = cmds.listRelatives(each, parent = True)[0]
                if parent != name + "_noToes_bone_geo":
                    if cmds.nodeType(each) == "transform":
                        proxyGeoMeshes.append(each)


        #skin the proxy geo meshes
        for mesh in proxyGeoMeshes:
            dupeMesh = cmds.duplicate(mesh, name = "skin_" + mesh)[0]
            cmds.setAttr(dupeMesh + ".overrideEnabled", lock = False)
            cmds.setAttr(dupeMesh + ".overrideDisplayType", 0)

            #create skinned geo group
            if not cmds.objExists("skinned_proxy_geo"):
                cmds.group(empty = True, name = "skinned_proxy_geo")

            cmds.parent(dupeMesh, "skinned_proxy_geo")

            boneName = mesh.partition(name + "_")[2]
            boneName = boneName.partition("_proxy_geo")[0]
            joint = prefix + boneName + suffix

            if not cmds.objExists(joint):
                cmds.delete(dupeMesh)

            else:
                cmds.select([dupeMesh, joint])
                cmds.skinCluster(tsb = True, maximumInfluences = 1, obeyMaxInfluences = True,  bindMethod = 0, skinMethod = 0, normalizeWeights = True)
                cmds.select(clear = True)



        #SPECIAL CASE FOR TOES/NO TOES
        numToes = 0
        for attr in ["bigToeJoints", "indexToeJoints", "middleToeJoints", "ringToeJoints", "pinkyToeJoints"]:
            value = cmds.getAttr(networkNode + "." + attr)
            if value > 0:
                numToes += 1

        if numToes == 0:
            if cmds.getAttr(networkNode + ".includeBall") == False:
                joint = prefix + "foot" + suffix
            else:
                joint = prefix + "ball" + suffix

            #dupe the toe_proxy geo
            dupeMesh = cmds.duplicate(name + "_toe_proxy_geo")[0]
            cmds.select(dupeMesh, hi = True)
            cmds.delete(constraints = True)
            cmds.parent(dupeMesh, "skinned_proxy_geo")

            #skin the geo
            if not cmds.objExists(joint):
                cmds.delete(dupeMesh)

            else:
                cmds.select([dupeMesh, joint])
                cmds.skinCluster(tsb = True, maximumInfluences = 1, obeyMaxInfluences = True,  bindMethod = 0, skinMethod = 0, normalizeWeights = True)
                cmds.select(clear = True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeSide(self):

        #gather information (current name, current parent, etc)
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        parent = cmds.getAttr(networkNode + ".parentModuleBone")
        currentSide = cmds.getAttr(networkNode + ".side")

        if cmds.getAttr(networkNode + ".aimMode") == True:
            self.aimMode_Setup(False)

        #call on base class delete
        cmds.select(self.name + "_mover_grp", hi = True)
        nodes = cmds.ls(sl = True)
        for node in nodes:
            cmds.lockNode(lock = False)
        cmds.delete(self.name + "_mover_grp")


        #figure out side
        if currentSide == "Left":
            cmds.setAttr(networkNode + ".side", lock = False)
            cmds.setAttr(networkNode + ".side", "Right", type = "string", lock = True)
            side = "Right"
        if currentSide == "Right":
            cmds.setAttr(networkNode + ".side", lock = False)
            cmds.setAttr(networkNode + ".side", "Left", type = "string", lock = True)
            side = "Left"


        #build new jmPath name
        jmPath = jointMover.partition(".ma")[0] + "_" + side + ".ma"
        self.jointMover_Build(jmPath)

        #parent the joint mover to the offset mover of the parent
        mover = ""

        if parent == "root":
            cmds.parent(name + "_mover_grp", "root_mover")
            mover = "root_mover"

        else:
            #find the parent mover name to parent to
            networkNodes = utils.returnRigModules()
            mover = utils.findMoverNodeFromJointName(networkNodes, parent)
            if mover != None:
                cmds.parent(name + "_mover_grp", mover)

        #create the connection geo between the two
        childMover = utils.findOffsetMoverFromName(name)
        rigging.createBoneConnection(mover, childMover, name)
        self.applyModuleChanges(self)

        self.aimMode_Setup(True)


        cmds.select(clear = True)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def aimMode_Setup(self, state):

        #get attributes needed
        name = self.groupBox.title()
        networkNode = self.returnNetworkNode
        side = cmds.getAttr(networkNode + ".side")

        #setup aim vector details per side
        legAim = [-1, 0, 0]
        legUp = [1, 0, 0]
        ballAim = [0, -1, 0]
        toeAim = [1, 0, 0]
        toeUp = [0, 1, 0]

        if side == "Right":
            legAim = [1, 0, 0]
            legUp = [-1, 0, 0]
            ballAim = [0, 1, 0]
            toeAim = [-1, 0, 0]
            toeUp = [0, -1, 0]

        #if passed in state is True:
        if state:
            #setup aim constraints

            #mesh movers on thigh/calf
            cmds.aimConstraint(name + "_calf_lra", name + "_thigh_mover_geo", aimVector = legAim, upVector = legUp, wut = "scene", wu = [0, 0, 1], mo = True)
            cmds.aimConstraint(name + "_foot_lra", name + "_calf_mover_geo", aimVector = legAim, upVector = legUp, wut = "scene", wu = [0, 0, 1], mo = True)


            cmds.aimConstraint(name + "_calf_mover_offset", name + "_thigh_mover_offset", aimVector = legAim, upVector = legUp, wut = "scene", wu = [0, 0, 1])
            cmds.aimConstraint(name + "_foot_mover_offset", name + "_calf_mover_offset", aimVector = legAim, upVector = legUp, wut = "scene", wu = [0, 0, 1])

            #ball
            if cmds.getAttr(name + "_ball_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ball_mover_offset", name + "_foot_mover_offset", aimVector = ballAim, upVector = legUp, wut = "scene", wu = [0, 0, 1], mo = True)

            #big toe
            if cmds.getAttr(name + "_bigtoe_proximal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_bigtoe_proximal_phalange_mover_offset", name + "_bigtoe_metatarsal_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_bigtoe_distal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_bigtoe_distal_phalange_mover_offset", name + "_bigtoe_proximal_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])

            #index toe
            if cmds.getAttr(name + "_index_proximal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_proximal_phalange_mover_offset", name + "_index_metatarsal_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_index_middle_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_middle_phalange_mover_offset", name + "_index_proximal_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_index_distal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_distal_phalange_mover_offset", name + "_index_middle_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])

            #middle toe
            if cmds.getAttr(name + "_middle_proximal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_proximal_phalange_mover_offset", name + "_middle_metatarsal_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_middle_middle_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_middle_phalange_mover_offset", name + "_middle_proximal_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_middle_distal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_distal_phalange_mover_offset", name + "_middle_middle_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])

            #ring toe
            if cmds.getAttr(name + "_ring_proximal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_proximal_phalange_mover_offset", name + "_ring_metatarsal_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_ring_middle_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_middle_phalange_mover_offset", name + "_ring_proximal_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_ring_distal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_distal_phalange_mover_offset", name + "_ring_middle_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])

            #pinky toe
            if cmds.getAttr(name + "_pinky_proximal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_proximal_phalange_mover_offset", name + "_pinky_metatarsal_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_pinky_middle_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_middle_phalange_mover_offset", name + "_pinky_proximal_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])
            if cmds.getAttr(name + "_pinky_distal_phalange_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_distal_phalange_mover_offset", name + "_pinky_middle_phalange_mover_offset", aimVector = toeAim, upVector = toeUp, wut = "scene", wu = [0, 0, 1])

        #if passed in state is False:
        if not state:
            cmds.select(name + "_mover_grp", hi = True)
            aimConstraints = cmds.ls(sl = True, exactType = "aimConstraint")

            for constraint in aimConstraints:
                cmds.lockNode(constraint, lock = False)
                cmds.delete(constraint)

            self.bakeOffsets()
            cmds.select(clear = True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def coplanarMode(self):

        #current selection
        currentSelection = cmds.ls(sl = True)

        #get the state of the button
        state = self.coplanarBtn.isChecked()

        #write the attribute on the module
        networkNode = self.returnNetworkNode

        import System.utils as utils

        aimState = cmds.getAttr(networkNode + ".aimMode")

        if state:


            #lock out offset movers as they aren't to be used in coplanar mode
            offsetMovers = self.returnJointMovers[1]
            for mover in offsetMovers:
                cmds.lockNode(mover, lock = False)
                for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]:
                    try:
                        cmds.setAttr(mover + attr, lock = True)
                    except:
                        pass

            #fire script job that watches the coplanarIkHandle attributes, and when they change, snap to IK knee in tz
            self.coplanarScriptJob1 = cmds.scriptJob(attributeChange = [self.name + "_coplanarIkHandle.translate", partial(riggingUtils.coPlanarModeSnap, self, self.name + "_coplanar_knee", self.name + "_calf_mover_offset", [self.name + "_coplanar_thigh", self.name + "_coplanar_knee"], [self.name + "_thigh_mover_offset", self.name + "_calf_mover_offset"], self.name + "_foot_mover", [])], kws = True)

            #make sure aim mode is on
            if not aimState:
                self.aimMode_Setup(True)


            #reselect current selection
            if len(currentSelection) > 0:
                cmds.select(currentSelection)

        if not state:
            #unlock all offset movers
            offsetMovers = self.returnJointMovers[1]
            for mover in offsetMovers:
                for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]:
                    try:
                        cmds.setAttr(mover + attr, lock = False)

                    except:
                        pass

                cmds.lockNode(mover, lock = True)

            cmds.scriptJob(kill = self.coplanarScriptJob1)
            self.aimMode_Setup(False)

            if aimState:
                self.aimMode_Setup(True)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def setupModelPoseForRig(self):

        createdConstraints = []

        legJoints = self.getMainLegJoints()

        thighMover = self.name + "_thigh_mover_offset"
        calfMover = self.name + "_calf_mover_offset"
        footMover = self.name + "_foot_mover_offset"

        footCtrlConst = cmds.parentConstraint(footMover, self.ikFootCtrl, mo = True)[0]
        createdConstraints.append(footCtrlConst)

        fkThighConst = cmds.parentConstraint(thighMover, "fk_" + legJoints[0] + "_anim")[0]
        createdConstraints.append(fkThighConst)

        fkCalfConst = cmds.parentConstraint(calfMover, "fk_" + legJoints[1] + "_anim")[0]
        createdConstraints.append(fkCalfConst)

        fkFootConst = cmds.parentConstraint(footMover, "fk_" + legJoints[2] + "_anim")[0]
        createdConstraints.append(fkFootConst)


        if len(legJoints) == 4:
            if legJoints[3] != None:
                ballMover = self.name + "_ball_mover_offset"

                fkBallConst = cmds.parentConstraint(ballMover, "fk_" + legJoints[3] + "_anim")[0]
                createdConstraints.append(fkBallConst)

        return createdConstraints



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def matchModelPose(self):

        #match the knee twist attribute to the offset mover for the knee
        legJoints = self.getMainLegJoints()

        #first create locators
        loc1 = cmds.spaceLocator(name = self.name + "_matchLoc1")[0]
        loc2 = cmds.spaceLocator(name = self.name + "_matchLoc2")[0]

        constraint = cmds.parentConstraint(self.name + "_calf_mover_offset", loc1)[0]
        cmds.delete(constraint)
        cmds.parent(loc1, self.name + "_calf_mover_offset")

        constraint = cmds.parentConstraint(legJoints[1], loc2)[0]
        cmds.delete(constraint)
        cmds.parent(loc2, legJoints[1])

        cmds.move(0, -30, 0, loc1, os = True, r = True)
        cmds.move(0, -30, 0, loc2, os = True, r = True)

        for x in range(1500):
            angle = mathUtils.getAngleBetween(loc1, loc2)
            if abs(angle) > .1:
                self.matchKneeTwist(angle, loc1, loc2)
            else:
                break

        cmds.delete(loc1)
        cmds.delete(loc2)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def matchKneeTwist(self, angle, object1, object2):

        currentVal = cmds.getAttr(self.ikFootCtrl + ".knee_twist")
        cmds.setAttr(self.ikFootCtrl + ".knee_twist", currentVal + .25)

        newAngle = mathUtils.getAngleBetween(object1, object2)
        if newAngle > angle:
            cmds.setAttr(self.ikFootCtrl + ".knee_twist", currentVal - .5)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX(self, importMethod, character):

        returnControls = []

        networkNode = self.returnRigNetworkNode
        fkControls = cmds.getAttr(networkNode + ".fkControls")
        ikControls = cmds.getAttr(networkNode + ".ikV1Controls")
        moduleName = cmds.getAttr(networkNode + ".moduleName")


        #find created joints
        joints = cmds.getAttr(networkNode + ".Created_Bones")

        splitJoints = joints.split("::")
        createdJoints = []
        legJoints = []

        for bone in splitJoints:
            if bone != "":
                createdJoints.append(bone)

        for joint in createdJoints:
            if joint.find("thigh") != -1:
                if joint.find("twist") == -1:
                    thighJoint = joint
                    legJoints.append(thighJoint)

            if joint.find("calf") != -1:
                if joint.find("twist") == -1:
                    calfJoint = joint
                    legJoints.append(calfJoint)

            if joint.find("foot") != -1:
                footJoint = joint
                legJoints.append(footJoint)

            if joint.find("ball") != -1:
                ballJoint = joint
                legJoints.append(ballJoint)


        #Handle Import Method/Constraints
        if importMethod == "FK":
            cmds.setAttr(character + ":" + moduleName + "_settings.mode", 0)

            for joint in legJoints:
                cmds.parentConstraint(joint, character + ":fk_" + joint + "_anim")
                returnControls.append(character + ":fk_" + joint + "_anim")


        if importMethod == "IK":
            cmds.parentConstraint(legJoints[2], character + ":ik_" + legJoints[2] + "_anim", mo = True)
            returnControls.append(character + ":ik_" + legJoints[2] + "_anim")

        if importMethod == "Both":
            cmds.parentConstraint(legJoints[2], character + ":ik_" + legJoints[2] + "_anim", mo = True)
            returnControls.append(character + ":ik_" + legJoints[2] + "_anim")

            for joint in legJoints:
                cmds.parentConstraint(joint, character + ":fk_" + joint + "_anim")
                returnControls.append(character + ":fk_" + joint + "_anim")


        if importMethod == "None":
            pass

        return returnControls




    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX_post(self, importMethod, character):

        #get leg joints/controls
        legJoints = self.getMainLegJoints()
        self.ikFootCtrl = character + ":ik_" + legJoints[2] + "_anim"

        cmds.refresh(force = True)

        #get start and end frames
        start = cmds.playbackOptions(q = True, min = True)
        end = cmds.playbackOptions(q = True, max = True)

        if importMethod == "IK" or importMethod == "Both":
            for i in range(int(start), int(end) + 1):
                cmds.currentTime(i)
                self.ikKneeMatch(character, legJoints[1], legJoints[0], character + ":" + legJoints[1])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def switchMode(self, mode, checkBox, range = False):

        #get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        #are we matching?
        if not range:
            match = checkBox.isChecked()
        else:
            match = True

        #if being called from match over frame range
        if range:
            if mode == matchData[1][0]:
                mode = "FK"
            if mode == matchData[1][1]:
                mode = "IK"


        #switch to FK mode
        if mode == "FK":
            #get current mode
            currentMode = cmds.getAttr(namespace + ":" + self.name + "_settings.mode")
            if currentMode == 0.0:
                cmds.warning("Already in FK mode.")
                return

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

            if match:
                #get fk controls
                controls = json.loads(cmds.getAttr(networkNode + ".fkControls"))

                #create a duplicate chain
                topCtrl = controls[0]
                topGrp = cmds.listRelatives(namespace + ":" + topCtrl, parent = True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world = True)


                #match the fk controls to the corresponding joint
                for control in controls:
                    joint = control.partition("fk_")[2].partition("_anim")[0]
                    joint = namespace + ":" + joint
                    constraint = cmds.parentConstraint(joint, control)[0]
                    cmds.delete(constraint)

                    translate = cmds.getAttr(control + ".translate")[0]
                    rotate = cmds.getAttr(control + ".rotate")[0]

                    cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2], type = 'double3')
                    cmds.setAttr(namespace + ":" + control + ".rotate", rotate[0], rotate[1], rotate[2], type = 'double3')

                    cmds.setKeyframe(namespace + ":" + control)

                #delete dupes
                cmds.delete(newControls[0])

                #switch modes
                if not range:
                    cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")


        #switch to IK mode
        if mode == "IK":

            #get current mode
            currentMode = cmds.getAttr(namespace + ":" + self.name + "_settings.mode")
            if currentMode == 1.0:
                return

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

            if match:

                #get IK controls
                controls = json.loads(cmds.getAttr(networkNode + ".ikV1Controls"))

                #create a duplicate foot anim
                control = controls[0]
                topGrp = cmds.listRelatives(namespace + ":" + control, parent = True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world = True)


                #duplicate the control once more and parent under the fkMatch node
                matchCtrl = cmds.duplicate(control, po = True)[0]
                cmds.parent(matchCtrl, control + "_fkMatch")

                #match the foot anim to the foot joint
                joint = control.partition("ik_")[2].partition("_anim")[0]
                joint = namespace + ":" + joint
                constraint = cmds.parentConstraint(joint, control + "_fkMatch")[0]
                cmds.delete(constraint)

                #unparent the match control from the fkMatch, and put it under the topGrp
                cmds.parent(matchCtrl, topGrp)

                #this will now give use good values
                translate = cmds.getAttr(matchCtrl + ".translate")[0]
                rotate = cmds.getAttr(matchCtrl + ".rotate")[0]

                cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2], type = 'double3')
                cmds.setAttr(namespace + ":" + control + ".rotate", rotate[0], rotate[1], rotate[2], type = 'double3')

                cmds.setKeyframe(namespace + ":" + control)

                #delete dupes
                cmds.delete(newControls[0])
                cmds.delete(matchCtrl)


                #match the toe wiggle control to the ball (if applicable)
                fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
                if len(fkControls) > 3:
                    toeWiggle = controls[3]
                    ball = fkControls[3]

                    rotate = cmds.getAttr(namespace + ":" + ball + ".rotate")[0]
                    cmds.setAttr(namespace + ":" + toeWiggle + ".rotate", rotate[0], rotate[1], rotate[2], type = 'double3')


                #match the knee twist
                legJoints = self.getMainLegJoints()
                self.ikKneeMatch(namespace, namespace + ":" + legJoints[1], namespace + ":" + legJoints[0],  namespace + ":ikV1_" + legJoints[1] + "_joint")


                #switch modes
                if not range:
                    cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def ikKneeMatch(self, character, startJoint, middleJoint, endJoint):

        #get leg joints/controls
        legJoints = self.getMainLegJoints()
        self.ikFootCtrl = character + ":ik_" + legJoints[2] + "_anim"

        #create locators
        startPoint = cmds.spaceLocator()[0]
        cmds.parentConstraint(startJoint, startPoint)[0]

        midPoint = cmds.spaceLocator()[0]
        cmds.parentConstraint(middleJoint, midPoint)[0]

        endPoint = cmds.spaceLocator()[0]
        cmds.parentConstraint(endJoint, endPoint)[0]

        #create angle node and hook up attrs to locs
        angleDimNode = cmds.createNode("angleDimension")
        cmds.connectAttr(startPoint + ".translate", angleDimNode + ".startPoint")
        cmds.connectAttr(midPoint + ".translate", angleDimNode + ".middlePoint")
        cmds.connectAttr(endPoint + ".translate", angleDimNode + ".endPoint")


        #find general direction to go in
        origAngle = cmds.getAttr(angleDimNode + ".angle")

        direction = 1
        if origAngle != 0:
            cmds.setAttr(self.ikFootCtrl + ".knee_twist", 1)
            newAngle = cmds.getAttr(angleDimNode + ".angle")

            if newAngle > origAngle:
                direction = -1


        #reset knee twist
        cmds.setAttr(self.ikFootCtrl + ".knee_twist", 0)


        #HIDE EVERYTHING
        panels = cmds.getPanel( type = "modelPanel")
        for panel in panels:
            editor = cmds.modelPanel(panel, q = True, modelEditor = True)
            cmds.modelEditor(editor, edit = True, allObjects = 0)


        #find best angle
        for x in range(3000):

            angle = cmds.getAttr(angleDimNode + ".angle")

            if angle > 0.5:
                currentVal = cmds.getAttr(self.ikFootCtrl + ".knee_twist")
                cmds.setAttr(self.ikFootCtrl + ".knee_twist", currentVal + direction)
                cmds.refresh()

            else:
                cmds.setKeyframe(self.ikFootCtrl + ".knee_twist")
                cmds.delete([startPoint, midPoint, endPoint])
                cmds.delete(cmds.listRelatives(angleDimNode, parent = True)[0])
                break

        #SHOW EVERYTHING
        panels = cmds.getPanel( type = "modelPanel")
        for panel in panels:
            editor = cmds.modelPanel(panel, q = True, modelEditor = True)
            cmds.modelEditor(editor, edit = True, allObjects = 1)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectRigControls(self, mode):


        #get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        #list any attributes on the network node that contain "controls"
        controls = cmds.listAttr(networkNode, st = "*Controls")
        fkControls = ["fkControls", "thighTwistControls", "calfTwistControls"]
        ikControls = ["ikV1Controls"]

        #get that data on that attr
        for control in controls:

            #select all controls
            if mode == "all":
                data = json.loads(cmds.getAttr(networkNode + "." + control))
                if data != None:
                    for each in data:
                        cmds.select(namespace + ":" + each, add = True)

            #select fk controls
            if mode == "fk":
                if control in fkControls:
                    data = json.loads(cmds.getAttr(networkNode + "." + control))
                    if data != None:
                        for each in data:
                            if each.find("fk") != -1:
                                cmds.select(namespace + ":" + each, add = True)

            #select ik controls
            if mode == "ik":
                if control in ikControls:
                    data = json.loads(cmds.getAttr(networkNode + "." + control))
                    if data != None:
                        for each in data:
                            if each.find("fk") == -1:
                                cmds.select(namespace + ":" + each, add = True)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    @classmethod
    def getinstances(cls):
        for ref in cls._instances:
            obj = ref()


