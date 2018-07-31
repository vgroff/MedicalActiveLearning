import numpy as np
import tensorflow as tf
import os

from keras.optimizers import Adam, SGD

from dltk.core import metrics as metrics

from cnnUtils import loadModel
from imageUtils import getDatasetInfo
from imageReader import readFunc

import pickle

import SimpleITK as sitk

from model import weighted_dice_coefficient_loss

from dltk.io.preprocessing import whitening


def writeNIFTI(arr, folder, name):
    new_sitk = sitk.GetImageFromArray(arr.astype(np.int32))
    #new_sitk.CopyInformation(original['sitk'])
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)


def predict():
    model = loadModel(1)
    
    folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
    trainPaths = getDatasetInfo(folder)

    outputFolder = "./predictions"

    print("Getting images")
    f = open("imgs.pkl", "rb")
    mngr = pickle.load(f)
    f.close()
    nStart = 19
    n = 1
    imgs, labels = mngr.getTrainImages(nStart, n)
    print(imgs[0][0][24][25][26])
    imgsActual = mngr.getImages(nStart, n)
    print(imgsActual[0][0][24][25][26])
    img2 = whitening(imgsActual[0][0])
    print(img2[24][25][26])
    img2 = np.stack([img2], axis=0).astype(np.float32)
    #img2 = np.swapaxes(img2, 0,3)
    
    #sgd = SGD(lr=0.0002, decay=1.2e-2, momentum=0.9, nesterov=True)
    #model.compile(optimizer = sgd, loss = 'binary_crossentropy', metrics = ['accuracy'])
    print("img", np.array(imgs).shape)
    result = model.predict(np.array([img2]))#, np.array(labels))
    print("result", result.shape)
    print(np.array(labels).shape, result.shape)
    with tf.Session() as sess:
        print(sess.run(weighted_dice_coefficient_loss(np.array(labels), result)))
    ones = 0
    zeroes = 0
    counts  = [0,0]
    counts2 = [0,0]
    counts3 = [0,0]
    for i, label in enumerate(result):
        #newLabel = np.moveaxis(label, 0, 3)
        print(label.shape)
        newLabel = np.argmax(label, axis=0)
        print(newLabel.shape)
        newLabel2 = np.argmax(labels[i], axis=0)
        for row in newLabel:
            for col in row:
                for depth in col:
                    #print(depth)
                    counts[depth] += 1
        for row in newLabel2:
            for col in row:
                for depth in col:
                    #print(depth)
                    counts3[depth] += 1
        writeNIFTI(newLabel, outputFolder, "{}_pred".format(i))
        writeNIFTI(newLabel2, outputFolder, "{}_truth".format(i))
        writeNIFTI(np.around(imgsActual[i][0]), outputFolder, "{}_actual".format(i))
        writeNIFTI(imgs[i][0], outputFolder, "{}_processed".format(i))
    print(counts, counts3)
        
if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    predict()
