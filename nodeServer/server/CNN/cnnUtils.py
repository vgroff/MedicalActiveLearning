import os, inspect
import cv2
from keras.preprocessing.image import img_to_array
import cv2
import random
import numpy as np
from keras.models import model_from_json
import pickle




def saveModel(model, num=1):
    # serialize model to JSON
    path = os.path.dirname(os.path.abspath(inspect.stack()[0][1])) 
    model_json = model.to_json()
    with open(path + "/models/model{}.json".format(num), "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("models/model{}.h5".format(num),)
    print("Saved model to disk")

    # later...

def loadModel(num=1):    # load json and create model
    path = os.path.dirname(os.path.abspath(inspect.stack()[0][1])) 
    json_file = open(path+'/models/model{}.json'.format(num), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(path+"/models/model{}.h5".format(num),)
    #print("Loaded model from disk")
    return loaded_model
