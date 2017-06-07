from ThirdParty.Qt import QtGui, QtCore, QtWidgets
from functools import partial
import maya.cmds as cmds
import os
import System.utils as utils

#Original Author: Jeremy Ernst


class ART_HelpMovie():
    def __init__(self, mainUI, moviePath):
        #Original Author: Jeremy Ernst

        #get the directory path of the tools
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.projectPath = settings.value("projectPath")
        self.iconsPath = settings.value("iconPath")
        self.mainUI = mainUI
        
        #images
        self.imageBkgrd =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/toolbar_background.png"))
        self.imageBtnBkrd =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/blue_field_background.png"))
        self.frameBackground =  utils.returnFriendlyPath(os.path.join(self.iconsPath, "System/field_background.png"))

        #build the UI
        if cmds.window("ART_HelpMovieWin", exists = True):
            cmds.deleteUI("ART_HelpMovieWin", wnd = True)
            
        self.buildHelpMovieUI(moviePath)
    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def buildHelpMovieUI(self, moviePath):
        #Original Author: Jeremy Ernst

        #create the main window
        self.mainWin = QtWidgets.QMainWindow(self.mainUI)
        self.mainWin.setStyleSheet("background-color: rgb(0, 0, 0);, color: rgb(0,0,0);")
        self.mainWin.setMinimumSize(660,520)
        self.mainWin.setMaximumSize(660,520)
        
        #create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.mainWin.setCentralWidget(self.mainWidget)
        
        #create the qFrame so we can have a background
        self.frame = QtWidgets.QFrame(self.mainWidget)
        self.frame.setStyleSheet("background-color: rgb(0,0,0);")
        self.frame.setMinimumSize(660,520)
        self.frame.setMaximumSize(660,520)
        
        #set qt object name
        self.mainWin.setObjectName("ART_HelpMovieWin")
        self.mainWin.setWindowTitle("Help")

        #font
        headerFont = QtGui.QFont()
        headerFont.setPointSize(10)
        headerFont.setBold(True)
        
        #create the mainLayout for the rig creator UI
        self.layout = QtWidgets.QVBoxLayout(self.frame)
        
        #set up the screen
        self.movie_screen = QtWidgets.QLabel()
        
        # expand and center the label 
        self.movie_screen.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.movie_screen)
        
        
        #buttons and button layout
        self.buttonlayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.buttonlayout)
        
        spacer = QtWidgets.QSpacerItem(60,0)
        self.buttonlayout.addSpacerItem(spacer)
        
        self.playBtn = QtWidgets.QPushButton("Close")
        self.buttonlayout.addWidget(self.playBtn)
        self.playBtn.clicked.connect(partial(self.close))
        self.playBtn.setStyleSheet("background-image: url(" + self.imageBtnBkrd + ");background-color: rgb(25, 175, 255);")
        self.playBtn.setMinimumHeight(40)
        self.playBtn.setMaximumHeight(40)
        self.playBtn.setFont(headerFont)
        
        spacer = QtWidgets.QSpacerItem(60,0)
        self.buttonlayout.addSpacerItem(spacer)
        
        
        #set movie from file path
        self.movie = QtGui.QMovie(moviePath, QtCore.QByteArray()) 
        self.movie.setCacheMode(QtGui.QMovie.CacheAll) 
        self.movie.setSpeed(100) 
        self.movie_screen.setMovie(self.movie)
        
        self.movie.start()
        
        
        #show
        self.mainWin.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def close(self):
        #Original Author: Jeremy Ernst

        if cmds.window("ART_HelpMovieWin", exists = True):
            cmds.deleteUI("ART_HelpMovieWin", wnd = True)
        