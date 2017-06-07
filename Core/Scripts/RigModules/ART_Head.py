"""
Author: Jeremy Ernst

===============
File Attributes
===============
    * **icon:** This is the image file (125x75 .png) that gets used in the RigCreatorUI

    * **hoverIcon:** When you hover over the module in the module list, it will swap to this icon
      (background changes to orange). There are .psd template files for these.

    * **search:** These are search terms that are accepted when searching the list of modules in the
      RigCreatorUI

    * **class name:** The name of the class.

    * **jointMover:** The relative path to the joint mover file. Relative to the ARTv2 root directory.

    * **baseName:** The default name the module will get created with. Users can then add a prefix and/or
      suffix to the base name.

    * **rigs:** This is a simple list of what rigs this module can build. This feature isn't implemented yet,
      but the plan is to query this list and present these options to the user for them to select what rigs
      they want to build for the module. Right now, it will build all rigs.

    * **fbxImport:** This is a list that will show the options for the module in the import mocap interface.
      Normally, this list will have at least None and FK.

    * **matchData:** This is a list of options that will be presented for the module in a comboBox in the
      match over frame range interface. First argument is  a bool as to whether the module can or can't
      match. The second arg is a list of strings to display for the match options. For example:
      matchData = [True, ["Match FK to IK", "Match IK to FK"]]

    * **controlTypes:** This is a list of lists, where each item in the main list is a list comprised of the
      name of the attribute that gets added to the network node that contains the control information.
      The second arg in each list entry is a control type, like FK or IK. This is used in the select
      rig controls interface for filtering out which controls on each module you want to select. On
      this module, the values are: controlTypes = [["fkControls", "FK"]], which means that the
      attribute that holds the control info is called fkControls, and those controls are of type FK.

        .. image:: /images/selectRigControls.png

===============
Class
===============
"""
# file imports
import json
import os
from functools import partial

import maya.cmds as cmds

import System.interfaceUtils as interfaceUtils
import System.riggingUtils as riggingUtils
import System.utils as utils
from System.ART_RigModule import ART_RigModule
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# file attributes
icon = "Modules/head.png"
hoverIcon = "Modules/hover_head.png"
search = "biped:head:neck"
className = "ART_Head"
jointMover = "Core/JointMover/ART_Head_1Neck.ma"
baseName = "Head"
rigs = ["FK"]
fbxImport = ["None", "FK"]
matchData = [False, None]  # This is for matching over frame range options. (Matching between rigs of the module)
controlTypes = [["fkControls", "FK"]]


