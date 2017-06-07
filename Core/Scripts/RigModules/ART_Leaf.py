import json
import os
from functools import partial

import maya.cmds as cmds

import System.interfaceUtils as interfaceUtils
import System.utils as utils
from System.ART_RigModule import ART_RigModule
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# file attributes
icon = "Modules/leafJoint.png"
hoverIcon = "Modules/hover_leafJoint.png"
search = "jnt:joint:leaf"
className = "ART_Leaf"
jointMover = "Core/JointMover/ART_Leaf.ma"
baseName = "jnt"
fbxImport = ["None", "FK"]
matchData = [False, None]  # This is for matching over frame range options. (Matching between rigs of the module)
controlTypes = [["leafControls", "FK"]]


class ART_Leaf(ART_RigModule):
    def __init__(self, rigUiInst, moduleUserName):
        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}

        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")

        ART_RigModule.__init__(self, "ART_Leaf_Module", "ART_Leaf", moduleUserName)

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
        cmds.addAttr(self.networkNode, sn="Created_Bones", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".Created_Bones", "jnt", type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="baseName", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".baseName", baseName, type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="canAim", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".canAim", False, lock=True)

        cmds.addAttr(self.networkNode, sn="aimMode", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".aimMode", False, lock=True)

        cmds.addAttr(self.networkNode, sn="controlType", at="enum",
                     en="Circle:Square:Triangle:Cube:Sphere:Cylinder:Arrow", keyable=False)
        cmds.setAttr(self.networkNode + ".controlType", 0, lock=True)

        cmds.addAttr(self.networkNode, sn="proxyShape", at="enum", en="Cube:Cylinder:Capsule:Sphere:Cone",
                     keyable=False)
        cmds.setAttr(self.networkNode + ".proxyShape", 0, lock=True)

        cmds.addAttr(self.networkNode, sn="hasDynamics", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".hasDynamics", False, lock=True)

        cmds.addAttr(self.networkNode, sn="transX", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".transX", True, lock=True)

        cmds.addAttr(self.networkNode, sn="transY", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".transY", True, lock=True)

        cmds.addAttr(self.networkNode, sn="transZ", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".transZ", True, lock=True)

        cmds.addAttr(self.networkNode, sn="rotX", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".rotX", True, lock=True)

        cmds.addAttr(self.networkNode, sn="rotY", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".rotY", True, lock=True)

        cmds.addAttr(self.networkNode, sn="rotZ", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".rotZ", True, lock=True)

        cmds.addAttr(self.networkNode, sn="scaleX", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".scaleX", True, lock=True)

        cmds.addAttr(self.networkNode, sn="scaleY", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".scaleY", True, lock=True)

        cmds.addAttr(self.networkNode, sn="scaleZ", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".scaleZ", True, lock=True)

        cmds.addAttr(self.networkNode, sn="customAttrs", dt="string", keyable=False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):

        networkNode = self.returnNetworkNode

        # groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 438, True)

        font = QtGui.QFont()
        font.setPointSize(8)

        headerFont = QtGui.QFont()
        headerFont.setPointSize(8)
        headerFont.setBold(True)

        # create a VBoxLayout to add to our Groupbox and then add a QFrame for our signal/slot
        self.mainLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.mainLayout.addWidget(self.frame)
        self.frame.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.frame.setMinimumSize(QtCore.QSize(320, 420))
        self.frame.setMaximumSize(QtCore.QSize(320, 420))

        # create layout that is a child of the frame
        self.layout = QtWidgets.QVBoxLayout(self.frame)

        # mirror module
        self.mirrorModLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.mirrorModLayout)
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
        self.layout.addLayout(self.currentParentMod)
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
        self.layout.addLayout(self.buttonLayout)
        self.changeNameBtn = QtWidgets.QPushButton("Change Name")
        self.changeParentBtn = QtWidgets.QPushButton("Change Parent")
        self.mirrorModuleBtn = QtWidgets.QPushButton("Mirror Module")
        self.buttonLayout.addWidget(self.changeNameBtn)
        self.buttonLayout.addWidget(self.changeParentBtn)
        self.buttonLayout.addWidget(self.mirrorModuleBtn)
        self.changeNameBtn.setObjectName("blueButton")
        self.changeParentBtn.setObjectName("blueButton")
        self.mirrorModuleBtn.setObjectName("blueButton")

        # button signal/slots
        self.changeNameBtn.clicked.connect(partial(self.changeModuleName, baseName, self, self.rigUiInst))
        self.changeParentBtn.clicked.connect(partial(self.changeModuleParent, self, self.rigUiInst))
        self.mirrorModuleBtn.clicked.connect(partial(self.setMirrorModule, self, self.rigUiInst))

        # bake offsets button
        self.bakeToolsLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.bakeToolsLayout)

        # Bake OFfsets
        self.bakeOffsetsBtn = QtWidgets.QPushButton("Bake Offsets")
        self.bakeOffsetsBtn.setFont(headerFont)
        self.bakeToolsLayout.addWidget(self.bakeOffsetsBtn)
        self.bakeOffsetsBtn.clicked.connect(self.bakeOffsets)
        self.bakeOffsetsBtn.setToolTip("Bake the offset mover values up to the global movers to get them in sync")
        self.bakeOffsetsBtn.setObjectName("blueButton")

        # settings for control shape
        self.controlShapeLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.controlShapeLayout)

        self.controlShapeLabel = QtWidgets.QLabel("Control Type: ")
        self.controlShapeLabel.setFont(font)
        self.controlShapeLayout.addWidget(self.controlShapeLabel)

        self.controlShapeType = QtWidgets.QComboBox()
        self.controlShapeLayout.addWidget(self.controlShapeType)
        self.controlShapeType.addItem("Circle")
        self.controlShapeType.addItem("Square")
        self.controlShapeType.addItem("Triangle")
        self.controlShapeType.addItem("Cube")
        self.controlShapeType.addItem("Sphere")
        self.controlShapeType.addItem("Cylinder")
        self.controlShapeType.addItem("Arrow")

        # settings for proxy geo shape
        self.proxyShapeLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.proxyShapeLayout)

        self.proxyShapeLabel = QtWidgets.QLabel("Proxy Shape: ")
        self.proxyShapeLabel.setFont(font)
        self.proxyShapeLayout.addWidget(self.proxyShapeLabel)

        self.proxyShapeType = QtWidgets.QComboBox()
        self.proxyShapeLayout.addWidget(self.proxyShapeType)
        self.proxyShapeType.addItem("Cube")
        self.proxyShapeType.addItem("Cylinder")
        self.proxyShapeType.addItem("Capsule")
        self.proxyShapeType.addItem("Sphere")
        self.proxyShapeType.addItem("Cone")

        # Rig Settings
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.layout.addItem(spacerItem)

        self.hasDynamics = QtWidgets.QCheckBox("Has Dynamics")
        self.layout.addWidget(self.hasDynamics)
        self.hasDynamics.setChecked(False)
        self.hasDynamics.clicked.connect(partial(self.applyModuleChanges, self))

        spacerItem = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.layout.addItem(spacerItem)

        label = QtWidgets.QLabel("Keyable Attributes:")
        label.setFont(headerFont)
        self.layout.addWidget(label)

        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        self.layout.addItem(spacerItem)

        # TRANSLATES
        self.translateSettingsLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.translateSettingsLayout)

        self.txAttr = QtWidgets.QCheckBox("TranslateX")
        self.txAttr.setChecked(True)
        self.translateSettingsLayout.addWidget(self.txAttr)
        self.txAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.tyAttr = QtWidgets.QCheckBox("TranslateY")
        self.tyAttr.setChecked(True)
        self.translateSettingsLayout.addWidget(self.tyAttr)
        self.tyAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.tzAttr = QtWidgets.QCheckBox("TranslateZ")
        self.tzAttr.setChecked(True)
        self.translateSettingsLayout.addWidget(self.tzAttr)
        self.tzAttr.clicked.connect(partial(self.applyModuleChanges, self))

        # ROTATES
        self.rotateSettingsLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.rotateSettingsLayout)

        self.rxAttr = QtWidgets.QCheckBox("RotateX")
        self.rxAttr.setChecked(True)
        self.rotateSettingsLayout.addWidget(self.rxAttr)
        self.rxAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.ryAttr = QtWidgets.QCheckBox("RotateY")
        self.ryAttr.setChecked(True)
        self.rotateSettingsLayout.addWidget(self.ryAttr)
        self.ryAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.rzAttr = QtWidgets.QCheckBox("RotateZ")
        self.rzAttr.setChecked(True)
        self.rotateSettingsLayout.addWidget(self.rzAttr)
        self.rzAttr.clicked.connect(partial(self.applyModuleChanges, self))

        # SCALES
        self.scaleSettingsLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.scaleSettingsLayout)

        self.sxAttr = QtWidgets.QCheckBox("ScaleX")
        self.sxAttr.setChecked(True)
        self.scaleSettingsLayout.addWidget(self.sxAttr)
        self.sxAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.syAttr = QtWidgets.QCheckBox("ScaleY")
        self.syAttr.setChecked(True)
        self.scaleSettingsLayout.addWidget(self.syAttr)
        self.syAttr.clicked.connect(partial(self.applyModuleChanges, self))

        self.szAttr = QtWidgets.QCheckBox("ScaleZ")
        self.szAttr.setChecked(True)
        self.scaleSettingsLayout.addWidget(self.szAttr)
        self.szAttr.clicked.connect(partial(self.applyModuleChanges, self))

        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(spacerItem)

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.frame.setVisible)
        self.groupBox.setChecked(False)

        # add custom attributes
        buttonLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(buttonLayout)

        self.addAttrBtn = QtWidgets.QPushButton("Add Custom Attribute")
        buttonLayout.addWidget(self.addAttrBtn)
        self.addAttrBtn.clicked.connect(self.customAttr_UI)

        self.removeAttrBtn = QtWidgets.QPushButton("Remove Selected Attr")
        buttonLayout.addWidget(self.removeAttrBtn)
        self.removeAttrBtn.clicked.connect(self.removeCustomAttr)

        self.customAttrsList = QtWidgets.QListWidget()
        self.layout.addWidget(self.customAttrsList)

        # add custom skeletonUI settings  name, parent, rig types to install, mirror module, thigh twist, calf twists,
        # ball joint, toes,
        # add to the rig cretor UI's module settings layout VBoxLayout
        self.rigUiInst.moduleSettingsLayout.addWidget(self.groupBox)

        # Populate the settings UI based on the network node attributes
        self.updateSettingsUI()

        # hook up combo box signals
        self.controlShapeType.currentIndexChanged.connect(partial(self.changeControlShape))
        self.proxyShapeType.currentIndexChanged.connect(partial(self.changeProxyGeo))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def removeCustomAttr(self):

        selected = self.customAttrsList.currentRow()
        selectedText = json.loads(self.customAttrsList.item(selected).text())
        self.customAttrsList.takeItem(selected)

        # remove custom attr info from network node attr
        networkNode = self.returnNetworkNode
        newList = []

        if cmds.objExists(networkNode + ".customAttrs"):

            data = json.loads(cmds.getAttr(networkNode + ".customAttrs"))

            if selectedText in data:
                for each in data:
                    if each != selectedText:
                        newList.append(each)

                jsonString = json.dumps(newList)
                cmds.setAttr(networkNode + ".customAttrs", lock=False)
                cmds.setAttr(networkNode + ".customAttrs", jsonString, type="string", lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def customAttr_UI(self):

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        if cmds.window("pyART_customAttr_UI_Win", exists=True):
            cmds.deleteUI("pyART_customAttr_UI_Win", wnd=True)

        # create window
        self.custAttr_mainWin = QtWidgets.QMainWindow(self.rigUiInst)
        self.custAttr_mainWin.setMinimumSize(300, 180)
        self.custAttr_mainWin.setMaximumSize(300, 180)
        self.custAttr_mainWin.setWindowTitle("Add Attribute")
        self.custAttr_mainWin.setStyleSheet(self.style)
        self.custAttr_mainWin.setObjectName("pyART_customAttr_UI_Win")

        # frame and layout
        self.custAttr_frame = QtWidgets.QFrame()
        self.custAttr_mainWin.setCentralWidget(self.custAttr_frame)

        mainLayout = QtWidgets.QVBoxLayout(self.custAttr_frame)

        # attribute name
        nameLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(nameLayout)

        label = QtWidgets.QLabel("Attribute Name:")
        label.setStyleSheet("background: transparent;")
        nameLayout.addWidget(label)

        self.custAttr_attrName = QtWidgets.QLineEdit()
        nameLayout.addWidget(self.custAttr_attrName)

        # attribute type
        typeLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(typeLayout)

        label = QtWidgets.QLabel("Attribute Type:")
        label.setStyleSheet("background: transparent;")
        typeLayout.addWidget(label)

        self.custAttr_attrType = QtWidgets.QComboBox()
        typeLayout.addWidget(self.custAttr_attrType)

        self.custAttr_attrType.addItem("Float")
        self.custAttr_attrType.addItem("Bool")
        self.custAttr_attrType.currentIndexChanged.connect(self.customAttr_UI_attrType)

        # min/max/default
        valueLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(valueLayout)

        self.custAttr_minField = QtWidgets.QLineEdit()
        self.custAttr_minField.setPlaceholderText("Min")
        valueLayout.addWidget(self.custAttr_minField)

        self.custAttr_maxField = QtWidgets.QLineEdit()
        self.custAttr_maxField.setPlaceholderText("Max")
        valueLayout.addWidget(self.custAttr_maxField)

        self.custAttr_defaultField = QtWidgets.QLineEdit()
        self.custAttr_defaultField.setPlaceholderText("Default")
        valueLayout.addWidget(self.custAttr_defaultField)

        # Ok/Cancel buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        self.custAttr_AcceptBTN = QtWidgets.QPushButton("Accept")
        buttonLayout.addWidget(self.custAttr_AcceptBTN)
        self.custAttr_AcceptBTN.setObjectName("blueButton")
        self.custAttr_AcceptBTN.clicked.connect(self.customAttr_UI_Accept)

        self.custAttr_CancelBTN = QtWidgets.QPushButton("Cancel")
        buttonLayout.addWidget(self.custAttr_CancelBTN)
        self.custAttr_CancelBTN.setObjectName("blueButton")

        # show window
        self.custAttr_mainWin.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def customAttr_UI_attrType(self):

        if self.custAttr_attrType.currentText() == "Float":
            self.custAttr_minField.setVisible(True)
            self.custAttr_maxField.setVisible(True)

        if self.custAttr_attrType.currentText() == "Bool":
            self.custAttr_minField.setVisible(False)
            self.custAttr_maxField.setVisible(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def customAttr_UI_Accept(self):

        # data list
        data = []
        networkNode = self.returnNetworkNode

        # get name
        name = self.custAttr_attrName.text()
        try:
            existingData = json.loads(cmds.getAttr(networkNode + ".customAttrs"))

            # double check that name is valid and doesn't already exist
            for each in existingData:
                if isinstance(each, list):
                    attrName = each[0]
                    if attrName == name:
                        cmds.warning("Attribute with given name already exists on this module.")
                        return
                else:
                    attrName = existingData[0]
                    if attrName == name:
                        cmds.warning("Attribute with given name already exists on this module.")
                        return
        except:
            pass

        data.append(name)

        # get type
        type = self.custAttr_attrType.currentText()
        data.append(type)

        if type == "Float":

            # get min/max
            minValue = self.custAttr_minField.text()
            maxValue = self.custAttr_maxField.text()

            if minValue != "" and maxValue != "":
                # validate
                try:
                    minValue = float(minValue)
                    maxValue = float(maxValue)

                    if minValue > maxValue:
                        cmds.warning("Min Value cannot be larger than the maximum value")
                        return

                except:
                    cmds.warning("Min or Max contain non-integers")
                    return

            data.append(minValue)
            data.append(maxValue)

        # get default
        defaultValue = self.custAttr_defaultField.text()

        try:
            defaultValue = float(defaultValue)

            if type == "Float":
                if minValue != "" and maxValue != "":
                    if defaultValue > maxValue or defaultValue < minValue:
                        cmds.warning("Default value not in range")
                        return

            if type == "Bool":
                if defaultValue > 1 or defaultValue < 0:
                    cmds.warning("Default value must be a 0 or 1")
                    return
        except:
            cmds.warning("Default value is a non-integer.")
            return

        data.append(defaultValue)

        # close UI
        cmds.deleteUI("pyART_customAttr_UI_Win", wnd=True)

        jsonString = json.dumps(data)

        # add to list
        self.customAttrsList.addItem(jsonString)

        # add to network node, get existing value
        newList = []
        try:
            existingData = json.loads(cmds.getAttr(networkNode + ".customAttrs"))
            if len(existingData) > 0:
                if isinstance(existingData[0], list):
                    for each in existingData:
                        newList.append(each)
        except:
            pass

        newList.append(data)
        jsonString = json.dumps(newList)
        cmds.setAttr(networkNode + ".customAttrs", lock=False)
        cmds.setAttr(networkNode + ".customAttrs", jsonString, type="string", lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addJointMoverToOutliner(self):

        index = self.rigUiInst.treeWidget.topLevelItemCount()

        # Add the module to the tree widget in the outliner tab of the rig creator UI
        self.outlinerWidgets[self.name + "_treeModule"] = QtWidgets.QTreeWidgetItem(self.rigUiInst.treeWidget)
        self.rigUiInst.treeWidget.topLevelItem(index).setText(0, self.name)
        foreground = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.outlinerWidgets[self.name + "_treeModule"].setForeground(0, foreground)

        # add the buttons
        self.createGlobalMoverButton(self.name, self.outlinerWidgets[self.name + "_treeModule"], self.rigUiInst)
        self.createOffsetMoverButton(self.name, self.outlinerWidgets[self.name + "_treeModule"], self.rigUiInst)
        self.createMeshMoverButton(self.name, self.outlinerWidgets[self.name + "_treeModule"], self.rigUiInst)

        # create selection script job for module
        self.updateBoneCount()
        self.createScriptJob()

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

        for mover in [self.name + "_mover", self.name + "_mover_offset", self.name + "_mover_geo"]:
            mirrorMover = mover.replace(moduleName, mirrorModule)
            for attr in [".ty", ".tz", ".ry", ".rz"]:
                value = cmds.getAttr(mirrorMover + attr)
                cmds.setAttr(mirrorMover + attr, value * -1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def applyModuleChanges(self, moduleInst, *args):

        networkNode = self.returnNetworkNode

        # translations
        cmds.setAttr(networkNode + ".transX", lock=False)
        cmds.setAttr(networkNode + ".transX", self.txAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".transY", lock=False)
        cmds.setAttr(networkNode + ".transY", self.tyAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".transZ", lock=False)
        cmds.setAttr(networkNode + ".transZ", self.tzAttr.isChecked(), lock=True)

        # rotations
        cmds.setAttr(networkNode + ".rotX", lock=False)
        cmds.setAttr(networkNode + ".rotX", self.rxAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".rotY", lock=False)
        cmds.setAttr(networkNode + ".rotY", self.ryAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".rotZ", lock=False)
        cmds.setAttr(networkNode + ".rotZ", self.rzAttr.isChecked(), lock=True)

        # scales
        cmds.setAttr(networkNode + ".scaleX", lock=False)
        cmds.setAttr(networkNode + ".scaleX", self.sxAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".scaleY", lock=False)
        cmds.setAttr(networkNode + ".scaleY", self.syAttr.isChecked(), lock=True)

        cmds.setAttr(networkNode + ".scaleZ", lock=False)
        cmds.setAttr(networkNode + ".scaleZ", self.szAttr.isChecked(), lock=True)

        # dynamics
        cmds.setAttr(networkNode + ".hasDynamics", lock=False)
        cmds.setAttr(networkNode + ".hasDynamics", self.hasDynamics.isChecked(), lock=True)

        # shapes
        cmds.setAttr(networkNode + ".controlType", lock=False)
        cmds.setAttr(networkNode + ".controlType", self.controlShapeType.currentIndex(), lock=True)

        cmds.setAttr(networkNode + ".proxyShape", lock=False)
        cmds.setAttr(networkNode + ".proxyShape", self.proxyShapeType.currentIndex(), lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateSettingsUI(self):

        cmds.refresh(force=True)
        networkNode = self.returnNetworkNode

        # shapes
        controlShape = cmds.getAttr(networkNode + ".controlType")
        self.controlShapeType.setCurrentIndex(controlShape)

        proxyShape = cmds.getAttr(networkNode + ".proxyShape")
        self.proxyShapeType.setCurrentIndex(proxyShape)

        # transformations
        self.txAttr.setChecked(cmds.getAttr(networkNode + ".transX"))
        self.tyAttr.setChecked(cmds.getAttr(networkNode + ".transY"))
        self.tzAttr.setChecked(cmds.getAttr(networkNode + ".transZ"))

        self.rxAttr.setChecked(cmds.getAttr(networkNode + ".rotX"))
        self.ryAttr.setChecked(cmds.getAttr(networkNode + ".rotY"))
        self.rzAttr.setChecked(cmds.getAttr(networkNode + ".rotZ"))

        self.sxAttr.setChecked(cmds.getAttr(networkNode + ".scaleX"))
        self.syAttr.setChecked(cmds.getAttr(networkNode + ".scaleY"))
        self.szAttr.setChecked(cmds.getAttr(networkNode + ".scaleZ"))

        # has dynamics
        self.hasDynamics.setChecked(cmds.getAttr(networkNode + ".hasDynamics"))

        # custom attrs
        self.customAttrsList.clear()
        try:
            data = json.loads(cmds.getAttr(networkNode + ".customAttrs"))

            if isinstance(data[0], list):
                for each in data:
                    jsonString = json.dumps(each)
                    self.customAttrsList.addItem(jsonString)
            else:
                jsonString = json.dumps(data)
                self.customAttrsList.addItem(jsonString)
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeProxyGeo(self, *args):

        currentSelection = cmds.ls(sl=True)

        # get new proxy geo value from comboBox
        newShape = self.proxyShapeType.currentText()

        # construct the path
        path = os.path.join(self.toolsPath, "Core/JointMover/controls/")
        fullPath = os.path.join(path, "proxy_" + newShape + ".ma")
        fullPath = utils.returnFriendlyPath(fullPath)

        # import the file
        cmds.file(fullPath, i=True, iv=True, type="mayaAscii", rnn=True)

        # assign materials if they exist, removing duplicate materials
        materials = [["*_blue_m", "blue_m"], ["*_green_m", "green_m"], ["*_red_m", "red_m"], ["*_white_m", "white_m"],
                     ["*_proxy_shader_tan", "proxy_shader_tan"], ["*_proxy_shader_black", "proxy_shader_black"]]
        deleteMaterials = []
        for material in materials:
            try:
                # select materials for the joint mover
                cmds.select(material[0])
                foundMaterials = cmds.ls(sl=True)

                # loop through each color material (dupes)
                for mat in foundMaterials:
                    cmds.hyperShade(objects=mat)
                    assignedGeo = cmds.ls(sl=True)

                    # select the geo and the original material, and assign
                    originalMaterial = material[1]
                    for geo in assignedGeo:
                        cmds.select([geo, originalMaterial])
                        cmds.hyperShade(assign=originalMaterial)

                    # delete the material no longer needed
                    deleteMaterials.append(mat)
            except:
                pass

        # delete all deleteMaterials
        for mat in deleteMaterials:
            cmds.delete(mat)

        # parent under mover_geo
        cmds.parent("proxy_geo", self.name + "_mover_geo", r=True)

        # delete old proxy geo
        cmds.delete(self.name + "_proxy_geo")
        proxy = cmds.rename("proxy_geo", self.name + "_proxy_geo")

        cmds.setAttr(proxy + ".overrideEnabled", True, lock=True)
        cmds.setAttr(proxy + ".overrideDisplayType", 2)

        # apply module changes
        self.applyModuleChanges(self)

        # re-select selection
        cmds.select(currentSelection)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeControlShape(self, *args):

        currentSelection = cmds.ls(sl=True)

        # get new proxy geo value from comboBox
        newShape = self.controlShapeType.currentText()

        # construct the path
        path = os.path.join(self.toolsPath, "Core/JointMover/controls/")
        fullPath = os.path.join(path, "shape_" + newShape + ".ma")
        fullPath = utils.returnFriendlyPath(fullPath)

        # import the file
        cmds.file(fullPath, i=True, iv=True, type="mayaAscii", rnn=True)

        # replace the shape node of each mover with the new ones from the file
        for mover in ["_mover", "_mover_offset", "_mover_geo"]:
            newMoverShape = cmds.listRelatives("shape_curve" + mover, children=True)[0]

            cmds.parent(newMoverShape, self.name + mover, r=True, shape=True)
            cmds.delete(self.name + mover + "Shape")
            cmds.rename(newMoverShape, self.name + mover + "Shape")

            cmds.delete("shape_curve" + mover)

        # refresh UI to capture new mover shapes and set thier visibility
        self.rigUiInst.setMoverVisibility()

        # apply module changes
        self.applyModuleChanges(self)

        # re-select selection
        cmds.select(currentSelection)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pinModule(self, state):

        networkNode = self.returnNetworkNode
        topLevelMover = self.name + "_mover"

        if state:

            loc = cmds.spaceLocator()[0]
            cmds.setAttr(loc + ".v", False, lock=True)
            constraint = cmds.parentConstraint(topLevelMover, loc)[0]
            cmds.delete(constraint)
            const = cmds.parentConstraint(loc, topLevelMover)[0]
            attrs = cmds.listAttr(topLevelMover, keyable=True)

            for attr in attrs:
                try:
                    cmds.setAttr(topLevelMover + "." + attr, keyable=False, lock=True)
                except:
                    pass
            if not cmds.objExists(networkNode + ".pinConstraint"):
                cmds.addAttr(networkNode, ln="pinConstraint", keyable=True, at="message")

            cmds.connectAttr(const + ".message", networkNode + ".pinConstraint")

        if not state:
            attrs = cmds.listAttr(topLevelMover, keyable=True)
            for attr in attrs:
                try:
                    cmds.setAttr(topLevelMover + "." + attr, lock=True)
                except:
                    pass

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
            joint = name

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

        if textEdit is not None:
            textEdit.append("        Building " + self.name + " Rig..")

        # get the created joint
        networkNode = self.returnNetworkNode
        joint = cmds.getAttr(networkNode + ".Created_Bones")
        joint = joint.replace("::", "")
        globalMover = joint + "_mover"
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")

        # determine the rigs to be built
        numRigs = 1
        if cmds.getAttr(networkNode + ".hasDynamics"):
            numRigs += 1

        builtRigs = []

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # create groups and settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create the rig group
        self.rigGrp = cmds.group(empty=True, name=self.name + "_group")
        constraint = cmds.parentConstraint(globalMover, self.rigGrp)[0]
        cmds.delete(constraint)

        # create the rig settings group
        self.rigSettings = cmds.group(empty=True, name=self.name + "_settings")
        cmds.parent(self.rigSettings, self.rigGrp)
        for attr in (cmds.listAttr(self.rigSettings, keyable=True)):
            cmds.setAttr(self.rigSettings + "." + attr, lock=True, keyable=False)

        # add mode attribute to settings
        cmds.addAttr(self.rigSettings, ln="mode", min=0, max=numRigs - 1, dv=0, keyable=True)

        # create the ctrl group (what will get the constraint to the parent)
        self.rigCtrlGrp = cmds.group(empty=True, name=self.name + "_ctrl_grp")
        constraint = cmds.parentConstraint(parentBone, self.rigCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.rigCtrlGrp, self.rigGrp)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # build the rigs
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       FK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # find the mover, duplicate it to create the rig control
        dupe = cmds.duplicate(globalMover, rr=True)[0]
        utils.deleteChildren(dupe)
        parent = cmds.listRelatives(dupe, parent=True)
        if parent is not None:
            cmds.parent(dupe, world=True)

        # turn on visiblity of the control
        cmds.setAttr(dupe + ".v", 1)

        # ensure pivot is correct
        piv = cmds.xform(joint, q=True, ws=True, rp=True)
        cmds.xform(dupe, ws=True, rp=piv)

        # rename the control
        fkControl = cmds.rename(dupe, joint + "_anim")

        # create an anim group for the control
        controlGrp = cmds.group(empty=True, name=joint + "_anim_grp")
        constraint = cmds.parentConstraint(joint, controlGrp)[0]
        cmds.delete(constraint)

        # create the space switcher group
        spaceSwitchFollow = cmds.duplicate(controlGrp, po=True, name=fkControl + "_space_switcher_follow")[0]
        spaceSwitch = cmds.duplicate(controlGrp, po=True, name=fkControl + "_space_switcher")[0]

        utils.deleteChildren(spaceSwitchFollow)
        utils.deleteChildren(spaceSwitch)

        cmds.parent(spaceSwitch, spaceSwitchFollow)
        cmds.parent(controlGrp, spaceSwitch)

        # parent the control under the controlGrp
        cmds.parent(fkControl, controlGrp)
        cmds.parent(spaceSwitchFollow, self.rigCtrlGrp)

        # freeze transformations on the control
        cmds.makeIdentity(fkControl, t=1, r=1, s=1, apply=True)

        # color the control
        cmds.setAttr(fkControl + ".overrideEnabled", 1)
        cmds.setAttr(fkControl + ".overrideColor", 18)

        # constrain joint
        cmds.parentConstraint(fkControl, "driver_" + joint)
        cmds.scaleConstraint(fkControl, "driver_" + joint)

        # parent under offset_anim if it exists(it always should)
        if cmds.objExists("offset_anim"):
            cmds.parent(self.rigGrp, "offset_anim")

        # check settings and lock attributes that need locking
        if not cmds.getAttr(networkNode + ".transX"):
            cmds.setAttr(fkControl + ".tx", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".transY"):
            cmds.setAttr(fkControl + ".ty", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".transZ"):
            cmds.setAttr(fkControl + ".tz", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".rotX"):
            cmds.setAttr(fkControl + ".rx", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".rotY"):
            cmds.setAttr(fkControl + ".ry", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".rotZ"):
            cmds.setAttr(fkControl + ".rz", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".scaleX"):
            cmds.setAttr(fkControl + ".sx", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".scaleY"):
            cmds.setAttr(fkControl + ".sy", lock=True, keyable=False)

        if not cmds.getAttr(networkNode + ".scaleZ"):
            cmds.setAttr(fkControl + ".sz", lock=True, keyable=False)

        # lock visibility regardless
        cmds.setAttr(fkControl + ".v", lock=True, keyable=False)

        # check for custom attributes and add them if they exist
        try:
            data = json.loads(cmds.getAttr(networkNode + ".customAttrs"))
            print data
            for each in data:
                attrName = each[0]
                attrType = each[1]

                if attrType == "Bool":
                    value = each[2]

                    if not cmds.objExists(fkControl + "." + attrName):
                        cmds.addAttr(fkControl, ln=attrName, at="bool", keyable=True, dv=value)

                if attrType == "Float":
                    minVal = each[2]
                    maxVal = each[3]
                    hasMin = True
                    hasMax = True

                    if minVal == '':
                        hasMin = False
                        minVal = 0

                    if maxVal == '':
                        hasMax = False
                        maxVal = 0

                    if not cmds.objExists(fkControl + "." + attrName):

                        if hasMin is False and hasMax is False:
                            cmds.addAttr(fkControl, ln=attrName, at="float", keyable=True, dv=float(each[4]))
                        if hasMin is False and hasMax is True:
                            cmds.addAttr(fkControl, ln=attrName, at="float", keyable=True, max=float(maxVal),
                                         dv=float(each[4]))
                        if hasMin is True and hasMax is False:
                            cmds.addAttr(fkControl, ln=attrName, at="float", keyable=True, min=float(minVal),
                                         dv=float(each[4]))

        except Exception, e:
            print e

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                   Dynamics                    # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if cmds.getAttr(networkNode + ".hasDynamics"):
            cubeGrp = cmds.group(empty=True, name=self.name + "_dyn_grp")
            const = cmds.parentConstraint(joint, cubeGrp)[0]
            cmds.delete(const)
            cmds.parent(cubeGrp, self.rigGrp)

            # make grp pivot same as parent bone
            piv = cmds.xform(parentBone, q=True, ws=True, rp=True)
            cmds.xform(cubeGrp, ws=True, piv=piv)
            cmds.parentConstraint("driver_" + parentBone, cubeGrp, mo=True)

            # creation: cube rigid body in same spot as leaf joint
            self.rigidCube = cmds.polyCube(name=self.name + "_dyn_obj")[0]
            const = cmds.parentConstraint(joint, self.rigidCube)[0]
            cmds.delete(const)

            cmds.setAttr(self.rigidCube + ".v", 0, lock=True)
            cmds.parent(self.rigidCube, cubeGrp)
            cmds.makeIdentity(self.rigidCube, t=1, r=1, s=1, apply=True)

            # usually this is done automatically, but for some reason, this damn cube would not add the attr
            # properly in the loop. so..hax
            cmds.addAttr(self.rigidCube, ln="sourceModule", dt="string")

            # create the rigid body
            cmds.select(self.rigidCube)
            rigidBody = cmds.rigidBody(act=True, m=1, damping=0.1, staticFriction=0.2, dynamicFriction=0.2,
                                       bounciness=0.6, layer=0, tesselationFactor=200)

            # create the spring constraint
            cmds.select(self.rigidCube)
            spring = cmds.constrain(spring=True, stiffness=100, damping=1.0, i=0)
            cmds.refresh(force=True)
            cmds.setAttr(spring + ".v", 0, lock=True)

            # position spring
            pos = cmds.xform(joint, q=True, ws=True, t=True)

            cmds.setAttr(spring + ".translateX", pos[0])
            cmds.setAttr(spring + ".translateY", pos[1])
            cmds.setAttr(spring + ".translateZ", pos[2])
            cmds.refresh(force=True)

            cmds.parent(spring, "driver_" + parentBone)

            # create a group that is point constrained to the cube, but orient constrained to the parent bone
            tracker = cmds.group(empty=True, name=self.name + "_dyn_tracker")
            const = cmds.parentConstraint(joint, tracker)[0]
            cmds.delete(const)

            cmds.parent(tracker, self.rigGrp)
            cmds.pointConstraint(self.rigidCube, tracker)
            orientConst = cmds.orientConstraint("driver_" + parentBone, tracker, mo=True)[0]

            # constrain joint
            cmds.parentConstraint(tracker, "driver_" + joint)
            cmds.scaleConstraint(tracker, "driver_" + joint)

            # add relevant settings to the settings node
            cmds.addAttr(self.rigSettings, ln="mass", keyable=True, dv=1)
            cmds.addAttr(self.rigSettings, ln="bounciness", keyable=True, dv=0.6, min=0, max=2)
            cmds.addAttr(self.rigSettings, ln="damping", keyable=True, dv=0.97, min=-10, max=10)
            cmds.addAttr(self.rigSettings, ln="springDamping", keyable=True, dv=1.0, min=-10, max=10)
            cmds.addAttr(self.rigSettings, ln="springStiffness", keyable=True, dv=500, min=0)
            cmds.addAttr(self.rigSettings, ln="orientToParent", keyable=True, dv=1, min=0, max=1)

            # then hook them up
            cmds.connectAttr(self.rigSettings + ".mass", rigidBody + ".mass")
            cmds.connectAttr(self.rigSettings + ".bounciness", rigidBody + ".bounciness")
            cmds.connectAttr(self.rigSettings + ".damping", rigidBody + ".damping")
            cmds.connectAttr(self.rigSettings + ".springStiffness", spring + ".springStiffness")
            cmds.connectAttr(self.rigSettings + ".springDamping", spring + ".springDamping")
            cmds.connectAttr(self.rigSettings + ".orientToParent", orientConst + ".driver_" + parentBone + "W0")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                   SETTINGS                    # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # mode
        if numRigs > 1:
            attrData = []

            """ CONSTRAINTS """
            # get the constraint connections on the driver joints for the leaf
            connections = []
            connections.extend(list(set(cmds.listConnections("driver_" + joint, type="constraint"))))

            for connection in connections:
                driveAttrs = []

                if cmds.nodeType(connection) in ["parentConstraint", "scaleConstraint"]:

                    # get those constraint target attributes for each constraint connection
                    targets = cmds.getAttr(connection + ".target", mi=True)
                    if len(targets) > 1:
                        for each in targets:
                            driveAttrs.append(
                                cmds.listConnections(connection + ".target[" + str(each) + "].targetWeight", p=True))

                        # add this data to our master list of constraint attribute data
                        attrData.append(driveAttrs)

            # setup set driven keys on our moder attr and those target attributes
            for i in range(numRigs):
                cmds.setAttr(self.rigSettings + ".mode", i)

                # go through attr data and zero out anything but the first element in the list
                for data in attrData:
                    for each in data:
                        cmds.setAttr(each[0], 0)

                    cmds.setAttr(data[i][0], 1)

                # set driven keys
                for data in attrData:
                    for each in data:
                        cmds.setDrivenKeyframe(each[0], cd=self.rigSettings + ".mode", itt="linear", ott="linear")

            # hook up control visibility
            cmds.setAttr(self.rigSettings + ".mode", 0)
            cmds.setAttr(controlGrp + ".v", 1)
            cmds.setDrivenKeyframe(controlGrp, at="visibility", cd=self.rigSettings + ".mode", itt="linear",
                                   ott="linear")

            cmds.setAttr(self.rigSettings + ".mode", 1)
            cmds.setAttr(controlGrp + ".v", 0)
            cmds.setDrivenKeyframe(controlGrp, at="visibility", cd=self.rigSettings + ".mode", itt="linear",
                                   ott="linear")

            cmds.setAttr(self.rigSettings + ".mode", 0)

        controls = [fkControl]
        if not cmds.objExists(networkNode + ".leafControls"):
            cmds.addAttr(networkNode, ln="leafControls", dt="string")
        jsonString = json.dumps(controls)
        cmds.setAttr(networkNode + ".leafControls", jsonString, type="string")

        # return data
        try:
            uiInst.rigData.append([self.rigCtrlGrp, "driver_" + parentBone, numRigs])

        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pickerUI(self, center, animUI, networkNode, namespace):

        # create qBrushes
        blueBrush = QtGui.QColor(100, 220, 255)
        clearBrush = QtGui.QBrush(QtCore.Qt.black)
        clearBrush.setStyle(QtCore.Qt.NoBrush)

        # create border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode
        borderItem = interfaceUtils.pickerBorderItem(center.x() - 40, center.y() - 70, 50, 50, clearBrush, moduleNode)

        # get controls
        networkNode = self.returnNetworkNode
        controls = json.loads(cmds.getAttr(networkNode + ".leafControls"))

        # anim button
        button = interfaceUtils.pickerButton(30, 30, [10, 2], namespace + controls[0], blueBrush, borderItem)
        button.setToolTip(self.name)

        # add right click menu to select settings
        fkIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/jointFilter.png"))))
        button.menu.addAction(fkIcon, "Settings", partial(self.selectSettings, namespace))
        button.menu.addAction("Change Button Color", partial(self.changeButtonColor, animUI, button, borderItem,
        namespace + controls[0]))

        # =======================================================================
        # #Create scriptJob for selection. Set scriptJob number to borderItem.data(5)
        # =======================================================================
        scriptJob = cmds.scriptJob(event=["SelectionChanged", partial(self.selectionScriptJob_animUI,
                                                                      [[button, namespace + controls[0], blueBrush]])],
                                   kws=True)

        borderItem.setData(5, scriptJob)
        animUI.selectionScriptJobs.append(scriptJob)

        return [borderItem, False, scriptJob]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeButtonColor(self, animUI, button, border, control, color=None):
        """
        Leaf joints give the user the option to change the button's color. This function will remove the existing
        scriptJob, set the new button color, and create a new scriptJob with that information.

        :param animUI: The animation UI instance
        :param button: The button whose color we wish to set.
        :param border: The border item of the button that holds the scriptJob number to kill
        :param control: The control this button selects.
        """
        print color, control
        # launch a color dialog to  get a new color
        if color is None:
            newColor = QtGui.QColorDialog.getColor()
        else:
            newColor = color

        # delete the existing scriptJob
        scriptJob = border.data(5)
        cmds.scriptJob(kill=scriptJob)
        animUI.selectionScriptJobs.remove(scriptJob)

        # set the button color
        button.brush.setColor(newColor)

        # create the new scriptJob
        scriptJob = cmds.scriptJob(event=["SelectionChanged", partial(self.selectionScriptJob_animUI,
                                                                      [[button, control, newColor]])],
                                   kws=True)
        border.setData(5, scriptJob)
        animUI.selectionScriptJobs.append(scriptJob)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectSettings(self, namespace):

        cmds.select(namespace + self.name + "_settings")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pasteSettings(self):

        # this shit right here is so hacky. For some reason, paste and reset have to run multiple times to get
        # everything
        # and I haven't taken the time to figure out why
        for i in range(4):

            tempDir = cmds.internalVar(userTmpDir=True)
            clipboardFile = os.path.normcase(os.path.join(tempDir, "ART_clipboard.txt"))

            if os.path.exists(clipboardFile):
                # load the data
                json_file = open(clipboardFile)
                data = json.load(json_file)
                json_file.close()

                # attempt to paste data if module type is the same
                networkNode = self.returnNetworkNode
                moduleType = cmds.getAttr(networkNode + ".moduleType")
                if moduleType == data[0][1]:

                    for each in data:
                        attr = each[0]
                        value = each[1]
                        attrType = str(cmds.getAttr(networkNode + "." + attr, type=True))

                        if attrType != "string":
                            cmds.setAttr(networkNode + "." + attr, lock=False)
                            cmds.setAttr(networkNode + "." + attr, value, lock=True)

                        if attr == "customAttrs":
                            cmds.setAttr(networkNode + "." + attr, lock=False)
                            try:
                                cmds.setAttr(networkNode + "." + attr, value, type="string", lock=True)
                            except:
                                pass

                    # relaunch the UI
                    self.updateSettingsUI()
                    self.applyModuleChanges(self)
            else:
                cmds.warning("No data in clipboard")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX(self, importMethod, character):

        returnControls = []

        networkNode = self.returnRigNetworkNode
        control = json.loads(cmds.getAttr(networkNode + ".leafControls"))
        joints = cmds.getAttr(networkNode + ".Created_Bones")
        joint = joints.partition("::")[0]

        if importMethod == "FK":
            cmds.parentConstraint(joint, character + ":" + control[0])
            returnControls.append(character + ":" + control[0])

        if importMethod == "None":
            pass

        return returnControls
