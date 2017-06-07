import json
import os
import time
import weakref
from functools import partial

import maya.cmds as cmds

import System.interfaceUtils as interfaceUtils
import System.riggingUtils as riggingUtils
import System.utils as utils
from System.ART_RigModule import ART_RigModule
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# file attributes
icon = "Modules/armStandard.png"
hoverIcon = "Modules/hover_armStandard.png"
search = "biped:arm"
className = "ART_Arm_Standard"
jointMover = "Core/JointMover/ART_Arm_Standard.ma"
baseName = "arm"
rigs = ["FK::IK"]
fbxImport = ["None", "FK", "IK", "Both"]
matchData = [True, ["Match FK to IK", "Match IK to FK"]]
controlTypes = [["fkControls", "FK"], ["ikControls", "IK"], ["upArmTwistControls", "FK"], ["loArmTwistControls", "FK"],
                ["fkFingerControls", "FK"], ["ikFingerControls", "IK"], ["clavControls", "FK"], ["clavControls", "IK"]]
sorting = 0

# begin class
class ART_Arm_Standard(ART_RigModule):
    _instances = set()

    def __init__(self, rigUiInst, moduleUserName):

        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}

        self.__class__._instances.add(weakref.ref(self))

        ART_RigModule.__init__(self, "ART_Arm_Standard_Module", "ART_Arm_Standard", moduleUserName)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addAttributes(self):
        # call the base class method first to hook up our connections to the master module
        ART_RigModule.addAttributes(self)

        # add custom attributes for this specific module
        bones = "clavicle::upperarm::lowerarm::hand::thumb_metacarpal::thumb_proximal::thumb_distal::index_proximal::"
        bones += "index_middle::index_distal::middle_proximal::middle_middle::middle_distal::ring_proximal::"
        bones += "ring_middle::ring_distal::pinky_proximal::pinky_middle::pinky_distal::"

        cmds.addAttr(self.networkNode, sn="Created_Bones", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".Created_Bones", bones, type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="baseName", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".baseName", baseName, type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="canAim", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".canAim", True, lock=True)

        cmds.addAttr(self.networkNode, sn="aimMode", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".aimMode", False, lock=True)

        # joint mover settings
        cmds.addAttr(self.networkNode, sn="armTwists", keyable=False)
        cmds.setAttr(self.networkNode + ".armTwists", 0, lock=True)

        cmds.addAttr(self.networkNode, sn="forearmTwists", keyable=False)
        cmds.setAttr(self.networkNode + ".forearmTwists", 0, lock=True)

        cmds.addAttr(self.networkNode, sn="thumbJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".thumbJoints", 2, lock=True)

        cmds.addAttr(self.networkNode, sn="thumbMeta", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".thumbMeta", True, lock=True)

        cmds.addAttr(self.networkNode, sn="indexJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".indexJoints", 3, lock=True)

        cmds.addAttr(self.networkNode, sn="indexMeta", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".indexMeta", False, lock=True)

        cmds.addAttr(self.networkNode, sn="middleJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".middleJoints", 3, lock=True)

        cmds.addAttr(self.networkNode, sn="middleMeta", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".middleMeta", False, lock=True)

        cmds.addAttr(self.networkNode, sn="ringJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".ringJoints", 3, lock=True)

        cmds.addAttr(self.networkNode, sn="ringMeta", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".ringMeta", False, lock=True)

        cmds.addAttr(self.networkNode, sn="pinkyJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".pinkyJoints", 3, lock=True)

        cmds.addAttr(self.networkNode, sn="pinkyMeta", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".pinkyMeta", False, lock=True)

        cmds.addAttr(self.networkNode, sn="side", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".side", "Left", type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="includeClavicle", keyable=False, at="bool")
        cmds.setAttr(self.networkNode + ".includeClavicle", True, lock=True)

        # rig creation settings
        cmds.addAttr(self.networkNode, sn="buildFK", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".buildFK", True, lock=True)

        cmds.addAttr(self.networkNode, sn="buildIK_V1", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".buildIK_V1", True, lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):
        networkNode = self.returnNetworkNode

        # groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 500, True)

        font = QtGui.QFont()
        font.setPointSize(8)

        headerFont = QtGui.QFont()
        headerFont.setPointSize(8)
        headerFont.setBold(True)

        # create a VBoxLayout to add to our Groupbox and then add a QFrame for our signal/slot
        self.layout = QtWidgets.QVBoxLayout(self.groupBox)
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.layout.addWidget(self.frame)

        self.frame.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.frame.setMinimumSize(QtCore.QSize(320, 465))
        self.frame.setMaximumSize(QtCore.QSize(320, 465))

        # add layout for custom settings
        self.customSettingsLayout = QtWidgets.QVBoxLayout(self.frame)

        # mirror module
        self.mirrorModLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.mirrorModLayout)
        self.mirrorModuleLabel = QtWidgets.QLabel("Mirror Module: ")
        self.mirrorModuleLabel.setFont(font)
        self.mirrorModLayout.addWidget(self.mirrorModuleLabel)

        mirror = cmds.getAttr(networkNode + ".mirrorModule")
        if mirror == "":
            mirror = "None"
        self.mirrorMod = QtWidgets.QLabel(mirror)
        self.mirrorMod.setFont(font)
        self.mirrorMod.setAlignment(QtCore.Qt.AlignHCenter)
        self.mirrorModLayout.addWidget(self.mirrorMod)

        # current parent
        self.currentParentMod = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.currentParentMod)
        self.currentParentLabel = QtWidgets.QLabel("Current Parent: ")
        self.currentParentLabel.setFont(font)
        self.currentParentMod.addWidget(self.currentParentLabel)

        parent = cmds.getAttr(networkNode + ".parentModuleBone")
        self.currentParent = QtWidgets.QLabel(parent)
        self.currentParent.setFont(font)
        self.currentParent.setAlignment(QtCore.Qt.AlignHCenter)
        self.currentParentMod.addWidget(self.currentParent)

        # button layout for name/parent
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

        # add side settings
        self.sideLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.sideLayout)
        self.sideLabel = QtWidgets.QLabel("Side:    ")
        self.sideLabel.setFont(font)
        self.leftSideBtn = QtWidgets.QRadioButton("Left Side")
        self.rightSideBtn = QtWidgets.QRadioButton("Right Side")
        self.sideLayout.addWidget(self.sideLabel)
        self.sideLayout.addWidget(self.leftSideBtn)
        self.sideLayout.addWidget(self.rightSideBtn)

        # get current side
        if cmds.getAttr(networkNode + ".side") == "Left":
            self.leftSideBtn.setChecked(True)
        if cmds.getAttr(networkNode + ".side") == "Right":
            self.rightSideBtn.setChecked(True)

        self.leftSideBtn.clicked.connect(self.changeSide)
        self.rightSideBtn.clicked.connect(self.changeSide)

        # coplanar mode and bake offsets layout
        self.armToolsLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.armToolsLayout)

        # Coplanar mode
        self.coplanarBtn = QtWidgets.QPushButton("Coplanar Mode")
        self.coplanarBtn.setFont(headerFont)
        self.armToolsLayout.addWidget(self.coplanarBtn)
        self.coplanarBtn.setCheckable(True)
        self.coplanarBtn.clicked.connect(self.coplanarMode)
        self.coplanarBtn.setToolTip("[EXPERIMENTAL] Forces arm joints to always be planar for best IK setup")

        # Bake OFfsets
        self.bakeOffsetsBtn = QtWidgets.QPushButton("Bake Offsets")
        self.bakeOffsetsBtn.setFont(headerFont)
        self.armToolsLayout.addWidget(self.bakeOffsetsBtn)
        self.bakeOffsetsBtn.clicked.connect(self.bakeOffsets)
        self.bakeOffsetsBtn.setToolTip("Bake the offset mover values up to the global movers to get them in sync")

        self.coplanarBtn.setObjectName("blueButton")
        self.bakeOffsetsBtn.setObjectName("blueButton")

        # Clavicle Settings
        spacerItem = QtWidgets.QSpacerItem(200, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.customSettingsLayout.addItem(spacerItem)

        self.clavicleCB = QtWidgets.QCheckBox("Include Clavicle?")
        self.clavicleCB.setChecked(True)
        self.customSettingsLayout.addWidget(self.clavicleCB)

        spacerItem = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.customSettingsLayout.addItem(spacerItem)

        # Twist Bone Settings
        self.twistSettingsLabel = QtWidgets.QLabel("Twist Bone Settings: ")
        self.twistSettingsLabel.setFont(headerFont)
        self.twistSettingsLabel.setStyleSheet("color: rgb(25, 175, 255);")
        self.customSettingsLayout.addWidget(self.twistSettingsLabel)

        self.separatorA = QtWidgets.QFrame()
        self.separatorA.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorA.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.customSettingsLayout.addWidget(self.separatorA)

        self.twistBonesLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.twistBonesLayout)

        self.twistForm = QtWidgets.QFormLayout()
        self.upperarmTwistLabel = QtWidgets.QLabel("UpperArm: ")
        self.upperarmTwistLabel.setFont(font)
        self.twistForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.upperarmTwistLabel)
        self.upperarmTwistNum = QtWidgets.QSpinBox()
        self.upperarmTwistNum.setMaximum(3)
        self.twistForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.upperarmTwistNum)
        self.twistBonesLayout.addLayout(self.twistForm)

        self.lowerArmTwistForm = QtWidgets.QFormLayout()
        self.lowerarmTwistLabel = QtWidgets.QLabel("LowerArm: ")
        self.lowerarmTwistLabel.setFont(font)
        self.lowerArmTwistForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lowerarmTwistLabel)
        self.lowerarmTwistNum = QtWidgets.QSpinBox()
        self.lowerarmTwistNum.setMaximum(3)
        self.lowerArmTwistForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lowerarmTwistNum)
        self.twistBonesLayout.addLayout(self.lowerArmTwistForm)

        # Hand Settings Section
        self.handSettingsLabel = QtWidgets.QLabel("Hand Settings: ")
        self.handSettingsLabel.setFont(headerFont)
        self.handSettingsLabel.setStyleSheet("color: rgb(25, 175, 255);")
        self.customSettingsLayout.addWidget(self.handSettingsLabel)

        self.separatorB = QtWidgets.QFrame()
        self.separatorB.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorB.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.customSettingsLayout.addWidget(self.separatorB)

        # Thumb Settings: add VBoxLayout
        self.fingerVBoxLayout = QtWidgets.QVBoxLayout()
        self.customSettingsLayout.addLayout(self.fingerVBoxLayout)

        # THUMB
        self.thumbLayout = QtWidgets.QHBoxLayout()

        self.thumbLabel = QtWidgets.QLabel("Thumb Joints: ")
        self.thumbLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.thumbLabel.setMinimumSize(QtCore.QSize(100, 20))
        self.thumbLabel.setMaximumSize(QtCore.QSize(100, 20))
        self.thumbLayout.addWidget((self.thumbLabel))

        self.thumbNum = QtWidgets.QSpinBox()
        self.thumbNum.setMaximum(2)
        self.thumbNum.setMinimumSize(QtCore.QSize(50, 20))
        self.thumbNum.setMaximumSize(QtCore.QSize(50, 20))
        self.thumbNum.setValue(2)
        self.thumbNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.thumbLayout.addWidget(self.thumbNum)

        self.thumbMeta = QtWidgets.QCheckBox("Include Metacarpal")
        self.thumbMeta.setChecked(True)
        self.thumbMeta.setMinimumSize(QtCore.QSize(150, 20))
        self.thumbMeta.setMaximumSize(QtCore.QSize(150, 20))
        self.thumbLayout.addWidget(self.thumbMeta)
        self.fingerVBoxLayout.addLayout(self.thumbLayout)

        # INDEX
        self.indexLayout = QtWidgets.QHBoxLayout()

        self.indexLabel = QtWidgets.QLabel("Index Joints: ")
        self.indexLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.indexLabel.setMinimumSize(QtCore.QSize(100, 20))
        self.indexLabel.setMaximumSize(QtCore.QSize(100, 20))
        self.indexLayout.addWidget((self.indexLabel))

        self.indexNum = QtWidgets.QSpinBox()
        self.indexNum.setMaximum(3)
        self.indexNum.setValue(3)
        self.indexNum.setMinimumSize(QtCore.QSize(50, 20))
        self.indexNum.setMaximumSize(QtCore.QSize(50, 20))
        self.indexNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.indexLayout.addWidget(self.indexNum)

        self.indexMeta = QtWidgets.QCheckBox("Include Metacarpal")
        self.indexMeta.setMinimumSize(QtCore.QSize(150, 20))
        self.indexMeta.setMaximumSize(QtCore.QSize(150, 20))
        self.indexLayout.addWidget(self.indexMeta)
        self.fingerVBoxLayout.addLayout(self.indexLayout)

        # MIDDLE
        self.middleLayout = QtWidgets.QHBoxLayout()

        self.middleLabel = QtWidgets.QLabel("Middle Joints: ")
        self.middleLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.middleLabel.setMinimumSize(QtCore.QSize(100, 20))
        self.middleLabel.setMaximumSize(QtCore.QSize(100, 20))
        self.middleLayout.addWidget((self.middleLabel))

        self.middleNum = QtWidgets.QSpinBox()
        self.middleNum.setMaximum(3)
        self.middleNum.setValue(3)
        self.middleNum.setMinimumSize(QtCore.QSize(50, 20))
        self.middleNum.setMaximumSize(QtCore.QSize(50, 20))
        self.middleNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.middleLayout.addWidget(self.middleNum)

        self.middleMeta = QtWidgets.QCheckBox("Include Metacarpal")
        self.middleMeta.setMinimumSize(QtCore.QSize(150, 20))
        self.middleMeta.setMaximumSize(QtCore.QSize(150, 20))
        self.middleLayout.addWidget(self.middleMeta)
        self.fingerVBoxLayout.addLayout(self.middleLayout)

        # RING
        self.ringLayout = QtWidgets.QHBoxLayout()

        self.ringLabel = QtWidgets.QLabel("Ring Joints: ")
        self.ringLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.ringLabel.setMinimumSize(QtCore.QSize(100, 20))
        self.ringLabel.setMaximumSize(QtCore.QSize(100, 20))
        self.ringLayout.addWidget((self.ringLabel))

        self.ringNum = QtWidgets.QSpinBox()
        self.ringNum.setMaximum(3)
        self.ringNum.setValue(3)
        self.ringNum.setMinimumSize(QtCore.QSize(50, 20))
        self.ringNum.setMaximumSize(QtCore.QSize(50, 20))
        self.ringNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.ringLayout.addWidget(self.ringNum)

        self.ringMeta = QtWidgets.QCheckBox("Include Metacarpal")
        self.ringMeta.setMinimumSize(QtCore.QSize(150, 20))
        self.ringMeta.setMaximumSize(QtCore.QSize(150, 20))
        self.ringLayout.addWidget(self.ringMeta)
        self.fingerVBoxLayout.addLayout(self.ringLayout)

        # PINKY
        self.pinkyLayout = QtWidgets.QHBoxLayout()

        self.pinkyLabel = QtWidgets.QLabel("Pinky Joints: ")
        self.pinkyLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.pinkyLabel.setMinimumSize(QtCore.QSize(100, 20))
        self.pinkyLabel.setMaximumSize(QtCore.QSize(100, 20))
        self.pinkyLayout.addWidget((self.pinkyLabel))

        self.pinkyNum = QtWidgets.QSpinBox()
        self.pinkyNum.setMaximum(3)
        self.pinkyNum.setValue(3)
        self.pinkyNum.setMinimumSize(QtCore.QSize(50, 20))
        self.pinkyNum.setMaximumSize(QtCore.QSize(50, 20))
        self.pinkyNum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.pinkyLayout.addWidget(self.pinkyNum)

        self.pinkyMeta = QtWidgets.QCheckBox("Include Metacarpal")
        self.pinkyMeta.setMinimumSize(QtCore.QSize(150, 20))
        self.pinkyMeta.setMaximumSize(QtCore.QSize(150, 20))
        self.pinkyLayout.addWidget(self.pinkyMeta)
        self.fingerVBoxLayout.addLayout(self.pinkyLayout)

        # rebuild button
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.customSettingsLayout.addItem(spacerItem)

        self.applyButton = QtWidgets.QPushButton("Apply Changes")
        self.customSettingsLayout.addWidget(self.applyButton)
        self.applyButton.setFont(headerFont)
        self.applyButton.setMinimumSize(QtCore.QSize(300, 40))
        self.applyButton.setMaximumSize(QtCore.QSize(300, 40))
        self.applyButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.applyButton.setEnabled(False)

        # button signal/slots
        self.changeNameBtn.clicked.connect(partial(self.changeModuleName, baseName, self, self.rigUiInst))
        self.changeParentBtn.clicked.connect(partial(self.changeModuleParent, self, self.rigUiInst))
        self.mirrorModuleBtn.clicked.connect(partial(self.setMirrorModule, self, self.rigUiInst))
        self.applyButton.clicked.connect(partial(self.applyModuleChanges, self))

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.frame.setVisible)
        self.groupBox.setChecked(False)

        # spinBox & checkbox signal/slots
        self.upperarmTwistNum.valueChanged.connect(self.toggleButtonState)
        self.lowerarmTwistNum.valueChanged.connect(self.toggleButtonState)
        self.thumbNum.valueChanged.connect(self.toggleButtonState)
        self.indexNum.valueChanged.connect(self.toggleButtonState)
        self.middleNum.valueChanged.connect(self.toggleButtonState)
        self.ringNum.valueChanged.connect(self.toggleButtonState)
        self.pinkyNum.valueChanged.connect(self.toggleButtonState)

        self.pinkyMeta.stateChanged.connect(self.toggleButtonState)
        self.ringMeta.stateChanged.connect(self.toggleButtonState)
        self.middleMeta.stateChanged.connect(self.toggleButtonState)
        self.indexMeta.stateChanged.connect(self.toggleButtonState)
        self.thumbMeta.stateChanged.connect(self.toggleButtonState)

        self.clavicleCB.stateChanged.connect(self.toggleButtonState)

        # add custom skeletonUI settings  name, parent, rig types to install, mirror module, thigh twist, calf twists,
        # ball joint, toes,
        # add to the rig cretor UI's module settings layout VBoxLayout
        self.rigUiInst.moduleSettingsLayout.addWidget(self.groupBox)

        # Populate the settings UI based on the network node attributes
        self.updateSettingsUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pickerUI(self, center, animUI, networkNode, namespace):

        self.namespace = namespace

        # create qBrushes
        yellowBrush = QtCore.Qt.yellow
        blueBrush = QtGui.QColor(100, 220, 255)
        purpleBrush = QtGui.QColor(111, 48, 161)
        greenBrush = QtGui.QColor(0, 255, 30)
        clearBrush = QtGui.QBrush(QtCore.Qt.black)
        clearBrush.setStyle(QtCore.Qt.NoBrush)
        side = cmds.getAttr(networkNode + ".side")

        # create the picker border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode

        borderItem = interfaceUtils.pickerBorderItem(center.x() - 80, center.y() - 130, 110, 260, clearBrush,
                                                     moduleNode)

        # get controls
        ikControls = json.loads(cmds.getAttr(networkNode + ".ikControls"))
        fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
        upArmTwistControls = json.loads(cmds.getAttr(networkNode + ".upArmTwistControls"))
        loArmTwistControls = json.loads(cmds.getAttr(networkNode + ".loArmTwistControls"))
        clavControls = []

        if cmds.objExists(networkNode + ".clavControls"):
            clavControls = json.loads(cmds.getAttr(networkNode + ".clavControls"))

        buttonData = []
        controls = []

        # =======================================================================
        # ik buttons
        # =======================================================================
        ikHandButton = interfaceUtils.pickerButton(20, 20, [50, 190], namespace + ikControls[0], yellowBrush,
                                                   borderItem)
        buttonData.append([ikHandButton, namespace + ikControls[0], yellowBrush])
        controls.append(namespace + ikControls[0])

        ikElbowButton = interfaceUtils.pickerButton(20, 20, [50, 100], namespace + ikControls[1], yellowBrush,
                                                    borderItem)
        buttonData.append([ikElbowButton, namespace + ikControls[1], yellowBrush])
        controls.append(namespace + ikControls[0])

        if len(clavControls) > 0:
            ikClavButton = interfaceUtils.pickerButton(20, 20, [50, 10], namespace + clavControls[1], yellowBrush,
                                                       borderItem)
            buttonData.append([ikClavButton, namespace + clavControls[1], yellowBrush])
            controls.append(namespace + clavControls[1])

        # =======================================================================
        # fk buttons
        # =======================================================================
        fkArmBtn = interfaceUtils.pickerButton(20, 60, [50, 35], namespace + fkControls[2], blueBrush, borderItem)
        buttonData.append([fkArmBtn, namespace + fkControls[2], blueBrush])
        controls.append(namespace + fkControls[2])

        fkElbowBtn = interfaceUtils.pickerButton(20, 60, [50, 125], namespace + fkControls[1], blueBrush, borderItem)
        buttonData.append([fkElbowBtn, namespace + fkControls[1], blueBrush])
        controls.append(namespace + fkControls[1])

        fkHandBtn = interfaceUtils.pickerButton(40, 40, [40, 215], namespace + fkControls[0], blueBrush, borderItem)
        buttonData.append([fkHandBtn, namespace + fkControls[0], blueBrush])
        controls.append(namespace + fkControls[0])

        if len(clavControls) > 0:
            fkClavButton = interfaceUtils.pickerButton(20, 20, [25, 10], namespace + clavControls[0], blueBrush,
                                                       borderItem)
            buttonData.append([fkClavButton, namespace + clavControls[0], blueBrush])
            controls.append(namespace + clavControls[0])

        # =======================================================================
        # twist bones
        # =======================================================================
        if upArmTwistControls != None:
            if len(upArmTwistControls) > 0:
                y = 35
                for i in range(len(upArmTwistControls)):
                    button = interfaceUtils.pickerButton(15, 15, [75, y], namespace + upArmTwistControls[i],
                                                         purpleBrush, borderItem)
                    buttonData.append([button, namespace + upArmTwistControls[i], purpleBrush])
                    controls.append(namespace + upArmTwistControls[i])
                    y = y + 22

        if loArmTwistControls != None:
            if len(loArmTwistControls) > 0:
                y = 170
                for i in range(len(loArmTwistControls)):
                    button = interfaceUtils.pickerButton(15, 15, [75, y], namespace + loArmTwistControls[i],
                                                         purpleBrush, borderItem)
                    buttonData.append([button, namespace + loArmTwistControls[i], purpleBrush])
                    controls.append(namespace + loArmTwistControls[i])
                    y = y - 22

        # =======================================================================
        # settings button
        # =======================================================================
        settingsBtn = interfaceUtils.pickerButton(20, 20, [85, 235], namespace + self.name + "_settings", greenBrush,
                                                  borderItem)
        buttonData.append([settingsBtn, namespace + ":" + self.name + "_settings", greenBrush])
        controls.append(namespace + ":" + self.name + "_settings")
        interfaceUtils.addTextToButton("S", settingsBtn)

        # =======================================================================
        # #FINGERS !!!! THIS IS A SUB-PICKER !!!!
        # =======================================================================

        # if there are fingers, create a finger picker
        fingerControls = json.loads(cmds.getAttr(networkNode + ".fkFingerControls"))
        ikFingerControls = json.loads(cmds.getAttr(networkNode + ".ikFingerControls"))

        if len(fingerControls) > 0:

            name = cmds.getAttr(networkNode + ".moduleName")
            fingerBorder = interfaceUtils.pickerBorderItem(center.x() + 35, center.y() - 75, 100, 100, clearBrush,
                                                           moduleNode, name + "_fingers")
            fingerBorder.setParentItem(borderItem)
            interfaceUtils.addTextToButton(side[0] + "_Fingers", fingerBorder, False, False, True)

            # create selection set lists
            thumbFingers = []
            indexFingers = []
            middleFingers = []
            ringFingers = []
            pinkyFingers = []

            metaCarpals = []
            distalKnuckles = []
            middleKnuckles = []
            proximalKnuckles = []
            fkFingerControls = []

            fingerButtonData = []
            # =======================================================================
            # THUMB
            # =======================================================================
            for finger in fingerControls:
                if finger.find("thumb_metacarpal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20, 40], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    thumbFingers.append(namespace + finger)

                if finger.find("thumb_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20, 55], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    thumbFingers.append(namespace + finger)

                if finger.find("thumb_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20, 75], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    thumbFingers.append(namespace + finger)

                # =======================================================================
                # INDEX
                # =======================================================================
                if finger.find("index_metacarpal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35, 25], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    indexFingers.append(namespace + finger)
                    metaCarpals.append(namespace + finger)

                if finger.find("index_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35, 40], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    indexFingers.append(namespace + finger)
                    proximalKnuckles.append(namespace + finger)

                if finger.find("index_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35, 55], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    indexFingers.append(namespace + finger)
                    middleKnuckles.append(namespace + finger)

                if finger.find("index_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35, 75], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    indexFingers.append(namespace + finger)
                    distalKnuckles.append(namespace + finger)

                # =======================================================================
                # MIDDLE
                # =======================================================================
                if finger.find("middle_metacarpal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50, 25], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    middleFingers.append(namespace + finger)
                    metaCarpals.append(namespace + finger)

                if finger.find("middle_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50, 40], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    middleFingers.append(namespace + finger)
                    proximalKnuckles.append(namespace + finger)

                if finger.find("middle_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50, 55], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    middleFingers.append(namespace + finger)
                    middleKnuckles.append(namespace + finger)

                if finger.find("middle_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50, 75], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    middleFingers.append(namespace + finger)
                    distalKnuckles.append(namespace + finger)

                # =======================================================================
                # RING
                # =======================================================================
                if finger.find("ring_metacarpal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65, 25], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    ringFingers.append(namespace + finger)
                    metaCarpals.append(namespace + finger)

                if finger.find("ring_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65, 40], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    ringFingers.append(namespace + finger)
                    proximalKnuckles.append(namespace + finger)

                if finger.find("ring_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65, 55], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    ringFingers.append(namespace + finger)
                    middleKnuckles.append(namespace + finger)

                if finger.find("ring_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65, 75], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    ringFingers.append(namespace + finger)
                    distalKnuckles.append(namespace + finger)

                # =======================================================================
                # PINKY
                # =======================================================================
                if finger.find("pinky_metacarpal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80, 25], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    pinkyFingers.append(namespace + finger)
                    metaCarpals.append(namespace + finger)

                if finger.find("pinky_proximal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80, 40], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    pinkyFingers.append(namespace + finger)
                    proximalKnuckles.append(namespace + finger)

                if finger.find("pinky_middle") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80, 55], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    pinkyFingers.append(namespace + finger)
                    middleKnuckles.append(namespace + finger)

                if finger.find("pinky_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80, 75], namespace + finger, blueBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, blueBrush])
                    fingerButtonData.append([button, namespace + finger, blueBrush])
                    controls.append(namespace + finger)
                    fkFingerControls.append(namespace + finger)
                    pinkyFingers.append(namespace + finger)
                    distalKnuckles.append(namespace + finger)

            # =======================================================================
            # IK FINGERS
            # =======================================================================
            for finger in ikFingerControls:

                if finger.find("index_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [35, 88], namespace + finger, yellowBrush,
                                                         fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("index_pv") != -1:
                    button = interfaceUtils.pickerButton(10, 6, [35, 67], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("middle_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [50, 88], namespace + finger, yellowBrush,
                                                         fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("middle_pv") != -1:
                    button = interfaceUtils.pickerButton(10, 6, [50, 67], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("ring_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [65, 88], namespace + finger, yellowBrush,
                                                         fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("ring_pv") != -1:
                    button = interfaceUtils.pickerButton(10, 6, [65, 67], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("pinky_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [80, 88], namespace + finger, yellowBrush,
                                                         fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("pinky_pv") != -1:
                    button = interfaceUtils.pickerButton(10, 6, [80, 67], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("thumb_distal") != -1:
                    button = interfaceUtils.pickerButton(10, 10, [20, 88], namespace + finger, yellowBrush,
                                                         fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("thumb_pv") != -1:
                    button = interfaceUtils.pickerButton(10, 6, [20, 67], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

                if finger.find("hand_global") != -1:
                    button = interfaceUtils.pickerButton(5, 98, [94, 2], namespace + finger, yellowBrush, fingerBorder)
                    buttonData.append([button, namespace + finger, yellowBrush])
                    fingerButtonData.append([button, namespace + finger, yellowBrush])
                    controls.append(namespace + finger)
                    button.setToolTip(finger)

            # =======================================================================
            # FINGER MASS SELECT BUTTONS
            # =======================================================================
            metaCarpalAll_btn = interfaceUtils.pickerButtonAll(10, 10, [5, 25], metaCarpals, greenBrush, fingerBorder)
            metaCarpalAll_btn.setToolTip("select all metacarpal controls")

            proxiKnuckle_btn = interfaceUtils.pickerButtonAll(10, 10, [5, 40], proximalKnuckles, greenBrush,
                                                              fingerBorder)
            proxiKnuckle_btn.setToolTip("select all proximal knuckles")
            midKnuckle_btn = interfaceUtils.pickerButtonAll(10, 10, [5, 55], middleKnuckles, greenBrush, fingerBorder)
            midKnuckle_btn.setToolTip("select all middle knuckles")
            distKnuckle_btn = interfaceUtils.pickerButtonAll(10, 10, [5, 75], distalKnuckles, greenBrush, fingerBorder)
            distKnuckle_btn.setToolTip("select all distal knuckles")

            thumbs_btn = interfaceUtils.pickerButtonAll(10, 10, [20, 5], thumbFingers, greenBrush, fingerBorder)
            thumbs_btn.setToolTip("select all thumb controls")
            indexes_btn = interfaceUtils.pickerButtonAll(10, 10, [35, 5], indexFingers, greenBrush, fingerBorder)
            indexes_btn.setToolTip("select all index finger controls")
            middles_btn = interfaceUtils.pickerButtonAll(10, 10, [50, 5], middleFingers, greenBrush, fingerBorder)
            middles_btn.setToolTip("select all middle finger controls")
            rings_btn = interfaceUtils.pickerButtonAll(10, 10, [65, 5], ringFingers, greenBrush, fingerBorder)
            rings_btn.setToolTip("select all ring finger controls")
            pinkys_btn = interfaceUtils.pickerButtonAll(10, 10, [80, 5], pinkyFingers, greenBrush, fingerBorder)
            pinkys_btn.setToolTip("select all pinky finger controls")

            allFinger_btn = interfaceUtils.pickerButtonAll(12, 12, [5, 8], fkFingerControls, greenBrush, fingerBorder)
            allFinger_btn.setToolTip("select all fk finger controls")

        # =======================================================================
        # go through button data, adding menu items
        # =======================================================================
        for each in buttonData:
            if each not in fingerButtonData:
                button = each[0]

                fkIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/jointFilter.png"))))
                ikIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/ikMode.png"))))
                zeroIcon1 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroAll.png"))))
                zeroIcon2 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroSel.png"))))
                selectIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/select.png"))))

                switchAction = QtWidgets.QAction('Match when Switching', button.menu)
                switchAction.setCheckable(True)
                switchAction.setChecked(True)

                button.menu.addAction(selectIcon, "Select All Arm Controls", partial(self.selectRigControls, "all"))
                button.menu.addAction(selectIcon, "Select FK Arm Controls", partial(self.selectRigControls, "fk"))
                button.menu.addAction(selectIcon, "Select IK Arm Controls", partial(self.selectRigControls, "ik"))
                button.menu.addSeparator()

                if len(clavControls) > 0:
                    if each[1] == namespace + clavControls[0] or each[1] == namespace + clavControls[1]:
                        button.menu.addAction(fkIcon, "(Clav) FK Mode",
                                              partial(self.switchClavMode, "FK", switchAction))
                        button.menu.addAction(ikIcon, "(Clav) IK Mode",
                                              partial(self.switchClavMode, "IK", switchAction))

                    else:
                        button.menu.addAction(fkIcon, "(Arm) FK Mode", partial(self.switchMode, "FK", switchAction))
                        button.menu.addAction(ikIcon, "(Arm) IK Mode", partial(self.switchMode, "IK", switchAction))

                else:
                    button.menu.addAction(fkIcon, "(Arm) FK Mode", partial(self.switchMode, "FK", switchAction))
                    button.menu.addAction(ikIcon, "(Arm) IK Mode", partial(self.switchMode, "IK", switchAction))

                button.menu.addAction(switchAction)

                button.menu.addSeparator()

                button.menu.addAction(zeroIcon1, "Zero Out Attrs (All)", partial(self.resetRigControls, True))
                button.menu.addAction(zeroIcon2, "Zero Out Attrs (Sel)", partial(self.resetRigControls, False))

        for each in fingerButtonData:
            button = each[0]

            fkIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/jointFilter.png"))))
            ikIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/ikMode.png"))))
            zeroIcon1 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroAll.png"))))
            zeroIcon2 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroSel.png"))))

            button.menu.addAction(fkIcon, "FK Mode (Finger)", partial(self.switchFingerMode, "FK", each[1]))
            button.menu.addAction(ikIcon, "IK Mode (Finger)", partial(self.switchFingerMode, "IK", each[1]))

            button.menu.addSeparator()
            button.menu.addAction(fkIcon, "FK Mode (All Fingers)", partial(self.switchFingerMode, "FK", "All"))
            button.menu.addAction(ikIcon, "IK Mode (All Fingers)", partial(self.switchFingerMode, "IK", "All"))

            button.menu.addSeparator()
            button.menu.addAction(zeroIcon1, "Zero Out Attrs (All)", partial(self.resetRigControls, True))
            button.menu.addAction(zeroIcon2, "Zero Out Attrs (Sel)", partial(self.resetRigControls, False))

        # =======================================================================
        # #Create scriptJob for selection. Set scriptJob number to borderItem.data(5)
        # =======================================================================
        scriptJob = cmds.scriptJob(event=["SelectionChanged", partial(self.selectionScriptJob_animUI, buttonData)],
                                   kws=True)
        borderItem.setData(5, scriptJob)
        animUI.selectionScriptJobs.append(scriptJob)

        # return data and set to mirror if side is right
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
    def addJointMoverToOutliner(self):

        index = self.rigUiInst.treeWidget.topLevelItemCount()
        self.outlinerWidgets = {}

        # Add the module to the tree widget in the outliner tab of the rig creator UI
        self.outlinerWidgets[self.name + "_treeModule"] = QtWidgets.QTreeWidgetItem(self.rigUiInst.treeWidget)
        self.rigUiInst.treeWidget.topLevelItem(index).setText(0, self.name)
        foreground = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.outlinerWidgets[self.name + "_treeModule"].setForeground(0, foreground)

        # add the clavicle
        self.outlinerWidgets[self.name + "_clavicle"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_clavicle"].setText(0, self.name + "_clavicle")
        self.createGlobalMoverButton(self.name + "_clavicle", self.outlinerWidgets[self.name + "_clavicle"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_clavicle", self.outlinerWidgets[self.name + "_clavicle"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_clavicle", self.outlinerWidgets[self.name + "_clavicle"],
                                   self.rigUiInst)

        # add the upperarm
        self.outlinerWidgets[self.name + "_upperarm"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_upperarm"].setText(0, self.name + "_upperarm")
        self.createGlobalMoverButton(self.name + "_upperarm", self.outlinerWidgets[self.name + "_upperarm"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_upperarm", self.outlinerWidgets[self.name + "_upperarm"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_upperarm", self.outlinerWidgets[self.name + "_upperarm"],
                                   self.rigUiInst)

        # add the upperarm twists
        self.outlinerWidgets[self.name + "_upperarm_twist_01"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_upperarm"])
        self.outlinerWidgets[self.name + "_upperarm_twist_01"].setText(0, self.name + "_upperarm_twist_01")
        self.createOffsetMoverButton(self.name + "_upperarm_twist_01",
                                     self.outlinerWidgets[self.name + "_upperarm_twist_01"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_upperarm_twist_01"].setHidden(True)

        self.outlinerWidgets[self.name + "_upperarm_twist_02"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_upperarm"])
        self.outlinerWidgets[self.name + "_upperarm_twist_02"].setText(0, self.name + "_upperarm_twist_02")
        self.createOffsetMoverButton(self.name + "_upperarm_twist_02",
                                     self.outlinerWidgets[self.name + "_upperarm_twist_02"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_upperarm_twist_02"].setHidden(True)

        self.outlinerWidgets[self.name + "_upperarm_twist_03"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_upperarm"])
        self.outlinerWidgets[self.name + "_upperarm_twist_03"].setText(0, self.name + "_upperarm_twist_03")
        self.createOffsetMoverButton(self.name + "_upperarm_twist_03",
                                     self.outlinerWidgets[self.name + "_upperarm_twist_03"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_upperarm_twist_03"].setHidden(True)

        # add the lowerarm
        self.outlinerWidgets[self.name + "_lowerarm"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_upperarm"])
        self.outlinerWidgets[self.name + "_lowerarm"].setText(0, self.name + "_lowerarm")
        self.createGlobalMoverButton(self.name + "_lowerarm", self.outlinerWidgets[self.name + "_lowerarm"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_lowerarm", self.outlinerWidgets[self.name + "_lowerarm"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_lowerarm", self.outlinerWidgets[self.name + "_lowerarm"],
                                   self.rigUiInst)

        # add the lowerarm twists
        self.outlinerWidgets[self.name + "_lowerarm_twist_01"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_lowerarm"])
        self.outlinerWidgets[self.name + "_lowerarm_twist_01"].setText(0, self.name + "_lowerarm_twist_01")
        self.createOffsetMoverButton(self.name + "_lowerarm_twist_01",
                                     self.outlinerWidgets[self.name + "_lowerarm_twist_01"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_lowerarm_twist_01"].setHidden(True)

        self.outlinerWidgets[self.name + "_lowerarm_twist_02"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_lowerarm"])
        self.outlinerWidgets[self.name + "_lowerarm_twist_02"].setText(0, self.name + "_lowerarm_twist_02")
        self.createOffsetMoverButton(self.name + "_lowerarm_twist_02",
                                     self.outlinerWidgets[self.name + "_lowerarm_twist_02"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_lowerarm_twist_02"].setHidden(True)

        self.outlinerWidgets[self.name + "_lowerarm_twist_03"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_lowerarm"])
        self.outlinerWidgets[self.name + "_lowerarm_twist_03"].setText(0, self.name + "_lowerarm_twist_03")
        self.createOffsetMoverButton(self.name + "_lowerarm_twist_03",
                                     self.outlinerWidgets[self.name + "_lowerarm_twist_03"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_lowerarm_twist_03"].setHidden(True)

        # add the hand
        self.outlinerWidgets[self.name + "_hand"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_lowerarm"])
        self.outlinerWidgets[self.name + "_hand"].setText(0, self.name + "_hand")
        self.createGlobalMoverButton(self.name + "_hand", self.outlinerWidgets[self.name + "_hand"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_hand", self.outlinerWidgets[self.name + "_hand"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_hand", self.outlinerWidgets[self.name + "_hand"], self.rigUiInst)

        # add the thumb
        self.outlinerWidgets[self.name + "_thumb_metacarpal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_thumb_metacarpal"].setText(0, self.name + "_thumb_metacarpal")
        self.createGlobalMoverButton(self.name + "_thumb_metacarpal",
                                     self.outlinerWidgets[self.name + "_thumb_metacarpal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thumb_metacarpal",
                                     self.outlinerWidgets[self.name + "_thumb_metacarpal"], self.rigUiInst)

        self.outlinerWidgets[self.name + "_thumb_proximal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_thumb_proximal"].setText(0, self.name + "_thumb_proximal")
        self.createGlobalMoverButton(self.name + "_thumb_proximal", self.outlinerWidgets[self.name + "_thumb_proximal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thumb_proximal", self.outlinerWidgets[self.name + "_thumb_proximal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_thumb_proximal", self.outlinerWidgets[self.name + "_thumb_proximal"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_thumb_distal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_thumb_proximal"])
        self.outlinerWidgets[self.name + "_thumb_distal"].setText(0, self.name + "_thumb_distal")
        self.createGlobalMoverButton(self.name + "_thumb_distal", self.outlinerWidgets[self.name + "_thumb_distal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_thumb_distal", self.outlinerWidgets[self.name + "_thumb_distal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_thumb_distal", self.outlinerWidgets[self.name + "_thumb_distal"],
                                   self.rigUiInst)

        # add the index finger
        self.outlinerWidgets[self.name + "_index_metacarpal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_index_metacarpal"].setText(0, self.name + "_index_metacarpal")
        self.createGlobalMoverButton(self.name + "_index_metacarpal",
                                     self.outlinerWidgets[self.name + "_index_metacarpal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_metacarpal",
                                     self.outlinerWidgets[self.name + "_index_metacarpal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_index_metacarpal"].setHidden(True)

        self.outlinerWidgets[self.name + "_index_proximal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_index_proximal"].setText(0, self.name + "_index_proximal")
        self.createGlobalMoverButton(self.name + "_index_proximal", self.outlinerWidgets[self.name + "_index_proximal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_proximal", self.outlinerWidgets[self.name + "_index_proximal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_proximal", self.outlinerWidgets[self.name + "_index_proximal"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_index_middle"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_index_proximal"])
        self.outlinerWidgets[self.name + "_index_middle"].setText(0, self.name + "_index_middle")
        self.createGlobalMoverButton(self.name + "_index_middle", self.outlinerWidgets[self.name + "_index_middle"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_middle", self.outlinerWidgets[self.name + "_index_middle"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_middle", self.outlinerWidgets[self.name + "_index_middle"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_index_distal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_index_middle"])
        self.outlinerWidgets[self.name + "_index_distal"].setText(0, self.name + "_index_distal")
        self.createGlobalMoverButton(self.name + "_index_distal", self.outlinerWidgets[self.name + "_index_distal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_index_distal", self.outlinerWidgets[self.name + "_index_distal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_index_distal", self.outlinerWidgets[self.name + "_index_distal"],
                                   self.rigUiInst)

        # add the middle finger
        self.outlinerWidgets[self.name + "_middle_metacarpal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_middle_metacarpal"].setText(0, self.name + "_middle_metacarpal")
        self.createGlobalMoverButton(self.name + "_middle_metacarpal",
                                     self.outlinerWidgets[self.name + "_middle_metacarpal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_metacarpal",
                                     self.outlinerWidgets[self.name + "_middle_metacarpal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_middle_metacarpal"].setHidden(True)

        self.outlinerWidgets[self.name + "_middle_proximal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_middle_proximal"].setText(0, self.name + "_middle_proximal")
        self.createGlobalMoverButton(self.name + "_middle_proximal",
                                     self.outlinerWidgets[self.name + "_middle_proximal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_proximal",
                                     self.outlinerWidgets[self.name + "_middle_proximal"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_proximal", self.outlinerWidgets[self.name + "_middle_proximal"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_middle_middle"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_middle_proximal"])
        self.outlinerWidgets[self.name + "_middle_middle"].setText(0, self.name + "_middle_middle")
        self.createGlobalMoverButton(self.name + "_middle_middle", self.outlinerWidgets[self.name + "_middle_middle"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_middle", self.outlinerWidgets[self.name + "_middle_middle"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_middle", self.outlinerWidgets[self.name + "_middle_middle"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_middle_distal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_middle_middle"])
        self.outlinerWidgets[self.name + "_middle_distal"].setText(0, self.name + "_middle_distal")
        self.createGlobalMoverButton(self.name + "_middle_distal", self.outlinerWidgets[self.name + "_middle_distal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_middle_distal", self.outlinerWidgets[self.name + "_middle_distal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_middle_distal", self.outlinerWidgets[self.name + "_middle_distal"],
                                   self.rigUiInst)

        # add the ring finger
        self.outlinerWidgets[self.name + "_ring_metacarpal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_ring_metacarpal"].setText(0, self.name + "_ring_metacarpal")
        self.createGlobalMoverButton(self.name + "_ring_metacarpal",
                                     self.outlinerWidgets[self.name + "_ring_metacarpal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_metacarpal",
                                     self.outlinerWidgets[self.name + "_ring_metacarpal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_ring_metacarpal"].setHidden(True)

        self.outlinerWidgets[self.name + "_ring_proximal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_ring_proximal"].setText(0, self.name + "_ring_proximal")
        self.createGlobalMoverButton(self.name + "_ring_proximal", self.outlinerWidgets[self.name + "_ring_proximal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_proximal", self.outlinerWidgets[self.name + "_ring_proximal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_proximal", self.outlinerWidgets[self.name + "_ring_proximal"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_ring_middle"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_ring_proximal"])
        self.outlinerWidgets[self.name + "_ring_middle"].setText(0, self.name + "_ring_middle")
        self.createGlobalMoverButton(self.name + "_ring_middle", self.outlinerWidgets[self.name + "_ring_middle"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_middle", self.outlinerWidgets[self.name + "_ring_middle"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_middle", self.outlinerWidgets[self.name + "_ring_middle"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_ring_distal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_ring_middle"])
        self.outlinerWidgets[self.name + "_ring_distal"].setText(0, self.name + "_ring_distal")
        self.createGlobalMoverButton(self.name + "_ring_distal", self.outlinerWidgets[self.name + "_ring_distal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_ring_distal", self.outlinerWidgets[self.name + "_ring_distal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_ring_distal", self.outlinerWidgets[self.name + "_ring_distal"],
                                   self.rigUiInst)

        # add the pinky finger
        self.outlinerWidgets[self.name + "_pinky_metacarpal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_pinky_metacarpal"].setText(0, self.name + "_pinky_metacarpal")
        self.createGlobalMoverButton(self.name + "_pinky_metacarpal",
                                     self.outlinerWidgets[self.name + "_pinky_metacarpal"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_metacarpal",
                                     self.outlinerWidgets[self.name + "_pinky_metacarpal"], self.rigUiInst)
        self.outlinerWidgets[self.name + "_pinky_metacarpal"].setHidden(True)

        self.outlinerWidgets[self.name + "_pinky_proximal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_hand"])
        self.outlinerWidgets[self.name + "_pinky_proximal"].setText(0, self.name + "_pinky_proximal")
        self.createGlobalMoverButton(self.name + "_pinky_proximal", self.outlinerWidgets[self.name + "_pinky_proximal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_proximal", self.outlinerWidgets[self.name + "_pinky_proximal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_proximal", self.outlinerWidgets[self.name + "_pinky_proximal"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_pinky_middle"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_pinky_proximal"])
        self.outlinerWidgets[self.name + "_pinky_middle"].setText(0, self.name + "_pinky_middle")
        self.createGlobalMoverButton(self.name + "_pinky_middle", self.outlinerWidgets[self.name + "_pinky_middle"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_middle", self.outlinerWidgets[self.name + "_pinky_middle"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_middle", self.outlinerWidgets[self.name + "_pinky_middle"],
                                   self.rigUiInst)

        self.outlinerWidgets[self.name + "_pinky_distal"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_pinky_middle"])
        self.outlinerWidgets[self.name + "_pinky_distal"].setText(0, self.name + "_pinky_distal")
        self.createGlobalMoverButton(self.name + "_pinky_distal", self.outlinerWidgets[self.name + "_pinky_distal"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pinky_distal", self.outlinerWidgets[self.name + "_pinky_distal"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pinky_distal", self.outlinerWidgets[self.name + "_pinky_distal"],
                                   self.rigUiInst)

        # create selection script job for module
        self.createScriptJob()

        # update based on spinBox values
        self.updateOutliner()
        self.updateBoneCount()
        self.rigUiInst.treeWidget.expandAll()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def aimMode_Setup(self, state):

        # get attributes needed
        name = self.groupBox.title()
        networkNode = self.returnNetworkNode
        side = cmds.getAttr(networkNode + ".side")

        # setup aim vector details per side
        armAim = [1, 0, 0]
        armUp = [0, 0, 1]
        handAim = [1, 0, 0]
        handUp = [0, -1, 0]

        if side == "Right":
            armAim = [-1, 0, 0]
            armUp = [0, 0, -1]
            handAim = [-1, 0, 0]
            handUp = [0, 1, 0]

        # if passed in state is True:
        if state:
            # setup aim constraints

            # clavicle
            cmds.aimConstraint(name + "_upperarm_lra", name + "_clavicle_mover_geo", aimVector=armAim, upVector=armUp,
                               wut="scene", wu=[0, 0, 1], mo=True)
            cmds.aimConstraint(name + "_upperarm_lra", name + "_clavicle_mover_offset", aimVector=armAim,
                               upVector=armUp, wut="scene", wu=[0, 0, 1], mo=True)

            # upperarm
            cmds.aimConstraint(name + "_lowerarm_lra", name + "_upperarm_mover_geo", aimVector=armAim, upVector=armUp,
                               skip="x", wut="scene", wu=[0, 0, 1], mo=True)
            cmds.aimConstraint(name + "_lowerarm_lra", name + "_upperarm_mover_offset", aimVector=armAim,
                               skip="x", upVector=armUp, wut="scene", wu=[0, 0, 1], mo=True)

            # lowerarm
            cmds.aimConstraint(name + "_hand_lra", name + "_lowerarm_mover_offset", aimVector=armAim, upVector=armUp,
                               wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            # index finger
            if cmds.getAttr(name + "_index_metacarpal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_proximal_lra", name + "_index_metacarpal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_index_proximal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_middle_lra", name + "_index_proximal_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_index_middle_lra", name + "_index_proximal_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_index_middle_mover_grp.v") == True:
                cmds.aimConstraint(name + "_index_distal_lra", name + "_index_middle_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_index_distal_lra", name + "_index_middle_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            # middle finger
            if cmds.getAttr(name + "_middle_metacarpal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_proximal_lra", name + "_middle_metacarpal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_middle_proximal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_middle_lra", name + "_middle_proximal_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_middle_middle_lra", name + "_middle_proximal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_middle_middle_mover_grp.v") == True:
                cmds.aimConstraint(name + "_middle_distal_lra", name + "_middle_middle_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_middle_distal_lra", name + "_middle_middle_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            # ring finger
            if cmds.getAttr(name + "_ring_metacarpal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_proximal_lra", name + "_ring_metacarpal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_ring_proximal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_middle_lra", name + "_ring_proximal_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_ring_middle_lra", name + "_ring_proximal_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_ring_middle_mover_grp.v") == True:
                cmds.aimConstraint(name + "_ring_distal_lra", name + "_ring_middle_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_ring_distal_lra", name + "_ring_middle_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            # pinky finger
            if cmds.getAttr(name + "_pinky_metacarpal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_proximal_lra", name + "_pinky_metacarpal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_pinky_proximal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_middle_lra", name + "_pinky_proximal_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_pinky_middle_lra", name + "_pinky_proximal_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_pinky_middle_mover_grp.v") == True:
                cmds.aimConstraint(name + "_pinky_distal_lra", name + "_pinky_middle_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_pinky_distal_lra", name + "_pinky_middle_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            # thumb finger
            if cmds.getAttr(name + "_thumb_metacarpal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_thumb_proximal_lra", name + "_thumb_metacarpal_mover_offset",
                                   aimVector=handAim, upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

            if cmds.getAttr(name + "_thumb_proximal_mover_grp.v") == True:
                cmds.aimConstraint(name + "_thumb_distal_lra", name + "_thumb_proximal_mover_geo", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])
                cmds.aimConstraint(name + "_thumb_distal_lra", name + "_thumb_proximal_mover_offset", aimVector=handAim,
                                   upVector=handUp, wut="scene", wu=[0, 0, 1], mo=True, skip=["x"])

        # if passed in state is False:
        if not state:
            cmds.select(name + "_mover_grp", hi=True)
            aimConstraints = cmds.ls(sl=True, exactType="aimConstraint")

            for constraint in aimConstraints:
                cmds.lockNode(constraint, lock=False)
                cmds.delete(constraint)

            self.bakeOffsets()
            cmds.select(clear=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def coplanarMode(self):

        # current selection
        currentSelection = cmds.ls(sl=True)

        # get the state of the button
        state = self.coplanarBtn.isChecked()

        # write the attribute on the module
        networkNode = self.returnNetworkNode

        import System.utils as utils
        aimState = cmds.getAttr(networkNode + ".aimMode")
        if state:

            # lock out offset movers as they aren't to be used in coplanar mode
            offsetMovers = self.returnJointMovers[1]
            for mover in offsetMovers:
                cmds.lockNode(mover, lock=False)
                for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]:
                    try:
                        cmds.setAttr(mover + attr, lock=True)
                    except:
                        pass

            # fire script job that watches the coplanarIkHandle attributes, and when they change, snap to IK knee in tz
            self.coplanarScriptJob1 = cmds.scriptJob(attributeChange=[self.name + "_coplanarIkHandle.translate",
                                                                      partial(riggingUtils.coPlanarModeSnap, self,
                                                                              self.name + "_coplanar_lowerarm",
                                                                              self.name + "_lowerarm_mover_offset",
                                                                              [self.name + "_coplanar_upperarm",
                                                                               self.name + "_coplanar_lowerarm"],
                                                                              [self.name + "_upperarm_mover_offset",
                                                                               self.name + "_lowerarm_mover_offset"],
                                                                              self.name + "_lowerarm_mover_offset",
                                                                              [])], kws=True)

            # make sure aim mode is on
            if not aimState:
                self.aimMode_Setup(True)

            # reselect current selection
            if len(currentSelection) > 0:
                cmds.select(currentSelection)

        if not state:
            # unlock all offset movers
            offsetMovers = self.returnJointMovers[1]
            for mover in offsetMovers:
                for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]:
                    try:
                        cmds.setAttr(mover + attr, lock=False)
                    except:
                        pass

                cmds.lockNode(mover, lock=True)

            cmds.scriptJob(kill=self.coplanarScriptJob1)
            self.aimMode_Setup(False)

            if aimState:
                self.aimMode_Setup(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateSettingsUI(self):

        # this function will update the settings UI when the UI is launched based on the network node settings
        # in the scene
        networkNode = self.returnNetworkNode

        upperarmTwists = cmds.getAttr(networkNode + ".armTwists")
        lowerarmTwists = cmds.getAttr(networkNode + ".forearmTwists")
        thumbJoints = cmds.getAttr(networkNode + ".thumbJoints")
        indexJoints = cmds.getAttr(networkNode + ".indexJoints")
        middleJoints = cmds.getAttr(networkNode + ".middleJoints")
        ringJoints = cmds.getAttr(networkNode + ".ringJoints")
        pinkyJoints = cmds.getAttr(networkNode + ".pinkyJoints")
        includeClav = cmds.getAttr(networkNode + ".includeClavicle")
        thumbMeta = cmds.getAttr(networkNode + ".thumbMeta")
        indexMeta = cmds.getAttr(networkNode + ".indexMeta")
        middleMeta = cmds.getAttr(networkNode + ".middleMeta")
        ringMeta = cmds.getAttr(networkNode + ".ringMeta")
        pinkyMeta = cmds.getAttr(networkNode + ".pinkyMeta")

        # update UI elements
        self.upperarmTwistNum.setValue(upperarmTwists)
        self.lowerarmTwistNum.setValue(lowerarmTwists)
        self.clavicleCB.setChecked(includeClav)

        self.thumbNum.setValue(thumbJoints)
        self.indexNum.setValue(indexJoints)
        self.middleNum.setValue(middleJoints)
        self.ringNum.setValue(ringJoints)
        self.pinkyNum.setValue(pinkyJoints)

        self.thumbMeta.setChecked(thumbMeta)
        self.indexMeta.setChecked(indexMeta)
        self.middleMeta.setChecked(middleMeta)
        self.ringMeta.setChecked(ringMeta)
        self.pinkyMeta.setChecked(pinkyMeta)

        # apply changes
        self.applyButton.setEnabled(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateOutliner(self):

        # whenever changes are made to the module settings, update the outliner to show the new or removed movers

        # CLAVICLE

        if not self.clavicleCB.isChecked():
            self.outlinerWidgets[self.originalName + "_clavicle"].setHidden(True)
        else:
            self.outlinerWidgets[self.originalName + "_clavicle"].setHidden(False)

        # UPPERARM TWISTS
        armTwists = self.upperarmTwistNum.value()
        if armTwists == 0:
            self.outlinerWidgets[self.originalName + "_upperarm_twist_01"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_03"].setHidden(True)
        if armTwists == 1:
            self.outlinerWidgets[self.originalName + "_upperarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_03"].setHidden(True)
        if armTwists == 2:
            self.outlinerWidgets[self.originalName + "_upperarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_03"].setHidden(True)
        if armTwists == 3:
            self.outlinerWidgets[self.originalName + "_upperarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_upperarm_twist_03"].setHidden(False)

        # LOWERARM TWISTS
        lowerarmTwists = self.lowerarmTwistNum.value()
        if lowerarmTwists == 0:
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_01"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_03"].setHidden(True)
        if lowerarmTwists == 1:
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_03"].setHidden(True)
        if lowerarmTwists == 2:
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_03"].setHidden(True)
        if lowerarmTwists == 3:
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_lowerarm_twist_03"].setHidden(False)

        # THUMB
        thumbBones = self.thumbNum.value()
        thumbMeta = self.thumbMeta.isChecked()

        if thumbBones == 0:
            self.outlinerWidgets[self.originalName + "_thumb_proximal"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_thumb_distal"].setHidden(True)
        if thumbBones == 1:
            self.outlinerWidgets[self.originalName + "_thumb_proximal"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thumb_distal"].setHidden(True)
        if thumbBones == 2:
            self.outlinerWidgets[self.originalName + "_thumb_proximal"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_thumb_distal"].setHidden(False)

        if thumbMeta:
            self.outlinerWidgets[self.originalName + "_thumb_metacarpal"].setHidden(False)
        if not thumbMeta:
            self.outlinerWidgets[self.originalName + "_thumb_metacarpal"].setHidden(True)

        # FINGERS
        fingers = [[self.indexNum, "index", self.indexMeta], [self.middleNum, "middle", self.middleMeta],
                   [self.ringNum, "ring", self.ringMeta], [self.pinkyNum, "pinky", self.pinkyMeta]]

        for finger in fingers:
            value = finger[0].value()
            meta = finger[2].isChecked()

            if value == 0:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_proximal"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_middle"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_distal"].setHidden(True)
            if value == 1:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_proximal"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_middle"].setHidden(True)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_distal"].setHidden(True)
            if value == 2:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_proximal"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_middle"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_distal"].setHidden(True)
            if value == 3:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_proximal"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_middle"].setHidden(False)
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_distal"].setHidden(False)

            if meta:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_metacarpal"].setHidden(False)
            if not meta:
                self.outlinerWidgets[self.originalName + "_" + finger[1] + "_metacarpal"].setHidden(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def applyModuleChanges(self, moduleInst):

        # get prefix/suffix
        name = self.groupBox.title()
        prefix = name.partition(baseName)[0]
        suffix = name.partition(baseName)[2]

        if len(prefix) > 0:
            if prefix.find("_") == -1:
                prefix = prefix + "_"
        if len(suffix) > 0:
            if suffix.find("_") == -1:
                suffix = "_" + suffix

        # create list of the new created bones
        armJoints = []

        if self.clavicleCB.isChecked():
            armJoints.append(prefix + "clavicle" + suffix)
            armJoints.append(prefix + "upperarm" + suffix)
        else:
            armJoints.append(prefix + "upperarm" + suffix)

        # upperarm twists
        upperarmTwists = self.upperarmTwistNum.value()
        for i in range(upperarmTwists):
            armJoints.append(prefix + "upperarm_twist_0" + str(i + 1) + suffix)

        armJoints.append(prefix + "lowerarm" + suffix)

        # lowerarm twists
        lowerarmTwists = self.lowerarmTwistNum.value()
        for i in range(lowerarmTwists):
            armJoints.append(prefix + "lowerarm_twist_0" + str(i + 1) + suffix)

        armJoints.append(prefix + "hand" + suffix)

        # FINGERS
        thumbJoints = ["proximal", "distal"]
        fingerJoints = ["proximal", "middle", "distal"]

        #  thumb
        thumbs = self.thumbNum.value()
        thumbMeta = self.thumbMeta.isChecked()
        if thumbMeta:
            armJoints.append(prefix + "thumb_metacarpal" + suffix)
        for i in range(thumbs):
            armJoints.append(prefix + "thumb_" + thumbJoints[i] + suffix)

        # index
        indexFingers = self.indexNum.value()
        indexMeta = self.indexMeta.isChecked()
        if indexMeta:
            armJoints.append(prefix + "index_metacarpal" + suffix)
        for i in range(indexFingers):
            armJoints.append(prefix + "index_" + fingerJoints[i] + suffix)

        # middle
        middleFingers = self.middleNum.value()
        middleMeta = self.middleMeta.isChecked()
        if middleMeta:
            armJoints.append(prefix + "middle_metacarpal" + suffix)
        for i in range(middleFingers):
            armJoints.append(prefix + "middle_" + fingerJoints[i] + suffix)

        # ring
        ringFingers = self.ringNum.value()
        ringMeta = self.ringMeta.isChecked()
        if ringMeta:
            armJoints.append(prefix + "ring_metacarpal" + suffix)
        for i in range(ringFingers):
            armJoints.append(prefix + "ring_" + fingerJoints[i] + suffix)

        # pinky
        pinkyFingers = self.pinkyNum.value()
        pinkyMeta = self.pinkyMeta.isChecked()
        if pinkyMeta:
            armJoints.append(prefix + "pinky_metacarpal" + suffix)
        for i in range(pinkyFingers):
            armJoints.append(prefix + "pinky_" + fingerJoints[i] + suffix)

        # build attrString
        attrString = ""
        for bone in armJoints:
            attrString += bone + "::"

        networkNode = self.returnNetworkNode
        cmds.setAttr(networkNode + ".Created_Bones", lock=False)
        cmds.setAttr(networkNode + ".Created_Bones", attrString, type="string", lock=True)

        # reset button
        self.applyButton.setEnabled(False)

        # update joint mover
        self.editJointMoverViaSpinBox(self.thumbNum, "thumb", True)
        self.editJointMoverViaSpinBox(self.indexNum, "index", False)
        self.editJointMoverViaSpinBox(self.middleNum, "middle", False)
        self.editJointMoverViaSpinBox(self.ringNum, "ring", False)
        self.editJointMoverViaSpinBox(self.pinkyNum, "pinky", False)

        self.editJointMoverTwistBones(self.upperarmTwistNum, "upperarm")
        self.editJointMoverTwistBones(self.lowerarmTwistNum, "lowerarm")

        self.editJointMoverMetaCarpals(self.thumbMeta, "thumb")
        self.editJointMoverMetaCarpals(self.indexMeta, "index")
        self.editJointMoverMetaCarpals(self.middleMeta, "middle")
        self.editJointMoverMetaCarpals(self.ringMeta, "ring")
        self.editJointMoverMetaCarpals(self.pinkyMeta, "pinky")

        self.includeClavicle()

        # set network node attributes
        cmds.setAttr(networkNode + ".armTwists", lock=False)
        cmds.setAttr(networkNode + ".armTwists", upperarmTwists, lock=True)

        cmds.setAttr(networkNode + ".forearmTwists", lock=False)
        cmds.setAttr(networkNode + ".forearmTwists", lowerarmTwists, lock=True)

        cmds.setAttr(networkNode + ".thumbJoints", lock=False)
        cmds.setAttr(networkNode + ".thumbJoints", thumbs, lock=True)

        cmds.setAttr(networkNode + ".indexJoints", lock=False)
        cmds.setAttr(networkNode + ".indexJoints", indexFingers, lock=True)

        cmds.setAttr(networkNode + ".middleJoints", lock=False)
        cmds.setAttr(networkNode + ".middleJoints", middleFingers, lock=True)

        cmds.setAttr(networkNode + ".ringJoints", lock=False)
        cmds.setAttr(networkNode + ".ringJoints", ringFingers, lock=True)

        cmds.setAttr(networkNode + ".pinkyJoints", lock=False)
        cmds.setAttr(networkNode + ".pinkyJoints", pinkyFingers, lock=True)

        cmds.setAttr(networkNode + ".includeClavicle", lock=False)
        cmds.setAttr(networkNode + ".includeClavicle", self.clavicleCB.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".thumbMeta", lock=False)
        cmds.setAttr(networkNode + ".thumbMeta", self.thumbMeta.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".indexMeta", lock=False)
        cmds.setAttr(networkNode + ".indexMeta", self.indexMeta.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".ringMeta", lock=False)
        cmds.setAttr(networkNode + ".ringMeta", self.ringMeta.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".middleMeta", lock=False)
        cmds.setAttr(networkNode + ".middleMeta", self.middleMeta.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".pinkyMeta", lock=False)
        cmds.setAttr(networkNode + ".pinkyMeta", self.pinkyMeta.isChecked(), lock=True)

        # update outliner
        self.updateOutliner()
        self.updateBoneCount()

        # clear selection
        cmds.select(clear=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editJointMoverViaSpinBox(self, uiWidget, searchKey, isThumb, *args):

        # uiWidget is the spinBox
        # isThumb will be the special case, since there are only the three joints instead of the 4
        # searchKey is the basname (thumb, middle, ring, etc)

        # unlock bone representations
        cmds.select(self.name + "_bone_representations", hi=True)
        selection = cmds.ls(sl=True, type="transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock=False)

        # check number in spinBox
        num = uiWidget.value()

        # set visibility on movers and geo depending on the value of num
        for i in range(num + 1):
            # purely for fanciness
            time.sleep(.05)
            cmds.refresh(force=True)

            if isThumb == False:

                moverList = ["_proximal", "_middle", "_distal"]
                for mover in moverList:
                    if moverList.index(mover) <= i - 1:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock=False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 1, lock=True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 1)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 1)

                    if i == 0:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock=False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 0, lock=True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 0)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 0)

            if isThumb == True:

                moverList = ["_proximal", "_distal"]
                for mover in moverList:
                    if moverList.index(mover) <= i - 1:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", True)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock=False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 1, lock=True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 1)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 1)

                    if i == 0:
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_offset", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_mover_geo", False)
                        self.toggleShapeVis(self.name + "_" + searchKey + mover + "_lra", False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", lock=False)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_mover_grp.v", 0, lock=True)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_bone_geo.v", 0)
                        cmds.setAttr(self.name + "_" + searchKey + mover + "_proxy_geo.v", 0)

        # relock bone representations
        cmds.select(self.name + "_bone_representations", hi=True)
        selection = cmds.ls(sl=True, type="transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock=True)

        # toggle mover vis
        self.rigUiInst.setMoverVisibility()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editJointMoverTwistBones(self, uiWidget, searchKey, *args):

        # check number in spinBox
        num = uiWidget.value()

        for i in range(num + 1):

            if i == 0:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 0, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 0, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock=True)

            if i == 1:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 0, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock=True)

            if i == 2:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 1, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 0, lock=True)

            if i == 3:
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_01_mover_grp.v", 1, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_02_mover_grp.v", 1, lock=True)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", lock=False)
                cmds.setAttr(self.name + "_" + searchKey + "_twist_03_mover_grp.v", 1, lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def editJointMoverMetaCarpals(self, uiWidget, searchKey, *args):

        # uiWidget is the spinBox
        # searchKey is the basname (index, middle, ring, etc)

        # unlock bone representations
        cmds.select(self.name + "_bone_representations", hi=True)
        selection = cmds.ls(sl=True, type="transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock=False)

        # toggle visibility
        if uiWidget.isChecked():
            try:
                cmds.parent(self.name + "_" + searchKey + "_proximal_mover_grp",
                            self.name + "_" + searchKey + "_metacarpal_mover")
            except Exception, e:
                print e

            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_mover_grp.v", 1, lock=True)
            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_bone_geo.v", 1)

        if not uiWidget.isChecked():
            try:
                cmds.parent(self.name + "_" + searchKey + "_proximal_mover_grp", self.name + "_hand_mover")
            except Exception, e:
                print e

            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_mover_grp.v", 0, lock=True)
            cmds.setAttr(self.name + "_" + searchKey + "_metacarpal_bone_geo.v", 0)

        # relock bone representations
        cmds.select(self.name + "_bone_representations", hi=True)
        selection = cmds.ls(sl=True, type="transform")

        for each in selection:
            cmds.setAttr(each + ".v", lock=True)

        # toggle mover vis
        self.rigUiInst.setMoverVisibility()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def includeClavicle(self, *args):
        state = self.clavicleCB.isChecked()

        if state == False:

            # hide clavicle mover controls
            cmds.setAttr(self.name + "_clavicle_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_clavicle_mover_grp.v", 0, lock=True)

            # parent upperarm to mover_grp
            try:
                cmds.parent(self.name + "_upperarm_mover_grp", self.name + "_mover_grp")
            except Exception, e:
                print e

        if state == True:

            # show clavicle mover controls
            cmds.setAttr(self.name + "_clavicle_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_clavicle_mover_grp.v", 1, lock=True)

            # parent upperarm to mover_grp
            try:
                cmds.parent(self.name + "_upperarm_mover_grp", self.name + "_clavicle_mover")
            except Exception, e:
                print e

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeSide(self):

        # gather information (current name, current parent, etc)
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        parent = cmds.getAttr(networkNode + ".parentModuleBone")
        currentSide = cmds.getAttr(networkNode + ".side")

        if cmds.getAttr(networkNode + ".aimMode") == True:
            self.aimMode_Setup(False)

        # call on base class delete
        movers = self.returnJointMovers

        for moverGrp in movers:
            for mover in moverGrp:
                cmds.lockNode(mover, lock=False)

        cmds.delete(self.name + "_mover_grp")

        # figure out side
        if currentSide == "Left":
            cmds.setAttr(networkNode + ".side", lock=False)
            cmds.setAttr(networkNode + ".side", "Right", type="string", lock=True)
            side = "Right"
        if currentSide == "Right":
            cmds.setAttr(networkNode + ".side", lock=False)
            cmds.setAttr(networkNode + ".side", "Left", type="string", lock=True)
            side = "Left"

        # build new jmPath name
        jmPath = jointMover.partition(".ma")[0] + "_" + side + ".ma"
        self.jointMover_Build(jmPath)

        # parent the joint mover to the offset mover of the parent
        mover = ""

        if parent == "root":
            cmds.parent(name + "_mover_grp", "root_mover")
            mover = "root_mover"

        else:
            # find the parent mover name to parent to
            networkNodes = utils.returnRigModules()
            mover = utils.findMoverNodeFromJointName(networkNodes, parent)
            if mover != None:
                cmds.parent(name + "_mover_grp", mover)

        # create the connection geo between the two
        childMover = utils.findOffsetMoverFromName(name)
        riggingUtils.createBoneConnection(mover, childMover, name)
        self.applyModuleChanges(self)

        self.aimMode_Setup(True)

        cmds.select(clear=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetSettings(self):
        for i in range(4):

            networkNode = self.returnNetworkNode
            attrs = cmds.listAttr(networkNode, ud=True)

            for attr in attrs:
                attrType = str(cmds.getAttr(networkNode + "." + attr, type=True))

                if attrType == "double":
                    if attr.find("Joints") == -1:
                        cmds.setAttr(networkNode + "." + attr, lock=False)
                        cmds.setAttr(networkNode + "." + attr, 0, lock=True)
                    else:
                        if attr.find("thumb") != -1:
                            cmds.setAttr(networkNode + "." + attr, lock=False)
                            cmds.setAttr(networkNode + "." + attr, 2, lock=True)
                        else:
                            cmds.setAttr(networkNode + "." + attr, lock=False)
                            cmds.setAttr(networkNode + "." + attr, 3, lock=True)

                if attrType == "bool":
                    if attr.find("thumbMeta") != -1 or attr.find("includeClavicle") != -1:
                        cmds.setAttr(networkNode + "." + attr, lock=False)
                        cmds.setAttr(networkNode + "." + attr, True, lock=True)

                    else:
                        cmds.setAttr(networkNode + "." + attr, lock=False)
                        cmds.setAttr(networkNode + "." + attr, False, lock=True)

                if attrType == "enum":
                    cmds.setAttr(networkNode + "." + attr, lock=False)
                    cmds.setAttr(networkNode + "." + attr, 0, lock=True)

        # relaunch the UI
        self.updateSettingsUI()
        self.applyModuleChanges(self)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pinModule(self, state):

        networkNode = self.returnNetworkNode
        includeClav = cmds.getAttr(networkNode + ".includeClavicle")

        if state:
            if includeClav:
                topLevelMover = self.name + "_clavicle_mover_grp"
            else:
                topLevelMover = self.name + "_upperarm_mover_grp"

            loc = cmds.spaceLocator()[0]
            cmds.setAttr(loc + ".v", False, lock=True)
            constraint = cmds.parentConstraint(topLevelMover, loc)[0]
            cmds.delete(constraint)
            const = cmds.parentConstraint(loc, topLevelMover)[0]

            if not cmds.objExists(networkNode + ".pinConstraint"):
                cmds.addAttr(networkNode, ln="pinConstraint", keyable=True, at="message")

            cmds.connectAttr(const + ".message", networkNode + ".pinConstraint")

        if not state:
            connections = cmds.listConnections(networkNode + ".pinConstraint")
            if len(connections) > 0:
                constraint = connections[0]
                cmds.delete(constraint)

        cmds.select(clear=True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skinProxyGeo(self):

        # get the network node
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        baseName = cmds.getAttr(networkNode + ".baseName")
        prefix = name.partition(baseName)[0]
        suffix = name.partition(baseName)[2]

        # get this module's proxy geo meshes
        cmds.select(name + "_mover_grp", hi=True)
        proxyGeoMeshes = []
        selection = cmds.ls(sl=True)
        for each in selection:
            if each.find("proxy_geo") != -1:
                parent = cmds.listRelatives(each, parent=True)[0]
                if cmds.nodeType(each) == "transform":
                    proxyGeoMeshes.append(each)

        # skin the proxy geo meshes
        for mesh in proxyGeoMeshes:
            dupeMesh = cmds.duplicate(mesh, name="skin_" + mesh)[0]
            cmds.setAttr(dupeMesh + ".overrideEnabled", lock=False)
            cmds.setAttr(dupeMesh + ".overrideDisplayType", 0)

            # create skinned geo group
            if not cmds.objExists("skinned_proxy_geo"):
                cmds.group(empty=True, name="skinned_proxy_geo")

            cmds.parent(dupeMesh, "skinned_proxy_geo")

            boneName = mesh.partition(name + "_")[2]
            boneName = boneName.partition("_proxy_geo")[0]
            joint = prefix + boneName + suffix

            if not cmds.objExists(joint):
                cmds.delete(dupeMesh)

            else:
                cmds.select([dupeMesh, joint])
                cmds.skinCluster(tsb=True, maximumInfluences=1, obeyMaxInfluences=True, bindMethod=0, skinMethod=0,
                                 normalizeWeights=True)
                cmds.select(clear=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildRigCustom(self, textEdit, uiInst):

        # get the network node and find out which rigs to build
        networkNode = self.returnNetworkNode
        buildFK = True
        buildIK_V1 = True

        # have it build all rigs by default, unless there is an attr stating otherwise (backwards- compatability)
        numRigs = 0
        if cmds.objExists(networkNode + ".buildFK"):
            buildFK = cmds.getAttr(networkNode + ".buildFK")
            if buildFK:
                numRigs += 1
        if cmds.objExists(networkNode + ".buildIK_V1"):
            buildIK_V1 = cmds.getAttr(networkNode + ".buildIK_V1")
            if buildIK_V1:
                numRigs += 1

        builtRigs = []

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # create groups and settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create the arm group
        armJoints = self.getMainArmJoints()
        self.armGroup = cmds.group(empty=True, name=self.name + "_group")
        constraint = cmds.parentConstraint(armJoints[1][0], self.armGroup)[0]
        cmds.delete(constraint)

        # create the arm settings group
        self.armSettings = cmds.group(empty=True, name=self.name + "_settings")
        cmds.parent(self.armSettings, self.armGroup)
        for attr in (cmds.listAttr(self.armSettings, keyable=True)):
            cmds.setAttr(self.armSettings + "." + attr, lock=True, keyable=False)

        # add mode attribute to settings
        if numRigs > 1:
            cmds.addAttr(self.armSettings, ln="mode", min=0, max=numRigs - 1, dv=0, keyable=True)

        # create the ctrl group (what will get the constraint to the parent)
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        self.armCtrlGrp = cmds.group(empty=True, name=self.name + "_arm_ctrl_grp")

        if cmds.getAttr(networkNode + ".includeClavicle"):
            constraint = cmds.parentConstraint(armJoints[0], self.armCtrlGrp)[0]
        else:
            constraint = cmds.parentConstraint("driver_" + parentBone, self.armCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.armCtrlGrp, self.armGroup)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # build the rigs
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       FK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # if build FK was true, build the FK rig now
        if buildFK:
            self.buildFkArm(textEdit, uiInst, builtRigs, networkNode)
            builtRigs.append(["FK", [self.armCtrlGrp]])

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       IK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if buildIK_V1:
            ikArmJoints = self.buildIkArm(textEdit, uiInst, builtRigs, networkNode)
            builtRigs.append(["IK", [self.ikCtrlGrp]])

        # ===================================================================
        # #create upper arm twist rig
        # ===================================================================
        twistJoints = self.getTwistJoints(True, False)

        if cmds.getAttr(networkNode + ".side") == "Left":
            twistCtrls = riggingUtils.createCounterTwistRig(twistJoints, self.name, networkNode, armJoints[1][0],
                                                            armJoints[1][1], self.armGroup, [-90, 0, 0])
        if cmds.getAttr(networkNode + ".side") == "Right":
            twistCtrls = riggingUtils.createCounterTwistRig(twistJoints, self.name, networkNode, armJoints[1][0],
                                                            armJoints[1][1], self.armGroup, [90, 0, 0])

        if not cmds.objExists(networkNode + ".upArmTwistControls"):
            cmds.addAttr(networkNode, ln="upArmTwistControls", dt="string")
        jsonString = json.dumps(twistCtrls)
        cmds.setAttr(networkNode + ".upArmTwistControls", jsonString, type="string")

        # create lowerarm twist rig
        twistJoints = self.getTwistJoints(False, True)
        twistCtrls = riggingUtils.createTwistRig(twistJoints, self.name, networkNode, armJoints[1][1], armJoints[1][2],
                                                 self.armGroup, [-90, 0, 0])

        if not cmds.objExists(networkNode + ".loArmTwistControls"):
            cmds.addAttr(networkNode, ln="loArmTwistControls", dt="string")
        jsonString = json.dumps(twistCtrls)
        cmds.setAttr(networkNode + ".loArmTwistControls", jsonString, type="string")

        # =======================================================================
        # # #build finger rigs (if needed)
        # =======================================================================
        # gather data on which fingers are available for rigging
        fingers = self.getFingerJoints()

        # create finger group
        self.fingerGrp = cmds.group(empty=True, name=self.name + "_finger_group")
        constraint = cmds.parentConstraint(armJoints[1][2], self.fingerGrp)[0]
        cmds.delete(constraint)
        cmds.parent(self.fingerGrp, self.armGroup)

        fingerNodes = self.buildFingers(fingers, textEdit, uiInst, builtRigs, networkNode)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                  CLAVICLE                     # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        if cmds.getAttr(networkNode + ".includeClavicle"):
            clavData = self.buildClavicleRig(textEdit, uiInst, builtRigs, networkNode)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #              Hook up ArmCtrlGrp               # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        if cmds.getAttr(networkNode + ".includeClavicle"):
            armCtrlPointConst = \
            cmds.pointConstraint(["fk_" + armJoints[0] + "_anim", self.name + "_clav_follow"], self.armCtrlGrp)[0]
            armCtrlOrientConst = \
            cmds.orientConstraint(["fk_" + armJoints[0] + "_anim", self.name + "_clav_follow"], self.armCtrlGrp)[0]

            attrData = []
            for connection in [armCtrlPointConst, armCtrlOrientConst]:
                driveAttrs = []
                targets = cmds.getAttr(connection + ".target", mi=True)
                if len(targets) > 1:
                    for each in targets:
                        driveAttrs.append(
                            cmds.listConnections(connection + ".target[" + str(each) + "].targetWeight", p=True))

                    attrData.append(driveAttrs)

        # setup set driven keys on our moder attr and those target attributes
        if cmds.getAttr(networkNode + ".includeClavicle"):
            for i in range(numRigs):
                cmds.setAttr(self.armSettings + ".clavMode", i)

                # go through attr data and zero out anything but the first element in the list
                for data in attrData:
                    for each in data:
                        cmds.setAttr(each[0], 0)

                    cmds.setAttr(data[i][0], 1)

                # set driven keys
                for data in attrData:
                    for each in data:
                        cmds.setDrivenKeyframe(each[0], cd=self.armSettings + ".clavMode", itt="linear", ott="linear")

        # =======================================================================
        # # auto clav set driven keys for ik arm
        # =======================================================================
        cmds.parent(ikArmJoints[0], self.armCtrlGrp)
        if cmds.getAttr(networkNode + ".includeClavicle"):
            if len(builtRigs) > 1:
                # set elbow pose constraint keys based on arm mode

                elbowConstAttrs = []

                targets = cmds.getAttr(clavData[0] + ".target", mi=True)
                if len(targets) > 1:
                    for each in targets:
                        elbowConstAttrs.append(
                            cmds.listConnections(clavData[0] + ".target[" + str(each) + "].targetWeight", p=True))

                for i in range(len(builtRigs)):
                    cmds.setAttr(self.armSettings + ".mode", i)
                    # go through attr data and zero out anything but the first element in the list
                    for data in elbowConstAttrs:
                        for each in data:
                            cmds.setAttr(each, 0)

                    cmds.setAttr(elbowConstAttrs[i][0], 1)

                    # set driven keys
                    for data in elbowConstAttrs:
                        for each in data:
                            cmds.setDrivenKeyframe(each, cd=self.armSettings + ".mode", itt="linear", ott="linear")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #            Hook up FK/IK Switching            # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # mode
        if numRigs > 1:
            attrData = []
            rampData = []

            """ CONSTRAINTS """
            # get the constraint connections on the driver joints for the arms
            connections = []
            for joint in armJoints[1]:
                connections.extend(list(set(cmds.listConnections("driver_" + joint, type="constraint"))))
                ramps = (list(set(cmds.listConnections("driver_" + joint, type="ramp"))))
                for ramp in ramps:
                    connections.append(ramp + ".uCoord")

                for connection in connections:
                    driveAttrs = []

                    if cmds.nodeType(connection) in ["pointConstraint", "orientConstraint"]:

                        # get those constraint target attributes for each constraint connection
                        targets = cmds.getAttr(connection + ".target", mi=True)
                        if len(targets) > 1:
                            for each in targets:
                                driveAttrs.append(
                                    cmds.listConnections(connection + ".target[" + str(each) + "].targetWeight",
                                                         p=True))

                            # add this data to our master list of constraint attribute data
                            attrData.append(driveAttrs)
                    else:
                        if cmds.nodeType(connection) == "ramp":
                            rampData.append(connection)

            rampData = list(set(rampData))

            # setup set driven keys on our moder attr and those target attributes
            for i in range(numRigs):

                cmds.setAttr(self.armSettings + ".mode", i)

                # go through attr data and zero out anything but the first element in the list
                for data in attrData:
                    for each in data:
                        cmds.setAttr(each[0], 0)

                    cmds.setAttr(data[i][0], 1)

                # set driven keys
                for data in attrData:
                    for each in data:
                        cmds.setDrivenKeyframe(each[0], cd=self.armSettings + ".mode", itt="linear", ott="linear")

            """ RAMPS """
            # direct connect mode to uCoord value (only works if there are 2 rigs...) <- not sure if that is the case
            #  still
            for data in rampData:
                # create a multiply node that takes first input of 1/numRigs and 2nd of mode direct connection
                multNode = cmds.shadingNode("multiplyDivide", asUtility=True,
                                            name=self.name + "_" + data.partition(".uCoord")[0] + "_mult")
                cmds.setAttr(multNode + ".input1X", float(float(1) / float(numRigs - 1)))
                cmds.connectAttr(self.armSettings + ".mode", multNode + ".input2X")
                cmds.connectAttr(multNode + ".outputX", data)

            # hook up control visibility
            for i in range(len(builtRigs)):
                cmds.setAttr(self.armSettings + ".mode", i)
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

                    cmds.setDrivenKeyframe(visNodes, at="visibility", cd=self.armSettings + ".mode", itt="linear",
                                           ott="linear")

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # # #            Parent Under Offset Ctrl           # # #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # parent under offset_anim if it exists(it always should)
            if cmds.objExists("offset_anim"):
                cmds.parent(self.armGroup, "offset_anim")

        # return data
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        try:
            if cmds.getAttr(networkNode + ".includeClavicle"):
                uiInst.rigData.append([self.name + "_auto_clav_grp", "driver_" + parentBone, numRigs])
                uiInst.rigData.append([self.clavCtrlGrp, "driver_" + parentBone, numRigs])

            else:
                uiInst.rigData.append([self.armCtrlGrp, "driver_" + parentBone, numRigs])
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildClavicleRig(self, textEdit, uiInst, builtRigs, networkNode):

        # add clavicle mode to rig settings
        cmds.addAttr(self.armSettings, ln="clavMode", min=0, max=1, dv=0, keyable=True)

        # Rig Joint
        joints = self.getMainArmJoints()
        clavJoint = joints[0]
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")

        rigJnt = cmds.createNode("joint", name=self.name + "_clav_rigJnt")
        const = cmds.parentConstraint(clavJoint, rigJnt)[0]
        cmds.delete(const)

        cmds.setAttr(rigJnt + ".v", 0, lock=True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       FK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create rig control
        data = riggingUtils.createControlFromMover(clavJoint, networkNode, True, False)

        fkControl = cmds.rename(data[0], "fk_" + clavJoint + "_anim")
        animGrp = cmds.rename(data[1], "fk_" + clavJoint + "_anim_grp")
        riggingUtils.colorControl(fkControl)

        for attr in [".translateX", ".translateY", ".translateZ", ".scaleX", ".scaleY", ".scaleZ", ".visibility"]:
            cmds.setAttr(fkControl + attr, lock=True, keyable=False)

        # create clav rig grp
        self.clavCtrlGrp = cmds.group(empty=True, name=self.name + "_clav_ctrl_grp")
        constraint = cmds.parentConstraint(parentBone, self.clavCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.clavCtrlGrp, self.armGroup)

        # parent fk clav to clav grp
        cmds.parent(animGrp, self.clavCtrlGrp)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       IK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create rig control
        ikControl = riggingUtils.createControl("arrow", 1, "ik_" + clavJoint + "_anim", True)
        ikCtrlGrp = cmds.group(empty=True, name="ik_" + clavJoint + "_anim_grp")

        cmds.setAttr(ikControl + ".rotateX", -90)
        cmds.makeIdentity(ikControl, t=1, r=1, s=1, apply=True)

        const = cmds.pointConstraint(joints[1][0], ikCtrlGrp)[0]
        cmds.delete(const)

        const = cmds.pointConstraint(joints[1][0], ikControl)[0]
        cmds.delete(const)
        const = cmds.orientConstraint(joints[1][0], ikControl, skip=["x"])[0]
        cmds.delete(const)

        cmds.parent(ikControl, ikCtrlGrp)
        cmds.makeIdentity(ikControl, t=1, r=1, s=1, apply=True)

        upArmPiv = cmds.xform(joints[1][0], q=True, ws=True, rp=True)
        cmds.xform(ikControl, ws=True, piv=upArmPiv)
        cmds.xform(ikCtrlGrp, ws=True, piv=upArmPiv)

        riggingUtils.colorControl(ikControl)

        for attr in [".rotateX", ".rotateY", ".rotateZ", ".scaleX", ".scaleY", ".scaleZ", ".visibility"]:
            cmds.setAttr(ikControl + attr, lock=True, keyable=False)

        # create the ik joint chain
        startJnt = cmds.createNode("joint", name=self.name + "_clav_ik_start")
        endJnt = cmds.createNode("joint", name=self.name + "_clav_ik_end")
        pointJnt = cmds.createNode("joint", name=self.name + "_clav_follow")

        const = cmds.parentConstraint(clavJoint, startJnt)[0]
        cmds.delete(const)

        const = cmds.parentConstraint(joints[1][0], endJnt)[0]
        cmds.delete(const)

        const = cmds.parentConstraint(clavJoint, pointJnt)[0]
        cmds.delete(const)

        cmds.parent(endJnt, startJnt)

        # hide joints
        for jnt in [startJnt, endJnt, pointJnt]:
            cmds.setAttr(jnt + ".v", 0, lock=True)

        # create the ikHandle
        ikNodes = cmds.ikHandle(sj=startJnt, ee=endJnt, sol="ikSCsolver", name=self.name + "_clav_ikHandle")[0]
        cmds.parent(ikNodes, ikControl)
        cmds.setAttr(ikNodes + ".v", 0, lock=True)
        cmds.setAttr(ikNodes + ".stickiness", 1)
        cmds.setAttr(ikNodes + ".snapEnable", 1)

        # =======================================================================
        # #lastly, connect controls up to blender nodes to drive driver joints
        # =======================================================================

        rigJntPointConst = cmds.pointConstraint([fkControl, startJnt], rigJnt, mo=True)[0]
        rigJointOrientConst = cmds.orientConstraint([fkControl, startJnt], rigJnt)[0]

        attrData = []
        for connection in [rigJntPointConst, rigJointOrientConst]:
            driveAttrs = []
            targets = cmds.getAttr(connection + ".target", mi=True)
            if len(targets) > 1:
                for each in targets:
                    driveAttrs.append(
                        cmds.listConnections(connection + ".target[" + str(each) + "].targetWeight", p=True))

                attrData.append(driveAttrs)

        cmds.setAttr(rigJointOrientConst + ".interpType", 2)

        # setup set driven keys on our moder attr and those target attributes
        for i in range(2):
            cmds.setAttr(self.armSettings + ".clavMode", i)

            # go through attr data and zero out anything but the first element in the list
            for data in attrData:
                for each in data:
                    cmds.setAttr(each[0], 0)

                cmds.setAttr(data[i][0], 1)

            # set driven keys
            for data in attrData:
                for each in data:
                    cmds.setDrivenKeyframe(each[0], cd=self.armSettings + ".clavMode", itt="linear", ott="linear")

        # =======================================================================
        # #connect controls up to blender nodes to drive driver joints
        # =======================================================================

        cmds.pointConstraint(rigJnt, "driver_" + clavJoint, mo=True)
        cmds.orientConstraint(rigJnt, "driver_" + clavJoint)

        # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into
        # input 2,and plugs that into driver joint
        if cmds.objExists("master_anim"):
            globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=clavJoint + "_globalScale")
            cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
            cmds.connectAttr(rigJnt + ".scale", globalScaleMult + ".input2")
            riggingUtils.createConstraint(globalScaleMult, "driver_" + clavJoint, "scale", False, 2, 1, "output")
        else:
            riggingUtils.createConstraint(rigJnt, "driver_" + clavJoint, "scale", False, 2, 1)

        # =======================================================================
        # #add IK matcher under FK clav control
        # =======================================================================
        ikMatchGrp = cmds.group(empty=True, name=self.name + "_ik_clav_matcher")
        cmds.parent(ikMatchGrp, fkControl)
        const = cmds.pointConstraint(ikControl, ikMatchGrp)[0]
        cmds.delete(const)

        # =======================================================================
        # #hook up auto clavicle
        # =======================================================================

        # create the main grp to hold all auto clav contents
        autoClavGrp = cmds.group(empty=True, name=self.name + "_auto_clav_grp")
        constraint = cmds.parentConstraint("driver_" + parentBone, autoClavGrp)[0]
        cmds.delete(constraint)

        # create invis arm chain
        invisArmJnts = []
        for joint in joints[1]:
            jnt = cmds.createNode("joint", name="auto_clav_" + joint)
            const = cmds.parentConstraint(joint, jnt)[0]
            cmds.delete(const)
            invisArmJnts.append(jnt)

        invisArmJnts.reverse()
        for i in range(len(invisArmJnts)):
            try:
                cmds.parent(invisArmJnts[i], invisArmJnts[i + 1])
            except IndexError:
                pass

            cmds.setAttr(invisArmJnts[i] + ".v", 0, lock=True)

        invisArmJnts.reverse()
        cmds.makeIdentity(invisArmJnts[0], t=0, r=1, s=0, apply=True)
        cmds.parent(invisArmJnts[0], autoClavGrp)

        # create the invis upper arm fk control/grp
        invisAnimGrp = cmds.group(empty=True, name="auto_clav_fk_" + joints[1][0] + "_anim_grp")
        const = cmds.parentConstraint(joints[1][0], invisAnimGrp)[0]
        cmds.delete(const)

        invisArmAnim = cmds.spaceLocator(name="auto_clav_fk_" + joints[1][0] + "_anim")[0]
        const = cmds.parentConstraint(joints[1][0], invisArmAnim)[0]
        cmds.delete(const)
        cmds.setAttr(invisArmAnim + ".v", 0, lock=True)

        cmds.parent(invisArmAnim, invisAnimGrp)
        cmds.parent(invisAnimGrp, autoClavGrp)

        # create orient loc/grp
        orientLocGrp = cmds.group(empty=True, name=self.name + "_auto_clav_orient_loc_grp")
        const = cmds.parentConstraint(joints[1][0], orientLocGrp)[0]
        cmds.delete(const)

        orientLoc = cmds.spaceLocator(name=self.name + "_auto_clav_orient_loc")[0]
        const = cmds.parentConstraint(joints[1][0], orientLoc)[0]
        cmds.delete(const)

        cmds.parent(orientLoc, orientLocGrp)
        cmds.parent(orientLocGrp, invisArmAnim)

        # orient constrain invis upper arm to orient loc
        cmds.orientConstraint(orientLoc, invisArmJnts[0])

        # connect real fk upperarm anim.rotate to invisArmAnim.rotate
        side = cmds.getAttr(networkNode + ".side")[0]
        if side == "L":
            cmds.connectAttr("fk_" + joints[1][0] + "_anim.rotate", invisArmAnim + ".rotate")
        else:
            reverseMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                           name=self.name + "_" + side + "_multNodeReverse")
            cmds.setAttr(reverseMult + ".input2X", -1)
            cmds.setAttr(reverseMult + ".input2Y", -1)
            cmds.setAttr(reverseMult + ".input2Z", -1)
            cmds.connectAttr("fk_" + joints[1][0] + "_anim.rotate", reverseMult + ".input1")
            cmds.connectAttr(reverseMult + ".output", invisArmAnim + ".rotate")

        # create a locator that tracks our elbow position
        currentElbowPose = cmds.spaceLocator(name=self.name + "_auto_clav_current_elbow_loc")[0]
        const = cmds.parentConstraint(joints[1][1], currentElbowPose)[0]
        cmds.delete(const)
        cmds.setAttr(currentElbowPose + ".v", 0, lock=True)

        # create a group for that locator
        currentPoseGrp = cmds.group(empty=True, name=self.name + "_auto_clav_current_elbow_grp")
        const = cmds.parentConstraint(joints[1][1], currentPoseGrp)[0]
        cmds.delete(const)

        cmds.parent(currentElbowPose, currentPoseGrp)
        cmds.parent(currentPoseGrp, autoClavGrp)

        # point constraint locator grp to invis lower arm
        cmds.pointConstraint(invisArmJnts[1], currentPoseGrp)

        # create switcher group
        switcherGrp = cmds.group(empty=True, name=self.name + "_auto_clav_switcher_grp")
        const = cmds.pointConstraint(invisArmJnts[0], switcherGrp)[0]
        cmds.delete(const)

        cmds.parent(switcherGrp, autoClavGrp)

        # point constrain to autoClavGrp
        cmds.pointConstraint(autoClavGrp, switcherGrp)

        # create ik master grp
        ikMasterGrp = cmds.group(empty=True, name=self.name + "_auto_clav_ik_master_grp")
        const = cmds.pointConstraint(invisArmJnts[0], ikMasterGrp)[0]
        cmds.delete(const)

        cmds.parent(ikMasterGrp, switcherGrp)
        cmds.makeIdentity(ikMasterGrp, t=1, r=1, s=1, apply=True)

        # create ik grp
        ikGrp = cmds.group(empty=True, name=self.name + "_auto_clav_ik_grp")
        const = cmds.pointConstraint(invisArmJnts[0], ikGrp)[0]
        cmds.delete(const)

        cmds.parent(ikGrp, ikMasterGrp)
        cmds.makeIdentity(ikGrp, t=1, r=1, s=1, apply=True)

        # connect ik clav anim.translate to this grp.translate
        cmds.connectAttr(ikControl + ".translate", ikGrp + ".translate")

        # create parent space group for driven group
        ikDrivenSpace = cmds.group(empty=True, name=self.name + "_auto_clav_ik_driven_space_grp")
        const = cmds.parentConstraint(invisArmJnts[0], ikDrivenSpace)[0]
        cmds.delete(const)

        cmds.parent(ikDrivenSpace, ikGrp)

        # create two more groups. ikDrivenGrp and autoClavTranslateGrp. drivenGrp is what will get the pose reader SDKs,
        # autoClavTranslateGrp is what will carry the ikHandle
        ikDrivenGrp = cmds.group(empty=True, name=self.name + "_auto_clav_ik_driven_grp")
        const = cmds.parentConstraint(invisArmJnts[0], ikDrivenGrp)[0]
        cmds.delete(const)

        cmds.parent(ikDrivenGrp, ikDrivenSpace)
        cmds.makeIdentity(ikDrivenGrp, t=1, r=1, s=1, apply=True)

        # create parent space group for autoClavTranslateGrp
        autoClavTransGrpSpace = cmds.group(empty=True, name=self.name + "_auto_clav_ik_trans_space_grp")
        const = cmds.parentConstraint(invisArmJnts[0], autoClavTransGrpSpace)[0]
        cmds.delete(const)

        cmds.parent(autoClavTransGrpSpace, ikGrp)

        autoClavTranslateGrp = cmds.group(empty=True, name=self.name + "_auto_clav_trans_grp")
        const = cmds.parentConstraint(invisArmJnts[0], autoClavTranslateGrp)[0]
        cmds.delete(const)

        cmds.parent(autoClavTranslateGrp, autoClavTransGrpSpace)
        cmds.makeIdentity(autoClavTranslateGrp, t=1, r=1, s=1, apply=True)

        # parent the ik clav ikHandle under the autoClavTranslateGrp
        cmds.parent(ikNodes, autoClavTranslateGrp)

        # add setting to arm settings for autoShoulders
        cmds.addAttr(self.armSettings, ln="autoShoulders", min=0, max=1, dv=0, keyable=True)

        # connect ikDrivenGrp.translate to multDivide node input1, connect autoShoulders attr to input 2,
        # connect output to autoClavTranslateGrp.translate
        clavTransMult = cmds.shadingNode("multiplyDivide", name=self.name + "_clav_trans_mult", asUtility=True)
        cmds.connectAttr(ikDrivenGrp + ".translate", clavTransMult + ".input1")
        cmds.connectAttr(self.armSettings + ".autoShoulders", clavTransMult + ".input2X")
        cmds.connectAttr(self.armSettings + ".autoShoulders", clavTransMult + ".input2Y")
        cmds.connectAttr(self.armSettings + ".autoShoulders", clavTransMult + ".input2Z")
        cmds.connectAttr(clavTransMult + ".output", autoClavTranslateGrp + ".translate")

        # make auto clav work for IK arm
        ikArmAutoClavGrp = cmds.group(empty=True, name=self.name + "_ikArm_auto_clav_grp")
        const = cmds.parentConstraint(self.ikHandCtrl, ikArmAutoClavGrp)[0]
        cmds.delete(const)

        ikArmAutoClavLoc = cmds.spaceLocator(name=self.name + "_ikArm_auto_clav_loc")[0]
        const = cmds.pointConstraint(joints[1][1], ikArmAutoClavLoc)[0]
        cmds.delete(const)
        cmds.setAttr(ikArmAutoClavLoc + ".v", 0, lock=True)

        cmds.parent(ikArmAutoClavGrp, self.ikHandCtrl)
        cmds.parent(ikArmAutoClavLoc, ikArmAutoClavGrp)

        cmds.makeIdentity(ikArmAutoClavLoc, t=1, r=1, s=1, apply=True)
        elbowLocConst = cmds.pointConstraint([invisArmJnts[1], ikArmAutoClavLoc], currentPoseGrp)[0]

        # aim ikArmAutoClavGrp to the IK PV
        cmds.aimConstraint(self.name + "_ik_elbow_anim", ikArmAutoClavGrp, aimVector=[-1, 0, 0], upVector=[0, 0, 1],
                           wut="scene", wu=[0, 0, 1])

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                    Clean Up                   # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        cmds.parent(startJnt, autoClavGrp)
        cmds.parent(ikCtrlGrp, autoClavGrp)
        cmds.parent(pointJnt, autoClavGrp)
        cmds.makeIdentity(pointJnt, t=0, r=1, s=0, apply=True)
        cmds.pointConstraint(endJnt, pointJnt, mo=True)

        # create a clavicle grp
        self.clavicleGrp = cmds.group(empty=True, name=self.name + "_clavicle_grp")
        const = cmds.parentConstraint(self.armCtrlGrp, self.clavicleGrp)[0]
        cmds.delete(const)

        cmds.parent(self.clavicleGrp, self.armGroup)

        # parent rigJnt to clavicle group
        cmds.parent(rigJnt, self.clavicleGrp)

        # parent autoClavGrp and self.clavCtrlGrp to clavicle grp
        cmds.parent(autoClavGrp, self.clavicleGrp)
        cmds.parent(self.clavCtrlGrp, self.clavicleGrp)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                  POSE READER                  # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        """
        Create vectors from the base locator, to the current locator, and from the base to a pose locator
        Subtract the end position with the base.
        Get the angle between the two vectors. compare the angle between the vectors to the max cone angle given.
        """

        cmds.loadPlugin('matrixNodes.dll')
        # global

        baseLoc = cmds.spaceLocator(name=self.name + "_poseReader_Base")[0]
        const = cmds.parentConstraint(self.name + "_base", baseLoc)[0]
        cmds.delete(const)
        cmds.parent(baseLoc, self.armGroup)
        cmds.setAttr(baseLoc + ".v", 0, lock=True)

        baseDM = cmds.shadingNode("decomposeMatrix", asUtility=True, name=self.name + "_poseReader_base_matrix")
        cmds.connectAttr(baseLoc + ".worldMatrix[0]", baseDM + ".inputMatrix")

        currentDM = cmds.shadingNode("decomposeMatrix", asUtility=True, name=self.name + "_poseReader_current_matrix")
        cmds.connectAttr(self.name + "_auto_clav_current_elbow_loc.worldMatrix[0]", currentDM + ".inputMatrix")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Arm Up
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        upArmLoc = cmds.spaceLocator(name=self.name + "_poseReader_armUp_pose")[0]
        const = cmds.parentConstraint(self.name + "_arm_up_pose", upArmLoc)[0]
        cmds.delete(const)
        cmds.parent(upArmLoc, self.armGroup)
        cmds.setAttr(upArmLoc + ".v", 0, lock=True)

        armUpTargetDM = cmds.shadingNode("decomposeMatrix", asUtility=True, name=self.name + "_poseReader_armUp_target")
        cmds.connectAttr(upArmLoc + ".worldMatrix[0]", armUpTargetDM + ".inputMatrix")

        # create plusMinusAverage node, set to subtract. armUpTargetDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armUpTargetPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                          name=self.name + "_poseReader_armUp_targetFromBase")
        cmds.setAttr(armUpTargetPMA + ".operation", 2)
        cmds.connectAttr(armUpTargetDM + ".outputTranslate", armUpTargetPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armUpTargetPMA + ".input3D[1]")

        # create plusMinusAverage node, set to subtract. currentDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armUpCurrentPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                           name=self.name + "_poseReader_armUp_currentFromBase")
        cmds.setAttr(armUpCurrentPMA + ".operation", 2)
        cmds.connectAttr(currentDM + ".outputTranslate", armUpCurrentPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armUpCurrentPMA + ".input3D[1]")

        # get angle between vectors
        armUpAngleBetween = cmds.shadingNode("angleBetween", asUtility=True, name=self.name + "_armUp_AngleBetween")
        cmds.connectAttr(armUpTargetPMA + ".output3D", armUpAngleBetween + ".vector1")
        cmds.connectAttr(armUpCurrentPMA + ".output3D", armUpAngleBetween + ".vector2")

        # add attr to the base locator for armUpConeAngle
        cmds.addAttr(baseLoc, ln="armUpConeAngle", keyable=True)
        cmds.setAttr(baseLoc + ".armUpConeAngle", 180)

        # halve the cone angle
        armUpMultDL = cmds.shadingNode("multDoubleLinear", asUtility=True, name=self.name + "_armUp_coneAngleMult")
        cmds.connectAttr(baseLoc + ".armUpConeAngle", armUpMultDL + ".input1")
        cmds.setAttr(armUpMultDL + ".input2", 0.5)

        # divide the angle between our vectors by the cone angle
        armUpConeRatio = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_armUp_coneAngleRatio")
        cmds.setAttr(armUpConeRatio + ".operation", 2)

        cmds.connectAttr(armUpAngleBetween + ".angle", armUpConeRatio + ".input1X")
        cmds.connectAttr(armUpMultDL + ".output", armUpConeRatio + ".input2X")

        # create condition. If result > 1, use 1. If result < 1, use result
        armUpCondition = cmds.shadingNode("condition", asUtility=True, name=self.name + "_armUp_condition")
        cmds.setAttr(armUpCondition + ".operation", 2)

        cmds.connectAttr(armUpConeRatio + ".outputX", armUpCondition + ".firstTerm")
        cmds.setAttr(armUpCondition + ".secondTerm", 1)
        cmds.setAttr(armUpCondition + ".colorIfTrueR", 1)
        cmds.connectAttr(armUpConeRatio + ".outputX", armUpCondition + ".colorIfFalseR")

        # plug condition result into a new plusMinusAvg (subtract) input3D[1]. set input3D[0] to 1
        armUpReversePMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                           name=self.name + "_poseReader_armUp_reverse")
        cmds.setAttr(armUpReversePMA + ".operation", 2)

        cmds.connectAttr(armUpCondition + ".outColorR", armUpReversePMA + ".input1D[1]")
        cmds.setAttr(armUpReversePMA + ".input1D[0]", 1)

        # add attr to base loc for armUp result
        cmds.addAttr(baseLoc, ln="armUpResult", dv=0, min=0, max=1, keyable=True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Arm Forward
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        armForwardLoc = cmds.spaceLocator(name=self.name + "_poseReader_armForward_pose")[0]
        const = cmds.parentConstraint(self.name + "_arm_forward_pose", armForwardLoc)[0]
        cmds.delete(const)
        cmds.parent(armForwardLoc, self.armGroup)
        cmds.setAttr(armForwardLoc + ".v", 0, lock=True)

        armForwardTargetDM = cmds.shadingNode("decomposeMatrix", asUtility=True,
                                              name=self.name + "_poseReader_armForward_target")
        cmds.connectAttr(armForwardLoc + ".worldMatrix[0]", armForwardTargetDM + ".inputMatrix")

        # create plusMinusAverage node, set to subtract. armUpTargetDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armForwardTargetPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                               name=self.name + "_poseReader_armForward_targetFromBase")
        cmds.setAttr(armForwardTargetPMA + ".operation", 2)
        cmds.connectAttr(armForwardTargetDM + ".outputTranslate", armForwardTargetPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armForwardTargetPMA + ".input3D[1]")

        # create plusMinusAverage node, set to subtract. currentDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armForwardCurrentPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                                name=self.name + "_poseReader_armForward_currentFromBase")
        cmds.setAttr(armForwardCurrentPMA + ".operation", 2)
        cmds.connectAttr(currentDM + ".outputTranslate", armForwardCurrentPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armForwardCurrentPMA + ".input3D[1]")

        # get angle between vectors
        armForwardAngleBetween = cmds.shadingNode("angleBetween", asUtility=True,
                                                  name=self.name + "_armForward_AngleBetween")
        cmds.connectAttr(armForwardTargetPMA + ".output3D", armForwardAngleBetween + ".vector1")
        cmds.connectAttr(armForwardCurrentPMA + ".output3D", armForwardAngleBetween + ".vector2")

        # add attr to the base locator for armUpConeAngle
        cmds.addAttr(baseLoc, ln="armForwardConeAngle", keyable=True)
        cmds.setAttr(baseLoc + ".armForwardConeAngle", 180)

        # halve the cone angle
        armForwardMultDL = cmds.shadingNode("multDoubleLinear", asUtility=True,
                                            name=self.name + "_armForward_coneAngleMult")
        cmds.connectAttr(baseLoc + ".armUpConeAngle", armForwardMultDL + ".input1")
        cmds.setAttr(armForwardMultDL + ".input2", 0.5)

        # divide the angle between our vectors by the cone angle
        armForwardConeRatio = cmds.shadingNode("multiplyDivide", asUtility=True,
                                               name=self.name + "_armForward_coneAngleRatio")
        cmds.setAttr(armForwardConeRatio + ".operation", 2)

        cmds.connectAttr(armForwardAngleBetween + ".angle", armForwardConeRatio + ".input1X")
        cmds.connectAttr(armForwardMultDL + ".output", armForwardConeRatio + ".input2X")

        # create condition. If result > 1, use 1. If result < 1, use result
        armForwardCondition = cmds.shadingNode("condition", asUtility=True, name=self.name + "_armForward_condition")
        cmds.setAttr(armForwardCondition + ".operation", 2)

        cmds.connectAttr(armForwardConeRatio + ".outputX", armForwardCondition + ".firstTerm")
        cmds.setAttr(armForwardCondition + ".secondTerm", 1)
        cmds.setAttr(armForwardCondition + ".colorIfTrueR", 1)
        cmds.connectAttr(armForwardConeRatio + ".outputX", armForwardCondition + ".colorIfFalseR")

        # plug condition result into a new plusMinusAvg (subtract) input3D[1]. set input3D[0] to 1
        armForwardReversePMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                                name=self.name + "_poseReader_armForward_reverse")
        cmds.setAttr(armForwardReversePMA + ".operation", 2)

        cmds.connectAttr(armForwardCondition + ".outColorR", armForwardReversePMA + ".input1D[1]")
        cmds.setAttr(armForwardReversePMA + ".input1D[0]", 1)

        # add attr to base loc for armUp result
        cmds.addAttr(baseLoc, ln="armForwardResult", dv=0, min=0, max=1, keyable=True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Arm Backward
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        armBackwardLoc = cmds.spaceLocator(name=self.name + "_poseReader_armBackward_pose")[0]
        const = cmds.parentConstraint(self.name + "_arm_back_pose", armBackwardLoc)[0]
        cmds.delete(const)
        cmds.parent(armBackwardLoc, self.armGroup)
        cmds.setAttr(armBackwardLoc + ".v", 0, lock=True)

        armBackwardTargetDM = cmds.shadingNode("decomposeMatrix", asUtility=True,
                                               name=self.name + "_poseReader_armBackward_target")
        cmds.connectAttr(armBackwardLoc + ".worldMatrix[0]", armBackwardTargetDM + ".inputMatrix")

        # create plusMinusAverage node, set to subtract. armUpTargetDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armBackwardTargetPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                                name=self.name + "_poseReader_armBackward_targetFromBase")
        cmds.setAttr(armBackwardTargetPMA + ".operation", 2)
        cmds.connectAttr(armBackwardTargetDM + ".outputTranslate", armBackwardTargetPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armBackwardTargetPMA + ".input3D[1]")

        # create plusMinusAverage node, set to subtract. currentDM.outputTranslate -> plusMinusAvg.input3D[0].
        # baseDM.outputTranslate -> plusMinusAvg.input3D[1]
        armBackwardCurrentPMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                                 name=self.name + "_poseReader_armBackward_currentFromBase")
        cmds.setAttr(armBackwardCurrentPMA + ".operation", 2)
        cmds.connectAttr(currentDM + ".outputTranslate", armBackwardCurrentPMA + ".input3D[0]")
        cmds.connectAttr(baseDM + ".outputTranslate", armBackwardCurrentPMA + ".input3D[1]")

        # get angle between vectors
        armBackwardAngleBetween = cmds.shadingNode("angleBetween", asUtility=True,
                                                   name=self.name + "_armBackward_AngleBetween")
        cmds.connectAttr(armBackwardTargetPMA + ".output3D", armBackwardAngleBetween + ".vector1")
        cmds.connectAttr(armBackwardCurrentPMA + ".output3D", armBackwardAngleBetween + ".vector2")

        # add attr to the base locator for armUpConeAngle
        cmds.addAttr(baseLoc, ln="armBackwardConeAngle", keyable=True)
        cmds.setAttr(baseLoc + ".armBackwardConeAngle", 180)

        # halve the cone angle
        armBackwardMultDL = cmds.shadingNode("multDoubleLinear", asUtility=True,
                                             name=self.name + "_armBackward_coneAngleMult")
        cmds.connectAttr(baseLoc + ".armUpConeAngle", armBackwardMultDL + ".input1")
        cmds.setAttr(armBackwardMultDL + ".input2", 0.5)

        # divide the angle between our vectors by the cone angle
        armBackwardConeRatio = cmds.shadingNode("multiplyDivide", asUtility=True,
                                                name=self.name + "_armBackward_coneAngleRatio")
        cmds.setAttr(armBackwardConeRatio + ".operation", 2)

        cmds.connectAttr(armBackwardAngleBetween + ".angle", armBackwardConeRatio + ".input1X")
        cmds.connectAttr(armBackwardMultDL + ".output", armBackwardConeRatio + ".input2X")

        # create condition. If result > 1, use 1. If result < 1, use result
        armBackwardCondition = cmds.shadingNode("condition", asUtility=True, name=self.name + "_armBackward_condition")
        cmds.setAttr(armBackwardCondition + ".operation", 2)

        cmds.connectAttr(armBackwardConeRatio + ".outputX", armBackwardCondition + ".firstTerm")
        cmds.setAttr(armBackwardCondition + ".secondTerm", 1)
        cmds.setAttr(armBackwardCondition + ".colorIfTrueR", 1)
        cmds.connectAttr(armBackwardConeRatio + ".outputX", armBackwardCondition + ".colorIfFalseR")

        # plug condition result into a new plusMinusAvg (subtract) input3D[1]. set input3D[0] to 1
        armBackwardReversePMA = cmds.shadingNode("plusMinusAverage", asUtility=True,
                                                 name=self.name + "_poseReader_armBackward_reverse")
        cmds.setAttr(armBackwardReversePMA + ".operation", 2)

        cmds.connectAttr(armBackwardCondition + ".outColorR", armBackwardReversePMA + ".input1D[1]")
        cmds.setAttr(armBackwardReversePMA + ".input1D[0]", 1)

        # add attr to base loc for armUp result
        cmds.addAttr(baseLoc, ln="armBackwardResult", dv=0, min=0, max=1, keyable=True)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #         SET DRIVEN KEYS (pose reader)         # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        side = cmds.getAttr(networkNode + ".side")[0]

        # arm up
        cmds.setAttr(baseLoc + ".armUpResult", 0)
        cmds.setAttr(ikDrivenGrp + ".translateZ", 0)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateZ", cd=baseLoc + ".armUpResult")

        cmds.setAttr(baseLoc + ".armUpResult", 1)
        if side == "L":
            cmds.setAttr(ikDrivenGrp + ".translateZ", cmds.getAttr(upArmLoc + ".translateZ"))
        else:
            cmds.setAttr(ikDrivenGrp + ".translateZ", cmds.getAttr(upArmLoc + ".translateZ") * -1)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateZ", cd=baseLoc + ".armUpResult")

        cmds.connectAttr(armUpReversePMA + ".output1D", baseLoc + ".armUpResult")

        # arm forward
        cmds.setAttr(baseLoc + ".armForwardResult", 0.5)
        cmds.setAttr(ikDrivenGrp + ".translateY", 0)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateY", cd=baseLoc + ".armForwardResult")

        cmds.setAttr(baseLoc + ".armForwardResult", 1)
        if side == "L":
            cmds.setAttr(ikDrivenGrp + ".translateY", cmds.getAttr(armForwardLoc + ".translateY") / 2)
        else:
            cmds.setAttr(ikDrivenGrp + ".translateY", (cmds.getAttr(armForwardLoc + ".translateY") / 2) * -1)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateY", cd=baseLoc + ".armForwardResult")

        cmds.connectAttr(armForwardReversePMA + ".output1D", baseLoc + ".armForwardResult")

        # arm backward
        cmds.setAttr(baseLoc + ".armBackwardResult", 0.5)
        cmds.setAttr(ikDrivenGrp + ".translateY", 0)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateY", cd=baseLoc + ".armBackwardResult")

        cmds.setAttr(baseLoc + ".armBackwardResult", 1)
        if side == "L":
            cmds.setAttr(ikDrivenGrp + ".translateY", cmds.getAttr(armBackwardLoc + ".translateY") / 2)
        else:
            cmds.setAttr(ikDrivenGrp + ".translateY", (cmds.getAttr(armBackwardLoc + ".translateY") / 2) * -1)
        cmds.setDrivenKeyframe(ikDrivenGrp + ".translateY", cd=baseLoc + ".armBackwardResult")

        cmds.connectAttr(armBackwardReversePMA + ".output1D", baseLoc + ".armBackwardResult")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                Hook Up Modes                  # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        cmds.setAttr(self.armSettings + ".clavMode", 0)
        cmds.setAttr(animGrp + ".v", 1)
        cmds.setAttr(ikCtrlGrp + ".v", 0)
        cmds.setDrivenKeyframe([animGrp + ".v", ikCtrlGrp + ".v"], cd=self.armSettings + ".clavMode")

        cmds.setAttr(self.armSettings + ".clavMode", 1)
        cmds.setAttr(animGrp + ".v", 0)
        cmds.setAttr(ikCtrlGrp + ".v", 1)
        cmds.setDrivenKeyframe([animGrp + ".v", ikCtrlGrp + ".v"], cd=self.armSettings + ".clavMode")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #               Add Data to Node                # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # add created control info to module
        if not cmds.objExists(networkNode + ".clavControls"):
            cmds.addAttr(networkNode, ln="clavControls", dt="string")
        clavCtrls = [fkControl, ikControl]
        jsonString = json.dumps(clavCtrls)
        cmds.setAttr(networkNode + ".clavControls", jsonString, type="string")

        return [elbowLocConst]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildFkArm(self, textEdit, uiInst, builtRigs, networkNode):

        # update progress
        if textEdit != None:
            textEdit.append("        Starting FK Arm Rig Build..")

        # build the rig
        slot = len(builtRigs)

        # find the joints in the arm module that need rigging
        joints = self.getMainArmJoints()
        fkControls = []
        self.topNode = None

        for joint in joints[1]:
            if joint.find("upperarm") != -1:
                data = riggingUtils.createControlFromMover(joint, networkNode, True, True)

                fkControl = cmds.rename(data[0], "fk_" + joint + "_anim")
                animGrp = cmds.rename(data[1], "fk_" + joint + "_anim_grp")
                spaceSwitcher = cmds.rename(data[2], "fk_" + joint + "_anim_space_switcher")
                spaceSwitchFollow = cmds.rename(data[3], "fk_" + joint + "_anim_space_switcher_follow")
                self.topNode = spaceSwitchFollow

                fkControls.append([spaceSwitchFollow, fkControl, joint])
                # color the control
                riggingUtils.colorControl(fkControl)

            else:
                data = riggingUtils.createControlFromMover(joint, networkNode, True, False)

                fkControl = cmds.rename(data[0], "fk_" + joint + "_anim")
                animGrp = cmds.rename(data[1], "fk_" + joint + "_anim_grp")

                fkControls.append([animGrp, fkControl, joint])

                # color the control
                riggingUtils.colorControl(fkControl)

        # create hierarchy
        fkControls.reverse()

        for i in range(len(fkControls)):
            try:
                cmds.parent(fkControls[i][0], fkControls[i + 1][1])
            except IndexError:
                pass

        # =======================================================================
        # #lastly, connect controls up to blender nodes to drive driver joints
        # =======================================================================
        for each in fkControls:
            control = each[1]
            joint = each[2]

            cmds.pointConstraint(control, "driver_" + joint, mo=True)
            cmds.orientConstraint(control, "driver_" + joint)

            # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into
            # input 2,and plugs that into driver joint
            if cmds.objExists("master_anim"):
                globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=joint + "_globalScale")
                cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
                cmds.connectAttr(control + ".scale", globalScaleMult + ".input2")
                riggingUtils.createConstraint(globalScaleMult, "driver_" + joint, "scale", False, 2, slot, "output")
            else:
                riggingUtils.createConstraint(control, "driver_" + joint, "scale", False, 2, slot)

        # #=======================================================================
        # clean up
        # #=======================================================================
        # parent top group into arm group
        cmds.parent(self.topNode, self.armCtrlGrp)

        # lock attrs
        for each in fkControls:
            control = each[1]
            for attr in [".scaleX", ".scaleY", ".scaleZ", ".visibility"]:
                cmds.setAttr(control + attr, lock=True, keyable=False)

        fkRigData = []
        for each in fkControls:
            fkRigData.append(each[1])

        # add created control info to module
        if not cmds.objExists(networkNode + ".fkControls"):
            cmds.addAttr(networkNode, ln="fkControls", dt="string")
        jsonString = json.dumps(fkRigData)
        cmds.setAttr(networkNode + ".fkControls", jsonString, type="string")

        # update progress
        if textEdit != None:
            textEdit.setTextColor(QtGui.QColor(0, 255, 18))
            textEdit.append("        SUCCESS: FK Build Complete!")
            textEdit.setTextColor(QtGui.QColor(255, 255, 255))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildIkArm(self, textEdit, uiInst, builtRigs, networkNode):

        # update progress
        if textEdit != None:
            textEdit.append("        Starting IK Arm Rig Build..")

        # build the rig
        slot = len(builtRigs)

        # find the joints in the arm module that need rigging
        joints = self.getMainArmJoints()
        ikControls = []

        # =======================================================================
        # # create the ik arm joint chain
        # =======================================================================

        ikArmJoints = []
        for joint in joints[1]:
            jnt = cmds.createNode("joint", name="ik_" + joint + "_jnt")
            const = cmds.parentConstraint(joint, jnt)[0]
            cmds.delete(const)
            ikArmJoints.append(jnt)

        # create the wrist end joint
        jnt = cmds.createNode("joint", name="ik_" + ikArmJoints[2] + "_end_jnt")
        const = cmds.parentConstraint(ikArmJoints[2], jnt)[0]
        cmds.delete(const)
        ikArmJoints.append(jnt)

        # create hierarchy
        ikArmJoints.reverse()
        for i in range(len(ikArmJoints)):
            try:
                cmds.parent(ikArmJoints[i], ikArmJoints[i + 1])
            except IndexError:
                pass

        ikArmJoints.reverse()

        cmds.setAttr(ikArmJoints[0] + ".v", 0, lock=True)

        # move hand end joint out a bit. If tx is negative, add -2, if positive, add 2
        cmds.makeIdentity(ikArmJoints[0], t=0, r=1, s=0, apply=True)

        if cmds.getAttr(ikArmJoints[2] + ".tx") > 0:
            cmds.setAttr(ikArmJoints[3] + ".tx", 10)
        else:
            cmds.setAttr(ikArmJoints[3] + ".tx", -10)

        # =======================================================================
        # # connect controls up to blender nodes to drive driver joints
        # =======================================================================
        for joint in joints[1]:
            sourceBone = "ik_" + joint + "_jnt"

            cmds.pointConstraint(sourceBone, "driver_" + joint, mo=True)
            cmds.orientConstraint(sourceBone, "driver_" + joint)

            # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into
            # input 2,and plugs that into driver joint
            if cmds.objExists("master_anim"):
                globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=joint + "_globalScale")
                cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
                cmds.connectAttr(sourceBone + ".scale", globalScaleMult + ".input2")
                riggingUtils.createConstraint(globalScaleMult, "driver_" + joint, "scale", False, 2, slot, "output")
            else:
                riggingUtils.createConstraint(sourceBone, "driver_" + joint, "scale", False, 2, slot)

        # =======================================================================
        # # create fk matching joints
        # =======================================================================
        fkMatchUpArm = cmds.duplicate(ikArmJoints[0], po=True, name="ik_" + joints[1][0] + "_fk_matcher")[0]
        fkMatchLowArm = cmds.duplicate(ikArmJoints[1], po=True, name="ik_" + joints[1][1] + "_fk_matcher")[0]
        fkMatchWrist = cmds.duplicate(ikArmJoints[2], po=True, name="ik_" + joints[1][2] + "_fk_matcher")[0]

        cmds.parent(fkMatchWrist, fkMatchLowArm)
        cmds.parent(fkMatchLowArm, fkMatchUpArm)

        # constrain fk match joints
        cmds.parentConstraint(ikArmJoints[0], fkMatchUpArm, mo=True)
        cmds.parentConstraint(ikArmJoints[1], fkMatchLowArm, mo=True)
        cmds.parentConstraint(ikArmJoints[2], fkMatchWrist, mo=True)

        # =======================================================================
        # # rotate order and preferred angle
        # =======================================================================
        # set rotate order on ikUpArm
        cmds.setAttr(ikArmJoints[0] + ".rotateOrder", 3)

        # set preferred angle on arm
        cmds.setAttr(ikArmJoints[1] + ".preferredAngleZ", -90)

        # =======================================================================
        # # create the ik control
        # =======================================================================
        handControlInfo = riggingUtils.createControlFromMover(joints[1][2], networkNode, True, True)

        cmds.parent(handControlInfo[0], world=True)
        constraint = cmds.orientConstraint(self.name + "_ik_hand_ctrl_orient", handControlInfo[3])[0]
        cmds.delete(constraint)
        cmds.makeIdentity(handControlInfo[2], t=1, r=1, s=1, apply=True)
        cmds.parent(handControlInfo[0], handControlInfo[1])
        cmds.makeIdentity(handControlInfo[0], t=1, r=1, s=1, apply=True)

        # rename the control info
        self.ikHandCtrl = cmds.rename(handControlInfo[0], "ik_" + joints[1][2] + "_anim")
        cmds.rename(handControlInfo[1], self.ikHandCtrl + "_grp")
        cmds.rename(handControlInfo[2], self.ikHandCtrl + "_space_switcher")
        spaceSwitcherFollow = cmds.rename(handControlInfo[3], self.ikHandCtrl + "_space_switcher_follow")

        fkMatchGrp = cmds.group(empty=True, name=self.ikHandCtrl + "_fkMatch_grp")
        constraint = cmds.parentConstraint(fkMatchWrist, fkMatchGrp)[0]
        cmds.delete(constraint)

        cmds.parent(fkMatchGrp, self.ikHandCtrl)

        fkMatch = cmds.group(empty=True, name=self.ikHandCtrl + "_fkMatch")
        constraint = cmds.parentConstraint(fkMatchWrist, fkMatch)[0]
        cmds.delete(constraint)
        cmds.parent(fkMatch, fkMatchGrp)

        # create RP IK on arm and SC ik from wrist to wrist end
        rpIkHandle = \
        cmds.ikHandle(name=self.name + "_rp_arm_ikHandle", solver="ikRPsolver", sj=ikArmJoints[0], ee=ikArmJoints[2])[0]
        scIkHandle = \
        cmds.ikHandle(name=self.name + "_sc_hand_ikHandle", solver="ikSCsolver", sj=ikArmJoints[2], ee=ikArmJoints[3])[
            0]

        cmds.parent(scIkHandle, rpIkHandle)
        cmds.setAttr(rpIkHandle + ".v", 0)
        cmds.setAttr(scIkHandle + ".v", 0)

        cmds.setAttr(rpIkHandle + ".stickiness", 1)
        cmds.setAttr(rpIkHandle + ".snapEnable", 1)

        cmds.setAttr(scIkHandle + ".stickiness", 1)
        cmds.setAttr(scIkHandle + ".snapEnable", 1)

        # parent IK to ik control
        cmds.parent(rpIkHandle, self.ikHandCtrl)

        # =======================================================================
        # # create the ik pole vector
        # =======================================================================
        ikPvCtrl = riggingUtils.createControl("sphere", 5, self.name + "_ik_elbow_anim", True)
        constraint = cmds.pointConstraint(ikArmJoints[1], ikPvCtrl)[0]
        cmds.delete(constraint)

        # create anim grp
        ikPvCtrlGrp = cmds.group(empty=True, name=self.name + "_ik_elbow_anim_grp")
        constraint = cmds.pointConstraint(ikArmJoints[1], ikPvCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(ikPvCtrl, ikPvCtrlGrp)
        cmds.makeIdentity(ikPvCtrl, t=1, r=1, s=1, apply=True)

        # create space switcher
        ikPvSpaceSwitch = cmds.duplicate(ikPvCtrlGrp, po=True, name=self.name + "_ik_elbow_anim_space_switcher")[0]

        # create space switcher follow
        ikPvSpaceSwitchFollow = \
        cmds.duplicate(ikPvCtrlGrp, po=True, name=self.name + "_ik_elbow_anim_space_switcher_follow")[0]

        cmds.parent(ikPvSpaceSwitch, ikPvSpaceSwitchFollow)
        cmds.parent(ikPvCtrlGrp, ikPvSpaceSwitch)

        # move out pv ctrl
        scaleFactor = riggingUtils.getScaleFactor()
        cmds.setAttr(ikPvCtrl + ".ty", 30 * scaleFactor)

        cmds.makeIdentity(ikPvCtrl, t=1, r=1, s=1, apply=True)

        # setup pole vector constraint
        cmds.poleVectorConstraint(ikPvCtrl, rpIkHandle)

        # create the match group
        pvMatchGrp = cmds.group(empty=True, name=ikPvCtrl + "_fkMatchGrp")
        constraint = cmds.parentConstraint(ikPvCtrl, pvMatchGrp)[0]
        cmds.delete(constraint)

        fk_controls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
        cmds.parent(pvMatchGrp, fk_controls[1])

        pvMatch = cmds.group(empty=True, name=ikPvCtrl + "_fkMatch")
        constraint = cmds.parentConstraint(ikPvCtrl, pvMatch)[0]
        cmds.delete(constraint)

        cmds.parent(pvMatch, pvMatchGrp)

        # =======================================================================
        # # setup squash and stretch
        # =======================================================================
        # add attrs to the hand ctrl
        cmds.addAttr(self.ikHandCtrl, longName=("stretch"), at='double', min=0, max=1, dv=0, keyable=True)
        cmds.addAttr(self.ikHandCtrl, longName=("squash"), at='double', min=0, max=1, dv=0, keyable=True)

        # need to get the total length of the arm chain
        totalDist = abs(cmds.getAttr(ikArmJoints[1] + ".tx") + cmds.getAttr(ikArmJoints[2] + ".tx"))

        # create a distanceBetween node
        distBetween = cmds.shadingNode("distanceBetween", asUtility=True, name=self.name + "_ik_arm_distBetween")

        # get world positions of thigh and ik
        baseGrp = cmds.group(empty=True, name=self.name + "_ik_arm_base_grp")
        endGrp = cmds.group(empty=True, name=self.name + "_ik_arm_end_grp")
        cmds.pointConstraint(ikArmJoints[0], baseGrp)
        cmds.pointConstraint(self.ikHandCtrl, endGrp)

        # hook in group translates into distanceBetween node inputs
        cmds.connectAttr(baseGrp + ".translate", distBetween + ".point1")
        cmds.connectAttr(endGrp + ".translate", distBetween + ".point2")

        # create a condition node that will compare original length to current length
        # if second term is greater than, or equal to the first term, the chain needs to stretch
        ikArmCondition = cmds.shadingNode("condition", asUtility=True, name=self.name + "_ik_arm_stretch_condition")
        cmds.setAttr(ikArmCondition + ".operation", 3)
        cmds.connectAttr(distBetween + ".distance", ikArmCondition + ".secondTerm")
        cmds.setAttr(ikArmCondition + ".firstTerm", totalDist)

        # hook up the condition node's return colors
        cmds.setAttr(ikArmCondition + ".colorIfTrueR", totalDist)
        cmds.connectAttr(distBetween + ".distance", ikArmCondition + ".colorIfFalseR")

        # add attr to foot control for stretch bias
        cmds.addAttr(self.ikHandCtrl, ln="stretchBias", minValue=-1.0, maxValue=1.0, defaultValue=0.0, keyable=True)

        # add divide node so that instead of driving 0-1, we're actually only driving 0 - 0.2
        divNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_stretchBias_Div")
        cmds.connectAttr(self.ikHandCtrl + ".stretchBias", divNode + ".input1X")
        cmds.setAttr(divNode + ".operation", 2)
        cmds.setAttr(divNode + ".input2X", 5)

        # create the add node and connect the stretchBias into it, adding 1
        addNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=self.name + "_stretchBias_Add")
        cmds.connectAttr(divNode + ".outputX", addNode + ".input1D[0]")
        cmds.setAttr(addNode + ".input1D[1]", 1.0)

        # connect output of addNode to new mult node input1x
        stretchBiasMultNode = cmds.shadingNode("multiplyDivide", asUtility=True,
                                               name=self.name + "_stretchBias_multNode")
        cmds.connectAttr(addNode + ".output1D", stretchBiasMultNode + ".input1X")

        # create the mult/divide node(set to divide) that will take the original creation length as a static value in
        # input2x,and the connected length into 1x. This will get the scale factor
        armDistMultNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_arm_dist_multNode")
        cmds.setAttr(armDistMultNode + ".operation", 2)  # divide
        cmds.connectAttr(ikArmCondition + ".outColorR", armDistMultNode + ".input1X")

        # set input2x to totalDist
        cmds.setAttr(stretchBiasMultNode + ".input2X", totalDist)
        cmds.connectAttr(stretchBiasMultNode + ".outputX", armDistMultNode + ".input2X")

        # This differs from the original code. Instead of using a condition, I will use a blendColors node so that
        # stretch % has an effect

        # create a blendColors node for stretch
        blendResult = cmds.shadingNode("blendColors", asUtility=True, name=self.name + "_arm_stretch_scaleFactor")
        cmds.setAttr(blendResult + ".color2R", 1)
        cmds.connectAttr(armDistMultNode + ".outputX", blendResult + ".color1R")
        cmds.connectAttr(self.ikHandCtrl + ".stretch", blendResult + ".blender")

        # create a blendColors node for squash
        blendResultSquash = cmds.shadingNode("blendColors", asUtility=True, name=self.name + "_arm_squash_scaleFactor")
        cmds.setAttr(blendResultSquash + ".color2R", 1)
        cmds.connectAttr(armDistMultNode + ".outputX", blendResultSquash + ".color1R")
        cmds.connectAttr(self.ikHandCtrl + ".squash", blendResultSquash + ".blender")

        # get the sqrt of the scale factor by creating a multiply node and setting it to power operation
        powerNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_sqrt_scaleFactor")
        cmds.setAttr(powerNode + ".operation", 3)
        cmds.connectAttr(blendResultSquash + ".outputR", powerNode + ".input1X")
        cmds.setAttr(powerNode + ".input2X", .5)

        # now divide 1 by that result
        squashDivNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_squash_Value")
        cmds.setAttr(squashDivNode + ".operation", 2)
        cmds.setAttr(squashDivNode + ".input1X", 1)
        cmds.connectAttr(powerNode + ".outputX", squashDivNode + ".input2X")

        # connect to arm joint scale attributes
        cmds.connectAttr(blendResult + ".outputR", ikArmJoints[0] + ".sx")
        cmds.connectAttr(blendResult + ".outputR", ikArmJoints[1] + ".sx")

        cmds.connectAttr(squashDivNode + ".outputX", ikArmJoints[1] + ".sy")
        cmds.connectAttr(squashDivNode + ".outputX", ikArmJoints[1] + ".sz")

        cmds.connectAttr(squashDivNode + ".outputX", ikArmJoints[0] + ".sy")
        cmds.connectAttr(squashDivNode + ".outputX", ikArmJoints[0] + ".sz")

        # =======================================================================
        # # color controls and lock attrs
        # =======================================================================
        for control in [self.ikHandCtrl, ikPvCtrl]:
            riggingUtils.colorControl(control)

        for attr in [".scaleX", ".scaleY", ".globalScale", ".visibility"]:
            cmds.setAttr(self.ikHandCtrl + attr, lock=True, keyable=False)

        for attr in [".scaleX", ".scaleY", ".scaleZ", ".rotateX", ".rotateY", ".rotateZ", ".visibility"]:
            cmds.setAttr(ikPvCtrl + attr, lock=True, keyable=False)

        # =======================================================================
        # # clean up IK nodes
        # =======================================================================
        self.ikCtrlGrp = cmds.group(empty=True, name=self.name + "_arm_ik_ctrls_grp")
        cmds.parent(self.ikCtrlGrp, self.armGroup)

        cmds.parent(ikPvSpaceSwitchFollow, self.ikCtrlGrp)
        cmds.parent(spaceSwitcherFollow, self.ikCtrlGrp)
        cmds.parent(fkMatchUpArm, self.ikCtrlGrp)

        cmds.parent(baseGrp, self.ikCtrlGrp)
        cmds.parent(endGrp, self.ikCtrlGrp)

        # add created control info to module
        ikRigData = [self.ikHandCtrl, ikPvCtrl]
        if not cmds.objExists(networkNode + ".ikControls"):
            cmds.addAttr(networkNode, ln="ikControls", dt="string")
        jsonString = json.dumps(ikRigData)
        cmds.setAttr(networkNode + ".ikControls", jsonString, type="string")

        # update progress
        if textEdit != None:
            textEdit.setTextColor(QtGui.QColor(0, 255, 18))
            textEdit.append("        SUCCESS: IK Build Complete!")
            textEdit.setTextColor(QtGui.QColor(255, 255, 255))

        return ikArmJoints

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildFingers(self, fingers, textEdit, uiInst, builtRigs, networkNode):

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # create groups
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        armJoints = self.getMainArmJoints()
        fkFingerCtrlsGrp = cmds.group(empty=True, name=self.name + "_fk_finger_ctrls")
        const = cmds.parentConstraint(armJoints[1][2], fkFingerCtrlsGrp)[0]
        cmds.delete(const)

        handDrivenMasterGrp = cmds.duplicate(fkFingerCtrlsGrp, po=True, name=self.name + "_hand_driven_master_grp")
        handDrivenGrp = cmds.duplicate(fkFingerCtrlsGrp, po=True, name=self.name + "_hand_driven_grp")

        cmds.parent(handDrivenMasterGrp, self.fingerGrp)
        cmds.parent(handDrivenGrp, handDrivenMasterGrp)
        cmds.parent(fkFingerCtrlsGrp, handDrivenGrp)

        # setup constraints/sdks on handDrivenGrp
        const = cmds.parentConstraint("driver_" + armJoints[1][2], handDrivenGrp)

        fkRigInfo = []

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # create metacarpal controls
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        metaCarpals = []
        phalanges = []
        for each in fingers:
            if each[0].find("metacarpal") != -1:
                if each[0].find("thumb") == -1:
                    metaCarpals.append(each[0])

            fingerData = []
            for finger in each:
                if finger.find("metacarpal") == -1:
                    if each[0].find("thumb") == -1:
                        fingerData.append(finger)

            for finger in each:
                if finger.find("thumb") != -1:
                    fingerData.append(finger)

            phalanges.append(fingerData)

        for metacarpal in metaCarpals:
            data = riggingUtils.createControlFromMover(metacarpal, networkNode, True, False)
            ctrl = cmds.rename(data[0], metacarpal + "_anim")
            grp = cmds.rename(data[1], metacarpal + "_anim_grp")
            cmds.parent(grp, handDrivenGrp)

            # color the control
            riggingUtils.colorControl(ctrl)
            fkRigInfo.append(ctrl)

            for attr in [".scaleX", ".scaleY", ".scaleZ", ".visibility"]:
                cmds.setAttr(ctrl + attr, lock=True, keyable=False)

        # first create a group for the IK handles to go into

        ikHandlesGrp = cmds.group(empty=True, name=self.name + "_fkOrient_ikHandles_grp")
        cmds.parent(ikHandlesGrp, handDrivenGrp)

        # setup constraints
        const = cmds.parentConstraint([handDrivenGrp[0], self.fingerGrp], ikHandlesGrp)[0]

        # add attr (globalStick)
        cmds.addAttr(self.armSettings, ln="globalSticky", dv=0, min=0, max=1, keyable=True)

        # set driven keys
        cmds.setAttr(self.armSettings + ".globalSticky", 0)
        cmds.setAttr(const + "." + handDrivenGrp[0] + "W0", 1)
        cmds.setAttr(const + "." + self.fingerGrp + "W1", 0)
        cmds.setDrivenKeyframe([const + "." + handDrivenGrp[0] + "W0", const + "." + self.fingerGrp + "W1"],
                               cd=self.armSettings + ".globalSticky", itt='linear', ott='linear')

        cmds.setAttr(self.armSettings + ".globalSticky", 1)
        cmds.setAttr(const + "." + handDrivenGrp[0] + "W0", 0)
        cmds.setAttr(const + "." + self.fingerGrp + "W1", 1)
        cmds.setDrivenKeyframe([const + "." + handDrivenGrp[0] + "W0", const + "." + self.fingerGrp + "W1"],
                               cd=self.armSettings + ".globalSticky", itt='linear', ott='linear')

        cmds.setAttr(self.armSettings + ".globalSticky", 0)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # create the FK orient joints
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        fkOrients = []

        for each in phalanges:
            if len(each) > 0:

                # find tip locator name
                nameData = self.returnPrefixSuffix
                splitString = each[0]
                if nameData[0] != None:
                    splitString = each[0].partition(nameData[0])[2]

                if nameData[1] != None:
                    splitString = splitString.partition(nameData[1])[0]

                splitString = splitString.partition("_")[0]
                tipLoc = self.name + "_" + splitString + "_tip"

                # create base and end joints
                baseJnt = cmds.createNode('joint', name="fk_orient_" + each[0] + "_jnt")
                const = cmds.parentConstraint(each[0], baseJnt)[0]
                cmds.delete(const)

                endJnt = cmds.createNode('joint', name="fk_orient_" + each[0] + "_end")
                const = cmds.parentConstraint(tipLoc, endJnt)[0]
                cmds.delete(const)

                cmds.parent(endJnt, baseJnt)
                cmds.makeIdentity(baseJnt, t=0, r=1, s=0, apply=True)
                cmds.setAttr(baseJnt + ".v", 0, lock=True)

                # create SC ik handles for each chain
                ikNodes = cmds.ikHandle(sol="ikSCsolver", name=baseJnt + "_ikHandle", sj=baseJnt, ee=endJnt)[0]
                cmds.parent(ikNodes, ikHandlesGrp)
                cmds.setAttr(ikNodes + ".v", 0)

                # parent orient joint to metacarpal control if it exists
                jntBaseName = self.getFingerBaseName(each[0]).partition("_")[0]
                metaCtrl = ""
                for each in metaCarpals:
                    if each.find(jntBaseName) != -1:
                        metaCtrl = each + "_anim"

                if cmds.objExists(metaCtrl):
                    cmds.parent(baseJnt, metaCtrl)
                    fkOrients.append(baseJnt)
                else:
                    fkOrients.append(baseJnt)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # create FK controls for the phalanges
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        fkInfo = []
        for each in phalanges:
            fingerData = []

            for finger in each:
                # create the FK control/anim grp/driven grp
                data = riggingUtils.createControlFromMover(finger, networkNode, True, False)
                ctrl = cmds.rename(data[0], finger + "_anim")
                grp = cmds.rename(data[1], finger + "_anim_grp")
                drivenGrp = cmds.group(empty=True, name=finger + "_driven_grp")
                const = cmds.parentConstraint(grp, drivenGrp)[0]
                cmds.delete(const)

                fkInfo.append([ctrl, finger])
                fkRigInfo.append(ctrl)

                # setup hierarchy
                cmds.parent(drivenGrp, grp)
                cmds.parent(ctrl, drivenGrp)

                cmds.makeIdentity(drivenGrp, t=1, r=1, s=1, apply=True)
                fingerData.append(ctrl)

                # color control
                riggingUtils.colorControl(ctrl)

                # lock attrs on ctrl
                cmds.setAttr(ctrl + ".v", lock=True, keyable=False)
                cmds.aliasAttr(ctrl + ".sz", rm=True)

            fingerData.reverse()

            for i in range(len(fingerData)):
                try:
                    cmds.parent(fingerData[i] + "_grp", fingerData[i + 1])
                except IndexError:
                    pass

            fingerData.reverse()

            # parent FK control to metacarpal control if it exists
            jntBaseName = self.getFingerBaseName(each[0]).partition("_")[0]
            metaCtrl = ""
            for each in metaCarpals:
                if each.find(jntBaseName) != -1:
                    metaCtrl = each + "_anim"

            jntName = fingerData[0].partition("_anim")[0]
            baseJnt = "fk_orient_" + jntName + "_jnt"

            # parent the control to the meta control or to the fk finger controls group
            if cmds.objExists(metaCtrl):
                if metaCtrl.find("thumb") == -1:
                    cmds.parent(fingerData[0] + "_grp", metaCtrl)
                else:
                    cmds.parent(fingerData[0] + "_grp", fkFingerCtrlsGrp)
                    cmds.parent(baseJnt, fkFingerCtrlsGrp)

            else:
                cmds.parent(fingerData[0] + "_grp", fkFingerCtrlsGrp)
                cmds.parent(baseJnt, fkFingerCtrlsGrp)

            # add sticky attribute
            if fingerData[0].find("thumb") == -1:
                cmds.addAttr(fingerData[0], ln="sticky", defaultValue=0, minValue=0, maxValue=1, keyable=True)

            # setup the constraint between the fk finger orient joint and the ctrlGrp

            if metaCtrl == '':
                masterObj = fkFingerCtrlsGrp
            else:
                masterObj = metaCtrl

            constraint = cmds.parentConstraint([masterObj, baseJnt], fingerData[0] + "_grp", mo=True)[0]

            # set driven keyframes on constraint
            if cmds.objExists(fingerData[0] + ".sticky"):
                cmds.setAttr(fingerData[0] + ".sticky", 1)
                cmds.setAttr(constraint + "." + masterObj + "W0", 0)
                cmds.setAttr(constraint + "." + baseJnt + "W1", 1)
                cmds.setDrivenKeyframe([constraint + "." + masterObj + "W0", constraint + "." + baseJnt + "W1"],
                                       cd=fingerData[0] + ".sticky", itt="linear", ott="linear")

                cmds.setAttr(fingerData[0] + ".sticky", 0)
                cmds.setAttr(constraint + "." + masterObj + "W0", 1)
                cmds.setAttr(constraint + "." + baseJnt + "W1", 0)
                cmds.setDrivenKeyframe([constraint + "." + masterObj + "W0", constraint + "." + baseJnt + "W1"],
                                       cd=fingerData[0] + ".sticky", itt="linear", ott="linear")

        # write FK data to network node
        if len(fkRigInfo) > 0:
            if not cmds.objExists(networkNode + ".fkFingerControls"):
                cmds.addAttr(networkNode, ln="fkFingerControls", dt='string')

            jsonString = json.dumps(fkRigInfo)
            cmds.setAttr(networkNode + ".fkFingerControls", jsonString, type="string")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # setup hand roll
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create our 4 locators(pivots) and position
        pinkyPiv = cmds.spaceLocator(name=self.name + "_hand_pinky_pivot")[0]
        thumbPiv = cmds.spaceLocator(name=self.name + "_hand_thumb_pivot")[0]
        midPiv = cmds.spaceLocator(name=self.name + "_hand_mid_pivot")[0]
        tipPiv = cmds.spaceLocator(name=self.name + "_hand_tip_pivot")[0]

        for piv in [pinkyPiv, thumbPiv, midPiv, tipPiv]:
            cmds.setAttr(piv + ".v", 0)

        # posititon locators

        const = cmds.parentConstraint(self.name + "_pinky_pivot", pinkyPiv)[0]
        cmds.delete(const)
        const = cmds.parentConstraint(self.name + "_thumb_pivot", thumbPiv)[0]
        cmds.delete(const)
        const = cmds.parentConstraint(self.name + "_palm_pivot", midPiv)[0]
        cmds.delete(const)
        const = cmds.parentConstraint(self.name + "_middle_tip", tipPiv)[0]
        cmds.delete(const)

        # create the control groups for the pivots so our values are zeroed
        for each in [pinkyPiv, thumbPiv, midPiv, tipPiv]:
            group = cmds.group(empty=True, name=each + "_grp")
            constraint = cmds.parentConstraint(each, group)[0]
            cmds.delete(constraint)
            cmds.parent(each, group)

        # setup hierarchy
        cmds.parent(thumbPiv + "_grp", pinkyPiv)
        cmds.parent(tipPiv + "_grp", thumbPiv)
        cmds.parent(midPiv + "_grp", tipPiv)

        # parent the arm IK handles under the midPiv locator
        cmds.parent(self.name + "_rp_arm_ikHandle", midPiv)
        cmds.parent(pinkyPiv + "_grp", self.ikHandCtrl)

        # add attrs to the IK hand control (side, roll, tip pivot)
        cmds.addAttr(self.ikHandCtrl, longName="side", defaultValue=0, keyable=True)
        cmds.addAttr(self.ikHandCtrl, longName="mid_bend", defaultValue=0, keyable=True)
        cmds.addAttr(self.ikHandCtrl, longName="mid_swivel", defaultValue=0, keyable=True)
        cmds.addAttr(self.ikHandCtrl, longName="tip_pivot", defaultValue=0, keyable=True)
        cmds.addAttr(self.ikHandCtrl, longName="tip_swivel", defaultValue=0, keyable=True)

        # hook up attrs to pivot locators
        cmds.connectAttr(self.ikHandCtrl + ".mid_bend", midPiv + ".rz")
        cmds.connectAttr(self.ikHandCtrl + ".tip_pivot", tipPiv + ".rz")

        cmds.connectAttr(self.ikHandCtrl + ".mid_swivel", midPiv + ".ry")
        cmds.connectAttr(self.ikHandCtrl + ".tip_swivel", tipPiv + ".ry")

        # set driven keys for side to side attr

        cmds.setAttr(self.ikHandCtrl + ".side", 0)
        cmds.setAttr(pinkyPiv + ".rx", 0)
        cmds.setAttr(thumbPiv + ".rx", 0)
        cmds.setDrivenKeyframe([pinkyPiv + ".rx", thumbPiv + ".rx"], cd=self.ikHandCtrl + ".side", itt='linear',
                               ott='linear')

        cmds.setAttr(self.ikHandCtrl + ".side", 180)
        cmds.setAttr(pinkyPiv + ".rx", -180)
        cmds.setAttr(thumbPiv + ".rx", 0)
        cmds.setDrivenKeyframe([pinkyPiv + ".rx", thumbPiv + ".rx"], cd=self.ikHandCtrl + ".side", itt='linear',
                               ott='linear')

        cmds.setAttr(self.ikHandCtrl + ".side", -180)
        cmds.setAttr(pinkyPiv + ".rx", 0)
        cmds.setAttr(thumbPiv + ".rx", 180)
        cmds.setDrivenKeyframe([pinkyPiv + ".rx", thumbPiv + ".rx"], cd=self.ikHandCtrl + ".side", itt='linear',
                               ott='linear')

        cmds.setAttr(self.ikHandCtrl + ".side", 0)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # setup ik fingers (if applicable)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        scaleFactor = riggingUtils.getScaleFactor()
        ikInfo = []
        ikCtrlData = []

        for each in phalanges:
            if len(each) == 3:
                ikJnts = []
                pvGrps = []

                # create the IK finger joints
                for bone in each:
                    jnt = cmds.createNode('joint', name="ik_" + bone + "_jnt")
                    const = cmds.parentConstraint(bone, jnt)[0]
                    cmds.delete(const)
                    ikJnts.append(jnt)

                # parent ik joints
                ikJnts.reverse()
                for i in range(len(ikJnts)):
                    try:
                        cmds.parent(ikJnts[i], ikJnts[i + 1])
                    except IndexError:
                        pass

                # create the ik tip jnt
                jnt = cmds.createNode('joint', name=ikJnts[0] + "_tip")

                # find tip locator name
                nameData = self.returnPrefixSuffix
                splitString = each[0]
                if nameData[0] != None:
                    splitString = each[0].partition(nameData[0])[2]

                if nameData[1] != None:
                    splitString = splitString.partition(nameData[1])[0]

                jntType = splitString.partition("_")[0]
                tipLoc = self.name + "_" + jntType + "_tip"

                const = cmds.parentConstraint(tipLoc, jnt)[0]
                cmds.delete(const)

                cmds.parent(jnt, ikJnts[0])
                ikJnts.reverse()
                ikJnts.append(jnt)

                cmds.makeIdentity(ikJnts[0], t=0, r=1, s=0, apply=True)

                # parent the ik to the handDrivenGrp
                cmds.parent(ikJnts[0], handDrivenGrp)
                cmds.setAttr(ikJnts[0] + ".v", 0, lock=True)

                # create the IK
                ikNodes = \
                cmds.ikHandle(sol="ikRPsolver", name=self.name + jntType + "_ikHandle", sj=ikJnts[0], ee=ikJnts[2])[0]
                ikTipNodes = \
                cmds.ikHandle(sol="ikSCsolver", name=self.name + jntType + "_tip_ikHandle", sj=ikJnts[2], ee=ikJnts[3])[
                    0]
                cmds.setAttr(ikNodes + ".v", 0)
                cmds.parent(ikTipNodes, ikNodes)

                # create the IK PV
                poleVector = cmds.spaceLocator(name=self.name + "_" + jntType + "_pv_anim")[0]
                constraint = cmds.parentConstraint(ikJnts[1], poleVector)[0]
                cmds.delete(constraint)
                riggingUtils.colorControl(poleVector)

                # create a pole vector group
                pvGrp = cmds.group(empty=True, name=poleVector + "_grp")
                constraint = cmds.parentConstraint(poleVector, pvGrp)[0]
                cmds.delete(constraint)
                pvGrps.append(pvGrp)

                # parent to the joint, and move out away from finger
                cmds.parent(poleVector, ikJnts[1])

                if cmds.getAttr(networkNode + ".side") == "Left":
                    cmds.setAttr(poleVector + ".ty", -40 * scaleFactor)

                if cmds.getAttr(networkNode + ".side") == "Right":
                    cmds.setAttr(poleVector + ".ty", 40 * scaleFactor)

                cmds.makeIdentity(poleVector, t=1, r=1, s=1, apply=True)
                cmds.parent(poleVector, pvGrp, absolute=True)
                cmds.makeIdentity(poleVector, t=1, r=1, s=1, apply=True)

                # create the IK finger controls
                data = riggingUtils.createControlFromMover(each[2], networkNode, True, True)
                ikFingerCtrl = cmds.rename(data[0], each[2] + "_ik_anim")
                ikFingerGrp = cmds.rename(data[1], each[2] + "_ik_anim_grp")
                spaceSwitcher = cmds.rename(data[2], each[2] + "_ik_anim_space_switcher")
                spaceFollow = cmds.rename(data[3], each[2] + "_ik_anim_space_switcher_follow")
                riggingUtils.colorControl(ikFingerCtrl)
                ikCtrlData.append(ikFingerCtrl)
                ikCtrlData.append(poleVector)

                # parent ik to ctrl
                cmds.parent(ikNodes, ikFingerCtrl)

                # create the PV constraint
                cmds.poleVectorConstraint(poleVector, ikNodes)

                # add attr to show pole vector control
                cmds.addAttr(ikFingerCtrl, longName="poleVectorVis", defaultValue=0, minValue=0, maxValue=1,
                             keyable=True)
                cmds.connectAttr(ikFingerCtrl + ".poleVectorVis", poleVector + ".v")

                for group in pvGrps:
                    cmds.parent(group, handDrivenGrp)

                # create the global IK control
                if not cmds.objExists(armJoints[1][2] + "_global_ik_anim"):
                    globalIkAnim = riggingUtils.createControl("square", 30, armJoints[1][2] + "_global_ik_anim", True)
                    riggingUtils.colorControl(globalIkAnim)

                    const = cmds.pointConstraint(midPiv, globalIkAnim)[0]
                    cmds.delete(const)

                    globalIkGrp = cmds.group(empty=True, name=globalIkAnim + "_grp")
                    const = cmds.pointConstraint(midPiv, globalIkGrp)[0]
                    cmds.delete(const)
                    const = cmds.orientConstraint(self.ikHandCtrl, globalIkGrp)[0]
                    cmds.delete(const)

                    cmds.parent(globalIkAnim, globalIkGrp)
                    cmds.makeIdentity(globalIkAnim, t=1, r=1, s=1, apply=True)

                    # translate down in z
                    cmds.setAttr(globalIkAnim + ".tz", -5)
                    cmds.makeIdentity(globalIkAnim, t=1, r=1, s=1, apply=True)

                    # reposition the grp to the control
                    cmds.parent(globalIkAnim, world=True)
                    constraint = cmds.pointConstraint(globalIkAnim, globalIkGrp)[0]
                    cmds.delete(constraint)

                    cmds.parent(globalIkAnim, globalIkGrp)
                    cmds.makeIdentity(globalIkAnim, t=1, r=1, s=1, apply=True)

                    # create a space switcher grp
                    globalIKSpaceFollow = \
                    cmds.duplicate(globalIkGrp, po=True, name=globalIkAnim + "_space_switcher_follow")[0]
                    globalIKSpaceSwitch = cmds.duplicate(globalIkGrp, po=True, name=globalIkAnim + "_space_switcher")[0]

                    globalMasterGrp = cmds.group(empty=True, name=self.name + "_global_finger_ik_grp")
                    const = cmds.parentConstraint(armJoints[1][2], globalMasterGrp)[0]
                    cmds.delete(const)

                    cmds.parent(globalIKSpaceSwitch, globalIKSpaceFollow)
                    cmds.parent(globalIkGrp, globalIKSpaceSwitch)
                    cmds.parent(globalIKSpaceFollow, globalMasterGrp)
                    cmds.parent(globalMasterGrp, self.fingerGrp)
                    cmds.parentConstraint("driver_" + armJoints[1][2], globalMasterGrp, mo=True)

                    # add global ctrl visibility attr
                    cmds.addAttr(self.armSettings, ln="globalIkVis", dv=0, min=0, max=1, keyable=True)
                    shape = cmds.listRelatives(globalIkAnim, shapes=True)[0]
                    cmds.connectAttr(self.armSettings + ".globalIkVis", shape + ".v")

                    ikCtrlData.append(globalIkAnim)

                # parent ik control grps to this global control
                cmds.parent(spaceFollow, globalIkAnim)

                # collect data per finger
                ikInfo.append([globalIKSpaceFollow, globalIkAnim, ikJnts, jntType, spaceFollow, pvGrp])

        # write IK data to network node
        if len(ikCtrlData) > 0:
            if not cmds.objExists(networkNode + ".ikFingerControls"):
                cmds.addAttr(networkNode, ln="ikFingerControls", dt='string')

            jsonString = json.dumps(ikCtrlData)
            cmds.setAttr(networkNode + ".ikFingerControls", jsonString, type="string")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # setup finger modes/driven keys
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for each in ikInfo:
            fkCtrl = each[2][0].partition("ik_")[2].rpartition("_jnt")[0] + "_anim_grp"
            cmds.addAttr(self.armSettings, ln=each[3] + "_finger_mode", dv=0, min=0, max=1, keyable=True)

            cmds.setAttr(self.armSettings + "." + each[3] + "_finger_mode", 0)
            cmds.setAttr(each[4] + ".v", 0)
            cmds.setAttr(each[5] + ".v", 0)
            cmds.setAttr(fkCtrl + ".v", 1)
            cmds.setDrivenKeyframe([each[4] + ".v", each[5] + ".v", fkCtrl + ".v"],
                                   cd=self.armSettings + "." + each[3] + "_finger_mode", itt='linear', ott='linear')

            cmds.setAttr(self.armSettings + "." + each[3] + "_finger_mode", 1)
            cmds.setAttr(each[4] + ".v", 1)
            cmds.setAttr(each[5] + ".v", 1)
            cmds.setAttr(fkCtrl + ".v", 0)
            cmds.setDrivenKeyframe([each[4] + ".v", each[5] + ".v", fkCtrl + ".v"],
                                   cd=self.armSettings + "." + each[3] + "_finger_mode", itt='linear', ott='linear')

            cmds.setAttr(self.armSettings + "." + each[3] + "_finger_mode", 0)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # parent IK finger joints under metacarpals (if they exist)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for each in ikInfo:
            metaCtrl = ""
            jntBaseName = self.getFingerBaseName(each[2][0]).partition("_")[0]
            for carpal in metaCarpals:
                if carpal.find(jntBaseName) != -1:
                    metaCtrl = carpal + "_anim"

            if cmds.objExists(metaCtrl):
                cmds.parent(each[2][0], metaCtrl)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # Hook up driver joints
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for each in fkInfo:
            fkCtrl = each[0]
            jnt = each[1]
            ikJnt = "ik_" + jnt + "_jnt"
            driverJnt = "driver_" + jnt

            # find joint base name
            nameData = self.returnPrefixSuffix
            splitString = jnt
            if nameData[0] != None:
                splitString = jnt.partition(nameData[0])[2]

            if nameData[1] != None:
                splitString = splitString.partition(nameData[1])[0]

            jntBaseName = splitString.partition("_")[0]

            if cmds.objExists(ikJnt):
                pConst = cmds.parentConstraint([fkCtrl, ikJnt], driverJnt, mo=True)[0]

                # set driven keys
                cmds.setAttr(self.armSettings + "." + jntBaseName + "_finger_mode", 0)
                cmds.setAttr(pConst + "." + fkCtrl + "W0", 1)
                cmds.setAttr(pConst + "." + ikJnt + "W1", 0)
                cmds.setDrivenKeyframe([pConst + "." + fkCtrl + "W0", pConst + "." + ikJnt + "W1"],
                                       cd=self.armSettings + "." + jntBaseName + "_finger_mode", itt='linear',
                                       ott='linear')

                cmds.setAttr(self.armSettings + "." + jntBaseName + "_finger_mode", 1)
                cmds.setAttr(pConst + "." + fkCtrl + "W0", 0)
                cmds.setAttr(pConst + "." + ikJnt + "W1", 1)
                cmds.setDrivenKeyframe([pConst + "." + fkCtrl + "W0", pConst + "." + ikJnt + "W1"],
                                       cd=self.armSettings + "." + jntBaseName + "_finger_mode", itt='linear',
                                       ott='linear')

                cmds.setAttr(self.armSettings + "." + jntBaseName + "_finger_mode", 0)

                # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale
                # into input 2, and plugs that into driver joint
                slot = 0
                for each in [fkCtrl, ikJnt]:
                    if cmds.objExists("master_anim"):
                        globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=jnt + "_globalScale")
                        cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
                        cmds.connectAttr(each + ".scale", globalScaleMult + ".input2")
                        riggingUtils.createConstraint(globalScaleMult, "driver_" + jnt, "scale", False, 2, slot,
                                                      "output")
                    else:
                        riggingUtils.createConstraint(each, "driver_" + jnt, "scale", False, 2, slot)

                    slot = slot + 1

            else:
                pConst = cmds.parentConstraint(fkCtrl, driverJnt)[0]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getMainArmJoints(self):

        clavicleJoint = None
        upperarmJoint = None
        lowerarmJoint = None
        handJoint = None

        returnData = []

        joints = self.returnCreatedJoints

        # clavicle
        for joint in joints:
            if joint.find("clavicle") != -1:
                clavicleJoint = joint

        # upperarm
        joints = self.returnCreatedJoints
        for joint in joints:
            if joint.find("upperarm") != -1:
                if joint.find("twist") == -1:
                    upperarmJoint = joint

        # lowerarm
        for joint in joints:
            if joint.find("lowerarm") != -1:
                if joint.find("twist") == -1:
                    lowerarmJoint = joint

        # hand
        for joint in joints:
            if joint.find("hand") != -1:
                handJoint = joint

        returnData = [clavicleJoint, [upperarmJoint, lowerarmJoint, handJoint]]
        return returnData

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getTwistJoints(self, upperarm, lowerarm):

        upperTwistBones = []
        lowerTwistBones = []

        joints = self.returnCreatedJoints

        # upper arm
        for joint in joints:
            if joint.find("upperarm") != -1:
                if joint.find("twist") != -1:
                    upperTwistBones.append(joint)

        # calf
        for joint in joints:
            if joint.find("lowerarm") != -1:
                if joint.find("twist") != -1:
                    lowerTwistBones.append(joint)

        if upperarm:
            return upperTwistBones
        if lowerarm:
            return lowerTwistBones

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getFingerJoints(self):

        joints = self.returnCreatedJoints
        indexJoints = []
        middleJoints = []
        ringJoints = []
        pinkyJoints = []
        thumbJoints = []

        for joint in joints:

            if joint.find("thumb") != -1:
                thumbJoints.append(joint)

            if joint.find("index") != -1:
                indexJoints.append(joint)

            if joint.find("middle") != -1:
                if joint.find("index") == -1:
                    if joint.find("ring") == -1:
                        if joint.find("pinky") == -1:
                            middleJoints.append(joint)

            if joint.find("ring") != -1:
                ringJoints.append(joint)

            if joint.find("pinky") != -1:
                pinkyJoints.append(joint)

        returnData = []
        for each in [indexJoints, middleJoints, ringJoints, pinkyJoints, thumbJoints]:
            if each != []:
                returnData.append(each)
        return returnData

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getFingerBaseName(self, finger):

        nameData = self.returnPrefixSuffix
        if nameData[0] != None:
            if nameData[1] != None:
                jointName = finger.partition(nameData[0] + "_")[2].partition("_" + nameData[1])[0]
            else:
                jointName = finger.partition(nameData[0] + "_")[2]
        else:
            if nameData[1] != None:
                jointName = finger.partition("_" + nameData[1])[0]
            else:
                jointName = finger.partition("_")[0]

        return jointName

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def switchClavMode(self, mode, checkBox, range=False):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")
        controls = json.loads(cmds.getAttr(networkNode + ".clavControls"))

        # are we matching?
        if not range:
            match = checkBox.isChecked()
        else:
            match = True

        # if being called from match over frame range
        if range:
            if mode == matchData[1][0]:
                mode = "FK"
            if mode == matchData[1][1]:
                mode = "IK"

        if mode == "FK":

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.clavMode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.clavMode")

            if match:
                dupe = cmds.duplicate(namespace + ":" + controls[0], rr=True, po=True)[0]
                const = cmds.orientConstraint(namespace + ":" + self.name + "_clav_ik_start", dupe)[0]
                cmds.delete(const)

                rotateXvalue = cmds.getAttr(dupe + ".rotateX")
                rotateYvalue = cmds.getAttr(dupe + ".rotateY")
                rotateZvalue = cmds.getAttr(dupe + ".rotateZ")

                cmds.setAttr(namespace + ":" + controls[0] + ".rotateX", rotateXvalue)
                cmds.setAttr(namespace + ":" + controls[0] + ".rotateY", rotateYvalue)
                cmds.setAttr(namespace + ":" + controls[0] + ".rotateZ", rotateZvalue)

                cmds.setKeyframe(namespace + ":" + controls[0])

                cmds.delete(dupe)
                cmds.setAttr(namespace + ":" + self.name + "_settings.clavMode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.clavMode")

        if mode == "IK":

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.clavMode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.clavMode")

            if match:
                dupe = cmds.duplicate(namespace + ":" + controls[1], rr=True)[0]
                const = cmds.pointConstraint(namespace + ":" + self.name + "_ik_clav_matcher", dupe)[0]
                cmds.delete(const)

                transXvalue = cmds.getAttr(dupe + ".translateX")
                transYvalue = cmds.getAttr(dupe + ".translateY")
                transZvalue = cmds.getAttr(dupe + ".translateZ")

                cmds.setAttr(namespace + ":" + controls[1] + ".translateX", transXvalue)
                cmds.setAttr(namespace + ":" + controls[1] + ".translateY", transYvalue)
                cmds.setAttr(namespace + ":" + controls[1] + ".translateZ", transZvalue)

                cmds.setKeyframe(namespace + ":" + controls[1])

                cmds.delete(dupe)

                cmds.setAttr(namespace + ":" + self.name + "_settings.clavMode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.clavMode")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def switchMode(self, mode, checkBox, range=False):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        # are we matching?
        if not range:
            match = checkBox.isChecked()
        else:
            match = True

        # if being called from match over frame range
        if range:
            if mode == matchData[1][0]:
                mode = "FK"
            if mode == matchData[1][1]:
                mode = "IK"

        # switch to FK mode
        if mode == "FK":
            # get current mode
            currentMode = cmds.getAttr(namespace + ":" + self.name + "_settings.mode")
            if currentMode == 0.0:
                cmds.warning("Already in FK mode.")
                return

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

            if match:
                # get fk controls
                controls = json.loads(cmds.getAttr(networkNode + ".fkControls"))

                # create a duplicate chain
                topCtrl = controls[2]
                topGrp = cmds.listRelatives(namespace + ":" + topCtrl, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # match the fk controls to the corresponding joint
                controls.reverse()
                for control in controls:
                    joint = control.partition("fk_")[2].partition("_anim")[0]
                    joint = namespace + ":" + joint

                    constraint = cmds.parentConstraint(joint, control)[0]

                    translate = cmds.getAttr(control + ".translate")[0]
                    rotate = cmds.getAttr(control + ".rotate")[0]

                    cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2],
                                 type='double3')
                    cmds.setAttr(namespace + ":" + control + ".rotate", rotate[0], rotate[1], rotate[2], type='double3')

                    cmds.setKeyframe(namespace + ":" + control)

                # delete dupes
                cmds.delete(newControls[0])

                # switch modes
                if not range:
                    cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

        # switch to IK mode
        if mode == "IK":

            # get current mode
            currentMode = cmds.getAttr(namespace + ":" + self.name + "_settings.mode")
            if currentMode == 1.0:
                return

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

            if match:

                # get IK controls
                controls = json.loads(cmds.getAttr(networkNode + ".ikControls"))

                # HAND
                # create a duplicate hand anim
                control = controls[0]
                topGrp = cmds.listRelatives(namespace + ":" + control, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # duplicate the control once more and parent under the fkMatch node
                matchCtrl = cmds.duplicate(control, po=True)[0]
                cmds.parent(matchCtrl, control + "_fkMatch")

                # match the hand anim to the hand joint
                joint = control.partition("ik_")[2].partition("_anim")[0]
                joint = namespace + ":" + joint
                constraint = cmds.parentConstraint(joint, control + "_fkMatch")[0]
                cmds.delete(constraint)

                # unparent the match control from the fkMatch, and put it under the topGrp
                cmds.parent(matchCtrl, topGrp)

                # this will now give use good values
                translate = cmds.getAttr(matchCtrl + ".translate")[0]
                rotate = cmds.getAttr(matchCtrl + ".rotate")[0]

                cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2],
                             type='double3')
                cmds.setAttr(namespace + ":" + control + ".rotate", rotate[0], rotate[1], rotate[2], type='double3')

                cmds.setKeyframe(namespace + ":" + control)

                # delete dupes
                cmds.delete(newControls[0])
                cmds.delete(matchCtrl)

                # ELBOW
                # create a duplicate elbow pv anim
                control = controls[1]
                topGrp = cmds.listRelatives(namespace + ":" + control, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # match to the pvMatch node
                constraint = cmds.pointConstraint(namespace + ":" + control + "_fkMatch", control)[0]
                cmds.delete(constraint)

                # this will now give use good values
                translate = cmds.getAttr(control + ".translate")[0]

                cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2],
                             type='double3')

                cmds.setKeyframe(namespace + ":" + control)

                # delete dupes
                cmds.delete(newControls[0])

                # switch modes
                if not range:
                    cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

        if range:
            self.switchClavMode(mode, checkBox, True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def switchFingerMode(self, mode, finger, range=False):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        # switch to FK mode
        if mode == "FK":
            if finger == "All":
                cmds.setAttr(namespace + ":" + self.name + "_settings.index_finger_mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.index_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.middle_finger_mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.middle_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.ring_finger_mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.ring_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.pinky_finger_mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.pinky_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.thumb_finger_mode", 0.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.thumb_finger_mode")

            else:
                if finger.partition(namespace)[2].find(":index") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.index_finger_mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.index_finger_mode")

                if finger.partition(namespace)[2].find(":middle") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.middle_finger_mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.middle_finger_mode")

                if finger.partition(namespace)[2].find(":ring") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.ring_finger_mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.ring_finger_mode")

                if finger.partition(namespace)[2].find(":pinky") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.pinky_finger_mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.pinky_finger_mode")

                if finger.partition(namespace)[2].find(":thumb") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.thumb_finger_mode", 0.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.thumb_finger_mode")

        if mode == "IK":

            if finger == "All":
                cmds.setAttr(namespace + ":" + self.name + "_settings.index_finger_mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.index_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.middle_finger_mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.middle_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.ring_finger_mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.ring_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.pinky_finger_mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.pinky_finger_mode")
                cmds.setAttr(namespace + ":" + self.name + "_settings.thumb_finger_mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.thumb_finger_mode")

            else:
                if finger.partition(namespace)[2].find(":index") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.index_finger_mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.index_finger_mode")

                if finger.partition(namespace)[2].find(":middle") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.middle_finger_mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.middle_finger_mode")

                if finger.partition(namespace)[2].find(":ring") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.ring_finger_mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.ring_finger_mode")

                if finger.partition(namespace)[2].find(":pinky") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.pinky_finger_mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.pinky_finger_mode")

                if finger.partition(namespace)[2].find(":thumb") == 0:
                    # switch modes
                    cmds.setAttr(namespace + ":" + self.name + "_settings.thumb_finger_mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.thumb_finger_mode")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX(self, importMethod, character):

        returnControls = []

        networkNode = self.returnRigNetworkNode
        moduleName = cmds.getAttr(networkNode + ".moduleName")

        # find created joints
        joints = cmds.getAttr(networkNode + ".Created_Bones")

        splitJoints = joints.split("::")
        createdJoints = []
        armJoints = []
        clavJoint = None

        fingers = []
        if cmds.objExists(networkNode + ".fkFingerControls"):
            fingers = json.loads(cmds.getAttr(networkNode + ".fkFingerControls"))

        for bone in splitJoints:
            if bone != "":
                createdJoints.append(bone)

        for joint in createdJoints:
            if joint.find("upperarm") != -1:
                if joint.find("twist") == -1:
                    upArmJnt = joint
                    armJoints.append(upArmJnt)

            if joint.find("lowerarm") != -1:
                if joint.find("twist") == -1:
                    loArmJnt = joint
                    armJoints.append(loArmJnt)

            if joint.find("hand") != -1:
                handJoint = joint
                armJoints.append(handJoint)

            if joint.find("clavicle") != -1:
                clavJoint = joint

        solveClav = False

        if cmds.getAttr(networkNode + ".includeClavicle"):
            solveClav = True
            clavControls = json.loads(cmds.getAttr(networkNode + ".clavControls"))

        # Handle Import Method/Constraints
        if importMethod == "FK":
            cmds.setAttr(character + ":" + moduleName + "_settings.mode", 0)
            cmds.setAttr(character + ":" + moduleName + "_settings.clavMode", 0)

            if solveClav:
                cmds.orientConstraint(clavJoint, character + ":" + clavControls[0])
                returnControls.append(character + ":" + clavControls[0])

            for joint in armJoints:
                cmds.orientConstraint(joint, character + ":fk_" + joint + "_anim")
                returnControls.append(character + ":fk_" + joint + "_anim")

            if len(fingers) > 0:
                for finger in fingers:
                    cmds.orientConstraint(finger.partition("_anim")[0], character + ":" + finger)
                    returnControls.append(character + ":" + finger)

        if importMethod == "IK":

            if solveClav:
                cmds.pointConstraint(armJoints[0], character + ":" + clavControls[1])
                returnControls.append(character + ":" + clavControls[1])

            cmds.parentConstraint(armJoints[2], character + ":ik_" + armJoints[2] + "_anim", mo=True)
            returnControls.append(character + ":ik_" + armJoints[2] + "_anim")

            cmds.pointConstraint(armJoints[1], character + ":" + self.name + "_ik_elbow_anim", mo=True)
            returnControls.append(character + ":" + self.name + "_ik_elbow_anim")

            if len(fingers) > 0:
                for finger in fingers:
                    cmds.orientConstraint(finger.partition("_anim")[0], character + ":" + finger)
                    returnControls.append(character + ":" + finger)

        if importMethod == "Both":
            if solveClav:
                cmds.orientConstraint(clavJoint, character + ":" + clavControls[0])
                returnControls.append(character + ":" + clavControls[0])

                cmds.pointConstraint(armJoints[0], character + ":" + clavControls[1])
                returnControls.append(character + ":" + clavControls[1])

            cmds.parentConstraint(armJoints[2], character + ":ik_" + armJoints[2] + "_anim", mo=True)
            returnControls.append(character + ":ik_" + armJoints[2] + "_anim")

            cmds.pointConstraint(armJoints[1], character + ":" + self.name + "_ik_elbow_anim", mo=True)
            returnControls.append(character + ":" + self.name + "_ik_elbow_anim")

            for joint in armJoints:
                cmds.orientConstraint(joint, character + ":fk_" + joint + "_anim")
                returnControls.append(character + ":fk_" + joint + "_anim")

            if len(fingers) > 0:
                for finger in fingers:
                    cmds.orientConstraint(finger.partition("_anim")[0], character + ":" + finger)
                    returnControls.append(character + ":" + finger)

        if importMethod == "None":
            pass

        return returnControls

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectRigControls(self, mode):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        # list any attributes on the network node that contain "controls"
        controls = cmds.listAttr(networkNode, st="*Controls")
        fkControls = ["fkControls", "upArmTwistControls", "loArmTwistControls", "fkFingerControls", "clavControls"]
        ikControls = ["ikControls", "ikFingerControls", "clavControls"]

        # get that data on that attr
        for control in controls:

            # select all controls
            if mode == "all":
                data = json.loads(cmds.getAttr(networkNode + "." + control))
                if data != None:
                    for each in data:
                        cmds.select(namespace + ":" + each, add=True)

            # select fk controls
            if mode == "fk":
                if control in fkControls:
                    data = json.loads(cmds.getAttr(networkNode + "." + control))
                    if data != None:
                        for each in data:
                            if each.find("fk") != -1:
                                cmds.select(namespace + ":" + each, add=True)

            # select ik controls
            if mode == "ik":
                if control in ikControls:
                    data = json.loads(cmds.getAttr(networkNode + "." + control))
                    if data != None:
                        for each in data:
                            if each.find("fk") == -1:
                                cmds.select(namespace + ":" + each, add=True)