class ART_Head(ART_RigModule):
    """This class creates the head module"""

    def __init__(self, rigUiInst, moduleUserName):
        """Initiate the class, taking in the instance to the interface and the user specified name.

        :param rigUiInst: This is the rig creator interface instance being passed in.
        :param moduleUserName: This is the name specified by the user on module creation.

        Instantiate the following class variables as well:
            * **self.rigUiInst:** take the passed in interface instance and make it a class var
            * **self.moduleUserName:** take the passed in moduleUserName and make it a class var
            * **self.outlinerWidget:** an empty list that will hold all of the widgets added to the outliner

        Also, read the QSettings to find out where needed paths are.
        """

        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}

        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")

        ART_RigModule.__init__(self, "ART_Head_Module", "ART_Head", moduleUserName)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addAttributes(self):
        """
        Add custom attributes this module needs to the network node.

        Always calls on base class function first, then extends with any attributes unique to the class.
        """

        # call the base class method first to hook up our connections to the master module
        ART_RigModule.addAttributes(self)

        # add custom attributes for this specific module
        cmds.addAttr(self.networkNode, sn="Created_Bones", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".Created_Bones", "neck_01::head::", type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="baseName", dt="string", keyable=False)
        cmds.setAttr(self.networkNode + ".baseName", baseName, type="string", lock=True)

        cmds.addAttr(self.networkNode, sn="canAim", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".canAim", False, lock=True)

        cmds.addAttr(self.networkNode, sn="aimMode", at="bool", keyable=False)
        cmds.setAttr(self.networkNode + ".aimMode", False, lock=True)

        cmds.addAttr(self.networkNode, sn="neckJoints", keyable=False)
        cmds.setAttr(self.networkNode + ".neckJoints", 1, lock=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):
        """
        This is the UI for the module that has all of the configuration settings.

        :param name:  user given name of module (prefix + base_name + suffix)
        :param width: width of the skeleton settings groupBox. 335 usually
        :param height: height of the skeleton settings groupBox.
        :param checkable: Whether or not the groupBox can be collapsed.


        Build the groupBox that contains all of the settings for this module. Parent the groupBox
        into the main skeletonSettingsUI layout.
        Lastly, call on updateSettingsUI to populate the UI based off of the network node values.

        .. image:: /images/skeletonSettings.png

        """
        # width, height, checkable

        networkNode = self.returnNetworkNode
        font = QtGui.QFont()
        font.setPointSize(8)

        headerFont = QtGui.QFont()
        headerFont.setPointSize(8)
        headerFont.setBold(True)

        # groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 228, True)

        # STANDARD BUTTONS

        # create a VBoxLayout to add to our Groupbox and then add a QFrame for our signal/slot
        self.mainLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.mainLayout.addWidget(self.frame)
        self.frame.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.frame.setMinimumSize(QtCore.QSize(320, 210))
        self.frame.setMaximumSize(QtCore.QSize(320, 210))

        # create layout that is a child of the frame
        self.layout = QtWidgets.QVBoxLayout(self.frame)

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
        self.buttonLayout.addWidget(self.changeNameBtn)
        self.buttonLayout.addWidget(self.changeParentBtn)
        self.changeNameBtn.setObjectName("blueButton")
        self.changeParentBtn.setObjectName("blueButton")

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

        # button signal/slots
        self.changeNameBtn.clicked.connect(partial(self.changeModuleName, baseName, self, self.rigUiInst))
        self.changeParentBtn.clicked.connect(partial(self.changeModuleParent, self, self.rigUiInst))

        # Number of Neck Bones
        self.neckLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.neckLayout)

        self.numNeckBonesLabel = QtWidgets.QLabel("Number of Neck Bones: ")
        self.numNeckBonesLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.numNeckBonesLabel.setMinimumSize(QtCore.QSize(200, 20))
        self.numNeckBonesLabel.setMaximumSize(QtCore.QSize(200, 20))
        self.neckLayout.addWidget((self.numNeckBonesLabel))

        self.numNeck = QtWidgets.QSpinBox()
        self.numNeck.setMaximum(3)
        self.numNeck.setMinimum(1)
        self.numNeck.setMinimumSize(QtCore.QSize(100, 20))
        self.numNeck.setMaximumSize(QtCore.QSize(100, 20))
        self.numNeck.setValue(1)
        self.numNeck.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.neckLayout.addWidget(self.numNeck)

        # rebuild button
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.layout.addItem(spacerItem)

        self.applyButton = QtWidgets.QPushButton("Apply Changes")
        self.layout.addWidget(self.applyButton)
        self.applyButton.setFont(headerFont)
        self.applyButton.setMinimumSize(QtCore.QSize(300, 40))
        self.applyButton.setMaximumSize(QtCore.QSize(300, 40))
        self.applyButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.applyButton.setEnabled(False)
        self.applyButton.clicked.connect(partial(self.applyModuleChanges, self))

        # spinBox & checkbox signal/slots
        self.numNeck.valueChanged.connect(self.toggleButtonState)

        # signal slot for groupbox checkbox
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.frame.setVisible)
        self.groupBox.setChecked(False)

        # add custom skeletonUI settings  name, parent, rig types to install, mirror module, etc.
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
    def updateSettingsUI(self):

        """
        Update the skeleton settings UI based on the network node values for this module.
        """

        networkNode = self.returnNetworkNode
        numNeck = cmds.getAttr(networkNode + ".neckJoints")

        # update UI elements
        self.numNeck.setValue(numNeck)

        # apply changes
        self.applyButton.setEnabled(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateNeck(self, attachedModules, oldNum):

        """
        Take the number of neck bones value and rebuild the joint mover.

        The head module has 3 joint mover files, 1 for each possible neck number. When the number of neck bones is
        changed, the current module has its information stored (placement, etc), the module is then deleted,
        the new joint mover path is constructed and brought in, and lastly it resolves any dependency issues.
        (Like if there was a leaf joint as a child of a neck bone that no longer exists)

        :param attachedModules: self.checkForDependencies()
        :param oldNum: the existing amount  of neck bones prior to the update
        """

        # gather information (current name, current parent, etc)
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        parent = cmds.getAttr(networkNode + ".parentModuleBone")
        newNum = int(cmds.getAttr(networkNode + ".neckJoints"))

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

        # delete joint mover
        cmds.delete(self.name + "_mover_grp")

        # build new jmPath name
        jmPath = jointMover.partition(".ma")[0].rpartition("_")[0] + "_" + str(newNum) + "Neck.ma"  # ART_Head_1Neck
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

        if mover is not None:
            cmds.parentConstraint(mover, self.name + "_mover_grp", mo=True)

        if cmds.objExists(self.name + "_mover_grp_scaleConstraint*"):
            cmds.delete(self.name + "_mover_grp_scaleConstraint*")

        if mover is not None:
            cmds.scaleConstraint(mover, self.name + "_mover_grp", mo=True)

        # create the connection geo between the two
        childMover = utils.findOffsetMoverFromName(name)
        riggingUtils.createBoneConnection(mover, childMover, name)
        self.applyModuleChanges(self)
        cmds.select(clear=True)

        # if there were any module dependencies, fix those now.
        if len(attachedModules) > 0:
            elementList = []

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
                                               "The following modules have had their parent changed due to the change\
                                               in this module's structure:",
                                               elementList, 5, winParent)
            win.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def applyModuleChanges(self, moduleInst):

        """
        Update the scene after the settings are changed in the skeleton settings UI.

        This means also updating the created_bones attr, updating the joint mover if needed,
        running self.updateNeck, updating the outliner, and updating the bone count.

        :param moduleInst: self (usually, but there are cases like templates where an inst on disc is passed in.)
        """

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
        joints = []

        # get current neck value
        currentNum = int(cmds.getAttr(networkNode + ".neckJoints"))

        # get new neck value
        uiNeckVal = self.numNeck.value()

        if uiNeckVal != currentNum:
            # update neck value, and call on update neck
            cmds.setAttr(networkNode + ".neckJoints", lock=False)
            cmds.setAttr(networkNode + ".neckJoints", uiNeckVal, lock=True)

            # look for any attached modules
            attachedModules = self.checkForDependencies()
            self.updateNeck(attachedModules, currentNum)

        for i in range(uiNeckVal):
            joints.append(prefix + "neck_0" + str(i + 1) + suffix)

        joints.append(prefix + "head" + suffix)

        # build attrString
        attrString = ""
        for bone in joints:
            attrString += bone + "::"

        networkNode = self.returnNetworkNode
        cmds.setAttr(networkNode + ".Created_Bones", lock=False)
        cmds.setAttr(networkNode + ".Created_Bones", attrString, type="string", lock=True)

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
    def toggleButtonState(self):

        """Toggle the state of the Apply Changes button."""

        state = self.applyButton.isEnabled()
        if state is False:
            self.applyButton.setEnabled(True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def addJointMoverToOutliner(self):

        """
        Add the joint movers for this module to the outliner.

        Depending on the module settings, different joint movers may or may not be added. Also, each "joint" usually
        has three movers: global, offset, and geo. However, not all joints do, so this method is also used to specify
        which joint movers for each joint are added to the outliner.

        .. image:: /images/outliner.png

        """
        index = self.rigUiInst.treeWidget.topLevelItemCount()

        # Add the module to the tree widget in the outliner tab of the rig creator UI
        self.outlinerWidgets[self.name + "_treeModule"] = QtWidgets.QTreeWidgetItem(self.rigUiInst.treeWidget)
        self.rigUiInst.treeWidget.topLevelItem(index).setText(0, self.name)
        foreground = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.outlinerWidgets[self.name + "_treeModule"].setForeground(0, foreground)

        # add the neck 01
        self.outlinerWidgets[self.name + "_neck_01"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_neck_01"].setText(0, self.name + "_neck_01")
        self.createGlobalMoverButton(self.name + "_neck_01", self.outlinerWidgets[self.name + "_neck_01"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_neck_01", self.outlinerWidgets[self.name + "_neck_01"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_neck_01", self.outlinerWidgets[self.name + "_neck_01"], self.rigUiInst)

        # add neck 02
        self.outlinerWidgets[self.name + "_neck_02"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_neck_01"])
        self.outlinerWidgets[self.name + "_neck_02"].setText(0, self.name + "_neck_02")
        self.createGlobalMoverButton(self.name + "_neck_02", self.outlinerWidgets[self.name + "_neck_02"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_neck_02", self.outlinerWidgets[self.name + "_neck_02"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_neck_02", self.outlinerWidgets[self.name + "_neck_02"], self.rigUiInst)

        # add neck 03
        self.outlinerWidgets[self.name + "_neck_03"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_neck_02"])
        self.outlinerWidgets[self.name + "_neck_03"].setText(0, self.name + "_neck_03")
        self.createGlobalMoverButton(self.name + "_neck_03", self.outlinerWidgets[self.name + "_neck_03"],
                                     self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_neck_03", self.outlinerWidgets[self.name + "_neck_03"],
                                     self.rigUiInst)
        self.createMeshMoverButton(self.name + "_neck_03", self.outlinerWidgets[self.name + "_neck_03"], self.rigUiInst)

        # add head
        self.outlinerWidgets[self.name + "_head"] = QtWidgets.QTreeWidgetItem(
                self.outlinerWidgets[self.name + "_treeModule"])
        self.outlinerWidgets[self.name + "_head"].setText(0, self.name + "_head")
        self.createGlobalMoverButton(self.name + "_head", self.outlinerWidgets[self.name + "_head"], self.rigUiInst)
        self.createOffsetMoverButton(self.name + "_head", self.outlinerWidgets[self.name + "_head"], self.rigUiInst)
        self.createMeshMoverButton(self.name + "_head", self.outlinerWidgets[self.name + "_head"], self.rigUiInst)

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
        """
        Whenever changes are made to the module settings, update the outliner to show the new or removed movers
        """

        # NECK
        numNeck = self.numNeck.value()
        if numNeck == 1:
            self.outlinerWidgets[self.originalName + "_neck_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_neck_02"].setHidden(True)
            self.outlinerWidgets[self.originalName + "_neck_03"].setHidden(True)

        if numNeck == 2:
            self.outlinerWidgets[self.originalName + "_neck_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_neck_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_neck_03"].setHidden(True)

        if numNeck == 3:
            self.outlinerWidgets[self.originalName + "_neck_01"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_neck_02"].setHidden(False)
            self.outlinerWidgets[self.originalName + "_neck_03"].setHidden(False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pinModule(self, state):
        """
        Pin the module in place so the parent does not move the module. Each module has to define how it needs to be
        pinned.
        """
        networkNode = self.returnNetworkNode
        topLevelMover = self.name + "_neck_01_mover_grp"

        if state:

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
        """
        Skin the proxy geo brought in by the module. Each module has to define how it wants to skin its proxy geo.
        """

        # get the network node
        networkNode = self.returnNetworkNode
        name = cmds.getAttr(networkNode + ".moduleName")
        baseName = cmds.getAttr(networkNode + ".baseName")
        prefix = name.partition(baseName)[0]
        suffix = name.partition(baseName)[2]

        if len(prefix) > 0:
            if prefix.find("_") == -1:
                prefix = prefix + "_"
        if len(suffix) > 0:
            if suffix.find("_") == -1:
                suffix = "_" + suffix

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
        """
        Build the rigs for this module.

        This method defines what rigs are built and how they are built when the asset is published. It posts any build
        info to the passed in textEdit.

        :param textEdit: passed in text edit that the rig build can post updates to
        :param uiInst:  passed in instance of the buildProgressUI
        """

        if textEdit is not None:
            textEdit.append("        Building " + self.name + " Rig..")

        # get the created joints
        networkNode = self.returnNetworkNode
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        joints = self.returnCreatedJoints

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # create groups and settings
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # create the rig group
        self.rigGrp = cmds.group(empty=True, name=self.name + "_group")
        constraint = cmds.parentConstraint(parentBone, self.rigGrp)[0]
        cmds.delete(constraint)

        # create the rig settings group
        self.rigSettings = cmds.group(empty=True, name=self.name + "_settings")
        cmds.parent(self.rigSettings, self.rigGrp)
        for attr in (cmds.listAttr(self.rigSettings, keyable=True)):
            cmds.setAttr(self.rigSettings + "." + attr, lock=True, keyable=False)

        # create the ctrl group (what will get the constraint to the parent)
        self.rigCtrlGrp = cmds.group(empty=True, name=self.name + "_ctrl_grp")
        constraint = cmds.parentConstraint(parentBone, self.rigCtrlGrp)[0]
        cmds.delete(constraint)

        cmds.parent(self.rigCtrlGrp, self.rigGrp)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Build the FK Neck Rig
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        fkControls = []
        self.topNode = None

        # get number of neck bones
        numNeck = cmds.getAttr(networkNode + ".neckJoints")
        neckJoints = []
        for i in range(len(joints) - 1):
            neckJoints.append(joints[i])

        # create FK controls for neck joints, adding space switching to base neck joint
        for joint in neckJoints:
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

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Build the FK Head Rig
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        headJoint = joints[-1]
        data = riggingUtils.createControlFromMover(headJoint, networkNode, True, True)

        headControl = cmds.rename(data[0], "fk_" + headJoint + "_anim")
        animGrp = cmds.rename(data[1], "fk_" + headJoint + "_anim_grp")
        spaceSwitcher = cmds.rename(data[2], "fk_" + headJoint + "_anim_space_switcher")
        spaceSwitchFollow = cmds.rename(data[3], "fk_" + headJoint + "_anim_space_switcher_follow")

        # color the control
        riggingUtils.colorControl(headControl, 17)

        # parent head to neck
        lastNeck = fkControls[0][1]
        cmds.parent(spaceSwitchFollow, lastNeck)

        fkControls.append([animGrp, headControl, headJoint])

        # parent head rig to rigGrp
        cmds.parent(self.topNode, self.rigCtrlGrp)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # lock attrs
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for each in fkControls:
            control = each[1]
            if control != headControl:
                for attr in [".scaleX", ".scaleY", ".globalScale", ".visibility"]:
                    cmds.setAttr(control + attr, lock=True, keyable=False)
            else:
                for attr in [".visibility"]:
                    cmds.setAttr(control + attr, lock=True, keyable=False)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # hook up to driver skeleton
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for each in fkControls:
            control = each[1]
            joint = each[2]

            cmds.pointConstraint(control, "driver_" + joint, mo=True)
            cmds.orientConstraint(control, "driver_" + joint)

            # plug master control scale into a new mult node that takes joint.scale into input 1, and master.scale
            # into input 2, and plugs that into driver joint
            if cmds.objExists("master_anim"):
                globalScaleMult = cmds.shadingNode("multiplyDivide", asUtility=True, name=joint + "_globalScale")
                cmds.connectAttr("master_anim.scale", globalScaleMult + ".input1")
                cmds.connectAttr(control + ".scale", globalScaleMult + ".input2")
                riggingUtils.createConstraint(globalScaleMult, "driver_" + joint, "scale", False, 2, 0, "output")
            else:
                riggingUtils.createConstraint(control, "driver_" + joint, "scale", False, 2, 0)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # add info to module
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        fkRigData = []
        for each in fkControls:
            fkRigData.append(each[1])

        # add created control info to module
        if not cmds.objExists(networkNode + ".fkControls"):
            cmds.addAttr(networkNode, ln="fkControls", dt="string")
        jsonString = json.dumps(fkRigData)
        cmds.setAttr(networkNode + ".fkControls", jsonString, type="string")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # #            Parent Under Offset Ctrl           # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # parent under offset_anim if it exists(it always should)
        if cmds.objExists("offset_anim"):
            cmds.parent(self.rigGrp, "offset_anim")

        # return data
        parentBone = cmds.getAttr(networkNode + ".parentModuleBone")
        try:
            uiInst.rigData.append([self.rigCtrlGrp, "driver_" + parentBone, 1])
        except:
            pass

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # update progress
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if textEdit is not None:
            textEdit.setTextColor(QtGui.QColor(0, 255, 18))
            textEdit.append("        SUCCESS: FK Build Complete!")
            textEdit.setTextColor(QtGui.QColor(255, 255, 255))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pickerUI(self, center, animUI, networkNode, namespace):
        """
        Build the animation picker for the module.


        :param center: the center of the QGraphicsScene
        :param animUI: the instance of the AnimationUI
        :param networkNode: the module's network node
        :param namespace: the namespace of the character

        """

        self.namespace = namespace
        neckJoints = cmds.getAttr(networkNode + ".neckJoints")

        # create qBrushes
        yellowBrush = QtCore.Qt.yellow
        blueBrush = QtGui.QColor(100, 220, 255)
        greenBrush = QtGui.QColor(0, 255, 30)
        clearBrush = QtGui.QBrush(QtCore.Qt.black)
        clearBrush.setStyle(QtCore.Qt.NoBrush)

        # create the picker border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode

        borderItem = interfaceUtils.pickerBorderItem(center.x() - 50, center.y() - 50, 100, 100, clearBrush, moduleNode)

        # get controls
        fkControls = json.loads(cmds.getAttr(networkNode + ".fkControls"))
        fkControls.reverse()
        buttonData = []

        # create buttons
        headButton = interfaceUtils.pickerButtonCustom(100, 100,
                                                       [[10, 60], [30, 60], [40, 40], [40, 10], [35, 5], [30, 0],
                                                        [10, 0], [5, 5], [0, 10], [0, 40], [10, 60]], [30, 5],
                                                       namespace + fkControls[0], yellowBrush, borderItem)
        buttonData.append([headButton, namespace + fkControls[0], yellowBrush])

        if neckJoints == 1:
            neck1Button = interfaceUtils.pickerButtonCustom(100, 100,
                                                            [[5, 55], [8, 63], [32, 63], [35, 55], [40, 85], [0, 85],
                                                             [5, 55]], [30, 5], namespace + fkControls[1], blueBrush,
                                                            borderItem)
            buttonData.append([neck1Button, namespace + fkControls[1], blueBrush])

        if neckJoints == 2:
            neck1Button = interfaceUtils.pickerButtonCustom(100, 100,
                                                            [[5, 55], [8, 63], [32, 63], [35, 55], [37, 68], [3, 68],
                                                             [5, 55]], [30, 5], namespace + fkControls[1], blueBrush,
                                                            borderItem)
            buttonData.append([neck1Button, namespace + fkControls[1], blueBrush])

            neck2Button = interfaceUtils.pickerButtonCustom(100, 100, [[3, 70], [37, 70], [40, 80], [0, 80]], [30, 5],
                                                            namespace + fkControls[2], blueBrush, borderItem)
            buttonData.append([neck2Button, namespace + fkControls[2], blueBrush])

        if neckJoints == 3:
            neck1Button = interfaceUtils.pickerButtonCustom(100, 100,
                                                            [[5, 55], [8, 63], [32, 63], [35, 55], [37, 68], [3, 68],
                                                             [5, 55]], [30, 5], namespace + fkControls[1], blueBrush,
                                                            borderItem)
            buttonData.append([neck1Button, namespace + fkControls[1], blueBrush])

            neck2Button = interfaceUtils.pickerButtonCustom(100, 100, [[3, 70], [37, 70], [38, 76], [2, 76]], [30, 5],
                                                            namespace + fkControls[2], blueBrush, borderItem)
            buttonData.append([neck2Button, namespace + fkControls[2], blueBrush])

            neck3Button = interfaceUtils.pickerButtonCustom(100, 100, [[2, 78], [38, 78], [40, 84], [0, 84]], [30, 5],
                                                            namespace + fkControls[3], blueBrush, borderItem)
            buttonData.append([neck3Button, namespace + fkControls[3], blueBrush])

        # =======================================================================
        # go through button data, adding menu items
        # =======================================================================
        for each in buttonData:
            button = each[0]

            zeroIcon1 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroAll.png"))))
            zeroIcon2 = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/zeroSel.png"))))
            selectIcon = QtGui.QIcon((utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/select.png"))))

            button.menu.addAction(selectIcon, "Select All Controls", partial(self.selectRigControls))
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
    def importFBX(self, importMethod, character):
        """
        Import FBX motion onto this module's rig controls.

        :param importMethod: The import method to be used (options defined in the file attributes)
        :param character: the namespace of the character

        Each module has to define what import methods it offers (at the very top of the module file) and then define
        how motion is imported using those methods.
        """

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

        # get joints
        joints = cmds.getAttr(networkNode + ".Created_Bones")
        splitJoints = joints.split("::")
        createdJoints = []

        for bone in splitJoints:
            if bone != "":
                createdJoints.append(bone)

        # IMPORT FK
        if importMethod == "FK":

            for joint in createdJoints:
                if cmds.objExists(character + ":" + "fk_" + joint + "_anim"):
                    cmds.parentConstraint(joint, character + ":" + "fk_" + joint + "_anim")
                    returnControls.append(character + ":" + "fk_" + joint + "_anim")

        # IMPORT NONE
        if importMethod == "None":
            pass

        return returnControls
