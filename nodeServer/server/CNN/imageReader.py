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

def readFunc(dataset, mode, params, crop=True):
    folder = params["folder"]
    for ID, dataPoint in enumerate(dataset):
        #print("Image {}/{}".format(ID+1, len(dataset)))
        # Read image
        imgPath = dataPoint["image"]
        img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
        img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        imgOrig = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        if (crop == True):
            # Only read label if training
            labelPath = dataPoint["label"]
            label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
            label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
            label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig, 9, 1, params["size"][0], randomized=True)
        else:
            #img = whitening(img)
            img = np.stack([img], axis=-1).astype(np.float32)

            # Pad images to the correct size
            size = params["depth"]
            diff = size - img.shape[0]
            if diff > 0:
                pad = math.floor(diff/2)
                paddings = tf.constant([[pad, pad], [0, 0], [0, 0], [0, 0]])
                img = tf.pad(img, paddings, "CONSTANT")
                if (diff % 2 == 1):
                    paddings = tf.constant([[1, 0], [0, 0], [0, 0], [0, 0]])
                    img = tf.pad(img, paddings, "CONSTANT")
                    img = tf.Session().run(img)
                img = resize3D(img, False, *params["size"])
                img = tf.Session().run(img)

        if (params["whiten"] == True):
            img = whitening(img)
            
        if mode == tf.estimator.ModeKeys.PREDICT:
            yield {'features': {'x': img},
                   'labels': None,
                   'sitk': img_sitk,
                   'subject_id': ID+1}
        else:
            if (crop == True):
                pass
            else:
                # Only read label if training
                labelPath = dataPoint["label"]
                label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
                label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
                #label = np.stack([label], axis=-1).astype(np.float32)
                diff = size - label.shape[0]
                if diff > 0:
                    pad = math.floor(diff/2)
                    paddings = tf.constant([[pad, pad], [0, 0], [0, 0]])
                    label = tf.pad(label, paddings, "CONSTANT")
                    if (diff % 2 == 1):
                        paddings = tf.constant([[1, 0], [0, 0], [0, 0]])
                        label = tf.pad(label, paddings, "CONSTANT")
                    label = tf.Session().run(label)
                #print(label.shape)
            catLabels = np.zeros(list(label.shape)+[2])
            #print(catLabels.shape)
            for i, row in enumerate(label):
                for j, col in enumerate(row):
                    for k, depth in enumerate(col):
                        #if (int(round(depth)) != 0):
                        #    print(int(round(depth)))
                        catLabels[i, j, k, int(round(depth))] = 1
                            
            #label = resize3D(label, False, *params["size"])
            #label = tf.Session().run(label)
            catLabels = resize3D(catLabels, False, *params["size"])
            catLabels = tf.Session().run(catLabels)
            if (crop == True):
                img = np.stack([img], axis=-1).astype(np.float32)
                img = resize3D(img, False, *params["size"])
                img = tf.Session().run(img)
                imgOrig = np.stack([imgOrig], axis=-1).astype(np.float32)
                imgOrig = resize3D(imgOrig, False, *params["size"])
                imgOrig = tf.Session().run(imgOrig)
            yield {'features': {'x': img},
                   'labels': {'y': catLabels},
                   'original': imgOrig,
                   'imgPath': imgPath,
                   'sitk': img_sitk,
                   'subject_id': ID+1}
    print("leaving reader")
    return


def getImages(folder, dataset, size, valFraction, nOrientations=1, augment=True, margins=[2,9], minMargins=[1,2]):
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
        if (augment == True and ID < valSplit):
            orientations = random.sample(range(0, 6), nOrientations)
        elif (augment == False and ID < valSplit):
            orientations = [True]*nOrientations
        elif (ID >= valSplit):
            orientations = [True]

        for orientationIndex, orientation in enumerate(orientations):
            print("Image {} orientation {}".format(ID, orientation))#, end="\r")
            info = {}
            imgPath = dataPoint["image"]
            info["path"] = imgPath
            img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
            img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
            imgOrig = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
            if (len(img.shape) > 3):
                img = img[0]
                imgOrig = imgOrig[0]
            maxVal = img.max()
            img /= maxVal
            imgOrig /= maxVal
            labelPath = dataPoint["label"]
            label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
            label = sitk.GetArrayFromImage(label_sitk).astype(np.int8)
            for i, row in enumerate(label):
                for j, col in enumerate(row):
                    for k, val in enumerate(col):
                        if (val > 1):
                            label[i,j,k] = 1
            label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig,
                                                             margins[1], margins[0],
                                                             size, minMargins, randomized=True)

            print("Original size", img.shape[0])

            resizeFactor = 1
            if (int(img.shape[0]) != size):
                resizeFactor = size / int(img.shape[0])
                img = zoom(img, resizeFactor, order=1, anti_aliasing=True, multichannel=False)
                imgOrig = zoom(imgOrig, resizeFactor, order=1, anti_aliasing=True, multichannel=False)
            img = whitening(img)
            #noise = np.random.normal(0, 0.1, img.shape)
            #img += noise
            img = np.stack([img], axis=-1)
            
            
            catLabels = np.zeros(list(label.shape)+[2])
            for i, row in enumerate(label):
                for j, col in enumerate(row):
                    for k, depth in enumerate(col):
                        catLabels[i, j, k, int(round(depth))] = 1
            catLabels = zoom(catLabels, [resizeFactor]*3, order=1, anti_aliasing=True,  multichannel=True)
            for i, row in enumerate(catLabels):
                for j, col in enumerate(row):
                    for k, depth in enumerate(col):
                        val = 0
                        if (depth[0] < depth[1]):
                            val = 1
                        catLabels[i, j, k, val] = 1
                        catLabels[i, j, k, (val+1)%2] = 0

            # img = np.stack([img], axis=-1).astype(np.float32)
            # img = resize3D(img, False, *shape)
            # img = tf.Session().run(img)
            # imgOrig = np.stack([imgOrig], axis=-1).astype(np.float32)
            # imgOrig = resize3D(imgOrig, False, *shape)
            # imgOrig = tf.Session().run(imgOrig)
        
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
                #print(img.shape, catLabels.shape)
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
