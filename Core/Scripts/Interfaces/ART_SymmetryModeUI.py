from ThirdParty.Qt import QtGui, QtCore, QtWidgets
from functools import partial
import maya.cmds as cmds
import System.utils as utils



class ART_SymmetryMode():

    def __init__(self, mainUI):

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")

        #build the UI
        self.buildSymmetryModeUI(mainUI)
        self.mainUI = mainUI


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildSymmetryModeUI(self, mainUI):

        if cmds.window("ART_SymmetryModeWin", exists = True):
            cmds.deleteUI("ART_SymmetryModeWin", wnd = True)

        #launch a UI to get the name information
        self.symmetryModeWin = QtWidgets.QMainWindow(mainUI)

        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        style = f.read()
        f.close()

        self.symmetryModeWin.setStyleSheet(style)


        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the main widget
        self.symModeWin_mainWidget = QtWidgets.QWidget()
        self.symmetryModeWin.setCentralWidget(self.symModeWin_mainWidget)

        #set qt object name
        self.symmetryModeWin.setObjectName("ART_SymmetryModeWin")
        self.symmetryModeWin.setWindowTitle("Mass Mirror Mode")

        #create the mainLayout for the rig creator UI
        self.symModeWin_mainLayout = QtWidgets.QVBoxLayout(self.symModeWin_mainWidget)
        self.symModeWin_mainLayout.setContentsMargins(0, 0, 0, 0)

        self.symmetryModeWin.setSizePolicy(mainSizePolicy)
        self.symmetryModeWin.setMinimumSize(QtCore.QSize( 600, 250 ))
        self.symmetryModeWin.setMaximumSize(QtCore.QSize( 600, 250 ))

        #create the background
        self.symModeWin_frame = QtWidgets.QFrame()
        self.symModeWin_frame.setObjectName("mid")
        self.symModeWin_mainLayout.addWidget(self.symModeWin_frame)



        #create the layout for the widgets
        self.symModeWin_widgetLayout = QtWidgets.QHBoxLayout(self.symModeWin_frame)
        self.symModeWin_widgetLayout.setContentsMargins(5, 5, 5, 5)

        #add the QListWidget Frame
        self.symModeWin_moduleListFrame = QtWidgets.QFrame()
        self.symModeWin_moduleListFrame.setObjectName("mid")
        self.symModeWin_moduleListFrame.setMinimumSize(QtCore.QSize( 450, 200 ))
        self.symModeWin_moduleListFrame.setMaximumSize(QtCore.QSize( 450, 200 ))
        self.symModeWin_moduleListFrame.setContentsMargins(20,0,20,0)


        #create the list widget
        self.symModeWin_moduleList = QtWidgets.QListWidget(self.symModeWin_moduleListFrame)
        self.symModeWin_widgetLayout.addWidget(self.symModeWin_moduleListFrame)
        self.symModeWin_moduleList.setMinimumSize(QtCore.QSize( 450, 200 ))
        self.symModeWin_moduleList.setMaximumSize(QtCore.QSize( 450, 200 ))
        self.symModeWin_moduleList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.symModeWin_moduleList.setSpacing(3)


        #add the layout for the buttons
        self.symModeWin_buttonLayoutAll = QtWidgets.QVBoxLayout()
        self.symModeWin_widgetLayout.addLayout(self.symModeWin_buttonLayoutAll)
        self.symModeWin_buttonLayoutAll.setContentsMargins(5, 20, 5, 20)

        #add the selection buttons
        self.symModeWin_selectionButtonLayout = QtWidgets.QVBoxLayout()
        self.symModeWin_buttonLayoutAll.addLayout(self.symModeWin_selectionButtonLayout)
        self.symModeWin_selectAllButton = QtWidgets.QPushButton("Select All")
        self.symModeWin_selectAllButton.setMinimumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_selectAllButton.setMaximumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_selectionButtonLayout.addWidget(self.symModeWin_selectAllButton)
        self.symModeWin_selectAllButton.clicked.connect(partial(self.symmetryMode_selectDeselect, True))
        self.symModeWin_selectAllButton.setObjectName("blueButton")

        self.symModeWin_selectNoneButton = QtWidgets.QPushButton("Clear Selection")
        self.symModeWin_selectNoneButton.setMinimumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_selectNoneButton.setMaximumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_selectionButtonLayout.addWidget(self.symModeWin_selectNoneButton)
        self.symModeWin_selectNoneButton.clicked.connect(partial(self.symmetryMode_selectDeselect, False))
        self.symModeWin_selectNoneButton.setObjectName("blueButton")

        #spacer
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.symModeWin_buttonLayoutAll.addItem(spacerItem)

        #add the mirror buttons
        self.symModeWin_mirrorButtonLayout = QtWidgets.QVBoxLayout()
        self.symModeWin_buttonLayoutAll.addLayout(self.symModeWin_mirrorButtonLayout)
        self.symModeWin_mirrorL2RButton = QtWidgets.QPushButton("Mirror Checked")
        self.symModeWin_mirrorL2RButton.setToolTip("Mirror selected modules to unselected modules")

        self.symModeWin_mirrorL2RButton.setMinimumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_mirrorL2RButton.setMaximumSize(QtCore.QSize( 115, 25 ))
        self.symModeWin_mirrorButtonLayout.addWidget(self.symModeWin_mirrorL2RButton)
        self.symModeWin_mirrorL2RButton.setObjectName("blueButton")

        self.symModeWin_mirrorL2RButton.clicked.connect(partial(self.symmetryMode_mirror))



        #populate the list widget
        modules = utils.returnRigModules()
        entries = []
        listMods = []

        for mod in modules:
            modName = cmds.getAttr(mod + ".moduleName")
            mirrorModule = cmds.getAttr(mod + ".mirrorModule")
            invalidTypes = [None, "None"]
            if mirrorModule not in invalidTypes:
                if modName not in listMods:
                    entries.append([modName, mirrorModule])
                    listMods.append(modName)
                    listMods.append(mirrorModule)

        self.symModeWinModues = {}

        if len(entries) == 0:
            item = QtWidgets.QListWidgetItem(self.symModeWin_moduleList)
            label = QtWidgets.QLabel("No modules with mirroring setup")
            item.setSizeHint(label.sizeHint())
            self.symModeWin_moduleList.addItem(item)
            self.symModeWin_moduleList.setItemWidget(item, label)


        for each in entries:

            #create a custom widget to add to each entry in the listWidget
            mainWidget = QtWidgets.QWidget()
            buttonLayout = QtWidgets.QHBoxLayout(mainWidget)

            #create the checkbox
            checkbox = QtWidgets.QCheckBox()
            checkbox.setMinimumSize(QtCore.QSize( 12, 12 ))
            checkbox.setMaximumSize(QtCore.QSize( 12, 12 ))
            checkbox.setChecked(True)
            buttonLayout.addWidget(checkbox)

            label = QtWidgets.QLabel("Mirror ")
            buttonLayout.addWidget(label)

            mirrorFrom = QtWidgets.QComboBox()
            mirrorFrom.addItem(each[0])
            mirrorFrom.addItem(each[1])
            buttonLayout.addWidget(mirrorFrom)
            mirrorFrom.setMinimumWidth(150)


            label = QtWidgets.QLabel(" To ")
            buttonLayout.addWidget(label)
            label.setAlignment(QtCore.Qt.AlignCenter)

            mirrorTo = QtWidgets.QComboBox()
            mirrorTo.addItem(each[1])
            mirrorTo.addItem(each[0])
            buttonLayout.addWidget(mirrorTo)
            mirrorTo.setMinimumWidth(150)

            #signal/slots
            mirrorFrom.currentIndexChanged.connect(partial(self.toggleComboBoxFrom, mirrorFrom, mirrorTo))
            mirrorTo.currentIndexChanged.connect(partial(self.toggleComboBoxTo, mirrorFrom, mirrorTo))

            #add this item widget to the list
            item = QtWidgets.QListWidgetItem(self.symModeWin_moduleList)
            index = entries.index(each)
            if (index % 2) == 0:
                item.setBackground(QtGui.QColor(106,106,108))
            else:
                item.setBackground(QtGui.QColor(46,46,48))

            item.setSizeHint(mainWidget.sizeHint())
            self.symModeWin_moduleList.addItem(item)
            self.symModeWin_moduleList.setItemWidget(item, mainWidget)



        #show the window
        self.symmetryModeWin.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def symmetryMode_selectDeselect(self, state):


        #find all items in the list
        items = self.symModeWin_moduleList.findItems('', QtCore.Qt.MatchRegExp)
        for each in items:
            itemWidget = self.symModeWin_moduleList.itemWidget(each)

            try:
                #get the layout of this widget
                layout = itemWidget.findChild(QtWidgets.QHBoxLayout)
                #find the checbox and check it
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if type(item.widget()) == QtWidgets.QCheckBox:
                        item.widget().setChecked(state)
            except:
                pass


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleComboBoxFrom(self, mirrorFrom, mirrorTo, *args):

        if mirrorFrom.currentText() == mirrorTo.currentText():
            index = mirrorTo.findText(mirrorFrom.currentText(), QtCore.Qt.MatchExactly)
            if index == 0:
                mirrorTo.setCurrentIndex(1)
            else:
                mirrorTo.setCurrentIndex(0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def toggleComboBoxTo(self, mirrorFrom, mirrorTo, *args):

        if mirrorTo.currentText() == mirrorFrom.currentText():
            index = mirrorFrom.findText(mirrorTo.currentText(), QtCore.Qt.MatchExactly)
            if index == 0:
                mirrorFrom.setCurrentIndex(1)
            else:
                mirrorFrom.setCurrentIndex(0)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def symmetryMode_mirror(self):

        #find all items in the list
        items = self.symModeWin_moduleList.findItems('', QtCore.Qt.MatchRegExp)
        for each in items:
            itemWidget = self.symModeWin_moduleList.itemWidget(each)

            try:
                #get the layout of this widget
                layout = itemWidget.findChild(QtWidgets.QHBoxLayout)

                #find the checkbox
                state = False
                for i in range(layout.count()):
                    item = layout.itemAt(i)

                    if type(item.widget()) == QtWidgets.QCheckBox:
                        #get the checkbox state
                        state = item.widget().isChecked()

                    if type(item.widget()) == QtWidgets.QComboBox:
                        if state == True:
                            moduleName = item.widget().currentText()
                            modules = utils.returnRigModules()
                            for mod in modules:
                                modName = cmds.getAttr(mod + ".moduleName")

                                if modName == moduleName:
                                    modType = cmds.getAttr(mod + ".moduleType")
                                    importMod = __import__("RigModules." + modType, {}, {}, [modType])
                                    reload(importMod)

                                    moduleClass = getattr(importMod, importMod.className)
                                    moduleInst = moduleClass(self.mainUI, modName)
                                    moduleInst.mirrorTransformations()

            except:
                pass