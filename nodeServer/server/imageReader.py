import SimpleITK as sitk
import os, sys
import numpy
import matplotlib.pyplot as plt


def sitk_show(img, title=None, margin=0.05, dpi=40 ):
    nda = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()
    figsize = (1 + margin) * nda.shape[0] / dpi, (1 + margin) * nda.shape[1] / dpi
    extent = (0, nda.shape[1]*spacing[1], nda.shape[0]*spacing[0], 0)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_axes([margin, margin, 1 - 2*margin, 1 - 2*margin])

    plt.set_cmap("gray")
    ax.imshow(nda,extent=extent,interpolation=None)
    
    if title:
        plt.title(title)
    
    plt.show()


def main(folder):
    fileNames = os.listdir(folder)
    imgs = []
    for fileName in fileNames:
        print(fileName,  fileName.split("."))
        split = fileName.split(".")
        name = ".".join(split[:-1])
        ext = split[-1]
        if ext == "mha":
            imgs.append(os.path.join(folder,fileName))
    print(imgs)
    img = sitk.ReadImage(imgs[0])
    sitk_show(img[:,:,56])
    
#/home/vincent/Documents/imperial/individual\ project/datasets/BRATS2015_Training/HGG/brats_2013_pat0001_1/VSD.Brain.XX.O.MR_T1.54513

# TO-DO:
# - Decode systematic file naming in order to match up labels and data, and convince yourelf that it is working
# - Convert labels to uniform labels, depending on what it looks like
# - Find and train the U-net

main(*sys.argv[1:])
