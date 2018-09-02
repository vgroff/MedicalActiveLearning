import sys, json, os, inspect
import numpy as np
import tensorflow as tf
#from graphCuts import graphCut
from imageUtils import cubePadding, softPadding, resize3D, toCategorical
from cnnUtils import loadModel
#from scipy.ndimage import zoom
from skimage.transform import rescale as zoom
import queue
from time import process_time as time
import pickle

from train import quickTrain
from namesdb import NamesDatabase

from dltk.io.preprocessing import whitening

import gridCut3D

import SimpleITK as sitk

from model import weighted_dice_coefficient_loss, weightedDiceLoss

#from skimage.transform import rescale as zoom


def writeNIFTI(arr, folder, name):
    new_sitk = sitk.GetImageFromArray(arr.astype(np.int32))
    #new_sitk.CopyInformation(original['sitk'])
    path = os.path.join(folder, "{}.nii.gz".format(name))
    sitk.WriteImage(new_sitk, path)



def listsToArray(lists):
    return np.array(lists)
    if (isinstance(lists, list) or isinstance(lists, tuple)):
        arr = []
        for l in lists:
            arr.append(listsToArray(l))
        arr = np.array(arr)
        return arr
    else:
        return lists

def arrayToLists(arrays):
    return arrays.tolist()
    if (isinstance(arrays, np.ndarray)):
        l = []
        for arr in arrays:
            l.append(arrayToLists(arr))
        l = list(l)
        return l
    else:
        return float(arrays)
    
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

def updateGeodesics(maxPathLength, stdDev, minEdge, img, probs, segmentation, weighting):
    # BFS with geodesic distances up to a certain distance
    qs = [queue.Queue(), queue.Queue()]
    nums = [0, 0]
    for i, row in enumerate(probs[0]):
        for j, col in enumerate(row):
            for k, val in enumerate(col):
                if (val < 0):
                    index = int(round(val))+2
                    qs[index].put([i,j,k])
                    nums[index] += 1
    directions = [ [1,0,0], [-1,0,0], [0,1,0], [0,-1,0], [0,0,1], [0,0,-1] ]
    c = 0
    for index in [0,1]:
        pathLengths = np.full(img.shape, fill_value=-1.0)
        computedPathLengths = np.full(img.shape, fill_value=-1.0)
        q = qs[index]
        while not q.empty():
            coords = q.get()

            row, col, depth = coords
            currPathLength = pathLengths[row, col, depth]
            # The if statement below is mean to skip over things in the queue that we have already computed
            if (computedPathLengths[row, col, depth] >= 0 and
                abs(currPathLength - computedPathLengths[row, col, depth]) < 0.0001):
                # If weve got a path length saved and it is the same as the current path length
                continue
            else:
                # Save path length
                if (currPathLength < 0):
                    currPathLength = 0
                computedPathLengths[row,col,depth] = currPathLength
            for direction in directions:
                # Go in every direction
                try:
                    newRow = row+direction[0]
                    newCol = col+direction[1]
                    newDepth = depth+direction[2]
                    if (newRow < 0 or newCol < 0 or newDepth < 0):
                        # Dont go to negative indices
                        continue
                    otherVal = segmentation[newRow, newCol, newDepth]
                    if (probs[0, newRow, newCol, newDepth] >= 0):# and index != otherVal:
                        # If this is a normal (non-scrible) and it has the opposite marking - does it need to have the opposite marking? Defeats the purpose maybe
                        i1 = img[row, col, depth]
                        i2 = img[newRow, newCol, newDepth]
                        length = 1 - np.exp(-(i2 - i1)**2/(2*stdDev**2)) + minEdge
                        newPathLength = currPathLength + length
                        if (newPathLength > maxPathLength):
                            # If weve gone over the maximum path length, abandon
                            continue
                        destPathLength = pathLengths[newRow, newCol, newDepth]
                        if (newPathLength < destPathLength*0.8
                            or newPathLength < destPathLength - 0.05
                            or destPathLength < 0):
                            # If weve made a shorter path, save it and place in queue
                            q.put([newRow, newCol, newDepth])
                            pathLengths[newRow, newCol, newDepth] = newPathLength
                            if index != otherVal:
                                weighting[0, newRow, newCol, newDepth] = 0
                                weighting[1, newRow, newCol, newDepth] = 0
                except IndexError as e:
                    pass
                    #print(e)
                    #print("{},{},{} out of bounds for array shape {}".format(newRow,newCol,newDepth, pathLengths.shape))
            nums[index] -=1

        
    
