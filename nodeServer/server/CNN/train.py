import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle
import sys

from cnnUtils import saveModel, loadModel
from imageUtils import ImageManager, getDatasetInfo
from model import getUNet, getUNet2, getPCNet

from imageReader import getImages

from keras.optimizers import Adam, SGD
from model import weighted_dice_coefficient_loss, weightedDiceLoss

from functools import partial

def prepImageManager(folders, size):
    mngr = None
    for i, folder in folders:
        print("Folder {}/{}".format(i+1,len(folders)))
        shape = [size]*3
        dataset = getDatasetInfo(folder)
        data = getImages(folder, dataset, length, 0.2, True, [0, 9], [1,2])
        if (mngr):
            mngr.addData(data)
        else:
            mngr = ImageManager(data)
    return mngr

def quickTrain(model, img, weighting, segmentation, epochs=1):
    labels = np.zeros(weighting.shape)
    c = 0
    for i, row in enumerate(segmentation):
        for j, col in enumerate(row):
            for k, val in enumerate(col):
                labels[int(round(val)),i,j,k] = 1
    #print("train to fit", segmentation, file=sys.stderr)
    lr = 2e-4#2.5e-5#1.2e-4#7.5e-5
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
        folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
        size = [length]*3 # 32,80,80
        dataset = getDatasetInfo(folder)
        data = getImages(folder, dataset, length, 0.2, True, [0, 9], [1,2])
        mngr = ImageManager(data)
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
    if (useOldModel == False):
        model = getUNet2((1,length,length,length), nClasses, lr=4e-5)
    else:
        model = loadModel(1)
        lr = 2.5e-5#1.2e-4#7.5e-5
        epochs = 5
        adam = Adam(lr=lr)
        sgd = SGD(lr=lr, momentum=0.95, decay=0.0, nesterov=False)
        model.compile(optimizer = adam, loss = weighted_dice_coefficient_loss)
    print("Training on {}, validating on {}".format(len(imgs), len(valImgs)))
    learning_rate_reduction = ReduceLROnPlateau(monitor='loss',
                                                patience=3,
                                                verbose=1,
                                                factor=0.75,
                                                min_lr=1e-5)
    model.fit(np.array(imgs), np.array(labels), batch_size=1, verbose=1, epochs=epochs,
              shuffle=True, validation_data=(np.array(valImgs), np.array(valLabels)),
              callbacks=[learning_rate_reduction])
    saveModel(model)

if __name__ == '__main__':
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
