import maxflow
import numpy as np

def edgeFactor(i1, i2, dist):
    return np.exp((i1 - i2)**2/0.5)/dist

shape = [3,3]
total = shape[0]*shape[1]

# Create a graph with integer capacities.
g = maxflow.Graph[float](total, total*8)
# Add two (non-terminal) nodes. Get the index to the first one.
nodes = g.add_nodes(9)

probs = [ [0.1, 0.2, 0.85],
          [0.1, 0.45, 0.95],
          [0.2, 0.8, 0.8]
          ]
edgeCoeff = 0.2
for i in range(shape[0]):
    for j in range(shape[1]):
        index = i * shape[1] + j
        onRight = index + 1
        onBottom = index + shape[1]
        onBottomRight = onBottom + 1
        onBottomLeft = onBottom - 1
        g.add_tedge(nodes[index],  -np.log(probs[i][j]), -np.log(1 - probs[i][j]))
        try:
            edge = edgeCoeff*edgeFactor(probs[i][j], probs[i][j+1], 1)
            print(edge)
            g.add_edge(nodes[index], nodes[onRight], edge, edge)
        except(IndexError):
            pass
        try:
            edge = edgeCoeff*edgeFactor(probs[i][j], probs[i+1][j], 1)
            g.add_edge(nodes[index], nodes[onBottom], edge, edge)
        except(IndexError):
            pass
        try:
            edge = edgeCoeff*edgeFactor(probs[i][j], probs[i+1][j+1], 2**0.5)
            g.add_edge(nodes[index], nodes[onBottomRight], edge, edge)
        except IndexError:
            pass
        try:
            edge = edgeCoeff*edgeFactor(probs[i][j], probs[i+1][j-1], 2**0.5)
            g.add_edge(nodes[index], nodes[onBottomLeft], edge, edge)
        except IndexError:
            pass
            
flow = g.maxflow()
print(flow)

for i in range(shape[0]):
    print(probs[i])

for i in range(shape[0]):
    a = []
    for j in range(shape[1]):
        index = i * shape[1] + j
        a.append(g.get_segment(nodes[index]))
    print(a)
        
