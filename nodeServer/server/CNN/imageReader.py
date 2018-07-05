import SimpleITK as sitk
import tensorflow as tf
import numpy as np
import os
import math

from dltk.io.preprocessing import whitening

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
    
def readFunc(dataset, mode, params):
    folder = params["folder"]
    for ID, dataPoint in enumerate(dataset):
        print("Image {}/{}".format(ID+1, len(dataset)))
        # Read image
        imgPath = dataPoint["image"]
        img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
        img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        img = whitening(img)
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
            diff = size - label.shape[0]
            if diff > 0:
                pad = math.floor(diff/2)
                paddings = tf.constant([[pad, pad], [0, 0], [0, 0]])
                label = tf.pad(label, paddings, "CONSTANT")
                if (diff % 2 == 1):
                    paddings = tf.constant([[1, 0], [0, 0], [0, 0]])
                    label = tf.pad(label, paddings, "CONSTANT")
                label = tf.Session().run(label)
            label = resize3D(label, True, *params["size"])
            label = tf.Session().run(label)
            print(type(img), type(label), img.shape, label.shape)
            yield {'features': {'x': img},
                   'labels': {'y': label},
                   'sitk': img_sitk,
                   'subject_id': ID+1}
    print("leaving reader")
    return
