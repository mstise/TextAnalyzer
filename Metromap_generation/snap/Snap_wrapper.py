import os
from scipy.sparse import csr_matrix
import numpy as np

def snap(num_docs):
    print('NUM DOCS: ' + str(num_docs))
    if num_docs > 8:
        num_docs = int(num_docs / 2)
    os.system("./snap/bigclam -o:snap/snapout/ -c:-1 -i:snap/edges -l:snap/labels -nc:" + str(num_docs) + " -mc:1 -xc:" + str(num_docs))

def get_data(term2idx, resetter, V):
    file = open('snap/snapout/cmtyvv.txt', 'r')
    lines = file.readlines()
    num_cmtys = len(lines)
    W = np.zeros((V.shape[0], num_cmtys))
    cmty_counter = 0
    for line in lines:
        tuples = line[:-1].split('\t')
        for tuple in tuples[:-1]:
            term, weight = tuple.split(',')
            W[term2idx[term], cmty_counter] = float(weight)
            if float(weight) == 0.0:
                W[term2idx[term], cmty_counter] = float(weight) + resetter * 2
        cmty_counter += 1
    W = np.maximum(resetter, W)
    return csr_matrix(W)





    #for i in list(W.shape)[0]:
