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
        if i > 18:
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
    for i, label in enumerate(result):
        #newLabel = np.moveaxis(label, 0, 3)
        print(label.shape)
        newLabel = np.argmax(label, axis=0)
        print(newLabel.shape)
        for row in newLabel:
            for col in row:
                for depth in col:
                    #print(depth)
                    counts[depth] += 1
    
    print(labels[0].shape)
    for label in labels:
        newLabel = label[0]#np.moveaxis(label, 0, 3)
        print(newLabel.shape)
        for row in newLabel:
            for col in row:
                for depth in col:
                    #if (int(round(depth)) > 0.1):
                        #print(depth)
                    counts2[int(round(depth))] += 1
    print(counts, counts2)
        #print(res)
        #print(np.sum(res))
        #print(np.sum(img))
        #dice = metrics.dice(newLabel, labels, 1)[1:].mean()
        #print("Dice score: {}".format(dice))
    print(ones, zeroes)
        
if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    predict()