def buildWeightArr(img, segmentation, probs, distanceLim=0.3, stdDev=0.1, minProb1=0.6, minProb2=0.6, scribbleWeight=40):
    weightArr = np.ones(probs.shape)
    scribbles = [[], []]
    mask = probs[0] < 0
    weightArr[0][mask] = scribbleWeight
    weightArr[1][mask] = scribbleWeight
    mask = ( (probs[0] > 0.5) & (probs[0] < minProb1)) | ((probs[1] > 0.5) & (probs[1] < minProb2))
    weightArr[0][mask] = 0
    weightArr[1][mask] = 0
    # for i, row in enumerate(probs[0]):
    #     for j, col in enumerate(row):
    #         for k, val in enumerate(col):
    #             if val < 0:
    #                 weightArr[0,i,j,k] = scribbleWeight
    #                 weightArr[1,i,j,k] = scribbleWeight
    #             else:
    #                 probs1 = probs[0,i,j,k]
    #                 probs2 = probs[1,i,j,k]
    #                 if (probs2 > 0.5 and probs2 < minProb2):
    #                     weightArr[0,i,j,k] = 0
    #                     weightArr[1,i,j,k] = 0
    #                 if (probs1 > 0.5 and probs1 < minProb1):
    #                     weightArr[0,i,j,k] = 0
    #                     weightArr[1,i,j,k] = 0
    updateGeodesics(0.25, 0.12, 0, img, probs, segmentation, weightArr)
    return weightArr
                    

def graphCuts(segImg, probs, edgeCoeff, stdDev, gridCuts, maxVal=None):
    if (gridCuts == True):
        if (maxVal == None):
            maxVal = float((26 * edgeCoeff) + 1)
        regTerms = []
        softening = 1e-8
        regTerms = np.zeros(probs.shape)
        regTerms = -np.log(probs+softening)
        regTerms[regTerms < 0] = 0
        regTerms = np.flip(regTerms,axis=0)
        regTerms[0][probs[0] == -2] = maxVal
        regTerms[1][probs[0] == -2] = 0
        regTerms[0][probs[0] == -1] = 0
        regTerms[1][probs[0] == -1] = maxVal
        regTerms = regTerms.tolist()
        regTermsVec = gridCut3D.CatVolume()
        regTermsVec = regTerms
        segImgVol   = gridCut3D.Volume()
        segImgVol   = segImg
        seg = gridCut3D.Volume()
        seg = listsToArray(gridCut3D.gridCut3D(segImgVol, regTermsVec, edgeCoeff, stdDev))
    else:
        seg = graphCut(segImg, probs, edgeCoeff, stdDev)
    return seg
    

