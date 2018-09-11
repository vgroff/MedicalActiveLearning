



from cnnUtils import loadModel
# # from imageUtils import getDatasetInfo

# import pickle

# # from predict import writeNIFTI

# # from imageReader import getImages

# from imageUtils import ImageManager, getDatasetInfo
# # from train import getImages
# # from predict import writeNIFTI
# # from imageReader import readFunc
# # import SimpleITK as sitk
# # from imageUtils import cropToSeg

# # from model import weighted_dice_coefficient_loss

# # import os
# # import tensorflow as tf
# # import numpy as np

# # from main import main

# from keras import activations
# from keras.models import *
# from keras.layers import *
# from train import prepImageManager
# ##
# ## This file is for code scraps and for testing stuff
# ##

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# tf.logging.set_verbosity(tf.logging.ERROR)
# os.environ["CUDA_VISIBLE_DEVICES"] = '0'

#model = loadModel(1)

# folderStub = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task"
# folderNames = ["09_Spleen"]#, "09_Spleen"] 
# folders = [folderStub+name for name in folderNames]
# numbers      = [10]#, 10]
# orientations = [1]#,1]
# mngr = prepImageManager(10, numbers, orientations, folders, 80)

# f = open("imgs.pkl", "rb")
# mngr = pickle.load(f)
# f.close()

# f = open("General_img.pkl", "wb")
# pickle.dump(mngr, f)
# f.close()

# imgs, labels, info = mngr.getTrainImages()
# valImgs, valLabels, valInfo = mngr.getValImages()
# trStart = 0
# trEnd = 15
# valStart = 0
# valEnd   = 5
# imgs, labels, info =  [imgs[trStart:trEnd], labels[trStart:trEnd], info[trStart:trEnd]]
# valImgs, valLabels, valInfo =  [valImgs[valStart:valEnd], valLabels[valStart:valEnd], valInfo[valStart:valEnd]]
# mngr = ImageManager([[imgs,labels,info],[valImgs,valLabels,valInfo]])
# f = open("Heart_img.pkl", "wb")
# pickle.dump(mngr, f)
# f.close()

# from cnnUtils import loadModel, saveModel
# model = loadModel(1)
# print(model.summary())

from imageUtils import getDatasetInfo
from skimage.transform import rescale as zoom
from predict import writeNIFTI
import SimpleITK as sitk
import os
import numpy as np

def writeNIFTI(arr, folder, name, meta, vals):
    new_sitk = sitk.GetImageFromArray(arr)
    for i, m in enumerate(meta):
        new_sitk.SetMetaData(m, vals[i])
    for m in meta:
        print(new_sitk.GetMetaData(m))
    #new_sitk.CopyInformation(copy)
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)


def writeNIFTI2(arr, folder, name):#, copy):
    new_sitk = sitk.GetImageFromArray(arr)
    #new_sitk.CopyInformation(copy)
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)

def writeNIFTI3(img, folder, name):
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(img, path)

folder=  "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task09_Spleen"
dataset = getDatasetInfo(folder )
dataPoint = dataset[0]
imgPath = dataPoint["image"]
labelPath = dataPoint["label"]
#info["path"] = imgPath
# Read in image and normalise it 0-1
img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
maxVal = img.max()
img /= maxVal
img = zoom(img, 0.5, order=1, anti_aliasing=True, multichannel=False)
img *= maxVal
label[label > 1] = 1
label = zoom(label, 0.5, order=1, anti_aliasing=True, multichannel=False)
label = np.rint(label).astype(np.int8)
#metaData = ["pixDims[0]", "pixDims[1]", "pixDims[2]", "pixDims[3]"]
#vals = ["1", "0.79", "0.79", "5"]

#metaData = ["pixdim[{}]".format(i) for i in range(8)]
#vals = []
#for meta in metaData:
#    vals.append(img_sitk.GetMetaData(meta))
#print(vals)

writeNIFTI2(img, "SpleensWhole", "img")
writeNIFTI2(label, "SpleensWhole", "label")

#print(img.shape)
#filt = sitk.ResampleImageFilter()
#filt.SetSize([256,256,26])
#img = filt.Execute(img_sitk)
#img = sitk.GetArrayFromImage(img).astype(np.float32)
#print(img.shape)
#writeNIFTI3(img, "SpleensWhole", "img")

# metaData = ["dim[{}]".format(i) for i in range(4)]
# vals = ["1", str(img.shape[0]), str(img.shape[1]), str(img.shape[2])]
# for i, meta in enumerate(metaData):
#     print(img_sitk.GetMetaData(meta), vals[i])
#     img_sitk.SetMetaData(meta, vals[i])
#     #vals.append(img_sitk.GetMetaData(meta))
# print(vals)

# writeNIFTI2(img, "SpleensWhole", "img", img_sitk)
# writeNIFTI2(label, "SpleensWhole", "label", img_sitk)

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
