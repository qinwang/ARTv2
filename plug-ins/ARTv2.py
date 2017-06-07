import os
import sys
import webbrowser

import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

# maya 2016 and before vs maya 2017 and after
try:
    from PySide import QtCore
except:
    from PySide2 import QtCore


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def makeMyCustomUI():
    gMainWindow = mel.eval('$temp1=$gMainWindow')
    customMenu = cmds.menu("epicGamesARTv2Menu", label="A.R.T. 2.0", parent=gMainWindow)

    # ART
    cmds.menuItem(parent=customMenu, label="Animation Rigging Toolkit 2.0", bld=True, enable=False)

    cmds.menuItem(parent=customMenu, divider=True, dividerLabel="Rigging:")
    cmds.menuItem(parent=customMenu, label="Rig Creator", c=ART_characterRigCreator)
    cmds.menuItem(parent=customMenu, label="Edit Rig", c=ART_EditRig)

    cmds.menuItem(parent=customMenu, divider=True, dividerLabel="Animation:")
    cmds.menuItem(parent=customMenu, label="Add Rig For Animation", c=ART_AddRig)
    cmds.menuItem(parent=customMenu, label="Animation Tools", c=ART_LaunchAnimTools)

    cmds.menuItem(parent=customMenu, divider=True, dividerLabel="Misc:")
    cmds.menuItem(parent=customMenu, label="Settings", c=launchSettings)
    cmds.menuItem(parent=customMenu, label="Check For Updates", c=ART_Update)
    cmds.menuItem(parent=customMenu, label="Report an Issue", c=ART_Report)

    cmds.menuItem(parent=customMenu, divider=True, dividerLabel="Help")
    cmds.menuItem(parent=customMenu, label="Technical Documentation", c=ART_TechDocs)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_writeStyleSheets(*args):
    import System.utils as utils
    reload(utils)

    import System.interfaceUtils as interfaceUtils
    reload(interfaceUtils)

    settings = QtCore.QSettings("Epic Games", "ARTv2")
    scriptPath = settings.value("scriptPAth")
    stylesheetDir = utils.returnNicePath(scriptPath, "Interfaces/StyleSheets/")
    stylesheets = os.listdir(stylesheetDir)

    for sheet in stylesheets:
        interfaceUtils.writeQSS(os.path.join(stylesheetDir, sheet))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_characterRigCreator(*args):
    ART_writeStyleSheets()
    import Interfaces.ART_RigCreatorUI as ART_RigCreatorUI
    reload(ART_RigCreatorUI)
    ART_RigCreatorUI.createUI()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_EditRig(*args):
    ART_writeStyleSheets()
    import Interfaces.ART_EditRigUI as ART_EditRigUI
    ART_EditRigUI.run()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_AddRig(*args):
    ART_writeStyleSheets()
    import Interfaces.ART_EditRigUI as ART_EditRigUI
    ART_EditRigUI.runAdd()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_LaunchAnimTools(*args):
    ART_writeStyleSheets()
    import Interfaces.ART_AnimationUI as ART_AnimationUI
    reload(ART_AnimationUI)
    ART_AnimationUI.run()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def launchSettings(*args):
    ART_writeStyleSheets()
    import System.ART_Settings as ART_Settings
    ART_Settings.run()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_Update(*args):
    ART_writeStyleSheets()
    import System.ART_Updater as ART_Updater
    ART_Updater.run()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_Report(*args):
    ART_writeStyleSheets()
    import System.ART_Reporter as ART_Reporter
    ART_Reporter.run()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ART_TechDocs(*args):
    settings = QtCore.QSettings("Epic Games", "ARTv2")
    toolsPath = settings.value("toolsPath")
    html_file = os.path.join(toolsPath, "Documentation\\build\\index.html")
    webbrowser.get().open('file://' + os.path.realpath(html_file))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def removeMyCustomUI():
    cmds.deleteUI("epicGamesARTv2Menu")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Function for allowing user to browse to Maya Tools directory location
