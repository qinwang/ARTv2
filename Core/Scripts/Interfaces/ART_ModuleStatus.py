from ThirdParty.Qt import QtGui, QtCore, QtWidgets
import maya.cmds as cmds
import System.utils as utils


windowTitle = "Module Stats"
windowObject = "pyArtModStatusUi"



class ART_ModStatusWin(QtWidgets.QMainWindow):

    def __init__(self, parent = None):


        super(ART_ModStatusWin, self).__init__(parent)

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")


        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        style = f.read()
        f.close()

        self.setStyleSheet(style)

        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        #set qt object name
        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)

        #create the mainLayout for the rig creator UI
        self.mainLayout = QtWidgets.QHBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setMinimumSize(QtCore.QSize(300, 400))
        self.setMaximumSize(QtCore.QSize(300, 600))
        self.resize(QtCore.QSize(300, 400))


        #create the background
        self.frame = QtWidgets.QFrame()
        self.frame.setObjectName("mid")
        self.mainLayout.addWidget(self.frame)


        #create the widget layout
        self.widgetLayout = QtWidgets.QVBoxLayout(self.frame)

        #create the table widget
        self.modTable = QtWidgets.QTableWidget()
        self.modTable.setObjectName("mid")
        self.widgetLayout.addWidget(self.modTable)
        self.modTable.setColumnCount(3)
        self.modTable.setHorizontalHeaderLabels(["Module", "Pinned", "Aiming"])
        self.modTable.setColumnWidth(0, 100)
        self.modTable.setColumnWidth(1, 65)
        self.modTable.setColumnWidth(2, 65)

        #populate the table widget
        self.populateTable()


        #add refresh button
        self.refreshButton = QtWidgets.QPushButton("Refresh")
        self.widgetLayout.addWidget(self.refreshButton)
        self.refreshButton.setObjectName("blueButton")
        self.refreshButton.clicked.connect(self.refresh)


        self.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def populateTable(self):

        pixmap = QtGui.QPixmap(20, 20)
        pixmap.fill(QtGui.QColor(0, 255, 0))
        iconOn = QtGui.QIcon(pixmap)

        pixmapOff = QtGui.QPixmap(20, 20)
        pixmapOff.fill(QtGui.QColor(255, 0, 0))
        iconOff = QtGui.QIcon(pixmapOff)

        modules = utils.returnRigModules()
        self.modTable.setRowCount(100 + len(modules))
        counter = 0
        for module in modules:

            aimState = False
            pinState = False

            #get module name
            moduleName = cmds.getAttr(module + ".moduleName")

            if cmds.objExists(module + ".aimMode"):
                aimState = cmds.getAttr(module + ".aimMode")
            if cmds.objExists(module + ".pinned"):
                pinState = cmds.getAttr(module + ".pinned")

            moduleItem = QtWidgets.QTableWidgetItem(moduleName)
            self.modTable.setItem(counter, 0, moduleItem)

            if aimState:
                lockItem = QtWidgets.QTableWidgetItem(iconOn, "")
            else:
                lockItem = QtWidgets.QTableWidgetItem(iconOff, "")

            self.modTable.setItem(counter, 2, lockItem)


            if pinState:
                pinItem = QtWidgets.QTableWidgetItem(iconOn, "")
            else:
                pinItem = QtWidgets.QTableWidgetItem(iconOff, "")

            self.modTable.setItem(counter, 1, pinItem)

            counter += 1

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def refresh(self):

        while self.modTable.rowCount() > 0:
            self.modTable.removeRow(0)

        self.populateTable()




def run(parent):

    if cmds.window("pyArtModStatusUi", exists = True):
        cmds.deleteUI("pyArtModStatusUi", wnd = True)

    win = ART_ModStatusWin(parent)
    win.show()

