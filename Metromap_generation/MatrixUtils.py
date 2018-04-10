import numpy as np
import scipy.sparse as sp

def init_matrix(shape, resetter):
    matrix = np.random.randint(2, size=shape)
    matrix = np.maximum(resetter, matrix)
    return matrix

def save_sparse_csr(filename, array):
    np.savez(filename, data=array.data, indices=array.indices,
             indptr=array.indptr, shape=array.shape)

def load_sparse_csr(filename):
    loader = np.load(filename)
    return sp.csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                      shape=loader['shape'])

def dot(X, Y):
    if sp.isspmatrix(X) and sp.isspmatrix(Y):
        return X * Y
    elif sp.isspmatrix(X) or sp.isspmatrix(Y):
        # avoid dense dot product with mixed factors
        return sp.csr_matrix(X) * sp.csr_matrix(Y)
    else:
        return np.asmatrix(X) * np.asmatrix(Y)

def save_snap_format(V, idx2term):
    edge_file = open("snap/edges", "w")
    for i in range(len(V.rows)):
        for index in V.rows[i]:
            edge_file.write(str(i) + "\t" + str(index) + "\n")
            edge_file.write(str(index) + "\t" + str(i) + "\n")
    edge_file.close()
    labels_file = open("snap/labels", "w")
    for i in range(len(V.rows)):
        labels_file.write(str(i) + "\t" + str(idx2term[str(i)]) + "\n")
    labels_file.close()