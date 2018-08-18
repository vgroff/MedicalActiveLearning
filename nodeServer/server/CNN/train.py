import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle
import sys
import random

from cnnUtils import saveModel, loadModel
from imageUtils import ImageManager, getDatasetInfo
from model import getUNet, getUNet2, getPCNet

from imageReader import getImages

from keras.optimizers import Adam, SGD
from model import weighted_dice_coefficient_loss, weightedDiceLoss

from functools import partial

def prepImageManager(numVal, numbers, orientations, folders, size):
    mngr = None
    for i, folder in enumerate(folders):
        print("Folder {}/{}".format(i+1,len(folders)))
        shape = [size]*3
        dataset = getDatasetInfo(folder)
        number = numbers[i]
        orientation = orientations[i]
        if (number < len(dataset)):
            dataset = dataset[:number]
        data = getImages(folder, dataset, size, numVal/len(dataset), orientation, True, [0, 10], [1,2])
        if (mngr):
            mngr.addData(data)
        else:
            mngr = ImageManager(data)
    return mngr


def generateImages(imgs, labels, imageSets):
    while True:
        for imageSet in imageSets:
            trImgs = imgs[imageSet[0]:imageSet[0]+imageSet[1]]
            trLabels = labels[imageSet[0]:imageSet[0]+imageSet[1]]
            if (imageSet[3] == True):
                ordering = random.sample(range(imageSet[1]), imageSet[1])
                newTrImgs = []
                newLabels = []
                for index in ordering:
                    newTrImgs.append(trImgs[index])
                    newLabels.append(trLabels[index])
                trImgs = newTrImgs
                trLabels = newLabels
            for i in range(imageSet[2]):
                for j, img in enumerate(trImgs):
                    yield np.array([img]), np.array([trLabels[j]])

def quickTrain(model, img, weighting, segmentation, epochs=1):
    labels = np.zeros(weighting.shape)
    c = 0
    for i, row in enumerate(segmentation):
        for j, col in enumerate(row):
            for k, val in enumerate(col):
                labels[int(round(val)),i,j,k] = 1
    lr = 0.8e-4#2.5e-5#1.2e-4#7.5e-5
    adam = Adam(lr=lr)
    sgd = SGD(lr=lr, momentum=0.95, decay=0.0, nesterov=False)
    loss = partial(weightedDiceLoss, weighting)
    model.compile(optimizer = adam, loss = loss)
    model.fit(np.array([img]), np.array([labels]), validation_split=0.0, batch_size=1, verbose=1, epochs=epochs)#, 
              #callbacks=[learning_rate_reduction])

    
def train():
    useOldImg   = True
    useOldModel = True
    nClasses = 2
    length = 80
    if (useOldImg == False):
        folderStub = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task"
        folderNames = ["02_Heart", "05_Prostate", "06_Lung", "07_Pancreas"] 
        folders = [folderStub+name for name in folderNames]
        numbers      = [20, 20, 35, 35]
        orientations = [2, 2, 1, 1]
        numVal = 5
        mngr = prepImageManager(numVal, numbers, orientations, folders, length)
        imgs, labels, info = mngr.getTrainImages()
        valImgs, valLabels, valInfo = mngr.getValImages()
        f = open("imgs.pkl", "wb")
        pickle.dump(mngr, f)
        f.close()
    else:
        print("Getting images...")
        f = open("imgs.pkl", "rb")
        mngr = pickle.load(f)
        f.close()
        imgs, labels, info = mngr.getTrainImages()
        valImgs, valLabels, valInfo = mngr.getValImages()
    print("Getting net...")
    lr = 1.0e-5#2.5e-5#1.2e-4#7.5e-5
    if (useOldModel == False):
        model = getUNet2((1,length,length,length), nClasses, lr=lr, loss_function="binary_crossentropy")
    else:
        model = loadModel(1)
        adam = Adam(lr=lr, epsilon=1e-3, amsgrad=True)
        sgd = SGD(lr=lr, momentum=0.96, decay=0.0, nesterov=False)
        model.compile(optimizer = sgd, loss = "binary_crossentropy", metrics=["accuracy", weighted_dice_coefficient_loss])
    print("Training on {}, validating on {}".format(len(imgs), len(valImgs)))
    learning_rate_reduction = ReduceLROnPlateau(monitor='loss',
                                                patience=3,
                                                verbose=1,
                                                factor=0.5,
                                                min_lr=0.5e-5)
    imageSets = [[90, 30, 4, False],[0, 30, 1, False],[60, 30, 5, False],[90, 30, 2, False],[30, 30, 1, False]]
    imageSets = [[0,120,1,True]]#[[60, 30, 4*1, True], [90, 30, 4*1, True], [0, 120, 1, True]]#, [90, 30, 10, False], [0, 120, 1, True]]
    epochs = 15
    imgGen = generateImages(imgs, labels, imageSets)
    model.fit_generator(imgGen, verbose=1, #metrics=["accuracy"],
                        steps_per_epoch=120, epochs=epochs,
                        shuffle=False, validation_data=(np.array(valImgs), np.array(valLabels)),
                        callbacks=[learning_rate_reduction])
    saveModel(model)

if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    train()

# TO-DO:
# - Multiple datasets at once
# - Not sure that mean weighted dice coefficient works with resized images. They will be both pushed towards 1 - but this might actually be ok but for graph cuts and for validation data, maybe. Could try a more normal loss function otherwise





# BIG PICTURE:
# - CNN on server is just trained in basic segmentation - automatic bounding-box
# - People can upload a dataset to fine-tune the network - here the bounding-box is done automatically
# - Then they can upload live data, doing the bounding-box themselves.
# On the front-end, people are walked through
# - upload picture or dataset
# - do bounding CUBE
# - correct via graph cuts
# - finishing touches
# - save to file or crop image
