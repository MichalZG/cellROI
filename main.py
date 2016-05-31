# import sys
from skimage import io, color
import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
# from skimage.filters import threshold_otsu
from skimage.filters import threshold_adaptive
from skimage import measure
# from pyqtgraph.Point import Point
from skimage.draw import polygon
from skimage import transform
import cv2
import glob
script_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.curdir


# pg.mkQApp()
# win = pg.GraphicsWindow()
app = QtGui.QApplication([])
# win = QtGui.QWidget()


class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(1000, 1200)
        self.w1 = QtGui.QGridLayout()
        self.setLayout(self.w1)

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

        self.rcheck = QtGui.QCheckBox('Plot contour')

        # List widget
        self.listWidget = QtGui.QListWidget()
        # Table widget
        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setColumnCount(3)
        # comboBox widget
        self.comboWidget = QtGui.QComboBox()
        self.comboWidget.addItem("ss")
        self.comboWidget.addItem("ww")
        # self.tableWidget.setMaximumSize(128, 128)
        # self.tableWidget.setMaximumWidth(self.tableWidget.sizeHintForColumn(0))
        # crosshair
        self.vline = pg.InfiniteLine(angle=90, movable=False)
        self.hline = pg.InfiniteLine(angle=0, movable=False)

        self.vBox = QtGui.QGridLayout()
        self.vBox.addWidget(self.listWidget)
        self.vBox.addWidget(self.tableWidget)
        self.w1.addWidget(self.mainPlot, 0, 0, 1, 1)
        self.w1.addWidget(self.histogram, 1, 0)
        self.w1.addWidget(self.roiPlot, 1, 1)
        self.w1.addWidget(self.contourPlot, 1, 2)
        self.w1.addWidget(self.rcheck, 2, 1)
        self.w1.addLayout(self.vBox, 0, 1)
        # self.w1.addWidget(self.listWidget, 0, 1)
        # self.w1.addWidget(self.tableWidget, 0, 2)
        # self.w1.addWidget(self.comboWidget, 0, 3)
        # win.addLayout(rcheck)

        # self.mainPlot.addItem(imgc)
        self.roiImage = pg.ImageItem()
        self.roiPlot.addItem(self.roiImage)
        self.contourImage = pg.ImageItem()
        self.contourPlot.addItem(self.contourImage)
        self.contourPlot.addItem(self.vline, ignoreBounds=True)
        self.contourPlot.addItem(self.hline, ignoreBounds=True)

        self.roi = pg.RectROI([100, 100], [100, 100], pen=(0, 9))
        self.roi.sigRegionChanged.connect(update)

        self.mainPlot.addItem(self.roi)

        self.vb = self.contourImage.getViewBox()
        self.proxy = pg.SignalProxy(self.contourPlot.scene().sigMouseMoved,
                                    rateLimit=60, slot=mouseMoved)
        self.contourPlot.scene().sigMouseClicked.connect(mouseClicked)
        self.listWidget.currentItemChanged.connect(onItemChanged)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(updateContours)
        self.timer.start(0)

    def addItemsToList(self, images):
        for im in images:
            item = QtGui.QListWidgetItem("%s" % im)
            self.listWidget.addItem(item)

    def setMainPlot(self, imgc):
        self.mainPlot.addItem(imgc)

    def addToTable(self, item):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(
            str(rowPosition)))
        self.tableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(
            '%.1f' % float(item[0])))
        self.tableWidget.setItem(rowPosition, 2, QtGui.QTableWidgetItem(
            '%.1f' % float(item[1])))


class Image:
    def __init__(self, fileName):
        self.regions = []
        self.fileName = fileName

    def loadData(self):
        self.rawData = io.imread(self.fileName)
        self.cData = self.rawData.copy()
        self.rawData = color.rgb2gray(self.rawData)
        self.rawData = transform.rotate(self.rawData, angle=90,
                                        clip=False, resize=True)
        self.cData = transform.rotate(self.cData, angle=90,
                                      clip=False, resize=True)
        self.b = self.cData[:, :, 0]
        self.g = self.cData[:, :, 1]
        self.r = self.cData[:, :, 2]

    def addRegion(self, region):
        self.regions.append(region)


class Region:
    def __init__(self):
        self.center = {'x': 0, 'y': 0}
        self.type = None
        self.array = None

    def saveRegion(self):
        pass


def loadData(fName):
    fData = io.imread(fName)
    cData = fData.copy()
    fData = color.rgb2gray(fData)
    # fData = fData[:, ::-1].T
    fData = transform.rotate(fData, angle=90, clip=False, resize=True)
    # fData = np.transpose(fData)
    cData = transform.rotate(cData, angle=90, clip=False, resize=True)
    # cData = cData[:, :, 2]
    # cData = cData.astype('float64')
    return fData, cData


