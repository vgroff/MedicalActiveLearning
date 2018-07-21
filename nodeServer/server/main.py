import sys, json, numpy as np

import graphCut from graphCuts


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
