# import sys
from skimage import io, color
import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# from skimage.filters import threshold_otsu
from skimage.filters import threshold_adaptive
from skimage import measure, img_as_ubyte
# from pyqtgraph.Point import Point
from skimage.draw import polygon
from skimage import transform
import cv2
import glob
import gui
import sys
# import pickle
import csv
import collections
import time

scriptPath = os.path.dirname(os.path.realpath(__file__))
workDir = os.getcwd()


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
        self.ui.saveContourButton.clicked.connect(saveContour)
        self.ui.saveAllContourButton.clicked.connect(saveAllContour)
        self.ui.deleteContourButton.clicked.connect(deleteContour)
        self.ui.deleteAllContourButton.clicked.connect(deleteAllContour)
        self.ui.blockSizeSpinBox.valueChanged.connect(blockSizeChoose)
        self.ui.offsetSpinBox.valueChanged.connect(offsetChoose)
        self.ui.methodComboBox.currentIndexChanged.connect(methodChoose)
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
        self.regionsCounter = {}
        self.fileName = fileName

    def loadData(self):
        self.rawData = io.imread(self.fileName, plugin='tifffile')
        self.rawData = cv2.merge((self.rawData[:, :, 0].T,
                                  self.rawData[:, :, 1].T,
                                  self.rawData[:, :, 2].T))
        self.cData = self.rawData.copy()
        self.grayData = self.rawData.copy()
        self.grayData = color.rgb2gray(self.rawData)
        self.hsvData = color.rgb2hsv(self.rawData)
        # self.grayData = self.grayData.convert('LA')
        # self.grayData = self.grayData.transpose(method=PIL.Image.TRANSPOSE)
        self.grayData = transform.rotate(self.grayData, angle=0)
        self.cData = transform.rotate(self.cData, angle=0)
        self.hsvData = transform.rotate(self.hsvData, angle=0)
        self.b = self.cData[:, :, 0]
        self.g = self.cData[:, :, 1]
        self.r = self.cData[:, :, 2]
        self.v = self.hsvData[:, :, 0]
        self.s = self.hsvData[:, :, 1]
        self.h = self.hsvData[:, :, 2]

        self.colorDict = {'RGB': self.cData,
                          'GRAY': self.grayData,
                          'B': self.b,
                          'G': self.g,
                          'R': self.r,
                          'HSV': self.hsvData,
                          'H': self.h,
                          'S': self.s,
                          'V': self.v}

    def loadRegions(self):
        try:
            regionsList = np.loadtxt(os.path.join(workDir, os.path.basename(
                self.fileName.split('.')[0]), 'regions_list.dat'),
                dtype='string', delimiter=',', ndmin=2)
            print 'loading regions...'

            for rData in regionsList:
                region = Region(rData[0], float(rData[1]),
                                float(rData[2]))
                region.imOld = True
                region.timeStamp = int(rData[3])
                region.showArrow()
                itemToList = "%s, %i, %.1f, %.1f" % (region._type,
                                                     region.timeStamp,
                                                     region.mouseCenter['x'],
                                                     region.mouseCenter['y'])
                win.addItemsToList(win.ui.contoursList, [itemToList])

                self.addRegion(region)
                if region._type in self.regionsCounter:
                    self.regionsCounter[region._type] += 1
                else:
                    self.regionsCounter[region._type] = 1
            updateLCD()

        except IOError:
            print 'no regions found!'

    def addRegion(self, region):
        self.regions.append(region)

    def saveImageRegions(self):
        try:
            os.mkdir(os.path.join(workDir, os.path.basename(
                self.fileName.split('.')[0])))
        except OSError:
            pass

        with open(os.path.join(workDir,
                               os.path.basename(
                                   self.fileName.split('.')[0]),
                               'regions_list.dat'), 'w') as f:
            for region in self.regions:
                f.write(','.join((region._type,
                                 str(region.mouseCenter['x']),
                                 str(region.mouseCenter['y']),
                                 str(region.timeStamp)+'\n')))
        for region in self.regions:
            if not region.imOld:
                region.saveRegion()


