import numpy as np
import tensorflow as tf

from keras.callbacks import ReduceLROnPlateau

import os
import pickle
import sys
import random

from keras import backend as K

from cnnUtils import saveModel, loadModel
from imageUtils import ImageManager, getDatasetInfo, pathImgMngr
from model import getUNet2

from imageReader import getImages

from keras.optimizers import Adam, SGD, RMSprop, Adadelta, Adagrad
from model import weighted_dice_coefficient_loss, weightedDiceLoss

from functools import partial

from keras.backend.common import epsilon
from scipy.ndimage import rotate

from predict import writeNIFTI

from keras.callbacks import ModelCheckpoint as checkpoint


def _to_tensor(x, dtype):
    """Convert the input `x` to a tensor of type `dtype`.
    # Arguments
        x: An object to be converted (numpy array, list, tensors).
        dtype: The destination type.
    # Returns
        A tensor.
    """
    return tf.convert_to_tensor(x, dtype=dtype)

def prepImageManager(numVal, numbers, orientations, folders, size):
    mngr = None
    for i, folder in enumerate(folders):
        print("Folder {}/{}".format(i+1,len(folders)))
        shape = [size]*3
        dataset = getDatasetInfo(folder)
        number = numbers[i]
        orientation = orientations[i]
        if (number < len(dataset)):
            dataset = dataset[:number]
        data = getImages(folder, dataset, None, numVal/len(dataset), orientation,
                         "softPadding", False, [0, 10], [1,2])
        if (mngr):
            mngr.addData(data)
        else:
            mngr = ImageManager(data)
    return mngr


def generateImages(imgs, labels, imageSets):
    while True:
       for imageSet in imageSets:
            trImgs = imgs[imageSet[0]:imageSet[0]+imageSet[1]]
            trLabels = labels[imageSet[0]:imageSet[0]+imageSet[1]]
            if (imageSet[3] == True):
                ordering = random.sample(range(imageSet[1]), imageSet[1])
                newTrImgs = []
                newLabels = []
                for index in ordering:
                    newImg = trImgs[index]
                    newCatLabels = trLabels[index]
                    for i in range(1,4):
                        if (random.random() > 0.5):
                            newImg = np.flip(newImg, axis=i)
                            newCatLabels = np.flip(newCatLabels, axis=i)
                    maxAngle = 1
                    axes = [[1,2],[1,3],[2,3]]
                    random.shuffle(axes)
                    noise = np.random.normal(0, 0.08, newImg.shape)
                    newTrImgs.append(newImg+noise)
                    newLabels.append(newCatLabels)
                trImgs = newTrImgs
                trLabels = newLabels
            for i in range(imageSet[2]):
                for j, img in enumerate(trImgs):
                    weight = 1
                    if (ordering[j] >= 30 and ordering[j] < 60):
                        weight = 1.0
                    elif (ordering[j] >= 60 and ordering[j] < 90):
                        weight = 1
                    yield np.array([img]), np.array([trLabels[j]]), np.array([weight])

def genValImages(imgs, labels):
    for i, img in enumerate(imgs):
        yield np.array([img]), np.array([labels[i]])

def cat_crossentropy(target, output, from_logits=False, axis=-1):
    """Categorical crossentropy between an output tensor and a target tensor.
    # Arguments
        target: A tensor of the same shape as `output`.
        output: A tensor resulting from a softmax
            (unless `from_logits` is True, in which
            case `output` is expected to be the logits).
        from_logits: Boolean, whether `output` is the
            result of a softmax, or is a tensor of logits.
        axis: Int specifying the channels axis. `axis=-1`
            corresponds to data format `channels_last`,
            and `axis=1` corresponds to data format
            `channels_first`.
    # Returns
        Output tensor.
    # Raises
        ValueError: if `axis` is neither -1 nor one of
            the axes of `output`.
    """
    output_dimensions = list(range(len(output.get_shape())))
    if axis != -1 and axis not in output_dimensions:
        raise ValueError(
            '{}{}{}'.format(
                'Unexpected channels axis {}. '.format(axis),
                'Expected to be -1 or one of the axes of `output`, ',
                'which has {} dimensions.'.format(len(output.get_shape()))))
    # Note: tf.nn.softmax_cross_entropy_with_logits
    # expects logits, Keras expects probabilities.
    if not from_logits:
        # scale preds so that the class probas of each sample sum to 1
        output /= tf.reduce_sum(output, axis, True)
        # manual computation of crossentropy
        _epsilon = _to_tensor(epsilon(), output.dtype.base_dtype)
        output = tf.clip_by_value(output, _epsilon, 1. - _epsilon)
        return - tf.reduce_sum(target * tf.log(output), axis)
    else:
        return tf.nn.softmax_cross_entropy_with_logits(labels=target,
logits=output)
              
