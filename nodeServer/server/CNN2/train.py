import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle

from cnnUtils import saveModel, loadModel
from imageUtils import DataManager, getDatasetInfo
from model import getUNet, getUNet2, getPCNet

from imageReader import readFunc

from keras.optimizers import Adam, SGD
from model import weighted_dice_coefficient_loss


def getImages(folder, size):
    print("Getting images")
    trainPaths = getDatasetInfo(folder)
    imgs = []
    labels = []
    i = 0
    for img in readFunc(trainPaths[:6], None,
                        {"folder":folder, "depth":132, "size":size, "whiten":True}):
        i += 1
        print("Image {}".format(i), end="\r")
        image = img["features"]["x"]
        label = img["labels"]["y"]
        newImg = np.swapaxes(image, 0,3)
        newLabel = np.swapaxes(label, 0,3)
        imgs.append(newImg)#img["features"]["x"])
        labels.append(newLabel)#img["labels"]["y"])
    return imgs, labels

def train():
    useOldImg = True
    useOldModel = True
    nClasses = 2
    if (useOldImg == False):
        folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
        size = [32, 80, 80] # 32,80,80
        imgs, labels = getImages(folder, size)
        mngr = DataManager(imgs, labels)
        f = open("imgs.pkl", "wb")
        pickle.dump(mngr, f)
        f.close()
    else:
        f = open("imgs.pkl", "rb")
        mngr = pickle.load(f)
        f.close()
        imgs, labels = mngr.getData()

    print("Getting net")
    if (useOldModel == False):
        model = getUNet2((1,80,80,32), nClasses, lr=0.8e-4)
    else:
        model = loadModel(1)
        adam = Adam(lr = 2.0e-4)
        model.compile(optimizer = adam, loss = weighted_dice_coefficient_loss)
    print("Training")
    learning_rate_reduction = ReduceLROnPlateau(monitor='loss',
                                                patience=3,
                                                verbose=1,
                                                factor=0.65,
                                                min_lr=2e-5)
    model.fit(np.array(imgs), np.array(labels), batch_size=1, verbose=1, epochs=40, shuffle=True,
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
# - Crop the input image, then train on all
# - Resize the output image correctly back to original size
# - Do augmentation on input images - Check the guys Github!!!
# - Do graphcuts/BIFSeg, using front-end


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
