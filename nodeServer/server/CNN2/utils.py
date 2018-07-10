import tensorflow as tf
import json
import os

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


