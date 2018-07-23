import sys, json
import numpy as np

import graphCuts


#Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])



def main():
    #get our data as an array from read_in()
    lines = read_in()

    #create a numpy array
    np_lines = np.array(lines)

    print("Welcome ", type(sys.argv[1]), type(np_lines), np_lines)

    return

#start process
if __name__ == '__main__':
    main()

# To-do:
# - Edit front-end to have a "graph-cut" button that tells you to give annotations and then produces the graph cut - need to know what to set the regional terms of scribbles to
# - Build an easy 3-D image for nice segmenting, or use one we already have if unnecessary - perhaps use a pre-cropped one? Might be good to deal with this soon. I the long term, will need to uncrop them aswell.
# - Look into what the edge factor needs to be when normalised?

# 73AAE9D75A7CFCD732DC359F26
