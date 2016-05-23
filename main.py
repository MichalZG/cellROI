import sys
from skimage import io, color
# import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from skimage.filters import threshold_otsu, rank
from skimage.morphology import watershed, disk
import numpy.ma as ma
from skimage.filters import sobel, threshold_adaptive
from scipy import ndimage as ndi
from skimage import data, color
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
from skimage import measure
script_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.curdir


# pg.mkQApp()
# win = pg.GraphicsWindow()
app = QtGui.QApplication([])
win = QtGui.QWidget()

def loadData(fName):
    fData = io.imread(fName)
    fData = color.rgb2gray(fData)  # cut only R channel
    fData = fData[:, ::-1].T
    return fData


def createHist(image):
    hist = pg.HistogramLUTItem()
    hist.setImageItem(image)
    # hist.setLevels(fData.min(), fData.max())
    return hist


def update():
    roi_arr = roi.getArrayRegion(fData, img)
    roiImage.setImage(roi_arr)
    histogram.setImageItem(roiImage)
    roiPlot.autoRange()
    otsu(roi_arr)


def updateContours():
    if rcheck.isChecked():
        roi_arr = roi.getArrayRegion(fData, img)
        contours = otsu(roi_arr)
        for c in contours:
            c = c.astype(int)
            roi_arr[c[:, 0], c[:, 1]] = 1
        roiImage.setImage(roi_arr)
    else:
        roi_arr = roi.getArrayRegion(fData, img)
        roiImage.setImage(roi_arr)


def otsu(roi_arr):
    otsu = threshold_adaptive(roi_arr, block_size=100, method='mean')
    otsu_arr = roi_arr >= otsu
    otsu_arr = otsu_arr.astype('float64')
    contours = makeContour(otsu_arr)
    for c in contours:
        c = c.astype(int)
        otsu_arr[c[:, 0], c[:, 1]] = 3
    contourImage.setImage(otsu_arr)
    contourPlot.autoRange()

    return contours


def makeContour(otsu_arr):
    contours = measure.find_contours(otsu_arr, 0.99)

    return contours


if __name__ == '__main__':
    fData = loadData("1.tif")
    img = pg.ImageItem()
    img.setImage(fData)
    win.resize(1000, 1200)

    # w1 = win.addLayout(row=3, col=3)
    w1 = QtGui.QGridLayout()
    win.setLayout(w1)

    mainPlot = pg.PlotWidget()
    mainPlot.setAspectLocked()
    mainPlot.setMouseEnabled(x=False, y=False)

    histogram = pg.HistogramLUTWidget()

    roiPlot = pg.PlotWidget()
    roiPlot.setAspectLocked()
    roiPlot.setMouseEnabled(x=False, y=False)

    contourPlot = pg.PlotWidget()
    contourPlot.setAspectLocked()
    contourPlot.setMouseEnabled(x=False, y=False)

    rcheck = QtGui.QCheckBox('Plot contour')

    w1.addWidget(mainPlot, 0, 0, 1, 3)
    w1.addWidget(histogram, 1, 0)
    w1.addWidget(roiPlot, 1, 1)
    w1.addWidget(contourPlot, 1, 2)
    w1.addWidget(rcheck, 2, 1)
    # win.addLayout(rcheck)

    mainPlot.addItem(img)
    roiImage = pg.ImageItem()
    roiPlot.addItem(roiImage)
    contourImage = pg.ImageItem()
    contourPlot.addItem(contourImage)

    roi = pg.RectROI([100, 100], [100, 100], pen=(0, 9))
    roi.sigRegionChanged.connect(update)

    mainPlot.addItem(roi)

    timer = QtCore.QTimer()
    timer.timeout.connect(updateContours)
    timer.start(0)

    win.show()
    app.exec_()