def epicToolsInstall_UI():
    if cmds.window("epicToolsInstall_UI", exists=True):
        cmds.deleteUI("epicToolsInstall_UI")

    window = cmds.window("epicToolsInstall_UI", w=300, h=100, title="Epic Games Tools Install", mnb=False, mxb=False)

    mainLayout = cmds.columnLayout(w=300, h=100)
    formLayout = cmds.formLayout(w=300, h=100)

    text = cmds.text(
        label="ERROR: Could not find Maya Tools directory.\n Please locate folder using the \'Browse\' button.", w=300)
    cancelButton = cmds.button(label="Cancel", w=140, h=50, c=cancel)
    browseButton = cmds.button(label="Browse", w=140, h=50, c=browse)

    cmds.formLayout(formLayout, edit=True, af=[(text, 'left', 10), (text, 'top', 10)])
    cmds.formLayout(formLayout, edit=True, af=[(cancelButton, 'left', 5), (cancelButton, 'top', 50)])
    cmds.formLayout(formLayout, edit=True, af=[(browseButton, 'right', 5), (browseButton, 'top', 50)])

    cmds.showWindow(window)
    cmds.window(window, edit=True, w=300, h=100)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# if user cancels out of UI setup
def cancel(*args):
    cmds.deleteUI("epicToolsInstall_UI")
    cmds.warning("Maya Tools will not be setup")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# function to browse to MayaTools location on disk
def browse(*args):
    # browser to tools directory
    mayaToolsDir = cmds.fileDialog2(dialogStyle=2, fileMode=3)[0]
    # confirm that this is actually the maya tools directory
    if os.path.basename(mayaToolsDir) != "ARTv2":
        cmds.warning("Selected directory is not valid. Please locate the ARTv2 directory.")


    else:
        cmds.deleteUI("epicToolsInstall_UI")

        # create file that contains this path
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        settings.setValue("toolsPath", os.path.normpath(mayaToolsDir))
        settings.setValue("scriptPath", os.path.normpath(mayaToolsDir + "/Core/Scripts"))
        settings.setValue("iconPath", os.path.normpath(mayaToolsDir + "/Core/Icons"))
        settings.setValue("projectPath", os.path.normpath(mayaToolsDir + "/Projects"))

        # run setup
        epicTools()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# check to see if tools exist
def epicTools():
    settings = QtCore.QSettings("Epic Games", "ARTv2")
    toolsPath = settings.value("toolsPath")
    scriptPath = settings.value("scriptPath")
    iconPath = settings.value("iconPath")
    projectPath = settings.value("projectPath")

    if toolsPath == None:
        epicToolsInstall_UI()

    if os.path.exists(toolsPath):
        paths = [returnFriendlyPath(scriptPath),
                 returnFriendlyPath(os.path.join(scriptPath, os.path.normpath("System"))),
                 returnFriendlyPath(os.path.join(scriptPath, os.path.normpath("Interfaces"))),
                 returnFriendlyPath(os.path.join(scriptPath, os.path.normpath("RigModules"))),
                 returnFriendlyPath(os.path.join(scriptPath, os.path.normpath("ThirdParty")))]
        defaultPaths = [returnFriendlyPath(os.path.join(toolsPath, os.path.normpath("Core/Scripts"))),
                        returnFriendlyPath(os.path.join(toolsPath, os.path.normpath("Core/Scripts/System"))),
                        returnFriendlyPath(os.path.join(toolsPath, os.path.normpath("Core/Scripts/Interfaces"))),
                        returnFriendlyPath(os.path.join(toolsPath, os.path.normpath("Core/Scripts/RigModules"))),
                        returnFriendlyPath(os.path.join(toolsPath, os.path.normpath("Core/Scripts/ThirdParty")))]

        # look in sys.path to see if path is in sys.path. if not, add it
        for path in defaultPaths:
            for sysPath in sys.path:
                sysPath = returnFriendlyPath(sysPath)
                if path == sysPath:
                    sys.path.remove(path)

        for path in paths:
            if not path in sys.path:
                sys.path.append(path)

    else:
        epicToolsInstall_UI()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# convenience function for returning an os friendly path
def returnFriendlyPath(path):
    nicePath = os.path.normpath(path)
    if nicePath.partition("\\")[2] != "":
        nicePath = nicePath.replace("\\", "/")
    return nicePath


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Jeremy Ernst\nEpic Games, Inc.", "1.0")
    status = mplugin.registerUI(makeMyCustomUI, removeMyCustomUI)

    # check for tools path
    epicTools()

    cmds.help(popupMode=True)
    return status


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
