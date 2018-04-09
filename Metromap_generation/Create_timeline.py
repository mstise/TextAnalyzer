#!/usr/bin/python
import random
import os
import itertools
import matplotlib.pylab as plb
import scipy.sparse as sp
import numpy as np
random.seed(10)
np.random.seed(10)
import nimfa
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, lil_matrix, rand
import shelve
import math
from scipy.stats import bernoulli
from Metromap_generation.MatrixUtils import init_matrix
from Metromap_generation.TimelineUtils import factorize

####################################################################################################################################
                                    #            SAVING            #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #
#load_adj = True        #False: Creates new adjacency matrix from docs (skal være False hvis paper_epsilon = True)                  #
#load_tf_idf = True      #False: Creates new mapping between target docs to tf-idf                                                  #
#load_W = True          #False: Cluster words by gradient descent                                                                  #
                                                                                                                                   #
####################################################################################################################################
                                    #       Cluster-Options        #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #
                                                                                                                                   #                                                                                           #
group_size = 3 #how many timelines?                                                                                                #
resetter = 0.001  #Resets to this value, if update is below it.                                                                    #
#resetter can take the following values:                                                                                           #
#resetter = 0.001 works best for now (paper_epsilon will have to be false in this case)                                            #
#resetter = 10**(-8) #This seems to be too low, and makes updates too large for convergence                                        #
#resetter = 0 # In this case, the divide by zero is handled by taking highest seen value to date (updates too large here as well)  #
paper_epsilon = False #If false the epsilon is used directly as threshold for clustering, with resetter-value                      #
#paper_noisify = False #Introduce noise in graph according to paper. This slows down the approach considerably (for litte dataset atleast)





########################################################################################################################

def run():
    #TODO: Need to collect W's for each cluster, and the corresponding calculated epsilon
    epsilons = open('dbs/epsilons', 'r').readlines()
    num_clusters = int(epsilons[-1])
    del(epsilons[-1])
    term2clusters = shelve.open("dbs/term2clusters")
    overallidx2term = shelve.open("dbs/overallidx2term")
    #term2idx, idx2term = overall_dics(num_doc_clusters)
    #cluster_adj = create_cluster_adj(epsilon, W)
    cluster_adj = create_cluster_adj(term2clusters, num_clusters, overallidx2term)
    W2 = init_matrix((list(cluster_adj.shape)[0], group_size), resetter)
    H2 = init_matrix((list(cluster_adj.shape)[1], group_size), resetter)
    W2, H2 = factorize(cluster_adj, group_size, resetter, W=W2, H=H2, update="log_update_2_mat", objective="log_obj_2_mat")


def create_cluster_adj(term2clusters, num_clusters, overallidx2term):
    total_terms = term2clusters.keys()
    cluster_adj = np.empty((len(total_terms), num_clusters))
    term_counter = 0
    for term in total_terms:
        lst = np.zeros((1, num_clusters))
        clusters = term2clusters[term]
        for cluster in clusters:
            lst[0,cluster] = 1
        cluster_adj[term_counter,:] = lst
        overallidx2term[str(term_counter)] = term
        term_counter += 1

    return csr_matrix(cluster_adj)

if __name__ == "__main__":
    run()