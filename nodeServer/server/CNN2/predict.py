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
    imgsAll, labelsAll = mngr.getData()
    
    imgs = []
    labels = []
    for i, img in enumerate(imgsAll):
        if i > 4:
            imgs.append(img)
            labels.append(labelsAll[i])
    #sgd = SGD(lr=0.0002, decay=1.2e-2, momentum=0.9, nesterov=True)
    #model.compile(optimizer = sgd, loss = 'binary_crossentropy', metrics = ['accuracy'])
    print("img", np.array(imgs).shape)
    result = model.predict(np.array(imgs))#, np.array(labels))
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
        writeNIFTI(imgs[i][0], outputFolder, "{}_actual".format(i))
    print(counts, counts3)
        
if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    predict()