def catCrossEntropy(target, output):
    return cat_crossentropy(target, output, from_logits=False, axis=1)


# Fine tune a model to fit a segmentation with a weighting matrix                    
def fineTune(model, img, weighting, segmentation, epochs=1, lr=5e-4, trainable=[30,29,26,22]):
    labels = np.zeros(weighting.shape)
    c = 0
    labels[0][segmentation == 0] = 1
    labels[1][segmentation == 1] = 1
    #lr = 10e-4#2.5e-5#1.2e-4#7.5e-5
    # 10e-4 and 30 works well
    sgd = SGD(lr=lr, momentum=0, decay=0.0, nesterov=False)
    adam = Adam(lr=lr, amsgrad=False)
    rms = RMSprop(lr=lr)
    adaDelta = Adadelta(lr=lr)
    adam = Adam(lr=lr)
    loss = weightedDiceLoss(_to_tensor(weighting, tf.float32))
    for i in range(1,31):
        layer = model.get_layer("conv3d_{}".format(i))
        layer.trainable = False
    for n in trainable:
        layer = model.get_layer("conv3d_{}".format(n))
        layer.trainable = True
    model.compile(optimizer = sgd, loss = catCrossEntropy)#loss)
    model.fit(np.array([img]), np.array([weighting*labels]), validation_split=0.0, batch_size=1, verbose=1, epochs=epochs)#, 
              #callbacks=[learning_rate_reduction])




def accuracy(y_true, y_pred):
    return K.mean(K.equal(K.argmax(y_true, axis=1),K.argmax(y_pred, axis=1)))

def diceScore(y_pred, y_true, hard=False):
    if hard == True:
        y_true = np.argmax(y_true, axis=0)
        y_pred = np.argmax(y_pred, axis=0)
    return 2 * np.sum(y_true*y_pred) / (np.sum(y_true) + np.sum(y_pred))