def main(imgOrig, labelOrig, model, cnn=True, doGraphCuts=True, BIFSeg=True):

    totalTime = time()
    manipTime = 0
    graphTime = 0
    predictTime = 0
    trainTime = 0
    loadTime  = 0

    t = time()
    imgOrig   = listsToArray(imgOrig)
    labelOrig = listsToArray(labelOrig)

    
    if (cnn == True):
        cnnSize = 80
        shape = [cnnSize]*3
        img, padding = softPadding(imgOrig)
        label, padding = softPadding(labelOrig)
        size = img.shape[0]
        resizeFactor = cnnSize / size
        img = whitening(img)
        img = np.stack([img], axis=0).astype(np.float32)
        manipTime += time() - t

        t = time()
        result = model.predict(np.array([img]))
        predictTime += time() - t
        
        if doGraphCuts == False:
            result = zoom(result[0], [1] + [1/resizeFactor]*3, order=1, multichannel=False )
            result = np.argmax(result, axis=0)

            result = result[ padding[0][0] : int(result.shape[0]) - padding[0][1],
                             padding[1][0] : int(result.shape[1]) - padding[1][1],
                             padding[2][0] : int(result.shape[2]) - padding[2][1]]
            return result
        else:
            # Resize probs.
            t = time()
            resultOrig = result[0]
            result = result[0]
            probsPadded = result
            probsPadded[0][label == 1] = -1
            probsPadded[0][label == 2] = -2
            probs = probsPadded[ :,
                             padding[0][0] : int(result.shape[1]) - padding[0][1],
                             padding[1][0] : int(result.shape[2]) - padding[1][1],
                             padding[2][0] : int(result.shape[3]) - padding[2][1]]

            img = img[0]
            stdDev = 0.2
            segImg = whitening(imgOrig)
            manipTime += time() - t
    else:
        probs, stdDev = buildGaussProbs(img, label)
        segImg = img

    t = time()
    edgeCoeff = 10
    gridCuts = True
    if (gridCuts):
        segImg = arrayToLists(segImg)
    seg = graphCuts(segImg, probs, edgeCoeff, stdDev, gridCuts, 10000)
    print(seg.shape, file=sys.stderr)
    graphTime += time() - t
    
    if (BIFSeg == True):
        iterations = 3
        for i in range(iterations):
            t = time()        
            seg = softPadding(seg)[0]
            #resizeFactor = cnnSize / size
            #seg = zoom(seg, resizeFactor, order=1, multichannel=False)
            weighting = buildWeightArr(img, seg, probs)

            
            stackedImg = np.stack([img], axis=0)
            manipTime += time() - t

            # To produce weight map if dsired
            # weighting = weighting[0][
            #                       padding[0][0] : int(weighting.shape[1]) - padding[0][1],
            #                       padding[1][0] : int(weighting.shape[2]) - padding[1][1],
            #                       padding[2][0] : int(weighting.shape[3]) - padding[2][1]]
            # weighting[weighting > 1] = 1
            # return weighting
            
            t = time()
            quickTrain(model, stackedImg, weighting, seg, 15)
            trainTime += time() - t
            
            t = time()
            result = model.predict(np.array([stackedImg]))
            predictTime += time() - t
            t = time()
            result = result[0]
            #result = zoom(result, [1] + [1/resizeFactor]*3, order=1, multichannel=False )
            result = result[ :,
                             padding[0][0] : int(result.shape[1]) - padding[0][1],
                             padding[1][0] : int(result.shape[2]) - padding[1][1],
                             padding[2][0] : int(result.shape[3]) - padding[2][1]]
            probs = result
            probs[0][labelOrig != 0] = -labelOrig[labelOrig != 0]
            #stdDev = 0.1
            manipTime += time() - t
            t = time()
            seg = graphCuts(segImg, probs, edgeCoeff, stdDev, gridCuts)                    
            graphTime += time() - t
    print("Total time:{}, Manip time: {}, Graph Time: {}, Load Time:{}, Pred Time: {}, Train time: {}".format(
        time()-totalTime, manipTime, graphTime, loadTime, predictTime, trainTime), file=sys.stderr)
    return seg

