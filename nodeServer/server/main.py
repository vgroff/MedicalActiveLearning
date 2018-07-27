import sys, json
import numpy as np

from graphCuts import graphCut


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

def buildProbsArr(img, label):
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
    

def main(img, label):

    #print("Converting lists to arrays...")
    img   = listsToArray(img)
    label = listsToArray(label)
    #print("Converted img to shape {} and label to shape {}".format(img.shape, label.shape))
    #print("Building probs array...")
    probs, stdDev = buildProbsArr(img, label)
    #print("Doing graph cut with stdDev {} ....".format(stdDev))
    seg = graphCut(img, probs, stdDev)
    #print("Graph cuts complete.")
    
    return seg

#start process
if __name__ == '__main__':
    #img = json.loads(sys.argv[1])
    #label = json.loads(sys.argv[2])
    #print("Loading data from std in...")
    
    lines = sys.stdin.readlines()
    img = json.loads(lines[0][:-1])
    label = json.loads(lines[1])
    seg = main(img, label)
    seg = seg.astype(int)
    np.set_printoptions(threshold=np.nan)
    print(np.array2string(seg, separator=", "))
    print("Done")

# Something weird is going on. Reducing the edge coefficient to zero produces the best results, but it should be helping out. Is the formula incorrect? Do we use another std.dev? Play around and see.
    
# To-do:
# - Get a nice unwhitened 3-D image
# - Test it out :|

# 73AAE9D75A7CFCD732DC359F26

    # img = np.array([
    #     np.array([np.array([0.80,0.85,0.90,0.80]),
    #               np.array([0.90,0.80,0.90,0.85]),
    #               np.array([0.75,0.85,0.76,0.85]),
    #               np.array([0.85,0.85,0.80,0.80])]),
        
    #     np.array([np.array([0.85,0.80,0.25,0.20]),
    #               np.array([0.90,0.75,0.20,0.20]),
    #               np.array([0.85,0.90,0.65,0.65]),
    #               np.array([0.85,0.80,0.60,0.65])]),
        
    #     np.array([np.array([0.45,0.35,0.20,0.23]),
    #               np.array([0.40,0.32,0.42,0.45]),
    #               np.array([0.35,0.35,0.55,0.65]),
    #               np.array([0.35,0.31,0.55,0.55])]),
        
    #     np.array([np.array([0.10,0.10,0.20,0.17]),
    #               np.array([0.15,0.15,0.25,0.12]),
    #               np.array([0.05,0.10,0.55,0.65]),
    #               np.array([0.10,0.05,0.56,0.60])])
    #     ])
    # label = np.array([
    #     np.array([np.array([1,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,1,0,0])]),
        
    #     np.array([np.array([0,0,2,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,1]),
    #               np.array([0,0,0,0])]),
        
    #     np.array([np.array([0,0,0,2]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0])]),
        
    #     np.array([np.array([0,0,0,2]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,2,0]),
    #               np.array([0,0,0,0])])
    # ])
