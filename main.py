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


pg.mkQApp()
win = pg.GraphicsLayoutWidget()


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


def update(roi):
    roi_arr = roi.getArrayRegion(fData, img)
    img1b.setImage(roi_arr)
    hist.setImageItem(img1b)
    v1b.autoRange()
    otsu(roi_arr)


def otsu(roi_arr):
    otsu = threshold_adaptive(roi_arr, block_size=100, method='mean')
    otsu_arr = roi_arr >= otsu
    otsu_arr = otsu_arr.astype('float64')
    contours = makeContour(otsu_arr)
    for c in contours:
        c = c.astype(int)
        otsu_arr[c[:, 0], c[:, 1]] = 3
    img3b.setImage(otsu_arr)
    v3b.autoRange()


def makeContour(otsu_arr):
    contours = measure.find_contours(otsu_arr, 0.99)
    return contours


if __name__ == '__main__':
    fData = loadData("1.tif")
    img = pg.ImageItem()
    img.setImage(fData)
    win.resize(800, 1200)

    w1 = win.addLayout(row=2, col=3)
    v1a = w1.addViewBox(row=1, col=1, rowspan=1, colspan=3,
                        lockAspect=True, enableMouse=False)
    hist = pg.HistogramLUTItem()
    v2a = w1.addItem(hist, row=2, col=1)
    v3b = w1.addViewBox(row=2, col=3, lockAspect=True, enableMouse=False)
    v1b = w1.addViewBox(row=2, col=2, lockAspect=True, enableMouse=False)
    v1a.addItem(img)
    img3b = pg.ImageItem()
    img1b = pg.ImageItem()
    v1b.addItem(img1b)
    v3b.addItem(img3b)
    v1a.disableAutoRange('xy')
    v1b.disableAutoRange('xy')
    v3b.disableAutoRange('xy')
    v1a.autoRange()
    v1b.autoRange()
    v3b.autoRange()
    roi = pg.RectROI([100, 100], [100, 100], pen=(0, 9))
    # roi = pg.EllipseROI([200, 200], [120, 120])
    roi.sigRegionChanged.connect(update)
    v1a.addItem(roi)
    update(roi)

    win.show()
    # start loop
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