def createHist(image):
    hist = pg.HistogramLUTItem()
    hist.setImageItem(image)
    # hist.setLevels(fData.min(), fData.max())
    return hist


def update():
    global roi_coords
    global roi_copy
    global roi_b
    global roi_g
    global roi_r
    roi_arr, roi_coords = win.roi.getArrayRegion(Im.rawData, imgc,
                                                 returnMappedCoords=True)
    roi_b = np.copy(win.roi.getArrayRegion(Im.b, imgc))
    roi_g = np.copy(win.roi.getArrayRegion(Im.g, imgc))
    roi_r = np.copy(win.roi.getArrayRegion(Im.r, imgc))
    roi_copy = np.copy(roi_arr)
    win.roiImage.setImage(roi_arr)
    win.histogram.setImageItem(win.roiImage)
    win.roiPlot.autoRange()
    otsu(roi_arr)


def updateContours():
    if win.rcheck.isChecked():
        roi_arr, roi_coords = win.roi.getArrayRegion(Im.rawData, imgc,
                                                     returnMappedCoords=True)
        temp_arr = roi_arr
        contours = otsu(temp_arr)
        for c in contours:
            c = c.astype(int)
            temp_arr[c[:, 0], c[:, 1]] = 1
        win.roiImage.setImage(temp_arr)
    else:
        pass
        # roi_arr, roi_coords = roi.getArrayRegion(fData, img,
        #                                         returnMappedCoords=True)
        # roiImage.setImage(roi_arr)


def otsu(roi_arr):
    otsu = threshold_adaptive(roi_arr, block_size=100, method='mean')
    otsu_arr = roi_arr >= otsu
    otsu_arr = otsu_arr.astype('float64')
    contours = makeContour(otsu_arr)
    for c in contours:
        c = c.astype(int)
        otsu_arr[c[:, 0], c[:, 1]] = 3
    win.contourImage.setImage(otsu_arr)
    win.contourPlot.autoRange()

    return contours


def makeContour(otsu_arr):
    global contours
    contours = measure.find_contours(otsu_arr, 0.99)

    return contours


def mouseMoved(evt):
    pos = evt[0]
    if win.contourPlot.sceneBoundingRect().contains(pos):
        mousePoint = win.vb.mapSceneToView(pos)
        # index = int(mousePoint.x())
        index = 50  # FIXME
        if index > 0 and index < 100:
            win.vline.setPos(mousePoint.x())
            win.hline.setPos(mousePoint.y())


def mouseClicked(evt):
    items = win.vb.scene().items(evt.scenePos())
    x_roi = items[1].x()
    y_roi = items[0].y()
    print x_roi, y_roi
    x_global = roi_coords[0][x_roi][y_roi]
    y_global = roi_coords[1][x_roi][y_roi]
    saveContour(x_roi, y_roi)
    win.addToTable([x_global, y_global])


def onItemChanged(curr, prev):
    global Im
    global img, imgc
    print type(curr.text())
    Im = Image(str(curr.text()))
    Im.loadData()
    img.setImage(Im.rawData)
    imgc.setImage(Im.cData)
    win.setMainPlot(imgc)


def saveContour(x_roi, y_roi):
    # check = False
    for c in contours:
        if measure.points_in_poly([[x_roi, y_roi]], c):
            mask = np.zeros_like(roi_copy)
            out = np.zeros_like(roi_copy)
            out_b = np.zeros_like(roi_copy)
            out_g = np.zeros_like(roi_copy)
            out_r = np.zeros_like(roi_copy)
            rr, cc = polygon(c[:, 0], c[:, 1])
            mask[rr, cc] = 1
            out_b[mask == 1] = roi_b[mask == 1]
            out_g[mask == 1] = roi_g[mask == 1]
            out_r[mask == 1] = roi_r[mask == 1]
            out[mask == 1] = roi_copy[mask == 1]
            np.savetxt('t.txt', c)
            io.imsave('b.bmp', out_b)
            io.imsave('g.bmp', out_g)
            io.imsave('r.bmp', out_r)
            out_rgb = cv2.merge((out_b, out_g, out_r))
            io.imsave('out_rgb.bmp', out_rgb)
            io.imsave('out_grey.bmp', out)


if __name__ == '__main__':
    images = sorted(glob.glob("*.tif"))

    Im = Image(images[0])
    Im.loadData()
    win = MainWindow()

    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(Im.rawData)
    imgc.setImage(Im.cData)
    win.setMainPlot(imgc)
    win.addItemsToList(images)
    win.show()
    app.exec_()
