# standard imports
import os
from stat import S_IWUSR, S_IREAD

import maya.cmds as cmds

import utils
from ThirdParty.Qt import QtGui, QtCore, QtWidgets

# maya 2016< maya2017> compatability
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def getMainWindow():
    import maya.OpenMayaUI as mui
    pointer = mui.MQtUtil.mainWindow()
    # pyside QMainWindow takes in a QWidget rather than QObject
    return shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def writeQSS(filePath):
    # this function takes the qss file given, and finds and replaces any image path URLs using the user's settings for
    # the icons path and changes the file on disk
    settings = QtCore.QSettings("Epic Games", "ARTv2")
    scriptsPath = settings.value("scriptPath")
    scriptsPath = utils.returnFriendlyPath(scriptsPath)
    iconPath = settings.value("iconPath")
    iconPath = utils.returnFriendlyPath(iconPath)

    f = open(filePath, "r")
    lines = f.readlines()
    f.close()

    newLines = []
    for line in lines:
        if line.find("url(") != -1:
            oldPath = line.partition("(")[2].rpartition("/")[0]
            replacePath = utils.returnNicePath(iconPath, "System")

            newLine = line.replace(oldPath, replacePath)
            newLines.append(newLine)
        else:
            newLines.append(line)

    os.chmod(filePath, S_IWUSR | S_IREAD)
    f = open(filePath, "w")
    for line in newLines:
        f.write(line)
    f.close()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def addTextToButton(text, parent, centered=True, top=False, bottom=False):
    text = QtWidgets.QGraphicsSimpleTextItem(text, parent)
    font = QtGui.QFont()
    font.setBold(True)
    font.setPointSize(12)

    text.setFont(font)
    textPos = parent.boundingRect().center()
    textRect = text.boundingRect()
    parentRect = parent.boundingRect()

    if centered:
        text.setPos(textPos.x() - textRect.width() / 2, textPos.y() - textRect.height() / 2)

    if top:
        text.setPos(textPos.x() - textRect.width() / 2, textPos.y() - (parentRect.height() / 2 + textRect.height()))

    if bottom:
        text.setPos(textPos.x() - textRect.width() / 2, textPos.y() + (parentRect.height() / 2))

    return text


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class progressDialog(object):
    '''
    range is a tuple (min,max)
    example:
        myBar = progressDialog((0,100000), label="Exporting weights")
        for i in range(0,100000):
            myBar.setValue(i)
    '''

    def __init__(self, range, label='Doin Stuff..', freq=10):
        self.rangeMin, self.rangeMax, self.freq = range[0], range[1], freq
        self.bar = QtWidgets.QProgressDialog(label, None, self.rangeMin, self.rangeMax)
        self.bar.setWindowModality(QtCore.Qt.WindowModal)
        self.bar.autoClose()

    def setValue(self, val):
        self.bar.show()
        QtWidgets.QApplication.processEvents()
        if val % self.freq == 0 or (val + 1) == self.rangeMax:
            self.bar.setValue(val + 1)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, title, parent=None):
        super(ProgressBar, self).__init__()

        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        self.style = f.read()
        f.close()

        self.setStyleSheet(self.style)
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)

        self.setMinimumSize(QtCore.QSize(400, 40))
        self.setMaximumSize(QtCore.QSize(400, 40))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class commentBoxItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, scene, view, animUI):

        super(commentBoxItem, self).__init__(x, y, w, h)

        self.brush = QtGui.QBrush(QtGui.QColor(60, 60, 60, 125))
        self.brushColor = self.brush.color()
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.scale = 1
        self.menu = QtWidgets.QMenu()
        self.scene = scene
        self.view = view
        self.animUI = animUI

        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        # add items to context menu
        self.menu.addAction("Change Color", self.changeBoxColor)
        self.menu.addAction("Rename", self.changeLabelText)
        self.menu.addAction("Remove Comment Box", self.deleteCommentBox)

        # add text
        self.textLabel = QtWidgets.QGraphicsTextItem("Comment Box", self, scene)
        self.textLabel.setPos(x, y - 20)
        self.textLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        # self.textLabel.setTextInteractionFlags(QtCore.Qt.TextEditable)

        self.classType = "comment"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def boundingRect(self):
        rect = QtCore.QRectF(self.x, self.y, self.width, self.height)
        return rect

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def paint(self, painter, option, widget):
        rec = self.boundingRect()

        self.blackPen = QtGui.QPen(QtCore.Qt.black)
        self.blackPen.setWidth(0)
        painter.setPen(self.blackPen)
        painter.fillRect(rec, self.brush)
        painter.drawRect(rec)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def contextMenuEvent(self, event):
        self.menu.exec_(event.screenPos())

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeBoxColor(self):

        # launch a color dialog to  get a new color
        newColor = QtGui.QColorDialog.getColor()
        newColor.setAlpha(100)
        self.brush.setColor(newColor)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def changeLabelText(self):

        text = QtWidgets.QInputDialog.getText(self.scene.parent(), "Comment Box", "Enter Label Text:")
        if text:
            self.textLabel.setPlainText(text[0])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def deleteCommentBox(self):

        self.scene.removeItem(self)
        self.animUI.rubberband.hide()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class pickerBorderItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, brush, moduleName, niceName=None):

        super(pickerBorderItem, self).__init__(x, y, w, h)

        self.brush = brush
        self.brushColor = brush.color()
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.scale = 1

        self.mouseDown = False

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        self.setData(QtCore.Qt.UserRole, moduleName)
        self.setData(2, niceName)
        self.classType = "border"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def boundingRect(self):
        rect = QtCore.QRectF(self.x, self.y, self.width, self.height)
        return rect

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def paint(self, painter, option, widget):
        rec = self.boundingRect()

        blackPen = QtGui.QPen(QtCore.Qt.transparent)
        blackPen.setWidth(0)
        blackPen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(blackPen)

        flags = self.flags()
        if flags & QtWidgets.QGraphicsItem.ItemIsMovable:
            blackPen = QtGui.QPen(QtCore.Qt.black)
            blackPen.setWidth(0)
            blackPen.setStyle(QtCore.Qt.DotLine)
            painter.setPen(blackPen)

        if self.isSelected():
            blackPen = QtGui.QPen(QtCore.Qt.white)
            blackPen.setWidth(0)
            blackPen.setStyle(QtCore.Qt.DotLine)
            painter.setPen(blackPen)

        painter.fillRect(rec, self.brush)
        painter.drawRect(rec)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def wheelEvent(self, event):

        # only if the focusable flag is set to true, do we continue
        flags = self.flags()
        if flags & QtWidgets.QGraphicsItem.ItemIsFocusable:

            self.scale = self.data(1)
            if self.scale is None:
                self.scale = 1
            scale = float(event.delta() / 8.0)
            self.scale = float((scale / 15.0) / 10) + self.scale
            self.setData(1, self.scale)

            self.setTransformOriginPoint(self.boundingRect().center())
            self.setScale(self.scale)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def keyPressEvent(self, event):

        self.setTransformOriginPoint(self.boundingRect().center())

        if event.key() == QtCore.Qt.Key_Left:
            self.setRotation(self.rotation() - 10)

        if event.key() == QtCore.Qt.Key_Right:
            self.setRotation(self.rotation() + 10)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class pickerButton(QtWidgets.QGraphicsItem):
    def __init__(self, width, height, relativePos, controlObj, brush, parent=None):

        super(pickerButton, self).__init__(parent)

        self.parentItem().setZValue(1)
        self.setZValue(2)

        self.brush = QtGui.QBrush(brush)
        self.brushColor = brush

        self.width = width
        self.height = height
        self.relativePos = relativePos
        self.object = controlObj

        self.setPos(self.parentItem().boundingRect().topLeft())
        self.setPos(self.pos().x() + self.relativePos[0], self.pos().y() + self.relativePos[1])
        self.menu = QtWidgets.QMenu()

        self.classType = "pickerButton"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def boundingRect(self):
        rect = QtCore.QRectF(0, 0, self.width, self.height)
        return rect

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def paint(self, painter, option, widget):
        rec = self.boundingRect()
        painter.fillRect(rec, self.brush)
        painter.drawRect(rec)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mousePressEvent(self, event):

        mods = cmds.getModifiers()
        if (mods & 1) > 0:
            cmds.select(self.object, tgl=True)
        if (mods & 1) == 0:
            cmds.select(self.object)

        if self.object in cmds.ls(sl=True):

            self.brush.setColor(QtCore.Qt.white)

        else:
            self.brush.setColor(self.brushColor)

        self.update()
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mousePressEventCustom(self, event):

        cmds.select(self.object, tgl=True)
        self.brush.setColor(self.brushColor)
        self.update()
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mouseMoveEvent(self, event):
        print "mouse move event"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def dragMoveEvent(self, event):
        print "drag move event"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def hoverMoveEvent(self, event):
        print "hover move event"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def contextMenuEvent(self, event):
        self.menu.exec_(event.screenPos())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class pickerButtonCustom(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, width, height, pointArray, relativePos, controlObj, brush, parent=None):

        super(pickerButtonCustom, self).__init__(parent)

        self.parentItem().setZValue(1)
        self.setZValue(2)

        self.brush = QtGui.QBrush(brush)
        self.brushColor = brush
        self.pointArray = pointArray
        self.poly = self.createPolygon()
        self.setPolygon(self.poly)

        # position item
        self.relativePos = relativePos
        self.object = controlObj
        self.setPos(self.parentItem().boundingRect().topLeft())
        self.setPos(self.pos().x() + self.relativePos[0], self.pos().y() + self.relativePos[1])

        # create menu
        self.menu = QtWidgets.QMenu()
        self.classType = "pickerButton"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def createPolygon(self):
        polygon = QtGui.QPolygonF()
        for each in self.pointArray:
            polygon.append(QtCore.QPointF(each[0], each[1]))
        return polygon

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon())

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mousePressEvent(self, event):

        mods = cmds.getModifiers()
        if (mods & 1) > 0:
            cmds.select(self.object, tgl=True)
        if (mods & 1) == 0:
            cmds.select(self.object)

        if self.object in cmds.ls(sl=True):

            self.brush.setColor(QtCore.Qt.white)

        else:
            self.brush.setColor(self.brushColor)

        self.update()
        QtWidgets.QGraphicsPolygonItem.mousePressEvent(self, event)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mousePressEventCustom(self, event):

        cmds.select(self.object, tgl=True)
        self.brush.setColor(self.brushColor)
        self.update()
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def contextMenuEvent(self, event):
        self.menu.exec_(event.screenPos())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class pickerButtonAll(QtWidgets.QGraphicsItem):
    def __init__(self, width, height, relativePos, controlObjects, brush, parent=None):

        super(pickerButtonAll, self).__init__(parent)

        self.parentItem().setZValue(1)
        self.setZValue(2)

        self.brush = QtGui.QBrush(brush)
        self.brushColor = brush

        self.width = width
        self.height = height
        self.relativePos = relativePos
        self.objects = controlObjects

        self.setPos(self.parentItem().boundingRect().topLeft())
        self.setPos(self.pos().x() + self.relativePos[0], self.pos().y() + self.relativePos[1])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def boundingRect(self):
        rect = QtCore.QRectF(0, 0, self.width, self.height)
        return rect

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def paint(self, painter, option, widget):
        rec = self.boundingRect()
        painter.fillRect(rec, self.brush)
        painter.drawRect(rec)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def mousePressEvent(self, event):

        mods = cmds.getModifiers()
        if (mods & 1) > 0:
            for obj in self.objects:
                cmds.select(obj, add=True)

        if (mods & 1) == 0:
            cmds.select(clear=True)
            for obj in self.objects:
                cmds.select(obj, tgl=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class DialogMessage(QtWidgets.QMainWindow):
    def __init__(self, title, message, elementList, elementSize, parent=None):
        super(DialogMessage, self).__init__(parent)

        # get the directory path of the
        settings = QtCore.QSettings("Epic Games", "ARTv2")
        self.toolsPath = settings.value("toolsPath")
        self.iconsPath = settings.value("iconPath")

        # load stylesheet
        styleSheetFile = utils.returnNicePath(self.toolsPath, "Core/Scripts/Interfaces/StyleSheets/mainScheme.qss")
        f = open(styleSheetFile, "r")
        style = f.read()
        f.close()

        self.setStyleSheet(style)

        # size policies
        mainSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # create the main widget
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        # set qt object name
        self.setObjectName("pyART_customDialogMessageWin")
        self.setWindowTitle(title)

        # create the mainLayout for the rig creator UI
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.resize(300, 200)
        self.setSizePolicy(mainSizePolicy)
        self.setMinimumSize(QtCore.QSize(300, 200))
        self.setMaximumSize(QtCore.QSize(300, 200))

        # create the background image
        self.frame = QtWidgets.QFrame()
        self.mainLayout.addWidget(self.frame)

        # create the layout for the widgets
        self.widgetLayout = QtWidgets.QVBoxLayout(self.frame)

        # add the message to the layout
        self.messageArea = QtWidgets.QTextEdit()
        self.messageArea.setReadOnly(True)
        self.widgetLayout.addWidget(self.messageArea)

        self.messageArea.setTextColor(QtGui.QColor(236, 217, 0))
        self.messageArea.append(message + "\n\n")

        string = ""
        for each in elementList:
            for i in range(elementSize):
                string += each[i] + " "

            self.messageArea.setTextColor(QtGui.QColor(255, 255, 255))
            self.messageArea.append(string)

        # add the OK button
        self.confirmButton = QtWidgets.QPushButton("OK")
        self.confirmButton.setObjectName("blueButton")
        self.widgetLayout.addWidget(self.confirmButton)
        self.confirmButton.clicked.connect(self.closeWindow)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def closeWindow(self):

        cmds.deleteUI("pyART_customDialogMessageWin", wnd=True)
