import tensorflow as tf
import numpy as np
import json
import os, inspect
import random



class ImageManager():
    def __init__(self, data):
        self.trainImgs    = data[0][0]
        self.trainLabels  = data[0][1]
        self.trainImgInfo = data[0][2]
        self.valImgs      = data[1][0]
        self.valLabels    = data[1][1]
        self.valImgInfo   = data[1][2]

    def getTrainImages(self, start=0, size=None):
        if size == None:
            size = len(self.trainImgs)
        return self.trainImgs[start:start+size], self.trainLabels[start:start+size], self.trainImgInfo[start:start+size]

    def getValImages(self, start=0, size=None):
        if size == None:
            size = len(self.valImgs)
        return self.valImgs[start:start+size], self.valLabels[start:start+size], self.valImgInfo[start:start+size]

    def addData(self, data):
        self.trainImgs    += data[0][0]
        self.trainLabels  += data[0][1]
        self.trainImgInfo += data[0][2]
        self.valImgs      += data[1][0]
        self.valLabels    += data[1][1]
        self.valImgInfo   += data[1][2]

    def save(self, name):
        f = open(path, "wb")
        pickle.dump(mngr, f)
        f.close()

def pathImgMngr(name):
    path = os.path.dirname(os.path.abspath(inspect.stack()[0][1])) 
    return path + "/" + name + "_img.pkl"


def getDatasetInfo(folder):
    with open(os.path.join(folder, "dataset.json")) as f:
        data = json.load(f)
    return data["training"]


def splitArr(arr, fraction):
    arr1 = []
    arr2 = []
    length = len(arr)
    for i in range(length):
        if (i < length*fraction):
            arr1.append(arr[i])
        else:
            arr2.append(arr[i])
    return arr1, arr2


def cropToSeg(labels, image, imageOrig, margin,  minMargin=1, minSize=0, minPadding=[0,0], randomized=False, process="cubePadding"):
    rowBounds   = [labels.shape[0],-1]
    colBounds   = [labels.shape[1],-1]
    depthBounds = [labels.shape[2],-1]
    rowMarginBounds = [labels.shape[0],0]
    colMarginBounds = [labels.shape[1],0]
    depthMarginBounds = [labels.shape[2],0]
    if randomized == True:
        rowMargin = [int((margin - minMargin+1)*random.random()) for i in range(2)]
        colMargin = [int((margin - minMargin+1)*random.random()) for i in range(2)]
        depthMargin = [int((margin - minMargin+1)*random.random()) for i in range(2)]
    else:
        rowMargin = [margin, margin]
        colMargin = [margin, margin]
        depthMargin = [margin, margin]
    for row, cols in enumerate(labels):
        for col, depths in enumerate(cols):
            for depth, val in enumerate(depths):
                if (labels[row, col, depth] != 0):
                    if row < rowBounds[0]:
                        rowBounds[0] = row
                        rowMarginBounds[0] = row - rowMargin[0]
                        if rowMarginBounds[0] < 0:
                            rowMarginBounds[0] = 0
                    if row > rowBounds[1]:
                        rowBounds[1] = row
                        rowMarginBounds[1] = row + rowMargin[1]
                        if rowMarginBounds[1] > labels.shape[0]:
                            rowMarginBounds[1] = labels.shape[0]
                    if col < colBounds[0]:
                        colBounds[0] = col
                        colMarginBounds[0] = col - colMargin[0]
                        if colMarginBounds[0] < 0:
                            colMarginBounds[0] = 0
                    if col > colBounds[1]:
                        colBounds[1] = col
                        colMarginBounds[1] = col + colMargin[1]
                        if colMarginBounds[1] > labels.shape[1]:
                            colMarginBounds[1] = labels.shape[1]
                    if depth < depthBounds[0]:
                        depthBounds[0] = depth
                        depthMarginBounds[0] = depth - depthMargin[0]
                        if depthMarginBounds[0] < 0:
                            depthMarginBounds[0] = 0
                    if depth > depthBounds[1]:
                        depthBounds[1] = depth
                        depthMarginBounds[1] = depth + depthMargin[1]
                        if depthMarginBounds[1] > labels.shape[2]:
                            depthMarginBounds[1] = labels.shape[2]
    labels = labels[rowMarginBounds[0]:rowMarginBounds[1]+1,
                    colMarginBounds[0]:colMarginBounds[1]+1,
                    depthBounds[0]:depthMarginBounds[1]+1]
    image = image[rowMarginBounds[0]:rowMarginBounds[1]+1,
                  colMarginBounds[0]:colMarginBounds[1]+1,
                  depthBounds[0]:depthMarginBounds[1]+1]
    imageOrig = imageOrig[rowMarginBounds[0]:rowMarginBounds[1]+1,
                          colMarginBounds[0]:colMarginBounds[1]+1,
                          depthBounds[0]:depthMarginBounds[1]+1]

    if process=="cubePadding":
        if (max(image.shape) > minSize):
                # If the image is already larger than the minimum size,
                # pad largest edge with randomized min padding
                minSize = int(round((minPadding[1] - minPadding[0]) * random.random() + minPadding[0] + minSize))
        image, padding = cubePadding(image, minSize)
        labels = cubePadding(labels, minSize)[0]
        imageOrig = cubePadding(imageOrig, minSize)[0]
    elif process=="softPadding":
        image, padding = softPadding(image)
        labels = softPadding(labels)[0]
        imageOrig = softPadding(imageOrig)[0]
    else:
        padding = []
    return labels, image, imageOrig, [rowMarginBounds, colMarginBounds, depthMarginBounds], padding


