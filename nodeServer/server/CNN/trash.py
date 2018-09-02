



from cnnUtils import loadModel
from imageUtils import getDatasetInfo

import pickle

from predict import writeNIFTI

from imageReader import getImages

from cnnUtils import loadModel, saveModel
from imageUtils import ImageManager, getDatasetInfo
from train import getImages
from predict import writeNIFTI
from imageReader import readFunc
import SimpleITK as sitk
from imageUtils import cropToSeg

from model import weighted_dice_coefficient_loss

import os
import tensorflow as tf
import numpy as np

from main import main

from keras import activations
from keras.models import *
from keras.layers import *
from train import prepImageManager
##
## This file is for code scraps and for testing stuff
##

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

#model = loadModel(1)

folderStub = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task"
folderNames = ["09_Spleen"]#, "09_Spleen"] 
folders = [folderStub+name for name in folderNames]
numbers      = [10]#, 10]
orientations = [1]#,1]
mngr = prepImageManager(10, numbers, orientations, folders, 80)
f = open("imgs_spleen10.pkl", "wb")
pickle.dump(mngr, f)
f.close()


# folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
# outputFolder = "trash"
# trainPaths = getDatasetInfo(folder)
# imgPath = trainPaths[0]["image"]
# img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
# img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
# imgOrig = np.copy(img)
# labelPath = trainPaths[0]["label"]
# label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
# label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
# label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig,
#                                                  9, 0,
#                                                  80, [0,0], randomized=True, process=None)


# imgPath = "/home/vincent/Documents/imperial/individual project/MedicalActiveCNN/nodeServer/server/clientPrint/"
# img_sitk = sitk.ReadImage("/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart/imagesTr/la_007.nii.gz")#imgPath+"img.nii.gz")
# labelPath = imgPath + "lbl.nii.gz"
# img = sitk.GetArrayFromImage(img_sitk)
# print(img[100][100][100], img[100][100][101])
# img = img.astype(np.float32)
# print(img[100][100][100], img[100][100][101])
# label_sitk = sitk.ReadImage(labelPath)
# label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
# print("EG", image[100][100][100], image[100][130][130])
# print(img.shape)
# seg = main(img, label, True)
# seg = np.asarray(np.around(seg), dtype=int)
# print(seg.shape, img.shape, label.shape)
# #writeNIFTI(img, outputFolder, "{}_actual".format(1))
# writeNIFTI(seg, imgPath, "{}_pred".format(1))
#writeNIFTI(label, outputFolder, "{}_truth".format(1))


# imgs, labels, info = getImages(folder, trainPaths[:1], 80, 1, True)[1]
# print(info[0]["path"])

# model = loadModel(1)
# result = model.predict(np.array(imgs))#, np.array(labels))

# for i, label in enumerate(result):
#     newLabel = np.argmax(label, axis=0)
#     newLabel2 = np.argmax(labels[i], axis=0)
#     print("dice:", tf.Session().run(weighted_dice_coefficient_loss(np.array(labels[i], dtype="float64"), np.array(result[i], dtype="float64"))))
#     writeNIFTI(newLabel, outputFolder, "{}_pred".format(i))
#     writeNIFTI(newLabel2, outputFolder, "{}_truth".format(i))
#     writeNIFTI(np.around(info[i]["imgOrig"]), outputFolder, "{}_actual".format(i))
#     writeNIFTI(imgs[i][0], outputFolder, "{}_processed".format(i))
