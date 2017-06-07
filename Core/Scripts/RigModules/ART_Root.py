#standard imports
import maya.cmds as cmds
import json
from functools import partial
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

#external imports
from System.ART_RigModule import ART_RigModule
import System.riggingUtils as riggingUtils
import System.interfaceUtils as interfaceUtils

#file attributes
icon = "Core/Icons/Modules/root.png"
search = "Root"
className = "ART_Root"
baseName = "root"
fbxImport = ["None", "Root Motion: Offset", "Root Motion: Master", "Root Motion: Root"]
matchData = [False, None]
controlTypes = [["rootControls", "FK"]]


class ART_Root(ART_RigModule):

    def __init__(self, rigUiInst, moduleUserName):
        self.rigUiInst = rigUiInst
        self.moduleUserName = moduleUserName
        self.outlinerWidgets = {}

        ART_RigModule.__init__(self, "ART_Root_Module", "ART_Root", moduleUserName)

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
        cmds.setAttr(self.networkNode + ".Created_Bones", "root", type = "string", lock = True)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def skeletonSettings_UI(self, name):
        #groupbox all modules get
        ART_RigModule.skeletonSettings_UI(self, name, 335, 85, False)

        #add a label to the root module saying this module cannot be edited or removed
        self.layout = QtWidgets.QVBoxLayout(self.groupBox)
        self.label = QtWidgets.QLabel("All rigs must have a root module. This module cannot be edited or removed.")
        self.layout.addWidget(self.label)
        self.label.setGeometry(QtCore.QRect(10, 20, 300, 60))
        self.label.setMinimumHeight(60)
        self.label.setWordWrap(True)


        #add to the rig cretor UI's module settings layout VBoxLayout
        self.rigUiInst.moduleSettingsLayout.addWidget(self.groupBox)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def pickerUI(self, center, animUI, networkNode, namespace):

        #create qBrushes
        yellowBrush = QtCore.Qt.yellow
        blueBrush = QtGui.QColor(100,220,255)
        purpleBrush = QtGui.QColor(111,48,161)
        clearBrush = QtGui.QBrush(QtCore.Qt.black)
        clearBrush.setStyle(QtCore.Qt.NoBrush)

        #create border item
        if networkNode.find(":") != -1:
            moduleNode = networkNode.partition(":")[2]
        else:
            moduleNode = networkNode
        borderItem = interfaceUtils.pickerBorderItem(center.x() - 40, center.y() - 70, 50, 98, clearBrush, moduleNode)

        #get controls + namespace
        networkNode = self.returnNetworkNode
        controls = json.loads(cmds.getAttr(networkNode + ".rootControls"))

        #master anim button
        masterBtn = interfaceUtils.pickerButton(30, 30, [10,2], namespace + controls[0], yellowBrush, borderItem)
        interfaceUtils.addTextToButton("M", masterBtn)

        #offset anim button
        offsetBtn = interfaceUtils.pickerButton(30, 30, [10,34], namespace + controls[1], blueBrush, borderItem)
        interfaceUtils.addTextToButton("O", offsetBtn)

        #root anim button
        rootBtn = interfaceUtils.pickerButton(30, 30, [10,66], namespace + controls[2], purpleBrush, borderItem)
        interfaceUtils.addTextToButton("R", rootBtn)

        #=======================================================================
        # #Create scriptJob for selection. Set scriptJob number to borderItem.data(5)
        #=======================================================================
        scriptJob = cmds.scriptJob(event = ["SelectionChanged", partial(self.selectionScriptJob_animUI,[[masterBtn,namespace + controls[0], yellowBrush],[offsetBtn, namespace + controls[1], blueBrush],[rootBtn, namespace + controls[2], purpleBrush]])], kws = True)
        borderItem.setData(5, scriptJob)
        animUI.selectionScriptJobs.append(scriptJob)

        return [borderItem, False, scriptJob]


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
        #add the buttons
        self.createGlobalMoverButton(self.name, self.outlinerWidgets[self.name + "_treeModule"], self.rigUiInst)

        #create selection script job for module
        self.updateBoneCount()
        self.createScriptJob()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildRigCustom(self, textEdit, uiInst):

        if textEdit != None:
            textEdit.append("        Building Root Rig..")

        #get the created joint
        networkNode = self.returnNetworkNode
        rootJoint = cmds.getAttr(networkNode + ".Created_Bones")

        #create the rig grp
        rigGrp = cmds.group(empty = True, name = "rig_grp")


        #Need to build 3 controls, the master, the offset, and the root control
        masterControls = riggingUtils.createControlFromMover(rootJoint, networkNode, False, True)

        #rename controls
        masterControl = cmds.rename(masterControls[0], "master_anim")
        masterCtrlGrp = cmds.rename(masterControls[1], "master_anim_grp")
        masterSpaceSwitch = cmds.rename(masterControls[2], "master_anim_space_switcher")
        masterSpace = cmds.rename(masterControls[3], "master_anim_space_switcher_follow")

        cmds.parent(masterSpace, rigGrp)
        #scale masterControl
        cmds.setAttr(masterControl + ".scale", 2, 2, 2, type = "double3")
        cmds.makeIdentity(masterControl, t = 1, r = 1, s = 1, apply = True)

        #alias attr master control
        cmds.aliasAttr("globalScale", masterControl + ".scaleZ")
        cmds.connectAttr(masterControl + ".globalScale", masterControl + ".scaleX")
        cmds.connectAttr(masterControl + ".globalScale", masterControl + ".scaleY")
        cmds.setAttr(masterControl + ".scaleX", keyable = False)
        cmds.setAttr(masterControl + ".scaleY", keyable = False)
        cmds.setAttr(masterControl + ".visibility", lock = True, keyable = False)

        #create offset anim control
        offsetAnim = riggingUtils.createControl("circle", 40, "offset_anim", False)
        cmds.parent(offsetAnim, masterControl)
        cmds.setAttr(offsetAnim + ".overrideEnabled", 1)
        cmds.setAttr(offsetAnim + ".overrideColor",  18)

        for attr in [".visibility", ".scaleX", ".scaleY", ".scaleZ"]:
            cmds.setAttr(offsetAnim + attr, lock = True, keyable = False)

        #create the root control
        rootAnim = riggingUtils.createControl("sphere", 5, "root_anim", False)
        cmds.parent(rootAnim, offsetAnim)
        cmds.makeIdentity(rootAnim, t = 1, r = 1, s = 1, apply = True)
        cmds.setAttr(rootAnim + ".overrideEnabled", 1)
        cmds.setAttr(rootAnim + ".overrideColor",  30)
        cmds.parentConstraint(rootAnim, "driver_root")
        cmds.scaleConstraint(rootAnim, "driver_root")

        for attr in [".visibility", ".scaleX", ".scaleY", ".scaleZ"]:
            cmds.setAttr(rootAnim + attr, lock = True, keyable = False)

        if not cmds.objExists(networkNode + ".rootControls"):
            cmds.addAttr(networkNode, ln = "rootControls", dt = "string")

        controlList = [masterControl, offsetAnim, rootAnim]
        jsonString = json.dumps(controlList)
        cmds.setAttr(networkNode + ".rootControls", jsonString, type = "string")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def importFBX(self, importMethod, character):

        returnControls = []

        if importMethod == "Root Motion: Offset":

            cmds.parentConstraint("root", character + ":" + "offset_anim")
            returnControls.append(character + ":" + "offset_anim")


        if importMethod == "Root Motion: Master":
            cmds.parentConstraint("root", character + ":" + "master_anim")
            returnControls.append(character + ":" + "master_anim")

        if importMethod == "Root Motion: Root":
            cmds.parentConstraint("root", character + ":" + "root_anim")
            returnControls.append(character + ":" + "root_anim")

        if importMethod == "None":
            pass

        return returnControls










