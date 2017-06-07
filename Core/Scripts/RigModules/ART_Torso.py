import maya.cmds as cmds
from System.ART_RigModule import ART_RigModule
import os, time, json, weakref
from functools import partial

import System.interfaceUtils as interfaceUtils
import System.riggingUtils as riggingUtils
import System.utils as utils

from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# file attributes
icon = "Modules/torso.png"
hoverIcon = "Modules/hover_torso.png"
search = "biped:torso:spine"
className = "ART_Torso"
jointMover = "Core/JointMover/ART_Torso_3Spine.ma"
baseName = "torso"
rigs = ["FK::IK"]
fbxImport = ["None", "FK", "IK", "Both"]
matchData = [True, ["Match FK to IK", "Match IK to FK"]]
controlTypes = [["pelvisControls", "FK"], ["fkControls", "FK"], ["ikControls", "IK"]]


# begin class
class ART_Torso(ART_RigModule):
    _instances = set()

    def __init__(self, rigUiInst, moduleUserName):

        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}
        self.__class__._instances.add(weakref.ref(self))

        ART_RigModule.__init__(self, "ART_Torso_Module", "ART_Torso", moduleUserName)

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
        cmds.setAttr(self.networkNode + ".Created_Bones", "pelvis::spine_01::spine_02::spine_03::", type="string",
                     lock=True)

        cmds.addAttr(self.networkNode, sn="baseName", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".baseName", baseName, type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="canAim", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".canAim", True, lock=True)

        cmds.addAttr(self.networkNode, sn="aimMode", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".aimMode", False, lock=True)

        # joint mover settings

        cmds.addAttr(self.networkNode, sn="includePelvis", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".includePelvis", True, lock=True)

        cmds.addAttr(self.networkNode, sn="spineJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".spineJoints", 3, lock=True)

        # rig creation settings
        cmds.addAttr(self.networkNode, sn="buildFK", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".buildFK", True, lock=True)

        cmds.addAttr(self.networkNode, sn="buildIK", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".buildIK", True, lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):
        networkNode = self.returnNetworkNode

        # groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 295, True)

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
        self.frame.setMinimumSize(QtCore.QSize(320, 260))
        self.frame.setMaximumSize(QtCore.QSize(320, 260))

        # add layout for custom settings
        self.customSettingsLayout = QtWidgets.QVBoxLayout(self.frame)

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
        self.buttonLayout.addWidget(self.changeNameBtn)
        self.buttonLayout.addWidget(self.changeParentBtn)
        self.changeNameBtn.setObjectName("blueButton")
        self.changeParentBtn.setObjectName("blueButton")

        # bake offsets button
        self.bakeToolsLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.bakeToolsLayout)

        # Bake OFfsets
        self.bakeOffsetsBtn = QtWidgets.QPushButton("Bake Offsets")
        self.bakeOffsetsBtn.setFont(headerFont)
        self.bakeToolsLayout.addWidget(self.bakeOffsetsBtn)
        self.bakeOffsetsBtn.clicked.connect(self.bakeOffsets)
        self.bakeOffsetsBtn.setToolTip("Bake the offset mover values up to the global movers to get them in sync")

        self.bakeOffsetsBtn.setObjectName("blueButton")

        # Pelvis Settings
        spacerItem = QtWidgets.QSpacerItem(200, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.customSettingsLayout.addItem(spacerItem)

        self.pelvisCB = QtWidgets.QCheckBox("Include Pelvis?")
        self.pelvisCB.setChecked(True)
        self.customSettingsLayout.addWidget(self.pelvisCB)
        self.pelvisCB.stateChanged.connect(self.toggleButtonState)
        spacerItem = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.customSettingsLayout.addItem(spacerItem)

        # Spine Bones
        self.spineLayout = QtWidgets.QHBoxLayout()
        self.customSettingsLayout.addLayout(self.spineLayout)

        self.numSpineBonesLabel = QtWidgets.QLabel("Number of Spine Bones: ")
        self.numSpineBonesLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.numSpineBonesLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.numSpineBonesLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.spineLayout.addWidget((self.numSpineBonesLabel))

        self.numSpine = QtWidgets.QSpinBox()
        self.numSpine.setMaximum(5)
        self.numSpine.setMinimum(2)
        self.numSpine.setMinimumSize(QtCore.QSize(100, 20))
        self.numSpine.setMaximumSize(QtCore.QSize(100, 20))
        self.numSpine.setValue(3)
        self.numSpine.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spineLayout.addWidget(self.numSpine)

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

        # add to the rig cretor UI's module settings layout VBoxLayout
        self.rigUiInst.moduleSettingsLayout.addWidget(self.groupBox)

        # button signal/slots
        self.changeNameBtn.clicked.connect(partial(self.changeModuleName, baseName, self, self.rigUiInst))
        self.changeParentBtn.clicked.connect(partial(self.changeModuleParent, self, self.rigUiInst))
        self.applyButton.clicked.connect(partial(self.applyModuleChanges, self))

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.frame.setVisible)
        self.groupBox.setChecked(False)

        # spinBox & checkbox signal/slots
        self.numSpine.valueChanged.connect(self.toggleButtonState)

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

        # create the picker border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode

        borderItem = interfaceUtils.pickerBorderItem(center.x() - 75, center.y() - 100, 150, 200, clearBrush,
                                                     moduleNode)

        # get controls
        fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
        fkControls.reverse()

        ikControls = None
        if cmds.objExists(networkNode + ".ikControls"):
            ikControls = json.loads(cmds.getAttr(networkNode + ".ikControls"))

        pelvisControls = None
        if cmds.objExists(networkNode + ".pelvisControls"):
            pelvisControls = json.loads(cmds.getAttr(networkNode + ".pelvisControls"))

        buttonData = []

        # get number of spine joints
        spineJoints = int(cmds.getAttr(networkNode + ".spineJoints"))

        if pelvisControls != None:
            pelvisButton = interfaceUtils.pickerButtonCustom(100, 20, [[0, 0], [100, 0], [90, 20], [10, 20]], [25, 175],
                                                             namespace + pelvisControls[0], blueBrush, borderItem)
            bodyButton = interfaceUtils.pickerButton(110, 20, [20, 150], namespace + pelvisControls[1], yellowBrush,
                                                     borderItem)
            buttonData.append([pelvisButton, namespace + pelvisControls[0], blueBrush])
            buttonData.append([bodyButton, namespace + pelvisControls[1], yellowBrush])

        if spineJoints == 2:
            spine1Button = interfaceUtils.pickerButtonCustom(100, 50, [[10, 0], [100, 0], [110, 50], [0, 50]], [20, 95],
                                                             namespace + fkControls[0], blueBrush, borderItem)
            spine2Button = interfaceUtils.pickerButtonCustom(100, 60, [[10, 60], [100, 60], [110, 0], [0, 0]], [20, 30],
                                                             namespace + fkControls[1], blueBrush, borderItem)
            buttonData.append([spine1Button, namespace + fkControls[0], blueBrush])
            buttonData.append([spine2Button, namespace + fkControls[1], blueBrush])

        if spineJoints == 3:
            chestAnimButton = interfaceUtils.pickerButton(120, 20, [15, 25], namespace + ikControls[0], yellowBrush,
                                                          borderItem)
            midAnimButton = interfaceUtils.pickerButton(90, 20, [30, 100], namespace + ikControls[1], yellowBrush,
                                                        borderItem)
            buttonData.append([chestAnimButton, namespace + ikControls[0], yellowBrush])
            buttonData.append([midAnimButton, namespace + ikControls[1], yellowBrush])

            spine1Button = interfaceUtils.pickerButtonCustom(80, 20, [[10, 0], [100, 0], [105, 20], [5, 20]], [20, 125],
                                                             namespace + fkControls[0], blueBrush, borderItem)
            spine2Button = interfaceUtils.pickerButtonCustom(80, 20, [[10, 20], [100, 20], [100, 0], [10, 0]], [20, 75],
                                                             namespace + fkControls[1], blueBrush, borderItem)
            spine3Button = interfaceUtils.pickerButtonCustom(80, 20, [[10, 20], [100, 20], [105, 0], [5, 0]], [20, 50],
                                                             namespace + fkControls[2], blueBrush, borderItem)
            buttonData.append([spine1Button, namespace + fkControls[0], blueBrush])
            buttonData.append([spine2Button, namespace + fkControls[1], blueBrush])
            buttonData.append([spine3Button, namespace + fkControls[2], blueBrush])

        if spineJoints == 4:
            chestAnimButton = interfaceUtils.pickerButton(120, 20, [15, 25], namespace + ikControls[0], yellowBrush,
                                                          borderItem)
            midAnimButton = interfaceUtils.pickerButton(90, 15, [30, 90], namespace + ikControls[1], yellowBrush,
                                                        borderItem)
            buttonData.append([chestAnimButton, namespace + ikControls[0], yellowBrush])
            buttonData.append([midAnimButton, namespace + ikControls[1], yellowBrush])

            spine1Button = interfaceUtils.pickerButtonCustom(80, 15, [[10, 0], [100, 0], [105, 15], [5, 15]], [20, 130],
                                                             namespace + fkControls[0], blueBrush, borderItem)
            spine2Button = interfaceUtils.pickerButtonCustom(80, 15, [[10, 15], [100, 15], [95, 0], [15, 0]], [20, 110],
                                                             namespace + fkControls[1], blueBrush, borderItem)
            spine3Button = interfaceUtils.pickerButtonCustom(80, 15, [[15, 15], [95, 15], [100, 0], [10, 0]], [20, 70],
                                                             namespace + fkControls[2], blueBrush, borderItem)
            spine4Button = interfaceUtils.pickerButtonCustom(80, 15, [[10, 15], [100, 15], [110, 0], [0, 0]], [20, 50],
                                                             namespace + fkControls[3], blueBrush, borderItem)
            buttonData.append([spine1Button, namespace + fkControls[0], blueBrush])
            buttonData.append([spine2Button, namespace + fkControls[1], blueBrush])
            buttonData.append([spine3Button, namespace + fkControls[2], blueBrush])
            buttonData.append([spine4Button, namespace + fkControls[3], blueBrush])

        if spineJoints == 5:
            chestAnimButton = interfaceUtils.pickerButton(120, 20, [15, 25], namespace + ikControls[0], yellowBrush,
                                                          borderItem)
            midAnimButton = interfaceUtils.pickerButton(90, 20, [30, 95], namespace + ikControls[1], yellowBrush,
                                                        borderItem)
            buttonData.append([chestAnimButton, namespace + ikControls[0], yellowBrush])
            buttonData.append([midAnimButton, namespace + ikControls[1], yellowBrush])

            spine1Button = interfaceUtils.pickerButtonCustom(80, 10, [[0, 10], [110, 10], [105, 0], [5, 0]], [20, 135],
                                                             namespace + fkControls[0], blueBrush, borderItem)
            spine2Button = interfaceUtils.pickerButtonCustom(80, 10, [[5, 10], [105, 10], [100, 0], [10, 0]], [20, 120],
                                                             namespace + fkControls[1], blueBrush, borderItem)
            spine3Button = interfaceUtils.pickerButtonCustom(80, 10, [[10, 10], [100, 10], [100, 0], [10, 0]], [20, 80],
                                                             namespace + fkControls[2], blueBrush, borderItem)
            spine4Button = interfaceUtils.pickerButtonCustom(80, 10, [[10, 10], [100, 10], [105, 0], [5, 0]], [20, 65],
                                                             namespace + fkControls[3], blueBrush, borderItem)
            spine5Button = interfaceUtils.pickerButtonCustom(80, 10, [[5, 10], [105, 10], [110, 0], [0, 0]], [20, 50],
                                                             namespace + fkControls[4], blueBrush, borderItem)
            buttonData.append([spine1Button, namespace + fkControls[0], blueBrush])
            buttonData.append([spine2Button, namespace + fkControls[1], blueBrush])
            buttonData.append([spine3Button, namespace + fkControls[2], blueBrush])
            buttonData.append([spine4Button, namespace + fkControls[3], blueBrush])
            buttonData.append([spine5Button, namespace + fkControls[4], blueBrush])

        # =======================================================================
        # settings button
        # =======================================================================
        settingsBtn = interfaceUtils.pickerButton(20, 20, [125, 180], namespace + self.name + "_settings", greenBrush,
                                                  borderItem)
        buttonData.append([settingsBtn, namespace + ":" + self.name + "_settings", greenBrush])
        interfaceUtils.addTextToButton("S", settingsBtn)

        # =======================================================================
        # go through button data, adding menu items
        # =======================================================================
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

            button.menu.addAction(selectIcon, "Select All Torso Controls", partial(self.selectRigControls, "all"))
            button.menu.addAction(selectIcon, "Select FK Torso Controls", partial(self.selectRigControls, "fk"))
            button.menu.addAction(selectIcon, "Select IK Torso Controls", partial(self.selectRigControls, "ik"))

            button.menu.addSeparator()

            button.menu.addAction(fkIcon, "FK Mode", partial(self.switchMode, "FK", switchAction))
            button.menu.addAction(ikIcon, "IK Mode", partial(self.switchMode, "IK", switchAction))
            button.menu.addAction(switchAction)

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
    def applyModuleChanges(self, moduleInst):

        networkNode = self.returnNetworkNode

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
        spineJoints = []

        if self.pelvisCB.isChecked():
            spineJoints.append(prefix + "pelvis" + suffix)

        # get current spine value
        currentNum = int(cmds.getAttr(networkNode + ".spineJoints"))

        # get new spine value
        uiSpineNum = self.numSpine.value()

        if uiSpineNum != currentNum:
            # update spine value, and call on update spine
            cmds.setAttr(networkNode + ".spineJoints", lock=False)
            cmds.setAttr(networkNode + ".spineJoints", uiSpineNum, lock=True)

            # look for any attached modules
            attachedModules = self.checkForDependencies()
            self.updateSpine(attachedModules, currentNum)

        for i in range(uiSpineNum):
            spineJoints.append(prefix + "spine_0" + str(i + 1) + suffix)

        # build attrString
        attrString = ""
        for bone in spineJoints:
            attrString += bone + "::"

        networkNode = self.returnNetworkNode
        cmds.setAttr(networkNode + ".Created_Bones", lock=False)
        cmds.setAttr(networkNode + ".Created_Bones", attrString, type="string", lock=True)

        # pelvis
        self.includePelvis()

        # reset button
        self.applyButton.setEnabled(False)

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
    def updateSpine(self, attachedModules, oldNum):

        # gather information (current name, current parent, etc)
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        parent = cmds.getAttr(networkNode + ".parentModuleBone")
        newNum = int(cmds.getAttr(networkNode + ".spineJoints"))

        # call on base class delete
        movers = self.returnJointMovers
        for moverGrp in movers:
            for mover in moverGrp:
                cmds.lockNode(mover, lock=False)

        # store mover positions (movers = [all global, all offset, all geo])
        basePositions = {}

        for each in movers:
            for mover in each:
                attrs = cmds.listAttr(mover, keyable=True)
                attrValues = []
                for attr in attrs:
                    value = cmds.getAttr(mover + "." + attr)
                    attrValues.append([attr, value])
                basePositions[mover] = attrValues

        if cmds.getAttr(networkNode + ".aimMode") == True:
            self.aimMode_Setup(False)

        # delete joint mover
        cmds.delete(self.name + "_mover_grp")

        # build new jmPath name
        jmPath = jointMover.partition(".ma")[0].rpartition("_")[0] + "_" + str(newNum) + "Spine.ma"
        self.jointMover_Build(jmPath)

        # apply base positions
        for key in basePositions:

            mover = key
            attrList = basePositions.get(key)

            for attr in attrList:
                if cmds.objExists(mover):
                    cmds.setAttr(mover + "." + attr[0], attr[1])

        # parent the joint mover to the offset mover of the parent
        mover = ""
        if parent == "root":
            mover = "root_mover"

        else:
            # find the parent mover name to parent to
            networkNodes = utils.returnRigModules()
            mover = utils.findMoverNodeFromJointName(networkNodes, parent)

        # delete the old constraint and create the new one
        if cmds.objExists(self.name + "_mover_grp_parentConstraint*"):
            cmds.delete(self.name + "_mover_grp_parentConstraint*")

        if mover != None:
            cmds.parentConstraint(mover, self.name + "_mover_grp", mo=True)

        if cmds.objExists(self.name + "_mover_grp_scaleConstraint*"):
            cmds.delete(self.name + "_mover_grp_scaleConstraint*")

        if mover != None:
            cmds.scaleConstraint(mover, self.name + "_mover_grp", mo=True)

        # create the connection geo between the two
        childMover = utils.findOffsetMoverFromName(name)
        riggingUtils.createBoneConnection(mover, childMover, name)
        self.applyModuleChanges(self)

        self.aimMode_Setup(True)

        cmds.select(clear=True)

        # if there were any module dependencies, fix those now.
        if len(attachedModules) > 0:
            elementList = []

            # first set parent to root mover since it will always be there
            for each in attachedModules:
                elementList.append([each[2], "  -> parent changed from:  ", each[1], "  to:  ", "root\n"])
                currentParent = cmds.listRelatives(each[2] + "_mover_grp", parent=True)[0]
                if currentParent != "root_mover":
                    cmds.parentConstraint("root_mover", each[2] + "_mover_grp", mo=True)
                    cmds.scaleConstraint("root_mover", each[2] + "_mover_grp", mo=True)
                    cmds.setAttr(each[0] + ".parentModuleBone", lock=False)
                    cmds.setAttr(each[0] + ".parentModuleBone", "root", type="string", lock=True)

                    # then, update settings UI for those dependency modules to display new parent info
                    modules = self.getAllModules

                    if each[0] in modules:
                        modName = cmds.getAttr(each[0] + ".moduleName")

                        for modInst in self.rigUiInst.moduleInstances:
                            if modInst.networkNode == each[0]:
                                # find the current groupBox for this module
                                for i in range(self.rigUiInst.moduleSettingsLayout.count()):
                                    if type(self.rigUiInst.moduleSettingsLayout.itemAt(
                                            i).widget()) == QtWidgets.QGroupBox:
                                        if self.rigUiInst.moduleSettingsLayout.itemAt(i).widget().title() == modName:
                                            self.rigUiInst.moduleSettingsLayout.itemAt(i).widget().setParent(None)

                                            # relaunch the skeleton settings UI with new info
                                            modInst.skeletonSettings_UI(modName)

                # create the connection geo between the two
                mover = "root_mover"
                childMover = utils.findOffsetMoverFromName(each[2])
                riggingUtils.createBoneConnection(mover, childMover, each[2])
                each[3].applyModuleChanges(each[3])
                cmds.select(clear=True)

            # warn user about changes
            winParent = interfaceUtils.getMainWindow()
            win = interfaceUtils.DialogMessage("Attention!",
                                               "The following modules have had their parent changed due\
                                                to the change in this module's structure:",
                                               elementList, 5, winParent)
            win.show()

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

        # add the pelvis
        self.outlinerWidgets[self.name + "_pelvis"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_pelvis"].setText(0, self.name + "_pelvis")
        self.createGlobalMoverButton(self.name + "_pelvis", self.outlinerWidgets[self.name + "_pelvis"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_pelvis", self.outlinerWidgets[self.name + "_pelvis"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_pelvis", self.outlinerWidgets[self.name + "_pelvis"], self.rigUiInst)

        # add spine01
        self.outlinerWidgets[self.name + "_spine_01"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_spine_01"].setText(0, self.name + "_spine_01")
        self.createGlobalMoverButton(self.name + "_spine_01", self.outlinerWidgets[self.name + "_spine_01"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_spine_01", self.outlinerWidgets[self.name + "_spine_01"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_spine_01", self.outlinerWidgets[self.name + "_spine_01"],
                                   self.rigUiInst)

        # add spine02
        self.outlinerWidgets[self.name + "_spine_02"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_spine_01"])
        self.outlinerWidgets[self.name + "_spine_02"].setText(0, self.name + "_spine_02")
        self.createGlobalMoverButton(self.name + "_spine_02", self.outlinerWidgets[self.name + "_spine_02"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_spine_02", self.outlinerWidgets[self.name + "_spine_02"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_spine_02", self.outlinerWidgets[self.name + "_spine_02"],
                                   self.rigUiInst)

        # add spine03
        self.outlinerWidgets[self.name + "_spine_03"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_spine_02"])
        self.outlinerWidgets[self.name + "_spine_03"].setText(0, self.name + "_spine_03")
        self.createGlobalMoverButton(self.name + "_spine_03", self.outlinerWidgets[self.name + "_spine_03"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_spine_03", self.outlinerWidgets[self.name + "_spine_03"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_spine_03", self.outlinerWidgets[self.name + "_spine_03"],
                                   self.rigUiInst)

        # add spine04
        self.outlinerWidgets[self.name + "_spine_04"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_spine_03"])
        self.outlinerWidgets[self.name + "_spine_04"].setText(0, self.name + "_spine_04")
        self.createGlobalMoverButton(self.name + "_spine_04", self.outlinerWidgets[self.name + "_spine_04"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_spine_04", self.outlinerWidgets[self.name + "_spine_04"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_spine_04", self.outlinerWidgets[self.name + "_spine_04"],
                                   self.rigUiInst)

        # add spine05
        self.outlinerWidgets[self.name + "_spine_05"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_spine_04"])
        self.outlinerWidgets[self.name + "_spine_05"].setText(0, self.name + "_spine_05")
        self.createGlobalMoverButton(self.name + "_spine_05", self.outlinerWidgets[self.name + "_spine_05"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_spine_05", self.outlinerWidgets[self.name + "_spine_05"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_spine_05", self.outlinerWidgets[self.name + "_spine_05"],
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
    def updateOutliner(self):

        # whenever changes are made to the module settings, update the outliner to show the new or removed movers

        # PELVIS

        if not self.pelvisCB.isChecked():
            self.outlinerWidgets[self.originalName + "_pelvis"].setHidden(True)
        else:
            self.outlinerWidgets[self.originalName + "_pelvis"].setHidden(False)

        # SPINE
        numSpine = self.numSpine.value()
        if numSpine == 2:
            self.outlinerWidgets[self.originalName + "_spine_03"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_spine_04"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_spine_05"].setHidden(True)
        if numSpine == 3:
            self.outlinerWidgets[self.originalName + "_spine_03"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_spine_04"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_spine_05"].setHidden(True)
        if numSpine == 4:
            self.outlinerWidgets[self.originalName + "_spine_03"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_spine_04"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_spine_05"].setHidden(True)
        if numSpine == 5:
            self.outlinerWidgets[self.originalName + "_spine_03"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_spine_04"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_spine_05"].setHidden(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def includePelvis(self, *args):
        state = self.pelvisCB.isChecked()

        if state == False:

            # hide clavicle mover controls
            cmds.setAttr(self.name + "_pelvis_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_pelvis_mover_grp.v", 0, lock=True)

            # parent upperarm to mover_grp
            try:
                cmds.parent(self.name + "_spine_01_mover_grp", self.name + "_mover_grp")
            except Exception, e:
                print e

        if state == True:

            # show clavicle mover controls
            cmds.setAttr(self.name + "_pelvis_mover_grp.v", lock=False)
            cmds.setAttr(self.name + "_pelvis_mover_grp.v", 1, lock=True)

            # parent upperarm to mover_grp
            try:
                cmds.parent(self.name + "_spine_01_mover_grp", self.name + "_pelvis_mover")
            except Exception, e:
                print e

        networkNode = self.returnNetworkNode
        cmds.setAttr(networkNode + ".includePelvis", lock=False)
        cmds.setAttr(networkNode + ".includePelvis", state, lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateSettingsUI(self):

        # this function will update the settings UI when the UI is launched based on the network node settings in the scene
        networkNode = self.returnNetworkNode

        includePelvis = cmds.getAttr(networkNode + ".includePelvis")
        numSpine = cmds.getAttr(networkNode + ".spineJoints")

        # update UI elements
        self.numSpine.setValue(numSpine)
        self.pelvisCB.setChecked(includePelvis)

        # apply changes
        self.applyButton.setEnabled(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createContextMenu(self, point):

        networkNode = self.returnNetworkNode

        # icons
        icon_reset = QtGui.QIcon(os.path.join(self.iconsPath, "System/reset.png"))
        icon_delete = QtGui.QIcon(os.path.join(self.iconsPath, "System/delete.png"))

        # create the context menu
        if networkNode != "ART_Root_Module":
            self.contextMenu = QtWidgets.QMenu()
            self.contextMenu.addAction(icon_reset, "Reset Settings", self.resetSettings)

            self.contextMenu.addSeparator()

            self.contextMenu.addAction(icon_delete, "Delete Module", self.deleteModule)
            self.contextMenu.exec_(self.groupBox.mapToGlobal(point))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetSettings(self):

        self.pelvisCB.setChecked(True)
        self.numSpine.setValue(3)

        # relaunch the UI
        self.applyModuleChanges(self)
        self.updateSettingsUI()

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
        numSpine = cmds.getAttr(networkNode + ".spineJoints")

        # setup aim vector details per side
        aimVector = [1, 0, 0]
        aimUp = [0, 1, 0]

        # if passed in state is True:
        if state:
            # setup aim constraints

            # pelvis
            cmds.aimConstraint(name + "_spine_01_lra", name + "_pelvis_mover_offset", aimVector=aimVector,
                               upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

            if numSpine == 2:
                cmds.aimConstraint(name + "_spine_02_lra", name + "_spine_01_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

            if numSpine == 3:
                cmds.aimConstraint(name + "_spine_02_lra", name + "_spine_01_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_03_lra", name + "_spine_02_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

            if numSpine == 4:
                cmds.aimConstraint(name + "_spine_02_lra", name + "_spine_01_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_03_lra", name + "_spine_02_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_04_lra", name + "_spine_03_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

            if numSpine == 5:
                cmds.aimConstraint(name + "_spine_02_lra", name + "_spine_01_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_03_lra", name + "_spine_02_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_04_lra", name + "_spine_03_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

                cmds.aimConstraint(name + "_spine_05_lra", name + "_spine_04_mover_offset", aimVector=aimVector,
                                   upVector=aimUp, wut="vector", wu=[0, 1, 0], mo=True)

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
    def pinModule(self, state):

        networkNode = self.returnNetworkNode
        includeClav = cmds.getAttr(networkNode + ".includePelvis")

        if state:
            if includeClav:
                topLevelMover = self.name + "_pelvis_mover_grp"
            else:
                topLevelMover = self.name + "_spine_01_mover_grp"

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
        buildIK = True

        # have it build all rigs by default, unless there is an attr stating otherwise (backwards- compatability)
        numRigs = 0
        if cmds.objExists(networkNode + ".buildFK"):
            buildFK = cmds.getAttr(networkNode + ".buildFK")
            if buildFK:
                numRigs += 1
        if cmds.objExists(networkNode + ".buildIK"):
            buildIK_V1 = cmds.getAttr(networkNode + ".buildIK")
            if buildIK_V1:
                numRigs += 1

        builtRigs = []

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # create groups and settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create the spine group
        spineJoints = self.returnCreatedJoints
        self.spineGroup = cmds.group(empty=True, name=self.name + "_group")
        constraint = cmds.parentConstraint(spineJoints[0], self.spineGroup)[0]
        cmds.delete(constraint)

        joints = []
        for jnt in spineJoints:
            if jnt.find("pelvis") == -1:
                joints.append(jnt)

        # create the spine settings group
        self.spineSettings = cmds.group(empty=True, name=self.name + "_settings")
        cmds.parent(self.spineSettings, self.spineGroup)
        for attr in (cmds.listAttr(self.spineSettings, keyable=True)):
            cmds.setAttr(self.spineSettings + "." + attr, lock=True, keyable=False)

        # create the ctrl group (what will get the constraint to the parent)
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        self.spineCtrlGrp = cmds.group(empty=True, name=self.name + "_spine_ctrl_grp")

        constraint = cmds.parentConstraint("driver_" + parentBone, self.spineCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.spineCtrlGrp, self.spineGroup)
        cmds.makeIdentity(self.spineCtrlGrp, t=1, r=1, s=1, apply=True)

        includePelvis = cmds.getAttr(networkNode + ".includePelvis")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # build the rigs
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        if includePelvis:
            self.buildHips(textEdit, uiInst, builtRigs, networkNode)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       FK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # if build FK was true, build the FK rig now
        if buildFK:
            fkInfo = self.buildFkSpine(textEdit, uiInst, builtRigs, networkNode)
            builtRigs.append(["FK", fkInfo])  # [1] = nodes to hide

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #                       IK                      # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # if build IK was true, build the IK rig now
        if buildIK:
            ikInfo = self.buildIKSpine(textEdit, uiInst, builtRigs, networkNode)
            if len(joints) > 2:
                builtRigs.append(["IK", ikInfo])  # [1] = nodes to hide

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #            Hook up FK/IK Switching            # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # add mode attribute to settings
        if len(builtRigs) > 1:
            cmds.addAttr(self.spineSettings, ln="mode", min=0, max=numRigs - 1, dv=0, keyable=True)

        # mode
        if len(builtRigs) > 1:
            attrData = []
            rampData = []

            """ CONSTRAINTS """
            # get the constraint connections on the driver joints for the arms
            connections = []
            for joint in spineJoints:
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

                cmds.setAttr(self.spineSettings + ".mode", i)

                # go through attr data and zero out anything but the first element in the list
                for data in attrData:
                    for each in data:
                        cmds.setAttr(each[0], 0)

                    cmds.setAttr(data[i][0], 1)

                # set driven keys
                for data in attrData:
                    for each in data:
                        cmds.setDrivenKeyframe(each[0], cd=self.spineSettings + ".mode", itt="linear", ott="linear")

            """ RAMPS """
            # direct connect mode to uCoord value (only works if there are 2 rigs...) <- not sure if that is the case still
            for data in rampData:
                # create a multiply node that takes first input of 1/numRigs and 2nd of mode direct connection
                multNode = cmds.shadingNode("multiplyDivide", asUtility=True,
                                            name=self.name + "_" + data.partition(".uCoord")[0] + "_mult")
                cmds.setAttr(multNode + ".input1X", float(float(1) / float(numRigs - 1)))
                cmds.connectAttr(self.spineSettings + ".mode", multNode + ".input2X")
                cmds.connectAttr(multNode + ".outputX", data)

            # hook up control visibility
            for i in range(len(builtRigs)):
                cmds.setAttr(self.spineSettings + ".mode", i)
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

                    cmds.setDrivenKeyframe(visNodes, at="visibility", cd=self.spineSettings + ".mode", itt="linear",
                                           ott="linear")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #            Parent Under Offset Ctrl           # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # parent under offset_anim if it exists(it always should)
        if cmds.objExists("offset_anim"):
            cmds.parent(self.spineGroup, "offset_anim")

        # return data
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        try:
            uiInst.rigData.append([self.spineCtrlGrp, "driver_" + parentBone, numRigs])
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildHips(self, textEdit, uiInst, builtRigs, networkNode):

        # update progress
        if textEdit != None:
            textEdit.append("        Building Pelvis Rig..")

        # find the joints in the spine module that need rigging
        allJnts = self.returnCreatedJoints
        joints = []
        for jnt in allJnts:
            if jnt.find("pelvis") != -1:
                joints.append(jnt)

        # create the grp and position and orient it correctly
        controlInfo = riggingUtils.createControlFromMover(joints[0], networkNode, True, True)
        self.bodyAnim = riggingUtils.createControl("square", 50, self.name + "_body_anim", True)

        constraint = cmds.pointConstraint(controlInfo[0], self.bodyAnim)[0]
        cmds.delete([constraint, controlInfo[0]])

        cmds.parent(self.bodyAnim, controlInfo[1])
        cmds.makeIdentity(self.bodyAnim, t=1, r=1, s=1, apply=True)

        self.bodyAnimGrp = cmds.rename(controlInfo[1], self.name + "_body_anim_grp")
        self.bodyAnimSpace = cmds.rename(controlInfo[2], self.name + "_body_anim_space_switcher")
        self.bodyAnimFollow = cmds.rename(controlInfo[3], self.name + "_body_anim_space_switcher_follow")
        riggingUtils.colorControl(self.bodyAnim, 17)

        # Pelvis
        hipControlInfo = riggingUtils.createControlFromMover(joints[0], networkNode, True, False)
        self.hipAnim = cmds.rename(hipControlInfo[0], self.name + "_hip_anim")
        self.hipAnimGrp = cmds.rename(hipControlInfo[1], self.name + "_hip_anim_grp")
        riggingUtils.colorControl(self.hipAnim, 18)

        cmds.parent(self.hipAnimGrp, self.bodyAnim)

        for each in [self.bodyAnim, self.hipAnim]:
            for attr in [".scaleX", ".scaleY", ".scaleZ", ".visibility"]:
                cmds.setAttr(each + attr, lock=True, keyable=False)

        cmds.parent(self.bodyAnimFollow, self.spineCtrlGrp)

        # =======================================================================
        # #lastly, connect controls up to blender nodes to drive driver joints
        # =======================================================================
        cmds.pointConstraint(self.hipAnim, "driver_" + joints[0], mo=True)
        cmds.orientConstraint(self.hipAnim, "driver_" + joints[0])

        # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into input 2, and plugs that into driver joint
        if cmds.objExists("master_anim"):
            globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=joints[0] + "_globalScale")
            cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
            cmds.connectAttr(self.hipAnim + ".scale", globalScaleMult + ".input2")
            riggingUtils.createConstraint(globalScaleMult, "driver_" + joints[0], "scale", False, 2, 0, "output")
        else:
            riggingUtils.createConstraint(self.hipAnim, "driver_" + joints[0], "scale", False, 2, 0)

        # add created control info to module
        if not cmds.objExists(networkNode + ".pelvisControls"):
            cmds.addAttr(networkNode, ln="pelvisControls", dt="string")
        jsonString = json.dumps([self.hipAnim, self.bodyAnim])
        cmds.setAttr(networkNode + ".pelvisControls", jsonString, type="string")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildFkSpine(self, textEdit, uiInst, builtRigs, networkNode):

        # update progress
        if textEdit != None:
            textEdit.append("        Starting FK Spine Rig Build..")

        # build the rig
        slot = len(builtRigs)

        # find the joints in the spine module that need rigging
        allJnts = self.returnCreatedJoints
        joints = []

        for jnt in allJnts:
            if jnt.find("pelvis") == -1:
                joints.append(jnt)

        fkControls = []
        self.topNode = None
        includePelvis = cmds.getAttr(networkNode + ".includePelvis")

        for joint in joints:
            if joint == joints[0]:
                data = riggingUtils.createControlFromMover(joint, networkNode, True, True)

                fkControl = cmds.rename(data[0], "fk_" + joint + "_anim")
                animGrp = cmds.rename(data[1], "fk_" + joint + "_anim_grp")
                spaceSwitcher = cmds.rename(data[2], "fk_" + joint + "_anim_space_switcher")
                spaceSwitchFollow = cmds.rename(data[3], "fk_" + joint + "_anim_space_switcher_follow")
                self.topNode = spaceSwitchFollow

                fkControls.append([spaceSwitchFollow, fkControl, joint])
                # color the control
                riggingUtils.colorControl(fkControl, 18)


            else:
                data = riggingUtils.createControlFromMover(joint, networkNode, True, False)

                fkControl = cmds.rename(data[0], "fk_" + joint + "_anim")
                animGrp = cmds.rename(data[1], "fk_" + joint + "_anim_grp")

                fkControls.append([animGrp, fkControl, joint])

                # color the control
                riggingUtils.colorControl(fkControl, 18)

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

            # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into input 2, and plugs that into driver joint
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
        if includePelvis:
            cmds.parent(self.topNode, self.bodyAnim)
        else:
            cmds.parent(self.topNode, self.spineCtrlGrp)

        # lock attrs
        for each in fkControls:
            control = each[1]
            for attr in [".visibility"]:
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

        return [spaceSwitchFollow]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildIKSpine(self, textEdit, uiInst, builtRigs, networkNode):

        slot = len(builtRigs)

        # find the joints in the spine module that need rigging
        allJnts = self.returnCreatedJoints
        joints = []

        for jnt in allJnts:
            if jnt.find("pelvis") == -1:
                joints.append(jnt)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Start SplineIK creation
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        if len(joints) > 2:
            # duplicate the spine joints we'll need for the spline IK

            parent = None
            rigJoints = []

            for joint in joints:
                spineBone = cmds.duplicate(joint, parentOnly=True, name="splineIK_" + joint)[0]

                if parent != None:
                    cmds.parent(spineBone, parent)

                else:
                    cmds.parent(spineBone, world=True)

                parent = spineBone
                rigJoints.append(str(spineBone))

            # create spine twist joints that will be children of the spline IK joints. This will allow us to control twist distribution directly
            for joint in rigJoints:
                twistJoint = cmds.duplicate(joint, name="twist_" + joint, parentOnly=True)[0]
                cmds.parent(twistJoint, joint)

            # find the driver top and mid joints
            topDriverJoint = "driver_" + joints[-1]
            midDriverJoint = "driver_" + joints[len(joints) / 2]

            ###########################################################################################################
            ###########################################################################################################
            # create the spline IK
            ###########################################################################################################
            ###########################################################################################################

            ikNodes = cmds.ikHandle(sj=str(rigJoints[0]), ee=str(rigJoints[len(rigJoints) - 1]), sol="ikSplineSolver",
                                    createCurve=True, simplifyCurve=True, parentCurve=False,
                                    name=str(rigJoints[0]) + "_splineIK")
            ikHandle = ikNodes[0]
            ikCurve = ikNodes[2]
            ikCurve = cmds.rename(ikCurve, self.name + "_spine_splineIK_curve")
            cmds.setAttr(ikCurve + ".inheritsTransform", 0)
            cmds.setAttr(ikHandle + ".v", 0)
            cmds.setAttr(ikCurve + ".v", 0)

            # create the three joints to skin the curve to
            botJoint = cmds.duplicate(rigJoints[0], name=self.name + "_splineIK_bot_jnt", parentOnly=True)[0]
            topJoint = \
                cmds.duplicate(rigJoints[len(rigJoints) - 1], name=self.name + "_splineIK_top_jnt", parentOnly=True)[0]
            midJoint = cmds.duplicate(topJoint, name=self.name + "_splineIK_mid_jnt", parentOnly=True)[0]

            cmds.parent([botJoint, topJoint, midJoint], world=True)

            constraint = cmds.pointConstraint([botJoint, topJoint], midJoint)[0]
            cmds.delete(constraint)

            # any joint that is not the bottom or top joint needs to be point constrained to be evenly spread
            drivenConsts = []
            if len(joints) == 3:
                drivenConst1 = cmds.pointConstraint([midJoint, rigJoints[1]], "twist_" + rigJoints[1], mo=True)[0]
                cmds.setAttr(drivenConst1 + "." + rigJoints[1] + "W1", 0)
                drivenConsts.append(drivenConst1)

            if len(joints) == 4:
                drivenConst1 = \
                    cmds.pointConstraint([botJoint, midJoint, rigJoints[1]], "twist_" + rigJoints[1], mo=True)[0]
                drivenConst2 = \
                    cmds.pointConstraint([topJoint, midJoint, rigJoints[2]], "twist_" + rigJoints[2], mo=True)[0]

                cmds.setAttr(drivenConst1 + "." + rigJoints[1] + "W2", 0)
                cmds.setAttr(drivenConst2 + "." + rigJoints[2] + "W2", 0)
                drivenConsts.append(drivenConst1)
                drivenConsts.append(drivenConst2)

            if len(joints) == 5:
                drivenConst1 = \
                    cmds.pointConstraint([botJoint, midJoint, rigJoints[1]], "twist_" + rigJoints[1], mo=True)[0]
                drivenConst2 = cmds.pointConstraint([midJoint, rigJoints[2]], "twist_" + rigJoints[2], mo=True)[0]
                drivenConst3 = \
                    cmds.pointConstraint([midJoint, topJoint, rigJoints[3]], "twist_" + rigJoints[3], mo=True)[0]

                cmds.setAttr(drivenConst1 + "." + rigJoints[1] + "W2", 0)
                cmds.setAttr(drivenConst2 + "." + rigJoints[2] + "W1", 0)
                cmds.setAttr(drivenConst3 + "." + rigJoints[3] + "W2", 0)

                drivenConsts.append(drivenConst1)
                drivenConsts.append(drivenConst2)
                drivenConsts.append(drivenConst3)

            # skin the joints to the curve
            cmds.select([botJoint, topJoint, midJoint])
            skin = cmds.skinCluster([botJoint, topJoint, midJoint], ikCurve, toSelectedBones=True)[0]

            # skin weight the curve
            curveShape = cmds.listRelatives(ikCurve, shapes=True)[0]
            numSpans = cmds.getAttr(curveShape + ".spans")
            degree = cmds.getAttr(curveShape + ".degree")
            numCVs = numSpans + degree

            # this should always be the case, but just to be safe
            if numCVs == 4:
                cmds.skinPercent(skin, ikCurve + ".cv[0]", transformValue=[(botJoint, 1.0)])
                cmds.skinPercent(skin, ikCurve + ".cv[1]", transformValue=[(botJoint, 0.5), (midJoint, 0.5)])
                cmds.skinPercent(skin, ikCurve + ".cv[2]", transformValue=[(midJoint, 0.5), (topJoint, 0.5)])
                cmds.skinPercent(skin, ikCurve + ".cv[3]", transformValue=[(topJoint, 1.0)])

            ###########################################################################################################
            ###########################################################################################################
            # create the spline IK controls
            ###########################################################################################################
            ###########################################################################################################

            ikControls = []

            ###############################################
            # TOP CTRL
            ###############################################

            data = riggingUtils.createControlFromMover(joints[-1], networkNode, True, True)

            topCtrl = cmds.rename(data[0], self.name + "_chest_ik_anim")
            animGrp = cmds.rename(data[1], self.name + "_chest_ik_anim_grp")
            driverGrp = cmds.duplicate(animGrp, parentOnly=True, name=self.name + "_chest_ik_anim_driver_grp")[0]
            spaceSwitcher = cmds.rename(data[2], self.name + "_chest_ik_anim_space_switcher")
            spaceSwitchFollow = cmds.rename(data[3], self.name + "_chest_ik_anim_space_switcher_follow")

            self.topNode = spaceSwitchFollow

            ikControls.append([spaceSwitchFollow, topCtrl, joints[-1]])

            cmds.parent(driverGrp, animGrp)
            cmds.parent(topCtrl, driverGrp)
            cmds.parent(topJoint, topCtrl)

            # color the control
            riggingUtils.colorControl(topCtrl, 17)

            ###############################################
            # MID CTRL
            ###############################################

            data = riggingUtils.createControlFromMover(joints[len(joints) / 2], networkNode, True, False)

            midCtrl = cmds.rename(data[0], self.name + "_mid_ik_anim")
            midGrp = cmds.rename(data[1], self.name + "_mid_ik_anim_grp")
            midDriver = cmds.duplicate(midGrp, parentOnly=True, name=self.name + "_mid_ik_anim_driver_grp")[0]
            midDriverTrans = cmds.duplicate(midGrp, parentOnly=True, name=self.name + "_mid_ik_anim_trans_driver_grp")[
                0]

            cmds.parent(midCtrl, midDriver)
            cmds.parent(midDriver, midDriverTrans)
            cmds.parent(midDriverTrans, midGrp)
            cmds.parent(midJoint, midCtrl)
            ikControls.append([midGrp, midCtrl, joints[len(joints) / 2]])

            # color the control
            riggingUtils.colorControl(midCtrl, 18)

            ###############################################
            # BOT CTRL
            ###############################################
            includePelvis = cmds.getAttr(networkNode + ".includePelvis")

            if includePelvis:
                cmds.parent(botJoint, self.hipAnim)

            else:
                cmds.parent(botJoint, self.spineCtrlGrp)

            ###########################################################################################################
            ###########################################################################################################
            # ADDING STRETCH
            ###########################################################################################################
            ###########################################################################################################

            # add the attr to the top ctrl
            cmds.addAttr(topCtrl, longName='stretch', defaultValue=0, minValue=0, maxValue=1, keyable=True)
            cmds.addAttr(topCtrl, longName='squash', defaultValue=0, minValue=0, maxValue=1, keyable=True)

            # create the curveInfo node#find
            cmds.select(ikCurve)
            curveInfoNode = cmds.arclen(cmds.ls(sl=True), ch=True, name=self.name + "_splineIK_curveInfo")
            originalLength = cmds.getAttr(curveInfoNode + ".arcLength")

            # create the multiply/divide node that will get the scale factor
            divideNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_splineIK_scaleFactor")
            divideNode_Inverse = cmds.shadingNode("multiplyDivide", asUtility=True,
                                                  name=self.name + "_splineIK_inverse")
            cmds.setAttr(divideNode + ".operation", 2)
            cmds.setAttr(divideNode + ".input2X", originalLength)
            cmds.setAttr(divideNode_Inverse + ".operation", 2)
            cmds.setAttr(divideNode_Inverse + ".input1X", originalLength)

            # create the blendcolors node
            blenderNode = cmds.shadingNode("blendColors", asUtility=True, name=self.name + "_splineIK_blender")
            cmds.setAttr(blenderNode + ".color2R", 1)

            blenderNode_Inverse = cmds.shadingNode("blendColors", asUtility=True,
                                                   name=self.name + "_splineIK_blender_inverse")
            cmds.setAttr(blenderNode_Inverse + ".color2R", 1)

            # connect attrs
            cmds.connectAttr(curveInfoNode + ".arcLength", divideNode + ".input1X")
            cmds.connectAttr(curveInfoNode + ".arcLength", divideNode_Inverse + ".input2X")
            cmds.connectAttr(divideNode + ".outputX", blenderNode + ".color1R")
            cmds.connectAttr(divideNode_Inverse + ".outputX", blenderNode_Inverse + ".color1R")

            cmds.connectAttr(topCtrl + ".stretch", blenderNode + ".blender")
            cmds.connectAttr(topCtrl + ".squash", blenderNode_Inverse + ".blender")

            # find ctrl upAxis
            upAxis = self.getUpAxis(topCtrl)
            if upAxis == "X":
                axisB = "Y"
                axisC = "Z"
            if upAxis == "Y":
                axisB = "X"
                axisC = "Z"
            if upAxis == "Z":
                axisB = "X"
                axisC = "Y"

            # apply squash and stretch to joints
            for i in range(len(rigJoints)):
                children = cmds.listRelatives(rigJoints[i], children=True)
                for child in children:
                    if child.find("twist") != -1:
                        twistJoint = child

                cmds.connectAttr(blenderNode_Inverse + ".outputR", twistJoint + ".scale" + axisB)
                cmds.connectAttr(blenderNode_Inverse + ".outputR", twistJoint + ".scale" + axisC)

            cmds.connectAttr(blenderNode + ".outputR", rigJoints[0] + ".scale" + upAxis)

            # setup drivenConst to only be active when stretch is on
            for const in drivenConsts:
                targets = cmds.getAttr(const + ".target", mi=True)
                for each in targets:
                    attr = cmds.listConnections(const + ".target[" + str(each) + "].targetWeight", p=True)

                    cmds.setAttr(topCtrl + ".stretch", 1)
                    cmds.setDrivenKeyframe(attr[0], cd=topCtrl + ".stretch")

                    cmds.setAttr(topCtrl + ".stretch", 0)
                    if len(joints) == 3:
                        if const == drivenConst1:
                            if each == targets[0]:
                                cmds.setAttr(attr[0], 0)
                            if each == targets[1]:
                                cmds.setAttr(attr[0], 1)

                    if len(joints) == 4:
                        if each == targets[2]:
                            cmds.setAttr(attr[0], 1)
                        else:
                            cmds.setAttr(attr[0], 0)

                    if len(joints) == 5:
                        if const == drivenConst1:
                            if each == targets[2]:
                                cmds.setAttr(attr[0], 1)
                            else:
                                cmds.setAttr(attr[0], 0)

                        if const == drivenConst2:
                            if each == targets[1]:
                                cmds.setAttr(attr[0], 1)
                            else:
                                cmds.setAttr(attr[0], 0)

                        if const == drivenConst3:
                            if each == targets[2]:
                                cmds.setAttr(attr[0], 1)
                            else:
                                cmds.setAttr(attr[0], 0)

                    cmds.setDrivenKeyframe(attr[0], cd=topCtrl + ".stretch")

            ###########################################################################################################
            ###########################################################################################################
            # ADDING TWiST
            ###########################################################################################################
            ###########################################################################################################

            # add twist amount attrs and setup
            cmds.select(topCtrl)
            cmds.addAttr(longName='twist_amount', defaultValue=1, minValue=0, keyable=True)

            # find number of spine joints and divide 1 by numSpineJoints
            num = len(joints)
            val = 1.0 / float(num)
            twistamount = val

            locGrp = cmds.group(empty=True, name=self.name + "_spineIK_twist_grp")
            if includePelvis:
                cmds.parent(locGrp, self.bodyAnim)

            else:
                cmds.parent(locGrp, self.spineCtrlGrp)

            for i in range(int(num - 1)):

                # create a locator that will be orient constrained between the body and chest
                locator = cmds.spaceLocator(name=joints[i] + "_twistLoc")[0]
                group = cmds.group(empty=True, name=joints[i] + "_twistLocGrp")
                constraint = cmds.parentConstraint(joints[i], locator)[0]
                cmds.delete(constraint)
                constraint = cmds.parentConstraint(joints[i], group)[0]
                cmds.delete(constraint)
                cmds.parent(locator, group)
                cmds.parent(group, locGrp)
                cmds.setAttr(locator + ".v", 0, lock=True)

                # duplicate the locator and parent it under the group. This will be the locator that takes the rotation x twist amount and gives us the final value

                orientLoc = cmds.duplicate(locator, name=joints[i] + "_orientLoc")[0]
                cmds.parent(orientLoc, locator)
                cmds.makeIdentity(orientLoc, t=1, r=1, s=1, apply=True)

                # set weights on constraint
                firstValue = 1 - twistamount
                secondValue = 1 - firstValue

                # create constraints between body/chest
                if includePelvis:
                    constraint = cmds.orientConstraint([self.bodyAnim, topCtrl], locator)[0]
                    cmds.setAttr(constraint + "." + self.bodyAnim + "W0", firstValue)
                    cmds.setAttr(constraint + "." + topCtrl + "W1", secondValue)

                else:
                    # find module's parent bone
                    constraint = cmds.orientConstraint([rigJoints[i], topCtrl], locator)[0]
                    cmds.setAttr(constraint + "." + rigJoints[i] + "W0", firstValue)
                    cmds.setAttr(constraint + "." + topCtrl + "W1", secondValue)

                # factor in twist amount
                twistMultNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=joints[i] + "_twist_amount")

                # expose the twistAmount on the control as an attr
                cmds.connectAttr(topCtrl + ".twist_amount", twistMultNode + ".input2X")
                cmds.connectAttr(topCtrl + ".twist_amount", twistMultNode + ".input2Y")
                cmds.connectAttr(topCtrl + ".twist_amount", twistMultNode + ".input2Z")
                cmds.connectAttr(locator + ".rotate", twistMultNode + ".input1")

                cmds.connectAttr(twistMultNode + ".output", orientLoc + ".rotate")

                # constrain the spine joint to the orientLoc
                if upAxis == "X":
                    skipped = ["y", "z"]
                if upAxis == "Y":
                    skipped = ["x", "z"]
                if upAxis == "Z":
                    skipped = ["x", "y"]

                cmds.orientConstraint([locator, rigJoints[i]], orientLoc, mo=True)
                cmds.orientConstraint(orientLoc, "twist_splineIK_" + joints[i])
                twistamount = twistamount + val

            # =======================================================================
            # #connect controls up to blender nodes to drive driver joints
            # =======================================================================
            for joint in joints:

                rigJnt = "twist_splineIK_" + joint

                if joint == joints[len(joints) - 1]:
                    cmds.pointConstraint(rigJnt, "driver_" + joint, mo=True)
                    cmds.orientConstraint(topJoint, "driver_" + joint)

                else:
                    cmds.pointConstraint(rigJnt, "driver_" + joint, mo=True)
                    cmds.orientConstraint(rigJnt, "driver_" + joint)

                # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale into input 2, and plugs that into driver joint
                if cmds.objExists("master_anim"):
                    globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=joint + "_globalScale")
                    cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
                    cmds.connectAttr(rigJnt + ".scale", globalScaleMult + ".input2")
                    riggingUtils.createConstraint(globalScaleMult, "driver_" + joint, "scale", False, 2, slot, "output")
                else:
                    riggingUtils.createConstraint(rigJnt, "driver_" + joint, "scale", False, 2, slot)

            # =======================================================================
            # #clean things up
            # =======================================================================

            # parent the components to the body anim or parent module bone

            if includePelvis:
                cmds.parent(midGrp, self.bodyAnim)
            else:
                cmds.parent(midGrp, self.spineCtrlGrp)

            # ensure after parenting the midGrp that everything is still nice and zeroed out.
            cmds.parent(midCtrl, world=True)
            cmds.parent(midJoint, world=True)

            for attr in [".rx", ".ry", ".rz"]:
                cmds.setAttr(midGrp + attr, 0)

            cmds.parent(midCtrl, midDriver)
            cmds.makeIdentity(midCtrl, t=1, r=1, s=0, apply=True)
            cmds.parent(midJoint, midCtrl)

            # parent the chest ik space switcher follow node to the body anim or parent module bone
            if includePelvis:
                cmds.parent(spaceSwitchFollow, self.bodyAnim)
            else:
                cmds.parent(spaceSwitchFollow, self.spineCtrlGrp)

            # ensure after parenting the space switcher follow for the ik chest, that everything is still nice and zeroed out.
            cmds.parent(topCtrl, world=True)
            cmds.parent(topJoint, world=True)
            for attr in [".rx", ".ry", ".rz"]:
                if cmds.getAttr(spaceSwitchFollow + attr) < 45:
                    if cmds.getAttr(spaceSwitchFollow + attr) > 0:
                        cmds.setAttr(spaceSwitchFollow + attr, 0)

                if cmds.getAttr(spaceSwitchFollow + attr) >= 80:
                    if cmds.getAttr(spaceSwitchFollow + attr) < 90:
                        cmds.setAttr(spaceSwitchFollow + attr, 90)

                if cmds.getAttr(spaceSwitchFollow + attr) > 90:
                    if cmds.getAttr(spaceSwitchFollow + attr) < 100:
                        cmds.setAttr(spaceSwitchFollow + attr, 90)

                if cmds.getAttr(spaceSwitchFollow + attr) <= -80:
                    if cmds.getAttr(spaceSwitchFollow + attr) > -90:
                        cmds.setAttr(spaceSwitchFollow + attr, -90)

                if cmds.getAttr(spaceSwitchFollow + attr) > -90:
                    if cmds.getAttr(spaceSwitchFollow + attr) < -100:
                        cmds.setAttr(spaceSwitchFollow + attr, -90)

            cmds.parent(topCtrl, driverGrp)
            cmds.makeIdentity(topCtrl, t=1, r=1, s=0, apply=True)
            cmds.parent(topJoint, topCtrl)

            # =======================================================================
            # #ensure top spine joint stays pinned to top ctrl
            # =======================================================================

            children = cmds.listRelatives(rigJoints[len(rigJoints) - 1], children=True)
            for child in children:
                if child.find("twist") != -1:
                    twistJoint = child

            topSpineBone = twistJoint.partition("twist_")[2]
            topSpineJointConstraint = cmds.pointConstraint([topJoint, topSpineBone], twistJoint)[0]

            # connect attr on top spine joint constraint
            targets = cmds.pointConstraint(topSpineJointConstraint, q=True, weightAliasList=True)

            cmds.connectAttr(topCtrl + ".stretch", topSpineJointConstraint + "." + targets[0])

            conditionNode = cmds.shadingNode("condition", asUtility=True, name=self.name + "_twist_stretch_toggle")
            cmds.connectAttr(topCtrl + ".stretch", conditionNode + ".firstTerm")
            cmds.setAttr(conditionNode + ".secondTerm", 1)
            cmds.setAttr(conditionNode + ".colorIfTrueR", 0)

            minusNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=self.name + "_twist_stretch_minus")
            cmds.setAttr(minusNode + ".operation", 2)
            cmds.connectAttr(conditionNode + ".secondTerm", minusNode + ".input1D[0]")
            cmds.connectAttr(topCtrl + ".stretch", minusNode + ".input1D[1]")
            cmds.connectAttr(minusNode + ".output1D", topSpineJointConstraint + "." + targets[1])

            # =======================================================================
            # #create stretch meter attr
            # =======================================================================
            cmds.addAttr(topCtrl, longName='stretchFactor', keyable=True)
            cmds.connectAttr(divideNode + ".outputX", topCtrl + ".stretchFactor")
            cmds.setAttr(topCtrl + ".stretchFactor", lock=True)

            cmds.addAttr(midCtrl, longName='stretchFactor', keyable=True)
            cmds.connectAttr(topCtrl + ".stretchFactor", midCtrl + ".stretchFactor")
            cmds.setAttr(midCtrl + ".stretchFactor", lock=True)

            # =======================================================================
            # #lock and hide attrs that should not be keyable
            # =======================================================================

            for control in [topCtrl, midCtrl]:
                for attr in [".sx", ".sy", ".sz", ".v"]:
                    cmds.setAttr(control + attr, keyable=False, lock=True)

            # =======================================================================
            # #organize scene
            # =======================================================================
            IKgrp = cmds.group(empty=True, name=self.name + "_ik_grp")
            cmds.parent(IKgrp, self.spineCtrlGrp)

            cmds.parent(ikCurve, IKgrp)
            cmds.parent(ikHandle, IKgrp)
            cmds.parent(rigJoints[0], IKgrp)

            for jnt in rigJoints:
                cmds.setAttr(jnt + ".v", 0, lock=True)

            for jnt in [botJoint, midJoint, topJoint]:
                cmds.setAttr(jnt + ".v", 0, lock=True)

            # =======================================================================
            # #create matching nodes
            # =======================================================================
            chest_match_node = cmds.duplicate(topCtrl, po=True, name=topCtrl + "_MATCH")
            cmds.parent(chest_match_node, topDriverJoint)

            mid_match_node = cmds.duplicate(midCtrl, po=True, name=midCtrl + "_MATCH")
            cmds.parent(mid_match_node, midDriverJoint)

            # =======================================================================
            # #setup auto spine
            # =======================================================================
            self.setupAutoSpine(textEdit, uiInst, builtRigs, networkNode, midDriver, midDriverTrans, topCtrl, botJoint)

            # add created control info to module
            if not cmds.objExists(networkNode + ".ikControls"):
                cmds.addAttr(networkNode, ln="ikControls", dt="string")
            jsonString = json.dumps([topCtrl, midCtrl])
            cmds.setAttr(networkNode + ".ikControls", jsonString, type="string")

            return [spaceSwitchFollow, midGrp]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def setupAutoSpine(self, textEdit, uiInst, builtRigs, networkNode, midDriver, midDriverTrans, topCtrl, botJnt):

        cmds.addAttr(topCtrl, longName='autoSpine', defaultValue=0, minValue=0, maxValue=1, keyable=True)
        cmds.addAttr(topCtrl, longName='rotationInfluence', defaultValue=.25, minValue=0, maxValue=1, keyable=True)

        topCtrlMultRY = cmds.shadingNode("multiplyDivide", asUtility=True,
                                         name=self.name + "_autoSpine_top_driver_mult_ry")
        topCtrlMultRZ = cmds.shadingNode("multiplyDivide", asUtility=True,
                                         name=self.name + "_autoSpine_top_driver_mult_rz")
        topCtrlMultSwitchRY = cmds.shadingNode("multiplyDivide", asUtility=True,
                                               name=self.name + "_autoSpine_top_mult_switch_ry")
        topCtrlMultSwitchRZ = cmds.shadingNode("multiplyDivide", asUtility=True,
                                               name=self.name + "_autoSpine_top_mult_switch_rz")

        # =======================================================================
        # create a node that will track all world space translations and rotations on the chest IK anim
        # =======================================================================
        chestMasterTrackNode = cmds.spaceLocator(name=self.name + "_chest_ik_track_parent")[0]
        constraint = cmds.parentConstraint(topCtrl, chestMasterTrackNode)[0]
        cmds.delete(constraint)

        chestTrackNode = cmds.spaceLocator(name=self.name + "_chest_ik_tracker")[0]
        constraint = cmds.parentConstraint(topCtrl, chestTrackNode)[0]
        cmds.delete(constraint)

        cmds.parent(chestTrackNode, chestMasterTrackNode)
        cmds.parentConstraint(topCtrl, chestTrackNode)

        if cmds.getAttr(networkNode + ".includePelvis"):
            cmds.parent(chestMasterTrackNode, self.bodyAnim)
        else:
            cmds.parent(chestMasterTrackNode, self.spineCtrlGrp)

        # hide locator
        cmds.setAttr(chestMasterTrackNode + ".v", 0)

        botJntLoc = cmds.group(empty=True, name=self.name + "_botJnt_tracker")
        constraint = cmds.parentConstraint(botJnt, botJntLoc)[0]
        cmds.delete(constraint)
        cmds.parent(botJntLoc, botJnt)
        cmds.makeIdentity(botJntLoc, t=1, r=1, s=1, apply=True)
        cmds.parentConstraint(botJnt, botJntLoc)[0]

        # =======================================================================
        # Rotate Y
        # =======================================================================
        cmds.connectAttr(chestTrackNode + ".ry", topCtrlMultRY + ".input1X")
        cmds.connectAttr(topCtrl + ".rotationInfluence", topCtrlMultRY + ".input2X")

        cmds.connectAttr(topCtrlMultRY + ".outputX", topCtrlMultSwitchRY + ".input1X")
        cmds.connectAttr(topCtrl + ".autoSpine", topCtrlMultSwitchRY + ".input2X")
        cmds.connectAttr(topCtrlMultSwitchRY + ".outputX", midDriver + ".tz")

        # =======================================================================
        # Rotate Z
        # =======================================================================
        multInverse = cmds.shadingNode("multiplyDivide", asUtility=True, name=self.name + "_autoSpine_mult_rz_inverse")
        cmds.connectAttr(topCtrl + ".rotationInfluence", multInverse + ".input1X")
        cmds.setAttr(multInverse + ".input2X", -1)

        cmds.connectAttr(chestTrackNode + ".rz", topCtrlMultRZ + ".input1X")
        cmds.connectAttr(multInverse + ".outputX", topCtrlMultRZ + ".input2X")

        cmds.connectAttr(topCtrlMultRZ + ".outputX", topCtrlMultSwitchRZ + ".input1X")
        cmds.connectAttr(topCtrl + ".autoSpine", topCtrlMultSwitchRZ + ".input2X")
        cmds.connectAttr(topCtrlMultSwitchRZ + ".outputX", midDriver + ".ty")

        # =======================================================================
        # Translate X
        # =======================================================================

        # Chest Control Translate X + Hip Control Translate X / 2 * autpSpine
        autoSpineTXNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=midDriverTrans + "_TX_Avg")
        cmds.setAttr(autoSpineTXNode + ".operation", 3)
        autoSpineTX_MultNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=midDriverTrans + "_TX_Mult")

        cmds.connectAttr(topCtrl + ".translateX", autoSpineTXNode + ".input1D[0]")
        cmds.connectAttr(botJntLoc + ".translateX", autoSpineTXNode + ".input1D[1]")
        cmds.connectAttr(autoSpineTXNode + ".output1D", autoSpineTX_MultNode + ".input1X")
        cmds.connectAttr(topCtrl + ".autoSpine", autoSpineTX_MultNode + ".input2X")
        cmds.connectAttr(autoSpineTX_MultNode + ".outputX", midDriverTrans + ".translateX")

        # =======================================================================
        # Translate Y
        # =======================================================================
        autoSpineTYNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=midDriverTrans + "_TY_Avg")
        cmds.setAttr(autoSpineTYNode + ".operation", 3)
        autoSpineTY_MultNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=midDriverTrans + "_TY_Mult")

        cmds.connectAttr(chestTrackNode + ".translateY", autoSpineTYNode + ".input1D[0]")
        cmds.connectAttr(botJntLoc + ".translateY", autoSpineTYNode + ".input1D[1]")
        cmds.connectAttr(autoSpineTYNode + ".output1D", autoSpineTY_MultNode + ".input1X")
        cmds.connectAttr(topCtrl + ".autoSpine", autoSpineTY_MultNode + ".input2X")
        cmds.connectAttr(autoSpineTY_MultNode + ".outputX", midDriverTrans + ".translateY")

        # =======================================================================
        # Translate Z
        # =======================================================================
        autoSpineTZNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=midDriverTrans + "_TZ_Avg")
        cmds.setAttr(autoSpineTZNode + ".operation", 3)
        autoSpineTZ_MultNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=midDriverTrans + "_TZ_Mult")

        cmds.connectAttr(chestTrackNode + ".translateZ", autoSpineTZNode + ".input1D[0]")
        cmds.connectAttr(botJntLoc + ".translateZ", autoSpineTZNode + ".input1D[1]")
        cmds.connectAttr(autoSpineTZNode + ".output1D", autoSpineTZ_MultNode + ".input1X")
        cmds.connectAttr(topCtrl + ".autoSpine", autoSpineTZ_MultNode + ".input2X")
        cmds.connectAttr(autoSpineTZ_MultNode + ".outputX", midDriverTrans + ".translateZ")

        cmds.setAttr(topCtrl + ".autoSpine", 1)

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
                controls.reverse()
                # create a duplicate chain
                topCtrl = controls[0]
                topGrp = cmds.listRelatives(namespace + ":" + topCtrl, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # match the fk controls to the corresponding joint

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
                cmds.warning("Already in IK mode.")
                return

            if not match:
                cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

            if match:

                # get IK controls
                controls = json.loads(cmds.getAttr(networkNode + ".ikControls"))

                # Chest
                # create a duplicate chest anim
                control = controls[0]
                topGrp = cmds.listRelatives(namespace + ":" + control, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # match the chest anim to the last spine joint
                fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
                joint = fkControls[0].partition("_anim")[0].partition("fk_")[2]
                joint = namespace + ":" + joint
                constraint = cmds.parentConstraint(joint, control)[0]
                cmds.delete(constraint)

                # this will now give use good values
                translate = cmds.getAttr(control + ".translate")[0]
                rotate = cmds.getAttr(control + ".rotate")[0]

                cmds.setAttr(namespace + ":" + control + ".translate", translate[0], translate[1], translate[2],
                             type='double3')
                cmds.setAttr(namespace + ":" + control + ".rotate", rotate[0], rotate[1], rotate[2], type='double3')

                cmds.setKeyframe(namespace + ":" + control)

                # delete dupes
                cmds.delete(newControls[0])

                # set auto spine off
                cmds.setAttr(namespace + ":" + control + ".autoSpine", 0)
                cmds.setKeyframe(namespace + ":" + control + ".autoSpine")

                # Mid Anim
                # create a duplicate mid spine anim
                control = controls[1]
                topGrp = cmds.listRelatives(namespace + ":" + control, parent=True)[0]
                newControls = cmds.duplicate(topGrp)
                cmds.parent(newControls[0], world=True)

                # match the mid spibne anim to the mid spine joint
                allJnts = self.returnCreatedJoints
                joints = []
                for jnt in allJnts:
                    if jnt.find("pelvis") == -1:
                        joints.append(jnt)

                joint = "driver_" + joints[len(joints) / 2]
                joint = namespace + ":" + joint
                constraint = cmds.parentConstraint(joint, control)[0]
                cmds.delete(constraint)

                # this will now give use good values
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
                    cmds.setAttr(namespace + ":" + self.name + "_settings.mode", 1.0)
                    cmds.setKeyframe(namespace + ":" + self.name + "_settings.mode")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetRigControls(self, resetAll):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        nonZeroAttrs = ["scale", "globalScale", "scaleX", "scaleY", "scaleZ", "twist_amount", "rotationInfluence",
                        "autoSpine"]

        if resetAll:

            # list any attributes on the network node that contain "controls"
            controls = cmds.listAttr(networkNode, st="*Controls")
            # get that data on that attr
            for control in controls:
                data = json.loads(cmds.getAttr(networkNode + "." + control))

                # reset the attr on each control

                try:
                    for each in data:
                        attrs = cmds.listAttr(namespace + ":" + each, keyable=True)
                        for attr in attrs:
                            if attr not in nonZeroAttrs:
                                try:
                                    cmds.setAttr(namespace + ":" + each + "." + attr, 0)
                                except:
                                    pass
                            else:
                                try:
                                    cmds.setAttr(namespace + ":" + each + "." + attr, 1)
                                except:
                                    pass
                except:
                    cmds.warning("skipped " + str(control) + ". No valid controls found to reset.")

        if not resetAll:
            selection = cmds.ls(sl=True)
            for each in selection:
                attrs = cmds.listAttr(each, keyable=True)

                for attr in attrs:
                    if attr not in nonZeroAttrs:

                        try:
                            cmds.setAttr(each + "." + attr, 0)
                        except:
                            pass
                    else:
                        try:
                            cmds.setAttr(each + "." + attr, 1)
                        except:
                            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getUpAxis(self, obj):

        cmds.xform(obj, ws=True, relative=True, t=[0, 0, 10])
        translate = cmds.getAttr(obj + ".translate")[0]
        newTuple = (abs(translate[0]), abs(translate[1]), abs(translate[2]))
        cmds.xform(obj, ws=True, relative=True, t=[0, 0, -10])

        highestVal = max(newTuple)
        axis = newTuple.index(highestVal)
        upAxis = None

        if axis == 0:
            upAxis = "X"

        if axis == 1:
            upAxis = "Y"

        if axis == 2:
            upAxis = "Z"

        return upAxis

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX(self, importMethod, character):

        returnControls = []

        # get basic info of node
        networkNode = self.returnRigNetworkNode
        moduleName = cmds.getAttr(networkNode + ".moduleName")
        baseModuleName = cmds.getAttr(networkNode + ".baseName")

        # find prefix/suffix of module name
        prefixSuffix = moduleName.split(baseModuleName)
        prefix = None
        suffix = None

        if prefixSuffix[0] != '':
            prefix = prefixSuffix[0]
        if prefixSuffix[1] != '':
            suffix = prefixSuffix[1]

        # get controls
        pelvisControls = json.loads(cmds.getAttr(networkNode + ".pelvisControls"))
        fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
        ikControls = json.loads(cmds.getAttr(networkNode + ".ikControls"))

        # get joints
        joints = cmds.getAttr(networkNode + ".Created_Bones")
        splitJoints = joints.split("::")
        createdJoints = []

        for bone in splitJoints:
            if bone != "":
                createdJoints.append(bone)

        # IMPORT (FK OR IK)
        for joint in createdJoints:
            if joint.find("pelvis") != -1:
                cmds.parentConstraint(joint, character + ":" + pelvisControls[1])
                returnControls.append(character + ":" + pelvisControls[1])

        # IMPORT FK
        if importMethod == "FK" or importMethod == "Both":
            cmds.setAttr(character + ":" + moduleName + "_settings.mode", 0)

            for joint in createdJoints:
                if cmds.objExists(character + ":" + "fk_" + joint + "_anim"):
                    cmds.parentConstraint(joint, character + ":" + "fk_" + joint + "_anim")
                    returnControls.append(character + ":" + "fk_" + joint + "_anim")

        # IMPORT IK
        if importMethod == "IK" or importMethod == "Both":
            cmds.setAttr(character + ":" + moduleName + "_settings.mode", 1)

            topJoint = createdJoints[-1]
            midJoint = createdJoints[(len(createdJoints)) / 2]

            cmds.parentConstraint(topJoint, character + ":" + ikControls[0])
            returnControls.append(character + ":" + ikControls[0])

            cmds.parentConstraint(midJoint, character + ":" + ikControls[1])
            returnControls.append(character + ":" + ikControls[1])

        # IMPORT NONE
        if importMethod == "None":
            pass

        return returnControls

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def resetRigControls(self, resetAll):

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]
        namespace = cmds.getAttr(characterNode + ".namespace")

        if resetAll:

            # list any attributes on the network node that contain "controls"
            controls = cmds.listAttr(networkNode, st="*Controls")
            # get that data on that attr
            for control in controls:
                data = json.loads(cmds.getAttr(networkNode + "." + control))

                # reset the attr on each control
                zeroAttrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
                nonZeroAttrs = ["scaleX", "scaleY", "scaleZ"]

                try:
                    for each in data:
                        attrs = cmds.listAttr(namespace + ":" + each, keyable=True)
                        for attr in attrs:
                            if attr in zeroAttrs:
                                cmds.setAttr(namespace + ":" + each + "." + attr, 0)
                            if attr in nonZeroAttrs:
                                cmds.setAttr(namespace + ":" + each + "." + attr, 1)
                            else:
                                pass
                except:
                    cmds.warning("skipped " + str(control) + ". No valid controls found to reset.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def selectRigControls(self, mode):

        controls = self.getControls()
        if controls == None:
            return
        ikControls = ["chest_ik_anim", "mid_ik_anim"]

        # get namespace
        networkNode = self.returnRigNetworkNode
        characterNode = cmds.listConnections(networkNode + ".parent")[0]

        try:
            namespace = cmds.getAttr(characterNode + ".namespace")
        except:
            namespace = ""

        if mode == "all":
            for control in controls:
                cmds.select(namespace + ":" + control, add=True)

        if mode == "fk":
            for control in controls:
                if control.find("fk_") == 0:
                    cmds.select(namespace + ":" + control, add=True)

        if mode == "ik":
            for control in controls:
                for ikControl in ikControls:
                    if control.find(ikControl) != -1:
                        cmds.select(namespace + ":" + control, add=True)
