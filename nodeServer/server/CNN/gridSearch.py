import os, sys, pickle
import numpy as np
import tensorflow as tf
from main import graphCuts, listsToArray, arrayToLists
from cnnUtils import loadModel


def calcDice(labels1, labels2):
    total = 0
    count = 0
    for index, row in enumerate(labels1):
        for j, col in enumerate(row):
            for k, val in enumerate(col):
                val2 = labels2[index,j,k]
                if val == 1:
                    total += 1
                if val2 == 1:
                    total += 1
                    if (val == val2):
                        count += 2
    return count/total


def diceScore(y_pred, y_true, hard=False):
    if hard == True:
        y_true = np.argmax(y_true, axis=0)
        y_pred = np.argmax(y_pred, axis=0)
    return 2 * np.sum(y_true*y_pred) / (np.sum(y_true) + np.sum(y_pred))

def main():
    model = loadModel("General")
    f = open("imgs_unseen.pkl", "rb")
    mngr = pickle.load(f)
    f.close()
    valImgs, valLabels, valInfo = mngr.getValImages()
    valStart = 0
    valEnd = 15
    valImgs, valLabels, valInfo = [valImgs[valStart:valEnd], valLabels[valStart:valEnd], valInfo[valStart:valEnd]]

    meanDice = 0
    meanDiceSq = 0
    preds = []
    diceOrigs = []
    for i, img in enumerate(valImgs):
        result = model.predict(np.array([img]))[0]
        preds.append(result)
        dice =  diceScore(result, valLabels[i], True)
        print("Dice {}: {}".format(i, dice))
        diceOrigs.append(dice)
        meanDice += dice
        meanDiceSq += dice**2
    meanDice = meanDice / len(valImgs)
    meanDiceStdDev = (meanDiceSq/len(valImgs) - meanDice**2)**0.5
    print("No Graph Cuts, mean: {}, err: {}".format(meanDice, meanDiceStdDev/len(valImgs)**0.5))
        
    edgeCoeffs = [4,7,10]
    stdDevs    = [0.1, 0.2, 0.4]
    for edgeCoeff in edgeCoeffs:
        for stdDev in stdDevs:
            meanDice  = 0
            meanDiceSq = 0
            stdDevDice = 0
            diffsMean = 0
            diffMeanSq = 0
            for i, pred in enumerate(preds):
                segImg = arrayToLists(valImgs[i][0])
                seg = graphCuts(segImg, pred, edgeCoeff, stdDev, True)
                dice =  diceScore(seg, np.argmax(valLabels[i],axis=0), False)
                diff = dice - diceOrigs[i]
                diffsMean += diff
                diffMeanSq += diff**2
                #print(np.count_nonzero(seg==0), np.count_nonzero(seg==1))
                #print("Dice: ", dice, seg.shape)
                meanDice += dice
                meanDiceSq += dice**2
            diffsMean = diffsMean / len(preds)
            diffStdDev = (diffMeanSq/len(preds) - diffsMean**2)**0.5
            diffsErr = diffStdDev / len(preds)**0.5
            meanDice = meanDice / len(valImgs)
            meanDiceStdDev = (meanDiceSq/len(valImgs) - meanDice**2)**0.5
            print("Coeff: {}, Std Dev: {}, Mean dice: {}, dice err: {}, t:  {}".format(edgeCoeff, stdDev, meanDice, meanDiceStdDev/len(valImgs)**0.5, diffsMean/diffsErr))

#start process
if __name__ == '__main__':

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    main()
