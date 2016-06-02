# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1479, 900)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.colorChooser = QtGui.QComboBox(self.centralwidget)
        self.colorChooser.setGeometry(QtCore.QRect(10, 10, 75, 33))
        self.colorChooser.setObjectName(_fromUtf8("colorChooser"))
        self.colorChooser.addItem(_fromUtf8(""))
        self.colorChooser.addItem(_fromUtf8(""))
        self.colorChooser.addItem(_fromUtf8(""))
        self.colorChooser.addItem(_fromUtf8(""))
        self.colorChooser.addItem(_fromUtf8(""))
        self.colorChooser.addItem(_fromUtf8(""))
        self.imagesList = QtGui.QListWidget(self.centralwidget)
        self.imagesList.setGeometry(QtCore.QRect(910, 50, 211, 421))
        self.imagesList.setObjectName(_fromUtf8("imagesList"))
        self.deleteContourButton = QtGui.QPushButton(self.centralwidget)
        self.deleteContourButton.setGeometry(QtCore.QRect(1360, 110, 85, 27))
        self.deleteContourButton.setObjectName(_fromUtf8("deleteContourButton"))
        self.saveContourButton = QtGui.QPushButton(self.centralwidget)
        self.saveContourButton.setGeometry(QtCore.QRect(1360, 50, 85, 27))
        self.saveContourButton.setObjectName(_fromUtf8("saveContourButton"))
        self.deleteAllContourButton = QtGui.QPushButton(self.centralwidget)
        self.deleteAllContourButton.setGeometry(QtCore.QRect(1360, 140, 85, 27))
        self.deleteAllContourButton.setObjectName(_fromUtf8(
            "deleteAllContourButton"))
        self.saveAllContourButton = QtGui.QPushButton(self.centralwidget)
        self.saveAllContourButton.setGeometry(QtCore.QRect(1360, 80, 85, 27))
        self.saveAllContourButton.setObjectName(_fromUtf8(
            "saveAllContourButton"))
        self.waterButton = QtGui.QCheckBox(self.centralwidget)
        self.waterButton.setGeometry(QtCore.QRect(550, 830, 101, 22))
        self.waterButton.setObjectName(_fromUtf8("waterButton"))
        self.contourButton = QtGui.QCheckBox(self.centralwidget)
        self.contourButton.setGeometry(QtCore.QRect(170, 830, 101, 22))
        self.contourButton.setObjectName(_fromUtf8("contourButton"))
        self.contoursList = QtGui.QListWidget(self.centralwidget)
        self.contoursList.setGeometry(QtCore.QRect(1140, 50, 211, 421))
        self.contoursList.setObjectName(_fromUtf8("contoursList"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 50, 881, 421))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.topLay = QtGui.QGridLayout(self.gridLayoutWidget)
        self.topLay.setHorizontalSpacing(6)
        self.topLay.setVerticalSpacing(0)
        self.topLay.setObjectName(_fromUtf8("topLay"))
        self.gridLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 480, 881, 341))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.botLay = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.botLay.setHorizontalSpacing(5)
        self.botLay.setVerticalSpacing(0)
        self.botLay.setObjectName(_fromUtf8("botLay"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1479, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.menuMenu.addAction(self.actionClose)
        self.menuAbout.addAction(self.actionHelp)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.mainPlot = pg.PlotWidget()
        self.mainPlot.setAspectLocked()
        self.mainPlot.setMouseEnabled(x=False, y=False)
        self.histogram = pg.HistogramLUTWidget()
        self.roiPlot = pg.PlotWidget()
        self.roiPlot.setAspectLocked()
        self.roiPlot.setMouseEnabled(x=False, y=False)
        self.contourPlot = pg.PlotWidget()
        self.contourPlot.setAspectLocked()
        self.contourPlot.setMouseEnabled(x=False, y=False)
        self.vline = pg.InfiniteLine(angle=90, movable=False)
        self.hline = pg.InfiniteLine(angle=0, movable=False)
        self.roiImage = pg.ImageItem()
        self.roiPlot.addItem(self.roiImage)
        self.contourImage = pg.ImageItem()
        self.contourPlot.addItem(self.contourImage)
        self.contourPlot.addItem(self.vline, ignoreBounds=True)
        self.contourPlot.addItem(self.hline, ignoreBounds=True)

        self.roi = pg.RectROI([100, 100], [100, 100], pen=(0, 9))
        # self.roi.sigRegionChanged.connect(update)

        self.mainPlot.addItem(self.roi)
        self.vb = self.contourImage.getViewBox()

        self.topLay.addWidget(self.mainPlot)
        self.botLay.addWidget(self.histogram, 0, 0)
        self.botLay.addWidget(self.roiPlot, 0, 1, 1, 2)
        self.botLay.addWidget(self.contourPlot, 0, 3, 1, 2)

        self.timer = QtCore.QTimer()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.colorChooser.setItemText(0, _translate("MainWindow", "RGB", None))
        self.colorChooser.setItemText(1, _translate("MainWindow", "R", None))
        self.colorChooser.setItemText(2, _translate("MainWindow", "G", None))
        self.colorChooser.setItemText(3, _translate("MainWindow", "B", None))
        self.colorChooser.setItemText(4, _translate("MainWindow", "GREY", None))
        self.colorChooser.setItemText(5, _translate("MainWindow", "HSV", None))
        self.deleteContourButton.setText(_translate(
            "MainWindow", "Delete", None))
        self.saveContourButton.setText(_translate(
            "MainWindow", "Save", None))
        self.deleteAllContourButton.setText(_translate(
            "MainWindow", "Delete All", None))
        self.saveAllContourButton.setText(_translate(
            "MainWindow", "Save All", None))
        self.waterButton.setText(_translate(
            "MainWindow", "Watershed", None))
        self.contourButton.setText(_translate(
            "MainWindow", "Plot contour", None))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu", None))
        self.menuAbout.setTitle(_translate("MainWindow", "About", None))
        self.actionClose.setText(_translate("MainWindow", "Close", None))
        self.actionHelp.setText(_translate("MainWindow", "Help", None))
