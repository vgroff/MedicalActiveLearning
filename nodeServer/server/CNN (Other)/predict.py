import tensorflow as tf
import numpy as np

from tensorflow.contrib import predictor

import os

import SimpleITK as sitk

from imageReader import readFunc
from utils import getDatasetInfo, splitArr

from dltk.core import metrics as metrics

def writeNIFTI(arr, folder, name, original):
    new_sitk = sitk.GetImageFromArray(arr.astype(np.int32))
    #new_sitk.CopyInformation(original['sitk'])
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)

def predict():
    modelPath = "./models"
    outputFolder = "./predictions"
    folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
    trainPaths = getDatasetInfo(folder)
    train_filenames, val_filenames = splitArr(trainPaths, 0.75)
    size = [33, 80, 80]
    nn = predictor.from_saved_model(os.path.join(modelPath, "1531182194"))

    # Fetch the output probability op of the trained network
    y_prob = nn._fetch_tensors['y_prob']
    num_classes = y_prob.get_shape().as_list()[-1]

    readParams = {"folder":folder, "depth":132, "size":size, "whiten": True}
    for example in readFunc(val_filenames, None, readParams):
        img = example["features"]["x"]
        img = np.array(img).reshape(1, *size, 1)
        # Make prediction
        results = nn({"x":img})

        # Calculate the prediction from the probabilities
        pred = results["y_prob"]
        pred = np.argmax(pred, -1)

        # Calculate the Dice coefficienti
        label = example["labels"]["y"]
        dsc = metrics.dice(pred, label, 2)[1:].mean()
        print(dsc)

        ID = example["subject_id"]

        writeNIFTI(example["features"]["x"], outputFolder, "{}_whit".format(ID), example)
        writeNIFTI(label, outputFolder, "{}_truth".format(ID), example)
        writeNIFTI(pred[0], outputFolder, "{}_pred".format(ID), example)

    readParams = {"folder":folder, "depth":132, "size":size, "whiten": False}
    for example in readFunc(val_filenames, None, readParams):
        writeNIFTI(example["features"]["x"], outputFolder, "{}".format(ID), example)

        
if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    predict()
