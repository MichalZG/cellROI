import sys
from skimage import io, color
import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

script_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.curdir


pg.mkQApp()
win = pg.GraphicsLayoutWidget()


def loadData(fName):
    fData = io.imread(fName)
    fData = color.rgb2gray(fData)  # cut only R channel
    fData = fData.T
    return fData


def addHist(img):
    hist = pg.HistogramLUTItem()
    hist.setImageItem(img)
    win.addItem(hist)


def update(roi):
    img1b.setImage(roi.getArrayRegion(fData, img1a), levels=(0, fData.max()))
    v1b.autoRange()


if __name__ == '__main__':
    fData = loadData("1.tif")
    # p1 = win.addPlot()
    img = pg.ImageItem()
    img.setImage(fData)
    # p1.addItem(img)
    win.resize(fData.shape[0], fData.shape[1])
    # addHist(img)
    # win.nextRow()
    w1 = win.addLayout(row=0, col=0)
    label1 = w1.addLabel('ss', row=0, col=0)
    v1a = w1.addViewBox(row=1, col=0, lockAspect=True)
    v1b = w1.addViewBox(row=2, col=0, lockAspect=True)
    img1a = pg.ImageItem(fData)
    v1a.addItem(img1a)
    img1b = pg.ImageItem()
    v1b.addItem(img1b)
    v1a.disableAutoRange('xy')
    v1b.disableAutoRange('xy')
    v1a.autoRange()
    v1b.autoRange()
    roi = pg.RectROI([20, 20], [20, 20], pen=(0, 9))
    roi.sigRegionChanged.connect(update)
    v1a.addItem(roi)
    update(roi)
    win.show()
    # start loop
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