def parseArgs():
    path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    f = open(path+"/nets.pkl", "rb")
    netsdb = pickle.load(f)
    f.close()

    models = {}
    for name in netsdb.getNames():
        models[name] = loadModel(name)
    print("Models loaded", file=sys.stderr)
    
    # action = sys.argv[1]
    # cnnName = None
    # try:
    #     cnnName = sys.argv[2]
    # except:
    #     pass
    
    lines = sys.stdin.readlines()
    action = lines[0][:-1]
    cnnName = lines[1][:-1]
    img = json.loads(lines[2][:-1])
    label = json.loads(lines[3])

    #f = open("nets.pkl", "rb")
    #db = pickle.load(f)
    #f.close()
    model = None
    graphCuts = True
    BIFSeg = False
    if action == "cnnSeg":
        cnn = True
        graphCuts = False
    elif action == "cnnGraphSeg":
        cnn = True
        graphCuts = True
    elif action == "cnnGraphBIFSeg":
        cnn = True
        graphCuts = True
        BIFSeg = True
    elif action == "graphCuts":
        cnn = False
    elif action == "query":
        pass

    if cnn == True:
        model = models[cnnName]
    print("MOD", model, file=sys.stderr)
    if action == "print":
        img   = listsToArray(img)
        label = listsToArray(label)
        outputFolder = "clientPrint/"
        folder = "/home/vincent/Documents/imperial/individual project/MedicalActiveCNN/nodeServer/server/"
        folder += outputFolder
        writeNIFTI(img, folder, "img")
        writeNIFTI(label, folder, "lbl")
        print(" Done")
    else:    
        seg = main(img, label, model, cnn, graphCuts, BIFSeg)
        seg = np.asarray(np.around(seg), dtype=int)
        np.set_printoptions(threshold=np.nan)
        print(np.array2string(seg, separator=", "))
        print("Done")



#start process
if __name__ == '__main__':

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    parseArgs()

    
    
# IMMEDIATE ORDERED:
# - Have a second weight for mislabelled scriblles and correctly labelled scribbles
# - Try Pythran or straight C code
# - Plot general loss graph+transfer learning graphs
# - Move LA from local to server
# - Get some dice scores
# - Code bundle

# IMMEDIATE:
# - Cut down on front end printing
# - Comment and clean up code
# - Report
# - Video thingy
# - check EVERYTHING work
    
# TO-DO:
# - Write weight array as image so it can be looked at
# - Need to reduce the time taken both on front and back end.
# - Try BIFSeg confidence value for all non-labelled pixels with weighting=abs(probs1 - probs2)
# - Have a second value of lambda for graphcuts for pixels that are differently labelled geodesically near a scribble?

# TO-DO:
# - Set scribble probs to infinity or 0 instead in graphcuts? already setting to 0, guessing the value is the same as infinity? Could still try setting it as inf or 1e10 or something
# - Have a second value of lambda for graphcuts for pixels that are differently labelled geodesically near a scribble? Or just regularly nearby?


# BIG PICTURE:
# - Offer "types" of CNNs, each with a specialization in an organ/tumour/imaging type. Offer ability to build new ones or to add images to existing ones.
# - Consider fine-tuning later layers only
# - Consider a geodesic mode on the front end, where the brush size is influenced by (2D) geodesic distances? Could have a slider to control the relative importance of the physical and geodesic distance, as well as a second variable to control the strength of the paths (sigma in the boundary eq.) and a "maxRadius" option too?
# - Change the front-end scrolling behaviour so that it jumps images if need be




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
    #               np.array([0.35,0.35,0.55,0.55]),
    #               np.array([0.35,0.31,0.60,0.65])]),
        
    #     np.array([np.array([0.10,0.10,0.20,0.17]),
    #               np.array([0.15,0.15,0.25,0.12]),
    #               np.array([0.05,0.10,0.55,0.65]),
    #               np.array([0.10,0.05,0.56,0.60])])

    #     ])
    # label =  np.array([
    #     np.array([np.array([1,0,1,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,1,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,2,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,2,0]),
    #               np.array([0,0,0,0])]),
    #     ])
    # seg = main(img, label, True, True, False)
