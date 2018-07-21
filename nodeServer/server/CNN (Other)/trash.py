from utils import resize3D
from imageReader import readFunc
from predict import writeNIFTI
from utils import getDatasetInfo, splitArr


modelPath = "./models"
outputFolder = "./predictions"
folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
trainPaths = getDatasetInfo(folder)
train_filenames, val_filenames = splitArr(trainPaths, 0.75)
size = [33, 80, 80]

readParams = {"folder":folder, "depth":132, "size":size, "whiten":False}
for example in readFunc(val_filenames[:1], None, readParams):
    label = example["labels"]["y"]
    ID = example["subject_id"]
    writeNIFTI(example["features"]["x"], outputFolder, "{}".format(ID), example)
    writeNIFTI(label, outputFolder, "{}_truth".format(ID), example)

readParams = {"folder":folder, "depth":132, "size":size, "whiten":True}
for example in readFunc(val_filenames[:1], None, readParams):
    label = example["labels"]["y"]
    ID = example["subject_id"]
    writeNIFTI(example["features"]["x"], outputFolder, "{}_whit".format(ID), example)
    writeNIFTI(label, outputFolder, "{}_truth".format(ID), example)
