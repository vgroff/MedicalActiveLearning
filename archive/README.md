# Deep Learning for 3D Image Segmentation

This project is an implemntation of the BIFSeg algorithm (https://arxiv.org/pdf/1710.04043.pdf) as a NodeJS website, which allows a CNN to perform segmentations on **unseen** organ types - that is to say, organ types that the CNN was not trained on.

![](https://raw.githubusercontent.com/vgroff/MedicalActiveLearning/master/archive/genBIFSEG2.png "Title")

The image above showns a CNN that has been trained on left atrium, prostate and hippocampus images, and it is performing a segmentation on a liver. In blue is the ground truth, in cyan is the initial segmentation, in green and yellow are user interactions and in red is the final segmentation.

Running the code requires training local models:

First, make sure you have CUDA, cuDnn and an NVIDIA GPU on the local machine. Install SimpleITK, numpy, pickle, keras and tensorflow with pip3.

Install pythran according to (https://github.com/serge-sans-paille/pythran/) and run pythran -DUSE_BOOST_SIMD -fopenmp -march=native geodesicMin.py in the server/CNN folder in order to compile geodesicMin

Then, download the medical decathlon data sets at medicaldecathlon.com, namely left atrium, prostate and hippocampus

In train.py, in the train function, change the path to whichever path the 3 folders are in, and make sure useOldImgs and useOldModels are set to False.

Change the names in the folders variable to change which folders you are training on (all 3 by default)

Train one CNN on the left atrium (python3 train.py), and rename model_1.h5 and model_1.json to model_Left Atrium, and rename imgs.pkl to Left Atrium_img.pkl

Train one CNN on the all 3 organs, and rename model_1.h5 and model_1.json to model_General, and rename imgs.pkl to General_img.pkl
Uncomment createDBs in the if name==__main__ function in query.db, run the file and re-comment it

Run npm install in the terminal in the top-level folder

Run npm run server

Head to localhost:8080 in the browser
