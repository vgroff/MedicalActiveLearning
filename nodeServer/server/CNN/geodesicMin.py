import numpy as np

def addToQueue(q, end, size, x, y, z):
    q[end, 0] = x
    q[end, 1] = y
    q[end, 2] = z
    return (end + 1) % size

def removeFromQueue(q, start, size):
    return q[start], (start + 1) % size

#pythran export updateGeodesicsOpt(float, float, float, float[][][], float[][][][], int[][][], float[][][][])
def updateGeodesicsOpt(maxPathLength, stdDev, minEdge, img, probs, segmentation, weighting):
    qStart = np.array([0,0])
    qEnd   = np.array([0,0])
    maxSize = img.shape[0]*img.shape[1]*img.shape[2]
    qs = np.zeros((2, maxSize, 3), dtype=np.float32)
    
    for i, row in enumerate(probs[0]):
        for j, col in enumerate(row):
            for k, val in enumerate(col):
                if (val < 0):
                    index = int(round(val))+2
                    qEnd[index] = addToQueue(qs[index], qEnd[index], maxSize, i, j, k)

    directions = [ [1,0,0], [-1,0,0], [0,1,0], [0,-1,0], [0,0,1], [0,0,-1] ]
    for index in [0,1]:
        pathLengths = np.zeros(img.shape, dtype=np.float32)#fill(img.shape, fill_value=-1.0)
        computedPathLengths = np.zeros(img.shape, dtype=np.float32)#np.fill(img.shape, fill_value=-1.0)

        pathLengths[:] = -1.0
        computedPathLengths[:] = -1.0
        
        # for i, row in enumerate(img):
        #     for j, col in enumerate(row):
        #         for k, val in enumerate(col):
        #             pathLengths[i,j,k] = -1.0
        #             computedPathLengths[i,j,k] = -1.0
                    
        q = qs[index]
        while (qStart[index] != qEnd[index]):
            coords, qStart[index] = removeFromQueue(q, qStart[index], maxSize)

            row, col, depth = coords
            row = int(row)
            col = int(col)
            depth = int(depth)
            currPathLength = pathLengths[row, col, depth]
            computedPathLength = computedPathLengths[row,col,depth]
            # The if statement below is mean to skip over things in the queue that we have already computed
            diff = abs(float(currPathLength - computedPathLength))
            b = computedPathLengths[row, col, depth] >= 0
            if (b==True and diff < 0.0001):
                # If weve got a path length saved and it is the same as the current path length
                z=0
            else:
                # Save path length
                if (currPathLength < 0):
                    currPathLength = 0
                computedPathLengths[row,col,depth] = currPathLength
                for direction in directions:
                    # Go in every direction
                    newRow = row+direction[0]
                    newCol = col+direction[1]
                    newDepth = depth+direction[2]
                    if (newRow < 0 or newCol < 0 or newDepth < 0):
                        # Dont go to negative indices
                        z = 0
                    elif (newRow >= img.shape[0] or newCol >= img.shape[1]
                          or newDepth >= img.shape[2]):
                        z = 0
                    else:
                        otherVal = segmentation[newRow, newCol, newDepth]
                        if (probs[0, newRow, newCol, newDepth] >= 0):# and index != otherVal:
                    # If this is a normal (non-scrible) and it has the opposite marking - does it need to have the opposite marking? Defeats the purpose maybe
                            i1 = img[row, col, depth]
                            i2 = img[newRow, newCol, newDepth]
                            length = 1 - np.exp(-(i2 - i1)**2/(2*stdDev**2)) + minEdge
                            newPathLength = currPathLength + length
                            if (newPathLength > maxPathLength):
                                # If weve gone over the maximum path length, abandon
                                z = 0
                            else:
                                destPathLength = pathLengths[newRow, newCol, newDepth]
                                if (newPathLength < destPathLength
                                    or destPathLength < 0):
                                    # If weve made a shorter path, save it and place in queue
                                    qEnd[index] = addToQueue(q, qEnd[index], maxSize, newRow, newCol, newDepth)
                                    pathLengths[newRow, newCol, newDepth] = newPathLength
                                    if index != otherVal:
                                        weighting[0, newRow, newCol, newDepth] = 0
                                        weighting[1, newRow, newCol, newDepth] = 0
