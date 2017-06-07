"""
Author: Jeremy Ernst
"""

from functools import partial

import maya.cmds as cmds
import System.utils as utils

from ThirdParty.Qt import QtCore, QtWidgets


class ART_BakeOffsets():
    """
    This clas builds a UI that allows the rigger to select modules to bake offset mover values up to the global mover
    controls, making the offset movers no longer offset from their global mover parents. It can be found on the rig
    creator toolbar with the following icon:
        .. image:: /images/bakeOffsetsButton.png

    The full interface looks like this, listing found modules in the scene to select and bake offsets down to.
        .. image:: /images/bakeOffsets.png

    """

    def __init__(self, mainUI):
        """
        Instantiates the class, getting the QSettings and then calling on ART_BakeOffsetsUI.buildBakeOffsetsUI to
        create the interface.

        :param mainUI: The instance of the Rig Creator UI where this class was called from.

        .. seealso:: ART_BakeOffsetsUI.buildBakeOffsetsUI

        """

        # get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")
        self.mainUI = mainUI

        # build the UI
        self.buildBakeOffsetsUI()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildBakeOffsetsUI(self):
        """
        Builds the interface, finding all modules and listing them for selection.

        """

        if cmds.window("ART_BakeOffsetsWin", exists=True):
            cmds.deleteUI("ART_BakeOffsetsWin", wnd=True)

        # launch a UI to get the name information
        self.bakeOffsetsWin = QtWidgets.QMainWindow(self.mainUI)

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.bakeOffsetsWin.setStyleSheet(self.style)

        # size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # create the main widget
        self.bakeOffsetsWin_mainWidget = QtWidgets.QWidget()
        self.bakeOffsetsWin.setCentralWidget(self.bakeOffsetsWin_mainWidget)

        # set qt object name
        self.bakeOffsetsWin.setObjectName("ART_BakeOffsetsWin")
        self.bakeOffsetsWin.setWindowTitle("Bake Offsets")

        # create the mainLayout for the rig creator UI
        self.bakeOffsetsWin_mainLayout = QtWidgets.QVBoxLayout(self.bakeOffsetsWin_mainWidget)
        self.bakeOffsetsWin_mainLayout.setContentsMargins(0, 0, 0, 0)

        self.bakeOffsetsWin.resize(400, 250)
        self.bakeOffsetsWin.setSizePolicy(mainSizePolicy)
        self.bakeOffsetsWin.setMinimumSize(QtCore.QSize(400, 250))
        self.bakeOffsetsWin.setMaximumSize(QtCore.QSize(400, 250))

        # create the background
        self.bakeOffsetsWin_frame = QtWidgets.QFrame()
        self.bakeOffsetsWin_mainLayout.addWidget(self.bakeOffsetsWin_frame)

        # create the layout for the widgets
        self.bakeOffsetsWin_widgetLayout = QtWidgets.QHBoxLayout(self.bakeOffsetsWin_frame)
        self.bakeOffsetsWin_widgetLayout.setContentsMargins(5, 5, 5, 5)

        # add the QListWidget Frame
        self.bakeOffsetsWin_moduleListFrame = QtWidgets.QFrame()
        self.bakeOffsetsWin_moduleListFrame.setMinimumSize(QtCore.QSize(265, 200))
        self.bakeOffsetsWin_moduleListFrame.setMaximumSize(QtCore.QSize(265, 200))
        self.bakeOffsetsWin_moduleListFrame.setContentsMargins(20, 0, 20, 0)

        # create the list widget
        self.bakeOffsetsWin_moduleList = QtWidgets.QListWidget(self.bakeOffsetsWin_moduleListFrame)
        self.bakeOffsetsWin_widgetLayout.addWidget(self.bakeOffsetsWin_moduleListFrame)
        self.bakeOffsetsWin_moduleList.setMinimumSize(QtCore.QSize(265, 200))
        self.bakeOffsetsWin_moduleList.setMaximumSize(QtCore.QSize(265, 200))
        self.bakeOffsetsWin_moduleList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.bakeOffsetsWin_moduleList.setSpacing(3)

        # add the layout for the buttons
        self.bakeOffsetsWin_buttonLayoutAll = QtWidgets.QVBoxLayout()
        self.bakeOffsetsWin_widgetLayout.addLayout(self.bakeOffsetsWin_buttonLayoutAll)
        self.bakeOffsetsWin_buttonLayoutAll.setContentsMargins(5, 20, 5, 20)

        # add the selection buttons
        self.bakeOffsetsWin_selectionButtonLayout = QtWidgets.QVBoxLayout()
        self.bakeOffsetsWin_buttonLayoutAll.addLayout(self.bakeOffsetsWin_selectionButtonLayout)
        self.bakeOffsetsWin_selectAllButton = QtWidgets.QPushButton("Select All")
        self.bakeOffsetsWin_selectAllButton.setMinimumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_selectAllButton.setMaximumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_selectionButtonLayout.addWidget(self.bakeOffsetsWin_selectAllButton)
        self.bakeOffsetsWin_selectAllButton.clicked.connect(self.bakeOffsetsWin_moduleList.selectAll)
        self.bakeOffsetsWin_selectAllButton.setObjectName("blueButton")

        self.bakeOffsetsWin_selectNoneButton = QtWidgets.QPushButton("Clear Selection")
        self.bakeOffsetsWin_selectNoneButton.setMinimumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_selectNoneButton.setMaximumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_selectionButtonLayout.addWidget(self.bakeOffsetsWin_selectNoneButton)
        self.bakeOffsetsWin_selectNoneButton.clicked.connect(self.bakeOffsetsWin_moduleList.clearSelection)
        self.bakeOffsetsWin_selectNoneButton.setObjectName("blueButton")

        # spacer
        spacerItem = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.bakeOffsetsWin_selectionButtonLayout.addItem(spacerItem)

        # add the buttons for reset settings and reset transforms
        self.bakeOffsetsWin_bakeOFfsetsBtn = QtWidgets.QPushButton("Bake Offsets")
        self.bakeOffsetsWin_bakeOFfsetsBtn.setMinimumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_bakeOFfsetsBtn.setMaximumSize(QtCore.QSize(115, 25))
        self.bakeOffsetsWin_selectionButtonLayout.addWidget(self.bakeOffsetsWin_bakeOFfsetsBtn)
        self.bakeOffsetsWin_bakeOFfsetsBtn.setToolTip("Turn on Aim Mode for selected modules.")
        self.bakeOffsetsWin_bakeOFfsetsBtn.clicked.connect(partial(self.bakeOffsets))
        self.bakeOffsetsWin_bakeOFfsetsBtn.setObjectName("blueButton")

        # populate the list widget
        modules = utils.returnRigModules()
        for module in modules:
            # get module name
            moduleName = cmds.getAttr(module + ".moduleName")
            if moduleName != "root":
                self.bakeOffsetsWin_moduleList.addItem(moduleName)

        # show the window
        self.bakeOffsetsWin.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def bakeOffsets(self):
        """
        Tales selected modules listed in the QListWidget and bakes the offset mover values up to the global mover
        parent. This is achieved by creating a locator in the space of the offset mover, zeroing the offset mover
        out, and constraining the global mover to the constraint. Finally, the constraints are removed and the
        locators deleted.

        """

        selected = self.bakeOffsetsWin_moduleList.selectedItems()
        items = []
        for each in selected:
            items.append(each.text())

        constraints = []
        locators = []

        # go through each module and create the locators for the offset movers
        for each in self.mainUI.moduleInstances:
            name = each.name
            if name in items:

                # get movers
                jointMovers = each.returnJointMovers

                # separate mover lists
                globalMovers = jointMovers[0]
                offsetMovers = jointMovers[1]

                # create locators for the offsetMovers, then zero out offset mover
                for mover in offsetMovers:
                    locatorName = mover.partition("_offset")[0] + "_loc"
                    loc = cmds.spaceLocator(name=locatorName)[0]

                    # constrain locator
                    constraint = cmds.parentConstraint(mover, loc)[0]
                    cmds.delete(constraint)

                    # parent locator under a copy of the locatorName
                    parentLoc = cmds.duplicate(loc)[0]
                    cmds.parent(loc, parentLoc)
                    locators.append(parentLoc)

                for mover in offsetMovers:
                    for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]:
                        try:
                            cmds.setAttr(mover + attr, 0)
                        except:
                            pass

        # now, for each global mover, find child groups that are constrained to them
        for each in self.mainUI.moduleInstances:
            name = each.name
            if name in items:
                # get movers
                jointMovers = each.returnJointMovers

                # separate mover lists
                globalMovers = jointMovers[0]
                offsetMovers = jointMovers[1]

                childGrps = []

                for mover in globalMovers:
                    try:

                        # find the mover group constrained to this mover (if any)
                        connection = cmds.listConnections(mover, type="parentConstraint")[0]
                        grp = cmds.listConnections(connection + ".constraintRotateX")[0]
                        if grp.find("_mover_grp") != -1:
                            childGrps.append([mover, grp])

                        # now take this group and delete the constraints
                        cmds.select(grp)
                        cmds.delete(constraints=True)

                    except Exception, e:
                        print e

        # now snap global movers to offset movers
        for each in self.mainUI.moduleInstances:
            name = each.name
            if name in items:
                # get movers
                jointMovers = each.returnJointMovers

                # separate mover lists
                globalMovers = jointMovers[0]
                offsetMovers = jointMovers[1]

                for mover in globalMovers:
                    if cmds.objExists(mover + "_loc"):
                        constraint = cmds.parentConstraint(mover + "_loc", mover)[0]
                        constraints.append(constraint)

        # now remove all locs
        for const in constraints:
            cmds.delete(const)

        for loc in locators:
            cmds.delete(loc)

        # finally, reconstrain mover_grps to their movers
        cmds.refresh(force=True)
        for group in childGrps:
            cmds.parentConstraint(group[0], group[1], mo=True)
            cmds.scaleConstraint(group[0], group[1])

        cmds.select(clear=True)