def train():
    useOldImg   = True
    useOldModel = True
    nClasses = 2
    length = 80
    if (useOldImg == False):
        # Build image set
        folderStub = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task"
        folderNames = ["02_Heart", "05_Prostate", "04_Hippocampus"] 
        folders = [folderStub+name for name in folderNames]
        numbers      = [20, 20, 35]
        orientations = [2, 2, 1]
        numVal = 5
        mngr = prepImageManager(numVal, numbers, orientations, folders, length)
        # Get the images
        imgs, labels, info = mngr.getTrainImages()
        valImgs, valLabels, valInfo = mngr.getValImages()
        # Save image set
        f = open("imgs.pkl", "wb")
        pickle.dump(mngr, f)
        f.close()
    else:
        # Get images from previous image set
        print("Getting images...")
        f = open("imgs_spleen10.pkl", "rb")
        mngr = pickle.load(f)
        f.close()
        imgs, labels, info = mngr.getTrainImages()
        valImgs, valLabels, valInfo = mngr.getValImages()
    print("Getting net...")
    lr = 20e-5#2.5e-5#1.2e-4#7.5e-5
    if (useOldModel == False):
        # Build Unet model
        model = getUNet2((1,None,None,None), nClasses, lr=lr,
                         n_base_filters=16, depth=5,
                         loss_function=weighted_dice_coefficient_loss, activation_name="softmax")
        sgd = SGD(lr=lr, momentum=0.95, decay=0.0, nesterov=False)
        model.compile(optimizer = sgd, loss = weighted_dice_coefficient_loss, metrics=[accuracy])
    else:
        # Load model from file
        model = loadModel(1)
        adam = Adam(lr=lr, epsilon=1e-3, amsgrad=True)
        sgd = SGD(lr=lr, momentum=0.95, decay=0.0, nesterov=False)
        model.compile(optimizer = sgd, loss = weighted_dice_coefficient_loss, metrics=[accuracy])
    print("Training on {}, validating on {}".format(len(imgs), len(valImgs)))
    cp = checkpoint("./savedWeights.h5", monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True, mode='auto', period=1)
    learning_rate_reduction = ReduceLROnPlateau(monitor='val_loss',
                                                patience=8,
                                                verbose=1,
                                                factor=0.5,
                                                min_lr=1e-5)
    imageSets = [[90, 30, 4, False],[0, 30, 1, False],[60, 30, 5, False],[90, 30, 2, False],[30, 30, 1, False]]
    # Select training and validation images
    imageSets = [[0,30,1,True]]
    valStart = 0
    valEnd   = 10
    valImgs, valLabels, valInfo = [valImgs[valStart:valEnd], valLabels[valStart:valEnd], valInfo[valStart:valEnd]]
    epochs = 200

    imageSets = [[0,4,1,True]]
    imgs = valImgs[0:4]
    labels = valLabels[0:4]
    valImgs = valImgs[4:10]
    valLabels = valLabels[4:10]
    
    # Build training and validation images
    imgGen = generateImages(imgs, labels, imageSets)
    valImgGen = generateImages(valImgs, valLabels, [[0,5,1,True]])
    bestAcc = 0    
    # Train on image generator
    model.fit_generator(imgGen, verbose=1, #metrics=["accuracy"],
                        steps_per_epoch=4, epochs=epochs,
                        validation_data = valImgGen, validation_steps = 5, 
                        shuffle=False)#, callbacks=[cp])#, learning_rate_reduction])
    saveModel(model)


def onlineTrain(name, epochs, lr):
    print("Getting images...")
    
    f = open(pathImgMngr(name), "rb")
    mngr = pickle.load(f)
    f.close()
    
    imgs, labels, info = mngr.getTrainImages()
    valImgs, valLabels, valInfo = mngr.getValImages()

    print("Getting model...")
    model = loadModel(name)
    sgd = SGD(lr=lr, momentum=0.99, decay=0.0, nesterov=False)
    model.compile(optimizer = sgd, loss = weighted_dice_coefficient_loss , metrics=["accuracy", weighted_dice_coefficient_loss])
    print("Training images...")
    model.fit(np.array(imgs), np.array(labels), batch_size=1, validation_data=[np.array(valImgs), np.array(valLabels)], shuffle=True, epochs=epochs, verbose=2)
    saveModel(model, name)


def callOnlineTrain():
    name = sys.argv[1]
    epochs = int(sys.argv[2])
    lr = float(sys.argv[3])
    onlineTrain(name, epochs, lr)
    print("Done")


        
if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    try:
        callOnlineTrain()
    except(IndexError):
        train()
        #checkImgs()

# TO-DO:
# - Multiple datasets at once
# - Not sure that mean weighted dice coefficient works with resized images. They will be both pushed towards 1 - but this might actually be ok but for graph cuts and for validation data, maybe. Could try a more normal loss function otherwise





# BIG PICTURE:
# - CNN on server is just trained in basic segmentation - automatic bounding-box
# - People can upload a dataset to fine-tune the network - here the bounding-box is done automatically
# - Then they can upload live data, doing the bounding-box themselves.
# On the front-end, people are walked through
# - upload picture or dataset
# - do bounding CUBE
# - correct via graph cuts
# - finishing touches
# - save to file or crop image
