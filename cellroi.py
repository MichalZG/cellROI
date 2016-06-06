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
        self.ui.colorChooser.currentIndexChanged.connect(colorChoose)
        self.ui.typeChooser.currentIndexChanged.connect(typeChoose)
        self.ui.timer.timeout.connect(updateContours)
        self.ui.timer.start(0)

    def addItemsToList(self, _list, items):
        for i in items:
            item = QtGui.QListWidgetItem("%s" % i)
            _list.addItem(item)

    def clearList(self, _list):
        _list.clear()

    def setMainPlot(self, image):
        self.ui.mainPlot.addItem(image)

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
        self.grayData = self.rawData.copy()
        self.grayData = color.rgb2gray(self.rawData)
        self.grayData = transform.rotate(self.grayData, angle=90,
                                         clip=False, resize=True)
        self.cData = transform.rotate(self.cData, angle=90,
                                      clip=False, resize=True)
        self.hsvData = color.rgb2hsv(self.rawData)
        self.hsvData = transform.rotate(self.hsvData, angle=90,
                                        clip=False, resize=True)

        self.b = self.cData[:, :, 0]
        self.g = self.cData[:, :, 1]
        self.r = self.cData[:, :, 2]
        self.h = self.hsvData[:, :, 0]
        self.s = self.hsvData[:, :, 1]
        self.v = self.hsvData[:, :, 2]

        self.colorDict = {'RGB': self.cData,
                          'GRAY': self.grayData,
                          'B': self.b,
                          'G': self.g,
                          'R': self.r,
                          'HSV': self.hsvData,
                          'H': self.h,
                          'S': self.s,
                          'V': self.v}

    def addRegion(self, region):
        self.regions.append(region)


class Region:
    def __init__(self, _type, x, y):
        self.mouseCenter = {'x': x, 'y': y}
        self._type = _type
        self.maskArray = None
        self.imagesArrays = {}
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
    roiArr, roiCoords = getRoi(Im.colorDict[currColor], imgc)
    win.ui.roiImage.setImage(roiArr)
    win.ui.histogram.setImageItem(win.ui.roiImage)
    win.ui.roiPlot.autoRange()
    otsu(roiArr)


def getRoi(dataToRoi, imageToRoi):
    global roiCoords
    global roiCopy
    # global roi_b
    # global roi_g
    # global roi_r
    roiArr, roiCoords = win.ui.roi.getArrayRegion(
        dataToRoi, imageToRoi, returnMappedCoords=True)
    roiCopy = np.copy(roiArr)
    roiSliceParam = win.ui.roi.getAffineSliceParams(
        dataToRoi, imageToRoi)
    roiSlice = win.ui.roi.getArraySlice(
        dataToRoi, imageToRoi)
    # print roi_slice
    # print roi_slice_param
    # roi_b = np.copy(win.ui.roi.getArrayRegion(Im.b, imgc))
    # roi_g = np.copy(win.ui.roi.getArrayRegion(Im.g, imgc))
    # roi_r = np.copy(win.ui.roi.getArrayRegion(Im.r, imgc))
    return roiArr, roiCoords


def updateContours():
    if win.ui.contourButton.isChecked():
        roiArr, roiCoords = getRoi(Im.colorDict[currColor], imgc)
        tempArr = np.copy(roiArr)
        contours = otsu(roipArr)
        for c in contours:
            c = c.astype(int)
            tempArr[c[:, 0], c[:, 1]] = 1
        win.ui.roiImage.setImage(roiArr)
    else:
        pass
        # roi_arr, roi_coords = roi.getArrayRegion(fData, img,
        #                                         returnMappedCoords=True)
        # roiImage.setImage(roi_arr)


def otsu(roiArr):
    otsu = threshold_adaptive(roiArr, block_size=100, method='mean')
    otsuArr = roiArr >= otsu
    otsuArr = otsuArr.astype('float64')
    contours = makeContour(otsuArr)
    for c in contours:
        c = c.astype(int)
        otsuArr[c[:, 0], c[:, 1]] = 3
    win.ui.contourImage.setImage(otsuArr)
    win.ui.contourPlot.autoRange()

    return contours


