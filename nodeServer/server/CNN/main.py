import sys, json, os
import numpy as np
import tensorflow as tf
from graphCuts import graphCut
from imageUtils import cubePadding, resize3D, toCategorical
from cnnUtils import loadModel
from scipy.ndimage import zoom


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
        cnnSize = 80
        shape = [cnnSize]*3
        img, padding = cubePadding(img, cnnSize)
        label, padding = cubePadding(label, cnnSize)
        size = img.shape[0]
        img = whitening(img)
        resizeFactor = cnnSize / size
        img = zoom(img, resizeFactor)
        img = np.stack([img], axis=0).astype(np.float32)
        #img = np.moveaxis(img, 3, 0)

        #catLabels = toCategorical(label)
        #catLabels = resize3D(catLabels, False, *shape)
        #catLabels = tf.Session().run(catLabels)

        model = loadModel(1)
        result = model.predict(np.array([img]))
        result = np.argmax(result[0], axis=0)
        print("NUM OBJECT PIX:", np.count_nonzero(result == 1), file=sys.stderr)
        #result = np.moveaxis(result, 3, 0)
        result = zoom(result, 1/resizeFactor)
        #result = result[0]
        result = result[ padding[0][0] : int(result.shape[0]) - padding[0][1],
                         padding[1][0] : int(result.shape[1]) - padding[1][1],
                         padding[2][0] : int(result.shape[2]) - padding[2][1]]
        
        print("NUM OBJECT PIX:", np.count_nonzero(result == 1), file=sys.stderr)
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
    seg = np.asarray(np.around(seg), dtype=int)
    np.set_printoptions(threshold=np.nan)
    print(np.array2string(seg, separator=", "))
    print("Done")

# Notes:
# - Getting shitty results still - try in trash.py?
# - 



