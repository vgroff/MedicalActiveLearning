








##
## This file is for code scraps and for testing stuff
##
from imageUtils import DataManager, getDatasetInfo
from train import getImages
from predict import writeNIFTI
from imageReader import readFunc

import os
import tensorflow as tf 

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
size = [64, 64, 64] # 32,80,80

trainPaths = getDatasetInfo(folder)
imgs = []
labels = []
i = 0
for img in readFunc(trainPaths[19:20], None,
                    {"folder":folder, "depth":132, "size":size, "whiten":True}):
    