def makeContour(otsuArr):
    global contours
    contours = measure.find_contours(otsuArr, 0.99)

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
    xRoi = items[1].x()
    yRoi = items[0].y()
    print xRoi, yRoi
    xRoiGlobal = roiCoords[0][xRoi][yRoi]
    yRoiGlobal = roiCoords[1][xRoi][yRoi]
    region = Region(currRegionType, xRoiGlobal, yRoiGlobal)
    if region._type in ('Cell', 'Red Cell', 'Other'):
        contour = checkContour(xRoi, yRoi)
        if contour is not None:
            itemToList = "%s, %.1f, %.1f" % (region._type,
                                             region.mouseCenter['x'],
                                             region.mouseCenter['y'])
            # itemToList = "%s, %.1f, %.1f" % ("Cell", x_global, y_global)
            win.addItemsToList(win.ui.contoursList, [itemToList])
            region.metaData['color'] = currColor
            region.contour = contour
            makeRegionData(region)
            Im.addRegion(region)
    else:
        itemToList = "%s, %.1f, %.1f" % (region._type,
                                         region.mouseCenter['x'],
                                         region.mouseCenter['y'])
        # itemToList = "%s, %.1f, %.1f" % ("Cell", x_global, y_global)
        win.addItemsToList(win.ui.contoursList, [itemToList])
        Im.addRegion(region)


def onItemChanged(curr, prev):
    global Im
    global img, imgc
    print type(curr.text())
    Im = imagesContener[str(curr.text())]
    Im.loadData()
    img.setImage(Im.grayData)
    imgc.setImage(Im.cData)
    win.clearList(win.ui.contoursList)
    if Im.regions:
        for region in Im.regions:
            itemToList = "%s, %.1f, %.1f" % (region._type,
                                             region.mouseCenter['x'],
                                             region.mouseCenter['y'])
            win.addItemsToList(win.ui.contoursList, [itemToList])
    # win.setMainPlot(imgc)


def checkContour(xRoi, yRoi):
    # check = False
    for contour in contours:
        if measure.points_in_poly([[xRoi, yRoi]], contour):
            return contour


def makeRegionData(region, nobkg=True):
    # check = False
    if nobkg:
        for c, arr in Im.colorDict.iteritems():
            if c not in ('RGB', 'HSV'):
                mask = np.zeros_like(roiCopy)
                out = np.zeros_like(roiCopy)
                rr, cc = polygon(region.contour[:, 0],
                                 region.contour[:, 1])
                # out_b = np.zeros_like(roiCopy)
                # out_g = np.zeros_like(roiCopy)
                # out_r = np.zeros_like(roiCopy)
                mask[rr, cc] = 1
                print c, arr
                roiArr, roiCoords = getRoi(arr, imgc)

                # out_b[mask == 1] = roi_b[mask == 1]
                # out_g[mask == 1] = roi_g[mask == 1]
                # out_r[mask == 1] = roi_r[mask == 1]
                out[mask == 1] = roiArr[mask == 1]
                # region.imagesArrays[
                np.savetxt('.'.join((c, 'txt')), region.contour)
                io.imsave('.'.join((c, 'bmp')), out)
                # out_rgb = cv2.merge((out_b, out_g, out_r))
                # io.imsave('out_rgb.bmp', out_rgb)
                # io.imsave('out_grey.bmp', out)


def colorChoose():
    global currColor
    currColor = str(win.ui.colorChooser.currentText())
    # imgc.setImage(Im.colorDict[currColor])
    update()


def typeChoose():
    global currRegionType
    currRegionType = str(win.ui.typeChooser.currentText())
    update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    images = sorted(glob.glob("*.tif"))
    imagesContener = {}
    currColor = 'GRAY'
    currRegionType = 'Cell'
    for image in images:
        imagesContener[image] = Image(image)
    Im = imagesContener.values()[0]
    Im.loadData()
    win = GuiInit()
    # win = gui.MainWindow()
    # win.setupUi()
    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(Im.grayData)
    imgc.setImage(Im.cData)
    win.setMainPlot(imgc)
    win.addItemsToList(win.ui.imagesList, images)
    win.show()
    sys.exit(app.exec_())
