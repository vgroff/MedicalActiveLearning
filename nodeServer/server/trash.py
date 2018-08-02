from CNN.imageUtils import ImageManager, getDatasetInfo
#from CNN.train import getImages
from CNN.predict import writeNIFTI
from CNN.imageReader import readFunc
import SimpleITK as sitk
from CNN.imageUtils import cropToSeg

from CNN.model import weighted_dice_coefficient_loss

import os
import tensorflow as tf
import numpy as np

from main import main

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
outputFolder = "trash"
trainPaths = getDatasetInfo(folder)
imgPath = trainPaths[0]["image"]
img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
imgOrig = np.copy(img)
labelPath = trainPaths[0]["label"]
label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig,
                                                 0, 9,
                                                 80, [0,0], randomized=True, process=None)
seg = main(img, label, True)
seg = np.asarray(np.around(seg), dtype=int)
print(seg)