class Region:
    def __init__(self, _type, x, y):
        self.mouseCenter = {'x': x, 'y': y}
        self._type = _type
        self.maskArray = None
        self.imagesArrays = {}
        self.contour = None
        self.metaData = {}
        self.regionImage = None
        self.imOld = False
        self.number = 0
        self.timeStamp = createTimeStamp()
        self.arrow = createArrow(self.mouseCenter['x'], self.mouseCenter['y'])

    def showArrow(self):
        win.ui.mainPlot.addItem(self.arrow)

    def hideArrow(self):
        win.ui.mainPlot.removeItem(self.arrow)

    def saveRegion(self):
        imageBaseName = os.path.basename(
            self.regionImage.fileName).split('.')[0]
        pathToSave = os.path.join(workDir, imageBaseName)
        for c, arr in self.imagesArrays.iteritems():
            io.imsave(os.path.join(pathToSave,
                                   '_'.join((
                                       self._type,
                                       str(self.timeStamp),
                                       c, imageBaseName+'.tif'))),
                      img_as_ubyte(arr))
        if self.contour is not None:
            np.savetxt(os.path.join(pathToSave,
                                    '_'.join((self._type,
                                              str(self.timeStamp),
                                              'contour.dat'))), self.contour)
        np.savetxt(os.path.join(pathToSave,
                                '_'.join((self._type,
                                          str(self.timeStamp),
                                          'mask.dat'))), self.mask)
        # pickle.dump(self.metaData,
        #            open(os.path.join(pathToSave, 'metaData.dat'), 'wb'))
        writer = csv.writer(open(os.path.join(pathToSave,
                                              '_'.join((self._type,
                                                       str(self.timeStamp),
                                                       'metaData.dat'))),
                                 'wb'), delimiter=':')

        self.sortedmetaData = collections.OrderedDict(sorted(
            self.metaData.items()))
        for k, v in self.sortedmetaData.iteritems():
            writer.writerow([k, v])


def update():
    roiArr, roiCoords = getRoi(Im.colorDict[currColor], imgc)
    win.ui.roiImage.setImage(roiArr)
    win.ui.histogram.setImageItem(win.ui.roiImage)
    win.ui.roiPlot.autoRange()
    threshold()


def createArrow(x, y):
    arrow = pg.ArrowItem(angle=270, tipAngle=40, baseAngle=30, headLen=20,
                         tailLen=None, brush='k')
    arrow.setPos(x, y)
    return arrow


def getRoi(dataToRoi, imageToRoi):
    global roiArr
    global roiCoords
    global roiCopy
    global roiSliceParam
    global roiSlice
    roiArr, roiCoords = win.ui.roi.getArrayRegion(
        dataToRoi, imageToRoi, returnMappedCoords=True)
    roiCopy = np.copy(roiArr)
    roiSliceParam = win.ui.roi.getAffineSliceParams(
        dataToRoi, imageToRoi)
    roiSlice = win.ui.roi.getArraySlice(
        dataToRoi, imageToRoi, returnSlice=False)

    return roiArr, roiCoords


def updateContours():
    if win.ui.contourButton.isChecked():
        roiArr, roiCoords = getRoi(Im.colorDict[currColor], imgc)
        tempArr = np.copy(roiArr)
        contours = threshold()
        for c in contours:
            c = c.astype(int)
            tempArr[c[:, 0], c[:, 1]] = 1
        win.ui.roiImage.setImage(tempArr)
    else:
        pass
        # roi_arr, roi_coords = roi.getArrayRegion(fData, img,
        #                                         returnMappedCoords=True)
        # roiImage.setImage(roi_arr)


def threshold():
    otsu = threshold_adaptive(roiArr, block_size=blockSize, method=threshMethod,
                              offset=offset)
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
    xRoiGlobal = roiCoords[0][xRoi][yRoi]
    yRoiGlobal = roiCoords[1][xRoi][yRoi]
    region = Region(currRegionType, xRoiGlobal, yRoiGlobal)
    if region._type in ('Cell', 'Red Cell', 'Other'):
        contour = checkContour(xRoi, yRoi)
        if contour is not None:
            region.metaData['color'] = currColor
            region.contour = contour
            makeRegionData(region)
            itemToList = "%s, %s, %.1f, %.1f" % (region._type,
                                                 region.timeStamp,
                                                 region.mouseCenter['x'],
                                                 region.mouseCenter['y'])
            win.addItemsToList(win.ui.contoursList, [itemToList])
            Im.addRegion(region)
            region.showArrow()
            updateLCD()
    else:
        region.metaData['color'] = currColor
        makeRegionData(region, nobkg=False)
        itemToList = "%s, %s, %.1f, %.1f" % (region._type,
                                             region.timeStamp,
                                             region.mouseCenter['x'],
                                             region.mouseCenter['y'])
        win.addItemsToList(win.ui.contoursList, [itemToList])
        region.showArrow()
        Im.addRegion(region)
        updateLCD()


def onItemChanged(curr, prev):
    global Im
    global img, imgc
    for region in Im.regions:
        region.hideArrow()
    Im = imagesContener[str(curr.text())]
    Im.loadData()
    img.setImage(Im.grayData)
    imgc.setImage(Im.cData)
    win.clearList(win.ui.contoursList)
    if Im.regions:
        for region in Im.regions:
            itemToList = "%s, %s, %.1f, %.1f" % (region._type,
                                                 region.timeStamp,
                                                 region.mouseCenter['x'],
                                                 region.mouseCenter['y'])
            win.addItemsToList(win.ui.contoursList, [itemToList])
            region.showArrow()


def checkContour(xRoi, yRoi):
    # check = False
    for contour in contours:
        if measure.points_in_poly([[xRoi, yRoi]], contour):
            return contour
    Im.saveImageRegions()


def saveContour():
    Im.saveImageRegions()


def saveAllContour():
    for image, im in imagesContener.iteritems():
        if im.regions:
            im.saveImageRegions()


def deleteContour():
    if win.ui.contoursList.currentItem() is not None:
        currItemText = win.ui.contoursList.currentItem().text().split(', ')
        win.ui.contoursList.takeItem(win.ui.contoursList.currentRow())
        _type, timeStamp = currItemText[0], currItemText[1]

        for i, region in enumerate(Im.regions):
            if (str(region._type) == str(_type) and
                    str(region.timeStamp) == str(timeStamp)):

                region.hideArrow()
                del Im.regions[i]
                Im.regionsCounter[region._type] -= 1

                files = glob.glob(os.path.join(workDir,
                                               os.path.basename(
                                                   Im.fileName.split('.')[0]),
                                               str(_type) + '_' +
                                               str(timeStamp) + '*.*'))
                for f in files:
                    os.remove(f)
                try:
                    with open(os.path.join(workDir,
                                           os.path.basename(
                                               Im.fileName.split('.')[0]),
                                           'regions_list.dat'), 'w') as f:
                        for region in Im.regions:
                            f.write(','.join((region._type,
                                             str(region.mouseCenter['x']),
                                             str(region.mouseCenter['y']),
                                             str(region.timeStamp)+'\n')))
                except IOError:
                    pass

        updateLCD()


def deleteAllContour():

    for region in Im.regions:
        region.hideArrow()

    Im.regions = []
    files = glob.glob(os.path.join(workDir,
                                   os.path.basename(
                                       Im.fileName.split('.')[0]), '*.*'))
    for f in files:
        os.remove(f)

    for k, v in Im.regionsCounter.iteritems():
        Im.regionsCounter[k] = 0
    win.clearList(win.ui.contoursList)
    updateLCD()


def makeRegionData(region, nobkg=True):
    # check = False
    if nobkg:
        rr, cc = polygon(region.contour[:, 0],
                         region.contour[:, 1])
        for c, arr in Im.colorDict.iteritems():
            if c not in ('RGB', 'HSV'):
                mask = np.zeros_like(roiCopy)
                out = np.zeros_like(roiCopy)

                Arr, Coords = getRoi(arr, imgc)
                region.imagesArrays[c+'_nomask'] = Arr
                mask[rr, cc] = 1
                out[mask == 1] = Arr[mask == 1]
                region.imagesArrays[c+'_mask'] = out
    else:
        for c, arr in Im.colorDict.iteritems():
            if c not in ('RGB', 'HSV'):
                mask = np.full(roiCopy.shape, 1)
                Arr, roiCoords = getRoi(arr, imgc)
                out = np.copy(Arr)
                region.imagesArrays[c+'_nomask'] = out

    if region._type not in Im.regionsCounter:
        Im.regionsCounter[region._type] = 1
    else:
        Im.regionsCounter[region._type] += 1

    region.regionImage = Im
    region.number = Im.regionsCounter[region._type]
    region.mask = mask
    region.metaData['shapeWidth'] = roiSliceParam[0][0]
    region.metaData['shapeLength'] = roiSliceParam[0][1]
    region.metaData['xStart'] = roiSlice[0][0][0]
    region.metaData['xEnd'] = roiSlice[0][0][1]
    region.metaData['yStart'] = roiSlice[0][1][0]
    region.metaData['yEnd'] = roiSlice[0][1][1]
    region.metaData['timeStamp'] = region.timeStamp
    # np.savetxt('.'.join((c, 'txt')), region.contour)
    # io.imsave('.'.join((c, 'bmp')), out)
    if nobkg:
        out_rgb_mask = cv2.merge((region.imagesArrays['B_mask'],
                                  region.imagesArrays['G_mask'],
                                  region.imagesArrays['R_mask']))

        out_hsv_mask = cv2.merge((region.imagesArrays['V_mask'],
                                  region.imagesArrays['S_mask'],
                                  region.imagesArrays['H_mask']))
        region.imagesArrays['RGB_mask'] = out_rgb_mask
        region.imagesArrays['HSV_mask'] = out_hsv_mask

    out_rgb_nomask = cv2.merge((region.imagesArrays['B_nomask'],
                                region.imagesArrays['G_nomask'],
                                region.imagesArrays['R_nomask']))

    out_hsv_nomask = cv2.merge((region.imagesArrays['V_nomask'],
                                region.imagesArrays['S_nomask'],
                                region.imagesArrays['H_nomask']))

    region.imagesArrays['RGB_nomask'] = out_rgb_nomask
    region.imagesArrays['HSV_nomask'] = out_hsv_nomask
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


def blockSizeChoose():
    global blockSize
    blockSize = int(win.ui.blockSizeSpinBox.value())
    threshold()


def offsetChoose():
    global offset
    offset = int(win.ui.offsetSpinBox.value()) / 1000.
    threshold()


def methodChoose():
    global threshMethod
    threshMethod = str(win.ui.methodComboBox.currentText())
    threshold()


def createTimeStamp():
    timeStamp = "%.2f" % round(time.time(), 2)
    timeStamp = timeStamp.replace(".", "")

    return timeStamp


def updateLCD():
    if 'Cell' in Im.regionsCounter:
        win.ui.lcdCells.display(Im.regionsCounter['Cell'])
    if 'Background' in Im.regionsCounter:
        win.ui.lcdBkgs.display(Im.regionsCounter['Background'])
    if 'Red Cell' in Im.regionsCounter:
        win.ui.lcdRedCells.display(Im.regionsCounter['Red Cell'])
    if 'Other' in Im.regionsCounter:
        win.ui.lcdOthers.display(Im.regionsCounter['Other'])


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = GuiInit()

    blockSize = 99
    offset = 0
    threshMethod = 'mean'

    win.ui.blockSizeSpinBox.setSingleStep(2)
    win.ui.blockSizeSpinBox.setValue(blockSize)
    win.ui.blockSizeSpinBox.setMinimum(1)
    win.ui.blockSizeSpinBox.setMaximum(199)
    win.ui.offsetSpinBox.setValue(offset)

    images = sorted(glob.glob("*.tif"))
    imagesContener = {}
    currColor = 'GRAY'
    currRegionType = 'Cell'
    for image in images[::-1]:
        Im = Image(image)
        imagesContener[image] = Im
    Im.loadData()
    # win = gui.MainWindow()
    # win.setupUi()
    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(Im.grayData)
    imgc.setImage(Im.cData)
    win.setMainPlot(imgc)
    win.addItemsToList(win.ui.imagesList, images)

    update()
    Im.loadRegions()
    win.show()
    sys.exit(app.exec_())
