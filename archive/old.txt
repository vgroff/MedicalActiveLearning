The best way to see the code in action would be to go to the website http://51.140.154.2:8080/,
do e-mail me if it is down or anything and I can talk to Anandha since I'm not sure how many Azure credits I get.


If you really want to run it locally, the main issue is that the submit size was too small to allow for the models or datasets, so you will have to make and train your own.

TRAINING MODELS AND RUNNING THE CODE:
First, make sure you have CUDA, cuDnn and an NVIDIA GPU on the local machine. Install SimpleITK, numpy, pickle, keras and tensorflow with pip3.
Install pythran according to (https://github.com/serge-sans-paille/pythran/) and run pythran -DUSE_BOOST_SIMD -fopenmp -march=native geodesicMin.py in the server/CNN folder
in order to compile geodesicMin
Then, download the medical decathlon data sets at medicaldecathlon.com, namely left atrium, prostate and hippocampus
In train.py, in the train function, change the path to whichever path the 3 folders are in, and make sure useOldImgs and useOldModels are set to False.
Change the names in the folders variable to change which folders you are training on (all 3 by default)
Train one CNN on the left atrium (python3 train.py), and rename model_1.h5 and model_1.json to model_Left Atrium, and rename imgs.pkl to Left Atrium_img.pkl
Train one CNN on the all 3 organs, and rename model_1.h5 and model_1.json to model_General, and rename imgs.pkl to General_img.pkl
Uncomment createDBs in the if name==__main__ function in query.db, run the file and re-comment it
Run npm install in the terminal in the top-level folder
Run npm run server
Head to localhost:8080 in the browser

USING THE WEBSITE:
Load a -nii or .nii.gz image with "load image" (can take a while with large images, front-end is not particularly well optimized yet)
Load the truth mask with "load mask" if desired
Click on the "crop" radio button, and draw a bounding box (in 3D) around the desired object. Click the "crop" button
Click on "CNN+Graph Cuts segmentation" button and wait for the result
Add scribbles to the image to relabel pixels
Click on the "Add annotations (BIFSeg)" button
