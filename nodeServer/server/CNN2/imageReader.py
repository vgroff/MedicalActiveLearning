import SimpleITK as sitk
import tensorflow as tf
import numpy as np
import os
import math

from dltk.io.preprocessing import whitening

from imageUtils import resize3D

def readFunc(dataset, mode, params):
    folder = params["folder"]
    for ID, dataPoint in enumerate(dataset):
        #print("Image {}/{}".format(ID+1, len(dataset)))
        # Read image
        imgPath = dataPoint["image"]
        img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
        img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
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
            yield {'features': {'x': img},
                   'labels': {'y': catLabels},
                   'sitk': img_sitk,
                   'subject_id': ID+1}
    print("leaving reader")
    return
