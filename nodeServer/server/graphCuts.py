import maxflow
import numpy as np

def edgeFactor(i1, i2, dist):
    return np.exp((i1 - i2)**2/0.5)/dist


def graphCut(img, probs):
    shape = img.shape
    total = shape[0]*shape[1]*shape[2]
    # Create a graph with integer capacities.
    g = maxflow.Graph[float](total, total*26)
    # Add two (non-terminal) nodes. Get the index to the first one.
    nodes = g.add_nodes(total)

    counts = np.zeros(shape)
    edgeCoeff = 0.2
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                index = i*shape[1]*shape[2] + j*shape[2] + k
                g.add_tedge(nodes[index],  -np.log(probs[i,j,k]), -np.log(1 - probs[i,j,k]))
                for img2d in range(i-1, i+2):
                    for coord in [[j, k+1], [j+1, k+1], [j+1, k], [j+1, k-1]]:
                        if (img2d >= 0 and coord[0] >= 0 and coord[1] >= 0) :
                            otherIndex = img2d*shape[1]*shape[2] + coord[0]*shape[2] + coord[1]
                            try:
                                edge = edgeCoeff*edgeFactor(img[i,j,k],
                                                            img[img2d, coord[0], coord[1]], 1)
                                g.add_edge(nodes[index], nodes[otherIndex], edge, edge)
                                #counts[i,j,k] += 1
                                #counts[img2d, coord[0], coord[1]] += 1
                            except(IndexError):
                                pass
                otherIndex = (i+1)*shape[1]*shape[2] + j*shape[2] + k
                if (i == 2 and j == 0 and k == 0):
                    print(otherIndex, img[i+1, j, k])
                          
                try:
                    edge = edgeCoeff*edgeFactor(img[i,j,k],
                                                img[i+1, j, k], 1)
                    g.add_edge(nodes[index], nodes[otherIndex], edge, edge)
                    #counts[i,j,k] += 1
                    #counts[i+1, j, k] += 1
                except(IndexError):
                    pass

    #print(counts)              
    flow = g.maxflow()

    for i in range(shape[0]):
        print(probs[i])
                
    for i in range(shape[0]):
        a = []
        for j in range(shape[1]):
            index = i * shape[1] + j
            a.append(g.get_segment(nodes[index]))
        print(a)
        
        
if __name__ == '__main__':
    img = np.array([
        np.array([np.array([0,0,0,0]), np.array([0,0,0,0]),
                  np.array([0,0,0,0]), np.array([0,0,0,0])]),
        np.array([np.array([0,0,0,0]), np.array([0,0,0,0]),
                  np.array([0,0,0,0]), np.array([0,0,0,0])]),
        np.array([np.array([0,0,0,0]), np.array([0,0,0,0]),
                  np.array([0,0,0,0]), np.array([0,0,0,0])]),
        np.array([np.array([0,0,0,0]), np.array([0,0,0,0]),
                  np.array([0,0,0,0]), np.array([0,0,0,0])])
        ])

    probs = np.array([
        np.array([np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5]),
                  np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5])]),
        np.array([np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5]),
                  np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5])]),
        np.array([np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5]),
                  np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5])]),
        np.array([np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5]),
                  np.array([0.5,0.5,0.5,0.5]), np.array([0.5,0.5,0.5,0.5])])
        ])
    graphCut(img, probs)
