def checkImgs():
    f = open("imgs.pkl", "rb")
    mngr = pickle.load(f)
    f.close()
    imgs, labels, info = mngr.getTrainImages()
    valImgs, valLabels, valInfo = mngr.getValImages()
    outputFolder = "./imgCheck"
    imageSets = [[0,90,1,True]]
    gen = generateImages(imgs, labels, imageSets)
    for i in range(10):
        print(i)
        img, label = next(gen)
        shift = np.zeros(img.shape)
        shift.fill(img.min())
        img += shift
        img *= 255
        print(img[0][0].shape, label[0].shape)
        newLabel = np.argmax(label[0], axis = 0)
        writeNIFTI(img[0][0], outputFolder, "{}_img".format(i))
        writeNIFTI(newLabel.astype(np.float32), outputFolder, "{}_lab".format(i))
    for index, img in enumerate(valImgs):
        i = index+10
        print(i)
        if (i%2 == 1):
            continue
        shift = np.zeros(img.shape)
        shift.fill(img.min())
        img += shift
        img *= 255
        writeNIFTI(img[0].astype(np.float32), outputFolder, "{}_img".format(i))
        writeNIFTI(np.argmax(valLabels[index], axis=0).astype(np.float32), outputFolder, "{}_lab".format(i))


        
def readFunc(dataset, mode, params, crop=True):
    folder = params["folder"]
    for ID, dataPoint in enumerate(dataset):
        #print("Image {}/{}".format(ID+1, len(dataset)))
        # Read image
        imgPath = dataPoint["image"]
        img_sitk = sitk.ReadImage(os.path.join(folder, imgPath))
        img = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        imgOrig = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        if (crop == True):
            # Only read label if training
            labelPath = dataPoint["label"]
            label_sitk = sitk.ReadImage(os.path.join(folder, labelPath))
            label = sitk.GetArrayFromImage(label_sitk).astype(np.float32)
            label, img, imgOrig, bounds, padding = cropToSeg(label, img, imgOrig, 9, 1, params["size"][0], randomized=True)
        else:
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
            if (crop == True):
                pass
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
            if (crop == True):
                img = np.stack([img], axis=-1).astype(np.float32)
                img = resize3D(img, False, *params["size"])
                img = tf.Session().run(img)
                imgOrig = np.stack([imgOrig], axis=-1).astype(np.float32)
                imgOrig = resize3D(imgOrig, False, *params["size"])
                imgOrig = tf.Session().run(imgOrig)
            yield {'features': {'x': img},
                   'labels': {'y': catLabels},
                   'original': imgOrig,
                   'imgPath': imgPath,
                   'sitk': img_sitk,
                   'subject_id': ID+1}
    print("leaving reader")
    return

                    
# img = np.array([
#     np.array([np.array([0.80,0.85,0.90,0.80]),
#               np.array([0.90,0.80,0.90,0.85]),
#               np.array([0.75,0.85,0.76,0.85]),
#               np.array([0.85,0.85,0.80,0.80])]),
    
#     np.array([np.array([0.85,0.80,0.25,0.20]),
#               np.array([0.90,0.75,0.20,0.20]),
#               np.array([0.85,0.90,0.65,0.65]),
#               np.array([0.85,0.80,0.60,0.65])]),
    
#     np.array([np.array([0.45,0.35,0.20,0.23]),
#               np.array([0.30,0.32,0.42,0.45]),
#               np.array([0.20,0.35,0.55,0.55]),
#               np.array([0.15,0.31,0.60,0.65])]),
    
#     np.array([np.array([0.10,0.10,0.20,0.17]),
#               np.array([0.15,0.15,0.25,0.12]),
#               np.array([0.05,0.10,0.55,0.65]),
#               np.array([0.10,0.05,0.56,0.60])])

# ])

# seg =  np.array([
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
# ])


# probs =  np.array([np.array([
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0])]),
#     np.array([np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([0,0,0,0]),
#               np.array([-1,0,0,0])]),
# ])])

# weight = np.zeros([2,4,4,4])
# weight[:] = 1

# updateGeodesics(0.25, 0.15, 0.0001, 0.005, img, probs, seg, weight)
# print(weight)
    
    
# IMMEDIATE ORDERED:
# - Have a second weight for mislabelled scriblles and correctly labelled scribbles
# - Try Pythran or straight C code
# - Get some Dice scores"
# - Move LA from local to server and generally prep server
# - Finish off website
# - Code bundle


# IMMEDIATE:
# - Cut down on front end printing
# - Comment and clean up code and get rid of this stuf (dev comments) and clean up import statements
# - Report
# - Video thingy
# - check EVERYTHING work
    
# TO-DO:
# - Write weight array as image so it can be looked at
# - Need to reduce the time taken both on front and back end.
# - Try BIFSeg confidence value for all non-labelled pixels with weighting=abs(probs1 - probs2)
# - Have a second value of lambda for graphcuts for pixels that are differently labelled geodesically near a scribble?

# TO-DO:
# - Set scribble probs to infinity or 0 instead in graphcuts? already setting to 0, guessing the value is the same as infinity? Could still try setting it as inf or 1e10 or something
# - Have a second value of lambda for graphcuts for pixels that are differently labelled geodesically near a scribble? Or just regularly nearby?


# BIG PICTURE:
# - Offer "types" of CNNs, each with a specialization in an organ/tumour/imaging type. Offer ability to build new ones or to add images to existing ones.
# - Consider fine-tuning later layers only
# - Consider a geodesic mode on the front end, where the brush size is influenced by (2D) geodesic distances? Could have a slider to control the relative importance of the physical and geodesic distance, as well as a second variable to control the strength of the paths (sigma in the boundary eq.) and a "maxRadius" option too?
# - Change the front-end scrolling behaviour so that it jumps images if need be




    # img = np.array([
    #     np.array([np.array([0.80,0.85,0.90,0.80]),
    #               np.array([0.90,0.80,0.90,0.85]),
    #               np.array([0.75,0.85,0.76,0.85]),
    #               np.array([0.85,0.85,0.80,0.80])]),
        
    #     np.array([np.array([0.85,0.80,0.25,0.20]),
    #               np.array([0.90,0.75,0.20,0.20]),
    #               np.array([0.85,0.90,0.65,0.65]),
    #               np.array([0.85,0.80,0.60,0.65])]),
        
    #     np.array([np.array([0.45,0.35,0.20,0.23]),
    #               np.array([0.40,0.32,0.42,0.45]),
    #               np.array([0.35,0.35,0.55,0.55]),
    #               np.array([0.35,0.31,0.60,0.65])]),
        
    #     np.array([np.array([0.10,0.10,0.20,0.17]),
    #               np.array([0.15,0.15,0.25,0.12]),
    #               np.array([0.05,0.10,0.55,0.65]),
    #               np.array([0.10,0.05,0.56,0.60])])

    #     ])
    # label =  np.array([
    #     np.array([np.array([1,0,1,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,1,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,2,0]),
    #               np.array([0,0,0,0])]),
    #     np.array([np.array([0,0,0,0]),
    #               np.array([0,0,0,0]),
    #               np.array([0,0,2,0]),
    #               np.array([0,0,0,0])]),
    #     ])
    # seg = main(img, label, True, True, False)
