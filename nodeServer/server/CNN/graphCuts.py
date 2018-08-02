import maxflow
import numpy as np

def edgeFactor(i1, i2, dist, edgeVal):
    return np.exp(((i1 - i2)/2*edgeVal**2)**2)/dist


def graphCut(img, probs, edgeVal=1):
    shape = img.shape
    total = shape[0]*shape[1]*shape[2]
    # Create a graph with integer capacities.
    g = maxflow.Graph[float](total, total*26)
    # Add two (non-terminal) nodes. Get the index to the first one.
    nodes = g.add_nodes(total)

    edgeFactors = np.zeros(shape)
    edgeCoeff = 0.15
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                index = i*shape[1]*shape[2] + j*shape[2] + k
                if (probs[i,j,k,0] > 0):
                    g.add_tedge(nodes[index],
                                -np.log(probs[i,j,k,0]),
                                -np.log(probs[i,j,k,1]))
                for img2d in range(i-1, i+2):
                    for coord in [[j, k+1], [j+1, k+1], [j+1, k], [j+1, k-1]]:
                        if (img2d >= 0 and coord[0] >= 0 and coord[1] >= 0) :
                            otherIndex = img2d*shape[1]*shape[2] + coord[0]*shape[2] + coord[1]
                            try:
                                dist = ((coord[0] - j)**2 + (coord[1] - k)**2 + (img2d - i)**2)**0.5
                                edge = edgeCoeff*edgeFactor(img[i,j,k],
                                                            img[img2d, coord[0], coord[1]],
                                                            dist, edgeVal)
                                g.add_edge(nodes[index], nodes[otherIndex], edge, edge)
                                edgeFactors[i,j,k] += edge
                                edgeFactors[img2d, coord[0], coord[1]] += edge
                            except(IndexError):
                                pass
                otherIndex = (i+1)*shape[1]*shape[2] + j*shape[2] + k                          
                try:
                    edge = edgeCoeff*edgeFactor(img[i,j,k],
                                                img[i+1, j, k], 1, edgeVal)
                    g.add_edge(nodes[index], nodes[otherIndex], edge, edge)
                    edgeFactors[i,j,k] += edge
                    edgeFactors[img2d, coord[0], coord[1]] += edge
                except(IndexError):
                    pass

    maxIndex = np.unravel_index(edgeFactors.argmax(), edgeFactors.shape)
    maxEdge = edgeFactors[maxIndex[0], maxIndex[1], maxIndex[2]]

    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                index = i*shape[1]*shape[2] + j*shape[2] + k
                if (probs[i,j,k,0] == -2):
                    g.add_tedge(nodes[index], 0, 1 + maxEdge)
                elif (probs[i,j,k,0] == -1):
                    g.add_tedge(nodes[index], 1 + maxEdge, 0)
    
    
    #print(counts)              
    flow = g.maxflow()

    arr = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                index = i*shape[1]*shape[2] + j*shape[2] + k
                arr[i,j,k] = (1 + g.get_segment(nodes[index])) % 2
    np.set_printoptions(precision=2, suppress=True)
    #print(img)
    #print(probs)
    #print(arr)
    
    return arr
        
        
if __name__ == '__main__':
    img = np.array([
        np.array([np.array([0.80,0.85,0.90,0.80]),
                  np.array([0.90,0.80,0.90,0.85]),
                  np.array([0.75,0.85,0.76,0.85]),
                  np.array([0.85,0.85,0.80,0.80])]),
        
        np.array([np.array([0.85,0.80,0.25,0.20]),
                  np.array([0.90,0.75,0.20,0.20]),
                  np.array([0.85,0.90,0.65,0.65]),
                  np.array([0.85,0.80,0.60,0.65])]),
        
        np.array([np.array([0.45,0.35,0.20,0.23]),
                  np.array([0.40,0.32,0.42,0.45]),
                  np.array([0.35,0.35,0.55,0.55]),
                  np.array([0.35,0.31,0.60,0.65])]),
        
        np.array([np.array([0.10,0.10,0.20,0.17]),
                  np.array([0.15,0.15,0.25,0.12]),
                  np.array([0.05,0.10,0.55,0.65]),
                  np.array([0.10,0.05,0.56,0.60])])
        ])

    probs = np.array([
        np.array([np.array([0.80,0.85,0.90,0.80]),
                  np.array([0.90,0.80,0.90,0.85]),
                  np.array([0.75,0.85,0.90,0.95]),
                  np.array([0.85,0.85,0.90,0.80])]),
        
        np.array([np.array([0.85,0.80,0.25,0.20]),
                  np.array([0.90,0.75,-1,0.20]),
                  np.array([0.85,0.90,0.50,0.45]),
                  np.array([0.85,0.80,0.55,0.45])]),
        
        np.array([np.array([0.45,0.35,0.20,0.23]),
                  np.array([0.40,0.32,0.22,0.25]),
                  np.array([0.35,0.25,0.35,0.45]),
                  np.array([0.35,0.21,0.30,0.45])]),
        
        np.array([np.array([0.10,0.10,0.20,0.17]),
                  np.array([0.15,0.15,0.25,0.12]),
                  np.array([0.05,0.10,0.45,0.55]),
                  np.array([0.10,0.05,0.46,0.50])])
        ])
    graphCut(img, probs)


# -2 is background, -1 is foreground
