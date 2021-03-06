import numpy as np
import tensorflow as tf
import os

from keras.optimizers import Adam, SGD

from dltk.core import metrics as metrics

from cnnUtils import loadModel
from imageUtils import getDatasetInfo, ImageManager
from imageReader import getImages

import pickle

import SimpleITK as sitk

from model import weighted_dice_coefficient_loss

from dltk.io.preprocessing import whitening


# Write image array arr to nifti file at folder/name.nii.gz
def writeNIFTI(arr, folder, name):
    new_sitk = sitk.GetImageFromArray(arr)
    #new_sitk.CopyInformation(original['sitk'])
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)


def predict():
    # Load model
    model = loadModel("General")

    # Folder for reading images
    folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task04_Hippocampus"
    trainPaths = getDatasetInfo(folder)

    # Folder for writing outputs
    outputFolder = "./spleens"
    
    # Get images
    print("Getting images")
    f = open("imgs_spleen10.pkl", "rb")
    mngr = pickle.load(f)
    f.close()

    imgs, labels, info = mngr.getValImages()
    #selection = [0,1,2,3,4]#[0,16,32,48]
    #print(len(imgs))
    #imgs, labels, info = [ [imgs[i] for i in selection], [labels[i] for i in selection],
    #                       [info[i] for i in selection] ]
    #imgsActual = [info[i]["imgOrig"] for i in range(len(info))]

    #data = getImages(folder, trainPaths[16:18], 80, 0)
    
    #mngr = ImageManager(data)
    #imgs, labels, info = mngr.getTrainImages()
    imgsActual = [info[i]["imgOrig"] for i in range(len(imgs))]
    
    result = []
    for img in imgs:
        result.append(model.predict(np.array([img])))



    dice = 0
    for i, label in enumerate(result):
        # Convert to binary labels
        newLabel = np.argmax(label, axis=0)
        newLabel2 = np.argmax(labels[i], axis=0)
        print(info[i]["path"])
        
        print("dice coefficient:", tf.Session().run(weighted_dice_coefficient_loss(np.array(labels[i], dtype="float64"), np.array(result[i], dtype="float64"))))
        
        dice += tf.Session().run(weighted_dice_coefficient_loss(np.array(labels[i], dtype="float64"), np.array(result[i], dtype="float64")))

        # Write results to file
        writeNIFTI(newLabel.astype(np.float32), outputFolder, "{}_pred".format(i))
        writeNIFTI(newLabel2.astype(np.float32), outputFolder, "{}_truth".format(i))
        writeNIFTI(imgsActual[i].astype(np.float32), outputFolder, "{}_actual".format(i))

    dice /= len(imgs)
    print("Dice av", dice)
                                                                
if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    predict()
