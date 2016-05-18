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


def createHist(image):
    hist = pg.HistogramLUTItem()
    hist.setImageItem(image)
    # hist.setLevels(fData.min(), fData.max())
    return hist


def update(roi):
    img1b.setImage(roi.getArrayRegion(fData, img))
    hist.setImageItem(img1b)
    v1b.autoRange()


if __name__ == '__main__':
    fData = loadData("1.tif")
    # p1 = win.addPlot()
    img = pg.ImageItem()
    img.setImage(fData)
    # p1.addItem(img)
    # win.resize(fData.shape[0], fData.shape[1])
    # addHist(img)
    # win.nextRow()
    w1 = win.addLayout(row=2, col=2)
    v1a = w1.addViewBox(row=1, col=1, rowspan=1, colspan=2, lockAspect=True)
    hist = pg.HistogramLUTItem()
    v2a = w1.addItem(hist, row=2, col=2)
    v1b = w1.addViewBox(row=2, col=1, lockAspect=True)
    v1a.addItem(img)
    # v2a.addItem(createHist())
    img1b = pg.ImageItem()
    v1b.addItem(img1b)
    v1a.disableAutoRange('xy')
    v1b.disableAutoRange('xy')
    v1a.autoRange()
    v1b.autoRange()
    roi = pg.RectROI([200, 200], [200, 200], pen=(0, 9))
    roi.sigRegionChanged.connect(update)
    v1a.addItem(roi)
    update(roi)
    win.show()
    # start loop
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
