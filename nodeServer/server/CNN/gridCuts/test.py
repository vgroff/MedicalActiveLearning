import gridCut3D
import numpy as np


img = gridCut3D.CatVolume()
img = [[[0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8]],
       [[0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8],
        [0.7, 0.8, 0.7, 0.8]],
       [[0.2, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.2, 0.1],
        [0.65, 0.6, 0.2, 0.1]],
       [[0.2, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.2, 0.1]]]
          

probs = gridCut3D.Volume()
probs = [[[0.7, 0.8, 0.7, 0.8],
          [0.7, 0.8, 0.7, 0.8],
          [0.9, 0.8, 0.7, 0.8],
          [0.7, 0.8, 0.7, 0.8]],
         [[0.7, 0.8, 0.7, 0.8],
          [0.7, 0.8, 0.9, 0.8],
          [0.7, 0.8, 0.7, 0.8],
          [0.7, 0.8, 0.7, 0.9]],
         [[0.2, 0.1, 0.2, 0.1],
          [0.2, 0.1, 0.2, 0.1],
          [0.2, 0.1, 0.2, 0.1],
          [0.45, 0.45, 0.2, 0.1]],
         [[0.2, 0.1, 0.2, 0.1],
          [0.2, 0.1, 0.2, 0.1],
          [0.2, 0.1, 0.2, 0.1],
          [0.2, 0.1, 0.2, 0.1]]]

regTerms = [[],[]]
for row in probs:
    regTerms[0].append([])
    regTerms[1].append([])
    for col in row:
        regTerms[0][-1].append([])
        regTerms[1][-1].append([])
        for val in col:
            regTerms[0][-1][-1].append(-np.log(val))
            regTerms[1][-1][-1].append(-np.log(1-val))
catVol = gridCut3D.CatVolume()
catVol = regTerms

for row in regTerms:
    for col in row:
        for val in col:
            print("{}, {}".format(round(val[0],2), round(val[1],2)))


seg = gridCut3D.Volume()
seg = gridCut3D.gridCut3D(img, regTerms, 2, 0.15)
for row in seg:
    print("-")
    for col in row:
        print(col)
