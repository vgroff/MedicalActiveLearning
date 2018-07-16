import tensorflow as tf
import json
import os



class ImageManager():
    def __init__(self, path, imgSize):
        self.data = []
        self.labels = []

        i = 0
        pics = os.listdir(os.getcwd() + path)
        random.shuffle(pics)
        for img in pics:
            # load the image, pre-process it, and store it in the data list
            imgPath = os.getcwd() + path + img

            image = cv2.imread(imgPath)
            image = cv2.resize(image, (imgSize, imgSize))
            image = img_to_array(image)
            self.data.append(image)

            # extract the class label from the image path and update the
            # labels list
            label = imgPath.split(os.path.sep)[-1].split(".")[0]
            if label == "dog":
                label = np.array([1,0])
            else:
                label = np.array([0,1])
            self.labels.append(label)

    def getImages(self, start, end):
        return self.data[start:end], self.labels[start:end]


class DataManager():
    def __init__(self, data, labels):
        self.labels = labels
        self.data = data

    def getData(self, start=0, end=None):
        if (end != None):
            return self.data[start:], self.labels[start:]
        else:
            return self.data[start:end], self.labels[start:end]

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


def cropToSeg(image, margin, minMargin=1, randomized=True):
    rowBounds   = [image.shape[0],-1]
    colBounds   = [image.shape[1],-1]
    depthBounds = [image.shape[2],-1]
    for row in image:
        for col in row:
            for depth in col:
                if (image[row, col, depth] != 0):
                    if row < rowBounds[0]:
                        rowBounds[0] = row
                    if row > rowBounds[1]:
                        rowBounds[1] = row
                    if col < colBounds[0]:
                        colBounds[0] = col
                    if col > colBounds[1]:
                        colBounds[1] = col
                    if depth < depthBounds[0]:
                        depthBounds[0] = depth
                    if depth > depthBounds[1]:
                        depthBounds[1] = depth


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


