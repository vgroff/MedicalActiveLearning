from model import getUnet

from imageReader import readFunc
from utils import getDatasetInfo, splitArr

def train():
    folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
    trainPaths = getDatasetInfo(folder)
    
    model.fit(imgs_train, imgs_mask_train, batch_size=32, nb_epoch=20, verbose=1, shuffle=True,
              validation_split=0.2)

if __name__ == '__main__':
    train()
