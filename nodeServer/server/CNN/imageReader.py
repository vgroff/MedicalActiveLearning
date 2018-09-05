import SimpleITK as sitk
import tensorflow as tf
import numpy as np
import os
import math
import random
#from scipy.ndimage import zoom
from skimage.transform import rescale as zoom

from dltk.io.preprocessing import whitening

from imageUtils import resize3D, cropToSeg

# Reads images from folder of given dataset for training/validation
def getImages(folder, dataset, size, valFraction, nOrientations=1, pad="cubePadding", augment=True, margins=[2,9], minMargins=[1,2]):
    shape      = [size]*3
    trImgs     = []
    trLabels   = []
    trImgInfo  = []
    valImgs    = []
    valLabels  = []
    valImgInfo = []
    valSplit   = int(round((1-valFraction)*len(dataset)))
    print("Training on {}, validating on {}".format(valSplit, len(dataset) - valSplit))
    
    for ID, dataPoint in enumerate(dataset):
        # Orientations for augmentation
        if (augment == True and ID < valSplit):
            orientations = random.sample(range(0, 6), nOrientations)
        elif (augment == False and ID < valSplit):
            orientations = [True]*nOrientations
        elif (ID >= valSplit):
            orientations = [True]

        for orientationIndex, orientation in enumerate(orientations):
            print("Image {} orientation {}".format(ID, orientation))#, end="\r")
            info = {}
            # Get path and store it
            imgPath = dataPoint["image"]
            info["path"] = imgPath
            # Read in image and normalise it 0-1
            img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
            img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
            imgOrig = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
            if (len(img.shape) > 3):
                img = img[0]
                imgOrig = imgOrig[0]
            maxVal = img.max()
            img /= maxVal
            imgOrig /= maxVal
            # Read in label and make all labels > 1 = 1
            labelPath = dataPoint["label"]
            label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
            label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
            label[label > 1] = 1
            label = np.rint(label)
            # Crop a bounding box around area of interest
            label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig,
                                                             margins[1], margins[0],
                                                             size, minMargins, randomized=True,
                                                             process="softPadding")

            print("Original shape", img.shape, padding)
            if (size != None):
                resizeFactor = 1
                if (int(img.shape[0]) != size):
                    resizeFactor = size / int(img.shape[0])
                    img = zoom(img, resizeFactor, order=1, anti_aliasing=True, multichannel=False)
                    imgOrig = zoom(imgOrig, resizeFactor, order=1, anti_aliasing=True, multichannel=False)

            # Normalise to mean = 0 std dev = 1
            img = whitening(img)
            #noise = np.random.normal(0, 0.1, img.shape)
            #img += noise
            img = np.stack([img], axis=-1)
            
            # Turn labels to categorical
            catLabels = np.zeros(list(label.shape)+[2])
            for i, row in enumerate(label):
                for j, col in enumerate(row):
                    for k, depth in enumerate(col):
                        catLabels[i, j, k, int(round(depth))] = 1
            if (size != None):
                catLabels = zoom(catLabels, [resizeFactor]*3, order=1, anti_aliasing=True,  multichannel=True)
                for i, row in enumerate(catLabels):
                    for j, col in enumerate(row):
                        for k, depth in enumerate(col):
                            val = 0
                            if (depth[0] < depth[1]):
                                val = 1
                            catLabels[i, j, k, val] = 1
                            catLabels[i, j, k, (val+1)%2] = 0


            # Move axis because need channels first
            if (augment == False and ID < valSplit):
                img = np.moveaxis(img, 3, 0)
                catLabels = np.moveaxis(catLabels, 3, 0)
                info["imgOrig"] = imgOrig
                trImgs.append(img)
                trLabels.append(catLabels)
                trImgInfo.append(info)
            elif (ID >= valSplit):
                img = np.moveaxis(img, 3, 0)
                catLabels = np.moveaxis(catLabels, 3, 0)
                info["imgOrig"] = imgOrig
                valImgs.append(img)
                valLabels.append(catLabels)
                valImgInfo.append(info)
            else:
                newImg = img
                newCatLabels = catLabels
                if (orientation == 0):
                    pass
                elif (orientation == 1 or orientation == 2):
                    newImg = np.moveaxis(newImg, orientation, 0)
                    newCatLabels = np.moveaxis(newCatLabels, orientation, 0)
                    imgOrig = np.moveaxis(imgOrig, orientation, 0)
                elif (orientation == 3):
                    newImg = np.moveaxis(newImg, 0, 2)
                    newCatLabels = np.moveaxis(newCatLabels, 0, 2)
                    imgOrig = np.moveaxis(imgOrig, 0, 2)
                elif (orientation == 4):
                    newImg = np.swapaxes(newImg, 2, 1)
                    newCatLabels = np.swapaxes(newCatLabels, 2, 1)
                    imgOrig = np.swapaxes(imgOrig, 2, 1)
                elif (orientation == 5):
                    newImg = np.swapaxes(newImg, 0, 2)
                    newCatLabels = np.swapaxes(newCatLabels, 0, 2)
                    imgOrig = np.swapaxes(imgOrig, 0, 2)
                for i in range(3):
                    if (random.random() > 0.5):
                        newImg = np.flip(newImg, axis=i)
                        newCatLabels = np.flip(newCatLabels, axis=i)
                        imgOrig = np.flip(imgOrig, axis=i)
                newImg = np.moveaxis(newImg, 3, 0)
                newCatLabels = np.moveaxis(newCatLabels, 3, 0)
                #print(newImg.shape, newCatLabels.shape)
                info["imgOrig"] = imgOrig
                trImgs.append(newImg)
                trLabels.append(newCatLabels)
                trImgInfo.append(info)
    return [ [trImgs, trLabels, trImgInfo], [valImgs, valLabels, valImgInfo] ]
    


# 
