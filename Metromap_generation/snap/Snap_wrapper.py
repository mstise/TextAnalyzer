import os
from scipy.sparse import csr_matrix
from Metromap_generation.MatrixUtils import init_matrix

def snap(num_docs):
    print('MAX CLUSTERS: ' + str(int(num_docs/2)))
    print('NUM DOCS: ' + str(num_docs))
    os.system("./snap/bigclam -o:snap/snapout/ -c:-1 -i:snap/edges -l:snap/labels -nc:" + str(num_docs) + " -mc:1 -xc:" + str(num_docs))

def get_data(term2idx, V):
    file = open('snap/snapout/cmtyvv.txt', 'r')
    lines = file.readlines()
    num_cmtys = len(lines)
    W = init_matrix((list(V.shape)[0], num_cmtys), 0.0)
    cmty_counter = 0
    for line in lines:
        tuples = line[:-1].split('\t')
        for tuple in tuples:
            term, weight = tuple.split(',')
            W[term2idx[term], cmty_counter] = weight
        cmty_counter += 1



    return csr_matrix(W)





    #for i in list(W.shape)[0]:
