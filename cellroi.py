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
    app = QtGui.QApplication(sys.argv)
    images = sorted(glob.glob("*.tif"))

    Im = Image(images[0])
    Im.loadData()
    win = GuiInit()
    # win = gui.MainWindow()
    # win.setupUi()
    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(Im.rawData)
    imgc.setImage(Im.cData)
    win.ui.setMainPlot(imgc)
    win.ui.addItemsToList(images)
    win.show()
    sys.exit(app.exec_())
