import sys
import pickle
import os
import json
from imageUtils import ImageManager, pathImgMngr, cubePadding
import numpy as np
from skimage.transform import rescale as zoom
from main import listsToArray
import tensorflow as tf
from dltk.io.preprocessing import whitening


def addToDB():

    cnnSize = 80
    name = sys.argv[1]

    lines = sys.stdin.readlines()
    img = json.loads(lines[0][:-1])
    label = json.loads(lines[1])
    img   = listsToArray(img)
    label = listsToArray(label)

    f = open(pathImgMngr(name), "rb")
    imgMngr = pickle.load(f)
    f.close()

    info = {"imgOrig": img}
    img = np.copy(img)

    maxVal = img.max()
    img /= maxVal

    minSize = max(img.shape)
    img = cubePadding(img, cnnSize)[0]
    resizeFactor = cnnSize / img.shape[0]
    img = zoom(img, resizeFactor, order=1, anti_aliasing=True, multichannel=False)
    img = whitening(img)
    img = np.stack([img], axis=0)

    label = cubePadding(label, cnnSize)[0]
    catLabels = np.zeros(list(label.shape)+[2])
    for i, row in enumerate(label):
        for j, col in enumerate(row):
            for k, depth in enumerate(col):
                catLabels[i, j, k, int(round(depth))] = 1
    catLabels = zoom(catLabels, [resizeFactor]*3, order=1, anti_aliasing=True,  multichannel=True)
    for i, row in enumerate(catLabels):
        for j, col in enumerate(row):
            for k, depth in enumerate(col):
                val = 0
                if (depth[0] < depth[1]):
                    val = 1
                catLabels[i, j, k, val] = 1
                catLabels[i, j, k, (val+1)%2] = 0
                
    catLabels = np.moveaxis(catLabels, 3, 0)

    nTrain = len(imgMngr.getTrainImages()[0])
    nVal   = len(imgMngr.getValImages()[0])

    valFrac = 1
    if nTrain != 0:
        valFrac = nVal / (nVal + nTrain)
    if (valFrac < 0.2):
        data = [[[],[],[]], [[img],[catLabels],[info]]]
    else:
        data = [[[img],[catLabels],[info]], [[],[],[]]]
    imgMngr.addData(data)
    f = open(pathImgMngr(name), "wb")
    pickle.dump(imgMngr, f)
    f.close()
    print(0)
    print("Done")

if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    addToDB()
