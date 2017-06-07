from ThirdParty.Qt import QtGui, QtCore, QtWidgets
import maya.cmds as cmds
import os, json
import utils, math, traceback, urllib2, zipfile
import shutil, errno, stat, base64
import System.git_utils as git

#maya 2016< 2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken



def getMainWindow():
    import maya.OpenMayaUI as mui
    pointer = mui.MQtUtil.mainWindow()
    #pyside QMainWindow takes in a QWidget rather than QObject
    return shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)



windowTitle = "ARTv2: Check For Updates"
windowObject = "pyArtUpdaterWin"



class ART_Updater(QtWidgets.QMainWindow):

    def __init__(self, parent = None):

        super(ART_Updater, self).__init__(parent)

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")

        self.toolsPath = settings.value("toolsPath")
        self.scriptPath = settings.value("scriptPath")
        self.iconsPath = settings.value("iconPath")
        self.projPath = settings.value("projectPath")

        #get github credentials
        self.credentials = git.getGitCreds()
        if self.credentials == None:
            git.gitCredsUI(self)
            self.credentials = git.getGitCreds()



        #build the UI
        self.buildSettingsUi()



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildSettingsUi(self):

        #fonts
        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.font.setBold(False)

        self.fontSmall = QtGui.QFont()
        self.fontSmall .setPointSize(9)
        self.fontSmall .setBold(False)

        self.titleFont = QtGui.QFont()
        self.titleFont.setPointSize(40)
        self.titleFont.setBold(True)


        #images
        frameBackground =  os.path.normcase(os.path.join(self.iconsPath, "System/field_background.png"))
        if frameBackground.partition("\\")[2] != "":
            frameBackground = frameBackground.replace("\\", "/")

        imageBkgrd =  os.path.normcase(os.path.join(self.iconsPath, "System/toolbar_background.png"))
        if imageBkgrd.partition("\\")[2] != "":
            imageBkgrd = imageBkgrd.replace("\\", "/")

        imageBtnBkrd =  os.path.normcase(os.path.join(self.iconsPath, "System/blue_field_background.png"))
        if imageBtnBkrd.partition("\\")[2] != "":
            imageBtnBkrd = imageBtnBkrd.replace("\\", "/")

        #load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()


        self.setStyleSheet(self.style)

        #size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setStyleSheet(self.style)
        self.mainWidget.setStyleSheet("background-color: rgb(0, 0, 0);, color: rgb(0,0,0);")
        self.setCentralWidget(self.mainWidget)

        #set qt object name
        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        #create the mainLayout for the rig creator UI
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.resize(600, 300)
        self.setSizePolicy(mainSizePolicy)
        self.setMinimumSize(QtCore.QSize( 600, 300 ))
        self.setMaximumSize(QtCore.QSize( 600, 300 ))


        #create the QFrame
        self.frame = QtWidgets.QFrame()
        self.layout.addWidget(self.frame)
        self.widgetLayout = QtWidgets.QVBoxLayout(self.frame)

        #info page styling
        self.frame.setStyleSheet("background-image: url(" + imageBkgrd + ");")


        #detailed information
        self.infoText = QtWidgets.QTextEdit()
        self.infoText.acceptRichText()
        self.infoText.setStyleSheet("background-color: rgb(120,120,120); background-image: url(" + frameBackground + ");")
        self.widgetLayout.addWidget(self.infoText)
        self.infoText.setMinimumSize(QtCore.QSize(550,170))
        self.infoText.setMaximumSize(QtCore.QSize(550,170))
        self.infoText.setReadOnly(True)
        self.infoText.setAutoFormatting(QtWidgets.QTextEdit.AutoBulletList)
        self.infoText.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)


        #progress bar
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setStyleSheet(self.style)
        self.progressBar.setMinimumSize(QtCore.QSize(550, 25))
        self.progressBar.setMaximumSize(QtCore.QSize(550, 25))
        self.widgetLayout.addWidget(self.progressBar)

        #button bar
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addLayout(self.buttonLayout)

        self.cancelButton = QtWidgets.QPushButton("Close")
        self.buttonLayout.addWidget(self.cancelButton)
        self.cancelButton.setStyleSheet(self.style)
        self.cancelButton.setObjectName("blueButton")
        self.cancelButton.clicked.connect(self.cancel)

        self.updateButton = QtWidgets.QPushButton("Update")
        self.buttonLayout.addWidget(self.updateButton)
        self.updateButton.setStyleSheet(self.style)
        self.updateButton.setObjectName("blueButton")
        self.updateButton.clicked.connect(self.downloadUpdates)

        if self.credentials != None:
            self.getInfo()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getInfo(self):

        #need to eventually swap this with the real file
        request = urllib2.Request("https://raw.githubusercontent.com/epicernst/Test/master/ARTv2_VersionInfo.json")
        base64String = base64.encodestring('%s:%s' % (self.credentials[0], self.credentials[1])).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64String)
        try:
            result = urllib2.urlopen(request)
        except Exception, e:
            self.infoText.setTextColor(QtGui.QColor(249,241,12))
            self.infoText.append(str(e))
            self.infoText.append("Your Github login credentials may be invalid or you do not have access to this repo.\n\n")
            self.infoText.setTextColor(QtGui.QColor(255,255,255))

            settings = QtCore.QSettings("Epic Games", "ARTv2")
            settings.remove("gitUser")
            settings.remove("gitPass")

            return


        content = json.loads(result.read())
        versions = content.get("versions")

        newFeatures = []
        majorFixes = []
        minorFixes = []

        for version in versions:
            data = versions.get(version)
            for key in data:
                if key == "New":
                    info = data.get(key)
                    for each in info:
                        newFeatures.append(each)

                if key == "Critical":
                    info = data.get(key)
                    for each in info:
                        majorFixes.append(each)

                if key == "Minor":
                    info = data.get(key)
                    for each in info:
                        minorFixes.append(each)


        #Compare local version to latest
        latestVersion = content.get("latest version")
        localVersion = self.checkLocalVersion()

        if float(latestVersion) > float(localVersion):
            self.infoText.append("You are not up to date!\n")
            self.infoText.append("Latest Version:   " + str(content.get("latest version")))
            self.infoText.append("Local Version:    " + str(localVersion))

            self.infoText.append("\n")


            #release notes
            self.infoText.setFont(self.titleFont)
            self.infoText.setTextColor(QtGui.QColor(48,255,0))
            self.infoText.setAlignment(QtCore.Qt.AlignCenter)
            self.infoText.append("|| NEW FEATURES ||")

            self.infoText.setFont(self.fontSmall)
            self.infoText.setAlignment(QtCore.Qt.AlignLeft)
            self.infoText.setTextColor(QtGui.QColor(255,255,255))
            for feature in newFeatures:
                self.infoText.append("        *" + str(feature))

            self.infoText.append("\n")
            self.infoText.setFont(self.titleFont)
            self.infoText.setTextColor(QtGui.QColor(249,168,12))
            self.infoText.setAlignment(QtCore.Qt.AlignCenter)
            self.infoText.append("|| MAJOR FIXES ||")

            self.infoText.setFont(self.fontSmall)
            self.infoText.setAlignment(QtCore.Qt.AlignLeft)
            self.infoText.setTextColor(QtGui.QColor(255,255,255))
            for fix in majorFixes:
                self.infoText.append("        *" + str(fix))

            self.infoText.append("\n")
            self.infoText.setFont(self.titleFont)
            self.infoText.setTextColor(QtGui.QColor(249,241,12))
            self.infoText.setAlignment(QtCore.Qt.AlignCenter)
            self.infoText.append("|| MINOR FIXES ||")

            self.infoText.setFont(self.fontSmall)
            self.infoText.setAlignment(QtCore.Qt.AlignLeft)
            self.infoText.setTextColor(QtGui.QColor(255,255,255))
            for each in minorFixes:
                self.infoText.append("        *" + str(each))

            self.infoText.moveCursor(QtGui.QTextCursor.Start)

        else:
            self.infoText.append("You are up-to-date!")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def checkLocalVersion(self):

        mayaModDir = os.environ["home"] + "/maya/modules/"
        if cmds.about(os = True) == "mac":
            mayaModDir = os.environ["home"] + "/Library/Preferences/Autodesk/maya/modules/"

        modName = "ARTv2.mod"
        modFile = mayaModDir + modName

        modFileObj = file(modFile, mode='r')
        lines = modFileObj.readlines()
        modFileObj.close()

        localVersion = float(lines[0].split(" ")[2])

        return localVersion


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def checkLatestVersion(self):

        info = git.getGitCreds()
        if info != None:
            user = info[0]
            password = info[1]

            #need to eventually swap this with the real file
            request = urllib2.Request("https://raw.githubusercontent.com/epicernst/Test/master/ARTv2_VersionInfo.json")
            base64String = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64String)
            result = urllib2.urlopen(request)
            content = json.loads(result.read())

            latestVersion = content.get("latest version")
            return latestVersion

        else:
            self.invalidCreds()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def updateLocalVersion(self):

        info = git.getGitCreds()
        if info != None:
            mayaModDir = cmds.internalVar(uad = True)
            mayaModDir = os.path.join(mayaModDir, "modules")
            mayaModDir = utils.returnFriendlyPath(os.path.join(mayaModDir, "ARTv2.mod"))

            if os.path.exists(mayaModDir):
                f = open(mayaModDir, 'r')
                line = f.readline()
                f.close()

                if line.find("+ ARTv2 ") != -1:
                    version = line.partition("+ ARTv2 ")[2].partition(" ")[0]
                    latest = self.checkLatestVersion()
                    newline = line.replace(str(version), str(latest))

                    f = open(mayaModDir, 'w')
                    f.write(newline)
                    f.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def findReadOnlyFiles(self, fullPath, listOfFiles):

        #list file contents
        contents = os.listdir(fullPath)
        for each in contents:
            if os.path.isfile(os.path.join(fullPath, each)):
                fileAttr = os.stat(os.path.join(fullPath, each)).st_mode
                if not fileAttr & stat.S_IWRITE:
                    try:
                        os.chmod(os.path.join(fullPath, each), stat.S_IWRITE)
                    except Exception, e:
                        listOfFiles.append([each, e])
            if os.path.isdir(os.path.join(fullPath, each)):
                self.findReadOnlyFiles(os.path.join(fullPath, each), listOfFiles)

        return listOfFiles

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def downloadUpdates(self):

        info = git.getGitCreds()
        if info != None:
            user = info[0]
            password = info[1]

        else:
            self.invalidCreds()
            return

        base64String = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
        opener = urllib2.build_opener()
        opener.addheaders = [("Authorization", "Basic %s" % base64String)]
        response = opener.open("https://github.com/epicernst/Test/archive/master.zip")

        zipContent = response.read()

        filename = os.path.basename("https://github.com/epicernst/Test/blob/master/master.zip")
        path = os.environ["home"]
        filePath = os.path.join(path, filename)

        with open(filePath, 'w') as f:
            f.write(zipContent)


        masterDir = os.path.dirname(filePath)
        mayaToolsZip = masterDir


        with zipfile.ZipFile(filePath, 'r') as zfile:
            for name in zfile.namelist():
                if name.find(".zip") != -1:
                    mayaToolsZip = os.path.join(mayaToolsZip, name)
            zfile.extractall(masterDir)



        baseToolsDir = os.path.dirname(self.toolsPath)
        wholeCopy = False

        fileIssues = []
        with zipfile.ZipFile(mayaToolsZip) as zf:
            removeDirs = ["MayaTools/Core/Scripts/", "MayaTools/Core/Icons/", "MayaTools/Core/JointMover/", "MayaTools/plug-ins/"]

            #set progress bar range
            self.progressBar.setMaximum(len(removeDirs) + 1)
            self.progressBar.setValue(0)

            for dir in removeDirs:
                fullPath = os.path.normpath(os.path.join(baseToolsDir, dir))

                #list file contents
                readOnlyFiles = self.findReadOnlyFiles(fullPath, fileIssues)

                #if readOnlyFiles is empty
                if len(readOnlyFiles) == 0:

                    #make a back-up of local versions
                    self.infoText.setTextColor(QtGui.QColor(0,0,0))
                    self.infoText.append("\n########################################################\n")
                    self.infoText.setTextColor(QtGui.QColor(255,255,255))
                    self.infoText.append("Creating Backup of current version.. " + str(dir))
                    self.infoText.moveCursor(QtGui.QTextCursor.End)

                    versionNumber = self.checkLocalVersion()
                    backupDir = os.path.join(os.path.dirname(self.toolsPath), "ARTv2/Backups")
                    backupDir = os.path.normpath(os.path.join(backupDir, str(versionNumber)))
                    printDir = backupDir
                    backupDir = utils.returnFriendlyPath(backupDir)
                    if not os.path.exists(backupDir):
                        os.makedirs(backupDir)

                    fullPath = utils.returnFriendlyPath(fullPath)

                    try:
                        shutil.move(fullPath, backupDir)
                        self.infoText.append("    Backups created in " + str(printDir))
                        self.infoText.moveCursor(QtGui.QTextCursor.End)
                    except Exception, e:
                        self.infoText.setTextColor(QtGui.QColor(249,168,12))
                        self.infoText.append(str(e))
                        self.infoText.setTextColor(QtGui.QColor(255,255,255))
                        wholeCopy = True

                    #extract zip file directory to original location
                    if wholeCopy == False:
                        for name in zf.namelist():
                            for each in removeDirs:
                                if name.find(each)!= -1:
                                    #extract directly to the base location
                                    try:
                                        zf.extract(name, baseToolsDir)

                                    except Exception, e:
                                        self.infoText.setTextColor(QtGui.QColor(249,168,12))
                                        self.infoText.append(str(e))
                                        self.infoText.setTextColor(QtGui.QColor(255,255,255))
                                        wholeCopy = True
                        self.infoText.append("    Extracted updated files to " + str(dir))
                        self.infoText.moveCursor(QtGui.QTextCursor.End)

                    #report on operations
                    value = self.progressBar.value()
                    self.progressBar.setValue(value + 1)




                #if readOnlyFiles is not empty
                else:
                    wholeCopy = True
                    if len(readOnlyFiles) > 0:
                        self.infoText.append("The following files were marked as read-only and could not be updated:")
                        for file in readOnlyFiles:
                            self.infoText.append("    " + str(file))
                            self.infoText.moveCursor(QtGui.QTextCursor.End)

            if wholeCopy:
                #report issues in UI
                self.infoText.setTextColor(QtGui.QColor(249,168,12))
                self.infoText.append("Could not apply updates automatically.")
                self.infoText.moveCursor(QtGui.QTextCursor.End)
                self.infoText.setTextColor(QtGui.QColor(255,255,255))


                #extract all to an Update folder
                version = self.checkLatestVersion()
                self.infoText.setTextColor(QtGui.QColor(255,255,255))
                updateDir = os.path.join(self.toolsPath, "Update_" + str(version))
                if not os.path.exists(updateDir):
                    os.makedirs(updateDir)

                self.infoText.append("Extracting updated files to:\n    " + str(updateDir))
                try:
                    zf.extractall(updateDir)
                except Exception, e:
                    self.infoText.setTextColor(QtGui.QColor(249,168,12))
                    self.infoText.append("Operation Failed")
                    self.infoText.append(str(e))
                    self.infoText.moveCursor(QtGui.QTextCursor.End)

                #report on operation
                self.infoText.append("Update Extracted. Since the automatic operation failed, you will need to manually integrate and apply the updates.")
                self.infoText.moveCursor(QtGui.QTextCursor.End)

            else:
                self.infoText.setTextColor(QtGui.QColor(48,255,0))
                self.infoText.append("\n\nUpdate Operation Completed!")
                self.infoText.append("You must restart Maya to have updates applied.")
                self.infoText.moveCursor(QtGui.QTextCursor.End)


        #delete zipFile
        try:
            os.remove(filePath)

            for each in os.listdir(os.path.dirname(mayaToolsZip)):
                path = os.path.dirname(mayaToolsZip)
                path = os.path.join(path, each)
                os.remove(path)

            os.chmod(os.path.dirname(mayaToolsZip), stat.S_IWRITE)
            shutil.rmtree(os.path.dirname(mayaToolsZip))

        except Exception, e:
            self.infoText.append("Unable to clean up temporary files..")
            self.infoText.append(str(e))

        value = self.progressBar.value()
        self.progressBar.setValue(value + 1)

        #update .mod file with latest version #
        self.updateLocalVersion()







# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def cancel(self):
        self.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def invalidCreds(self):

        self.infoText.setTextColor(QtGui.QColor(249,241,12))
        self.infoText.append("You have either not setup your Github credentials under Settings, or your github account is not linked with your Epic Games account.")
        self.infoText.append("For more information on linking your github and Epic Games accounts, see:\n")
        self.infoText.append("https://www.unrealengine.com/ue4-on-github")
        self.infoText.setTextColor(QtGui.QColor(255,255,255))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def run():

    if cmds.window("pyArtUpdaterWin", exists = True):
        cmds.deleteUI("pyArtUpdaterWin", wnd = True)

    gui = ART_Updater(getMainWindow())
    gui.show()