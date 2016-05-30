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
script_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.curdir


# pg.mkQApp()
# win = pg.GraphicsWindow()
app = QtGui.QApplication([])
win = QtGui.QWidget()




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
    roi_arr, roi_coords = roi.getArrayRegion(fData, imgc,
                                             returnMappedCoords=True)
    roi_b = np.copy(roi.getArrayRegion(b, imgc))
    roi_g = np.copy(roi.getArrayRegion(g, imgc))
    roi_r = np.copy(roi.getArrayRegion(r, imgc))
    roi_copy = np.copy(roi_arr)
    roiImage.setImage(roi_arr)
    histogram.setImageItem(roiImage)
    roiPlot.autoRange()
    otsu(roi_arr)


def updateContours():
    if rcheck.isChecked():
        roi_arr, roi_coords = roi.getArrayRegion(fData, imgc,
                                                 returnMappedCoords=True)
        temp_arr = roi_arr
        contours = otsu(temp_arr)
        for c in contours:
            c = c.astype(int)
            temp_arr[c[:, 0], c[:, 1]] = 1
        roiImage.setImage(temp_arr)
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
    contourImage.setImage(otsu_arr)
    contourPlot.autoRange()

    return contours


def makeContour(otsu_arr):
    global contours
    contours = measure.find_contours(otsu_arr, 0.99)

    return contours


def mouseMoved(evt):
    pos = evt[0]
    if contourPlot.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        if index > 0 and index < 100:
            vline.setPos(mousePoint.x())
            hline.setPos(mousePoint.y())


def mouseClicked(evt):
    items = vb.scene().items(evt.scenePos())
    x_roi = items[1].x()
    y_roi = items[0].y()
    print x_roi, y_roi
    print roi_coords[0][x_roi][y_roi], roi_coords[1][x_roi][y_roi]
    saveContour(x_roi, y_roi)


def translateCoords():
    pass


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
            io.imsave('b.tif', out_b)
            io.imsave('g.tif', out_g)
            io.imsave('r.tif', out_r)
            out_rgb = cv2.merge((out_b, out_g, out_r))
            io.imsave('out_rgb.tif', out_rgb)
            io.imsave('out_grey.tif', out)


if __name__ == '__main__':
    fData, cData = loadData("1.tif")
    # b, g, r = cv2.split(cData)
    b = cData[:, :, 0]
    g = cData[:, :, 1]
    r = cData[:, :, 2]
    # b = transform.rotate(b, angle=270, clip=False, resize=True)
    # g = transform.rotate(g, angle=270, clip=False, resize=True)
    # r = transform.rotate(r, angle=270, clip=False, resize=True)
    img = pg.ImageItem()
    imgc = pg.ImageItem()
    img.setImage(fData)
    imgc.setImage(cData)
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
    # crosshair
    vline = pg.InfiniteLine(angle=90, movable=False)
    hline = pg.InfiniteLine(angle=0, movable=False)

    w1.addWidget(mainPlot, 0, 0, 1, 3)
    w1.addWidget(histogram, 1, 0)
    w1.addWidget(roiPlot, 1, 1)
    w1.addWidget(contourPlot, 1, 2)
    w1.addWidget(rcheck, 2, 1)
    # win.addLayout(rcheck)

    mainPlot.addItem(imgc)
    roiImage = pg.ImageItem()
    roiPlot.addItem(roiImage)
    contourImage = pg.ImageItem()
    contourPlot.addItem(contourImage)
    contourPlot.addItem(vline, ignoreBounds=True)
    contourPlot.addItem(hline, ignoreBounds=True)

    roi = pg.RectROI([100, 100], [100, 100], pen=(0, 9))
    roi.sigRegionChanged.connect(update)

    mainPlot.addItem(roi)

    vb = contourImage.getViewBox()
    proxy = pg.SignalProxy(contourPlot.scene().sigMouseMoved, rateLimit=60,
                           slot=mouseMoved)
    contourPlot.scene().sigMouseClicked.connect(mouseClicked)

    timer = QtCore.QTimer()
    timer.timeout.connect(updateContours)
    timer.start(0)

    win.show()
    app.exec_()
