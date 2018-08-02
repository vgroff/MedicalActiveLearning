import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle

from cnnUtils import saveModel, loadModel
from imageUtils import ImageManager, getDatasetInfo
from model import getUNet, getUNet2, getPCNet

from imageReader import getImages

from keras.optimizers import Adam, SGD
from model import weighted_dice_coefficient_loss


# def getImages(folder, size):
#     print("Getting images")
#     trainPaths = getDatasetInfo(folder)
#     imgs = []
#     labels = []
#     imageOrigs = []
#     i = 0
#     for img in readFunc(trainPaths[:4], None,
#                         {"folder":folder, "depth":132, "size":size, "whiten":True}):
#         i += 1
#         print("Image {}".format(i), end="\r")
#         image = img["features"]["x"]
#         label = img["labels"]["y"]
#         imageOrig = img["original"]
#         imgPath = img["imgPath"]
#         newImg = np.swapaxes(image, 0,3)
#         newLabel = np.swapaxes(label, 0,3)
#         imageOrig = np.swapaxes(imageOrig, 0, 3)
#         yield { "imgTr": newImg, "label": newLabel, "img": imageOrig , "imgPath": imgPath }

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
        lr = 3.5e-4
        adam = Adam(lr=lr)
        sgd = SGD(lr=lr, momentum=0.95, decay=0.0, nesterov=True)
        model.compile(optimizer = sgd, loss = weighted_dice_coefficient_loss)
    print("Training on {}, validating on {}".format(len(imgs), len(valImgs)))
    learning_rate_reduction = ReduceLROnPlateau(monitor='loss',
                                                patience=2,
                                                verbose=1,
                                                factor=0.7,
                                                min_lr=1e-5)
    model.fit(np.array(imgs), np.array(labels), batch_size=1, verbose=1, epochs=10, shuffle=True,
              validation_data=(np.array(valImgs), np.array(valLabels)),
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
# Train on lower learning rate with SGD!
# Need proper image augmentation. IDEAS:
# - More samples
# - Rotations
# For multiple segmentations, might be most efficient to have a segmentation with large margins and then cut that up multiple times.





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
