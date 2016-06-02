# import sys
from skimage import io, color
import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# from skimage.filters import threshold_otsu
from skimage.filters import threshold_adaptive
from skimage import measure
# from pyqtgraph.Point import Point
from skimage.draw import polygon
from skimage import transform
import cv2
import glob
import gui
import sys
script_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.curdir


class GuiInit(QtGui.QMainWindow):
    def __init__(self):
        super(GuiInit, self).__init__()
        # build ui
        self.ui = gui.MainWindow()
        self.ui.setupUi(self)
        self.ui.imagesList.currentItemChanged.connect(onItemChanged)
        self.ui.roi.sigRegionChanged.connect(update)
        self.ui.proxy = pg.SignalProxy(
            self.ui.contourPlot.scene().sigMouseMoved,
            rateLimit=60, slot=mouseMoved)
        self.ui.contourPlot.scene().sigMouseClicked.connect(mouseClicked)
        self.ui.timer.timeout.connect(updateContours)
        self.ui.timer.start(0)

    def addItemsToList(self, _list, items):
        for i in items:
            item = QtGui.QListWidgetItem("%s" % i)
            _list.addItem(item)

    def clearList(self, _list):
        _list.clear()

    def setMainPlot(self, imgc):
        self.ui.mainPlot.addItem(imgc)

    def addToTable(self, item):
        rowPosition = self.ui.contoursList.rowCount()
        self.ui.contoursList.insertRow(rowPosition)
        self.ui.contoursList.setItem(rowPosition, 0, QtGui.QTableWidgetItem(
            str(rowPosition)))
        self.ui.tableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(
            '%.1f' % float(item[0])))
        self.ui.tableWidget.setItem(rowPosition, 2, QtGui.QTableWidgetItem(
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
    def __init__(self, _type, x, y):
        self.mouseCenter = {'x': x, 'y': y}
        self._type = _type
        self.maskArray = None
        self.imageArray = None
        self.contour = None
        self.metaData = {}

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


def update():
    global roi_coords
    global roi_copy
    global roi_b
    global roi_g
    global roi_r
    roi_arr, roi_coords = win.ui.roi.getArrayRegion(Im.rawData, imgc,
                                                    returnMappedCoords=True)
    roi_b = np.copy(win.ui.roi.getArrayRegion(Im.b, imgc))
    roi_g = np.copy(win.ui.roi.getArrayRegion(Im.g, imgc))
    roi_r = np.copy(win.ui.roi.getArrayRegion(Im.r, imgc))
    roi_copy = np.copy(roi_arr)
    win.ui.roiImage.setImage(roi_arr)
    win.ui.histogram.setImageItem(win.ui.roiImage)
    win.ui.roiPlot.autoRange()
    otsu(roi_arr)


def updateContours():
    if win.ui.contourButton.isChecked():
        roi_arr, roi_coords = win.ui.roi.getArrayRegion(Im.rawData, imgc,
                                                        returnMappedCoords=True)
        temp_arr = roi_arr
        contours = otsu(temp_arr)
        for c in contours:
            c = c.astype(int)
            temp_arr[c[:, 0], c[:, 1]] = 1
        win.ui.roiImage.setImage(temp_arr)
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
    win.ui.contourImage.setImage(otsu_arr)
    win.ui.contourPlot.autoRange()

    return contours


def makeContour(otsu_arr):
    global contours
    contours = measure.find_contours(otsu_arr, 0.99)

    return contours


def mouseMoved(evt):
    pos = evt[0]
    if win.ui.contourPlot.sceneBoundingRect().contains(pos):
        mousePoint = win.ui.vb.mapSceneToView(pos)
        # index = int(mousePoint.x())
        index = 50  # FIXME
        if index > 0 and index < 100:
            win.ui.vline.setPos(mousePoint.x())
            win.ui.hline.setPos(mousePoint.y())


def mouseClicked(evt):
    items = win.ui.vb.scene().items(evt.scenePos())
    x_roi = items[1].x()
    y_roi = items[0].y()
    print x_roi, y_roi
    x_global = roi_coords[0][x_roi][y_roi]
    y_global = roi_coords[1][x_roi][y_roi]
    region = Region('Cell', x_global, y_global)
    if checkContour(x_roi, y_roi):
        itemToList = "%s, %.1f, %.1f" % (region._type,
                                         region.mouseCenter['x'],
                                         region.mouseCenter['y'])
        # itemToList = "%s, %.1f, %.1f" % ("Cell", x_global, y_global)
        win.addItemsToList(win.ui.contoursList, [itemToList])


def onItemChanged(curr, prev):
    global Im
    global img, imgc
    print type(curr.text())
    Im = Image(str(curr.text()))
    Im.loadData()
    img.setImage(Im.rawData)
    imgc.setImage(Im.cData)
    win.clearList(win.ui.contoursList)
    if Im.regions:
        for region in Im.regions:
            itemToList = "%s, %.1f, %.1f" % (region._type,
                                             region.mouseCenter['x'],
                                             region.mouseCenter['y'])
            win.addItemsToList(win.ui.contoursList, itemToList)
    # win.setMainPlot(imgc)


def checkContour(x_roi, y_roi):
    # check = False
    for c in contours:
        if measure.points_in_poly([[x_roi, y_roi]], c):
            return True


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

            return True
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    images = sorted(glob.glob("*.tif"))
    imagesContener = {}
    for image in images:
        imagesContener[image] = Image(image)
    Im = imagesContener.values()[0]
    Im.loadData()
    win = GuiInit()
    # win = gui.MainWindow()
    # win.setupUi()
    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(Im.rawData)
    imgc.setImage(Im.cData)
    win.setMainPlot(imgc)
    win.addItemsToList(win.ui.imagesList, images)
    win.show()
    sys.exit(app.exec_())
