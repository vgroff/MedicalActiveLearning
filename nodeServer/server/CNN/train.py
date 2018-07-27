import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle

from cnnUtils import saveModel, loadModel
from imageUtils import ImageManager, getDatasetInfo
from model import getUNet, getUNet2, getPCNet

from imageReader import readFunc

from keras.optimizers import Adam, SGD
from model import weighted_dice_coefficient_loss


def getImages(folder, size):
    print("Getting images")
    trainPaths = getDatasetInfo(folder)
    imgs = []
    labels = []
    imageOrigs = []
    i = 0
    for img in readFunc(trainPaths, None,
                        {"folder":folder, "depth":132, "size":size, "whiten":True}):
        i += 1
        print("Image {}".format(i), end="\r")
        image = img["features"]["x"]
        label = img["labels"]["y"]
        imageOrig = img["original"]
        imgPath = img["imgPath"]
        newImg = np.swapaxes(image, 0,3)
        newLabel = np.swapaxes(label, 0,3)
        imageOrig = np.swapaxes(imageOrig, 0, 3)
        yield { "imgTr": newImg, "label": newLabel, "img": imageOrig , "imgPath": imgPath }

def train():
    useOldImg = True
    useOldModel = True
    nClasses = 2
    if (useOldImg == False):
        folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
        size = [64, 64, 64] # 32,80,80
        func = getImages(folder, size)
        mngr = ImageManager(func)
        imgs, labels = mngr.getTrainImages()
        f = open("imgs.pkl", "wb")
        pickle.dump(mngr, f)
        f.close()
    else:
        print("Getting images...")
        f = open("imgs.pkl", "rb")
        mngr = pickle.load(f)
        f.close()
        imgs, labels = mngr.getTrainImages()
    print("Getting net...")
    if (useOldModel == False):
        model = getUNet2((1,64,64,64), nClasses, lr=5e-4)
    else:
        model = loadModel(1)
        adam = Adam(lr = 0.2e-4)
        model.compile(optimizer = adam, loss = weighted_dice_coefficient_loss)
    print("Training")
    learning_rate_reduction = ReduceLROnPlateau(monitor='loss',
                                                patience=2,
                                                verbose=1,
                                                factor=0.65,
                                                min_lr=1.0e-5)
    model.fit(np.array(imgs), np.array(labels), batch_size=1, verbose=1, epochs=35, shuffle=True,
              validation_split=0.2, callbacks=[learning_rate_reduction])
    saveModel(model)

if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    train()

# TO-DO:
# - Do graphcuts/BIFSeg, using front-end
# - Resize the output image correctly back to original size



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
