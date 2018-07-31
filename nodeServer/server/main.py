import sys, json, os
import numpy as np
import tensorflow as tf
from graphCuts import graphCut
from CNN.imageUtils import cubePadding, resize3D, toCategorical
from CNN.cnnUtils import loadModel

from dltk.io.preprocessing import whitening


def listsToArray(lists):
    if (isinstance(lists, list)):
        arr = []
        for l in lists:
            arr.append(listsToArray(l))
        arr = np.array(arr)
        return arr
    else:
        return lists

def gaussian(x, mean, stdDev):
    coeff = (1/(stdDev*(2*np.pi)**0.5))
    return np.exp( - (x-mean)**2/(2*stdDev**2) ) 

def buildGaussProbs(img, label):
    shape = label.shape
    arr = np.zeros(list(label.shape) + [2])
    sumArr = [0,0]
    sumSqArr = [0,0]
    counts = [0,0]
    sumInt = 0
    sumSqInt = 0
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                sumInt   += img[i,j,k]
                sumSqInt += img[i,j,k]**2
                if (label[i,j,k] != 0):
                    arr[i,j,k,0] = -label[i,j,k]
                    arr[i,j,k,1] = -label[i,j,k]
                    index = abs(label[i,j,k] - 2)
                    sumArr[index] += img[i,j,k]
                    sumSqArr[index] += img[i,j,k]**2
                    counts[index] += 1
    total  = shape[0]*shape[1]*shape[2]
    stdDev = (sumSqInt/total - (sumInt/total)**2)**0.5
    means = [(sumArr[i]/counts[i]) for i in range(len(counts))]
    stdDevs = [(sumSqArr[i]/counts[i] - (sumArr[i]/counts[i])**2)**0.5 for i in range(len(counts))]
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                if (label[i,j,k] == 0):
                    arr[i,j,k,0] = gaussian(img[i,j,k], means[0], stdDevs[0])
                    #if (arr[i,j,k,0] > 1):
                    #    print(img[i,j,k])
                    arr[i,j,k,1] = gaussian(img[i,j,k], means[1], stdDevs[1])
                    
    #print(sumInt/total, stdDev)
    #print(means,stdDevs)
    return arr, stdDev
    

def main(img, label, cnn=True):

    img   = listsToArray(img)
    label = listsToArray(label)
    
    if (cnn == True):
        cnnSize = 64
        shape = [cnnSize]*3
        img, padding = cubePadding(img, cnnSize)
        label, padding = cubePadding(label, cnnSize)
        img = whitening(img)
        img = np.stack([img], axis=-1).astype(np.float32)
        img = resize3D(img, False, *shape)
        img = tf.Session().run(img)
        img = np.moveaxis(img, 3, 0)
        print("HEYHEY", img.shape, file=sys.stderr)
        #img = np.swapaxes(img, 0,3)
        #print(img[0][24][25][26])
        #return label
        #catLabels = toCategorical(label)
        #catLabels = resize3D(catLabels, False, *shape)
        #catLabels = tf.Session().run(catLabels)
        model = loadModel(1)
        result = model.predict(np.array([img]))
        #result = np.swapaxes(result[0], 0, 3)
        print("HEYHEY", result.shape, file=sys.stderr)
        result = np.argmax(result[0], axis=0)
        return result
    else:
        probs, stdDev = buildGaussProbs(img, label)
        seg = graphCut(img, probs, stdDev)
        return seg

#start process
if __name__ == '__main__':
    #img = json.loads(sys.argv[1])
    #label = json.loads(sys.argv[2])
    #print("Loading data from std in...")
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    
    action = sys.argv[1]
    lines = sys.stdin.readlines()
    img = json.loads(lines[0][:-1])
    label = json.loads(lines[1])
    
    if action == "cnnSeg":
        cnn = True
    elif action == "graphCuts":
        cnn = False
    seg = main(img, label, cnn)
    seg = seg.astype(int)
    np.set_printoptions(threshold=np.nan)
    print(np.array2string(seg, separator=", "))
    print("Done")

# Notes:
# - Need a better CNN...

# TO-DO:
# - Send pic to CNN, then correct with graph cuts. Need to pad+resize and unresize+unpad images from CNN result back to "normal" image. Write a generic pad+resize function that takes the size as an argument - only resize if need be, otherwise pad - (shortened version of cropToSeg - fix that too) but save the original start and end indices so that it can be undone - test it all. 