def cubePadding(image, minCubeLength):
    maxSize = max(image.shape)
    if (maxSize < minCubeLength):
        maxSize = minCubeLength
    padding = [[(maxSize - image.shape[0])//2, (maxSize - image.shape[0] + 1)//2],
               [(maxSize - image.shape[1])//2, (maxSize - image.shape[1] + 1)//2],
               [(maxSize - image.shape[2])//2, (maxSize - image.shape[2] + 1)//2]]
    image = tf.pad(image, padding, "CONSTANT")
    image = tf.Session().run(image)
    return image, padding

def softPadding(image, vals=[32, 64, 80, 96, 112, 128,
                             155, 160, 176, 192, 224, 256, 288,
                             352, 384, 448, 512]):
    newShape = [0,0,0]
    for index, shape in enumerate(image.shape):
        if (shape < vals[0]):
            newShape[index] = vals[0]
            continue
        for i, val in enumerate(vals):
            if (shape >= val and shape <= vals[i+1]):
                if shape == val:
                    newShape[index] = val
                else:
                    newShape[index] = vals[i+1]
                continue
    padding = [[(newShape[0] - image.shape[0])//2, (newShape[0] - image.shape[0] + 1)//2],
               [(newShape[1] - image.shape[1])//2, (newShape[1]- image.shape[1] + 1)//2],
               [(newShape[2] - image.shape[2])//2, (newShape[2] - image.shape[2] + 1)//2]]
    image = tf.pad(image, padding, "CONSTANT")
    image = tf.Session().run(image)
    return image, padding
    
def unpad(image, bounds):
    rowMarginBounds = bounds[0]
    colMarginBounds = bounds[1]
    depthMarginBounds = bounds[2]
    image = image[rowMarginBounds[0]:rowMarginBounds[1]+1,
                  colMarginBounds[0]:colMarginBounds[1]+1,
                  depthBounds[0]:depthMarginBounds[1]+1]
    return image

def toCategorical(label):
    catLabels = np.zeros(list(label.shape)+[2])
    #print(catLabels.shape)
    for i, row in enumerate(label):
        for j, col in enumerate(row):
            for k, depth in enumerate(col):
                catLabels[i, j, k, int(round(depth))] = 1
    catLabels = resize3D(catLabels, False, *params["size"])
    catLabels = tf.Session().run(catLabels)
    return catLabels

def resize_by_axis(image, dim_1, dim_2, ax, is_grayscale):

    resized_list = []


    if is_grayscale:
        unstack_img_depth_list = [tf.expand_dims(x,2) for x in tf.unstack(image, axis = ax)]
        for i in unstack_img_depth_list:
            resized_list.append(tf.image.resize_images(i, [dim_1, dim_2],method=0))
        stack_img = tf.squeeze(tf.stack(resized_list, axis=ax))

    else:
        unstack_img_depth_list = tf.unstack(image, axis = ax)
        for i in unstack_img_depth_list:
            resized_list.append(tf.image.resize_images(i, [dim_1, dim_2],method=0))
        stack_img = tf.stack(resized_list, axis=ax)

    return stack_img

def resize3D(image, grayscale, rows, cols, depth):
    resized_along_depth = resize_by_axis(image, rows, cols, 2, grayscale)
    resized_along_width = resize_by_axis(resized_along_depth, rows, depth, 1, grayscale)
    return resized_along_width

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
#tf.logging.set_verbosity(tf.logging.ERROR)
#os.environ["CUDA_VISIBLE_DEVICES"] = '0'
#import numpy as np
#a = np.array([
#    np.array([ np.array([0,0,0]), np.array([0,0,0]), np.array([0,0,0]) ]),
#    np.array([ np.array([0,0,0]), np.array([0,1,0]), np.array([0,0,0]) ]),
#    np.array([ np.array([0,1,0]), np.array([1,1,0]), np.array([0,0,0]) ]),
#    np.array([ np.array([0,0,0]), np.array([0,0,0]), np.array([0,0,0]) ])
#               ])
#print(a.shape)
#b = cropToSeg(a, 1, minMargin=0, randomized=True)
#print(b, b.shape)
