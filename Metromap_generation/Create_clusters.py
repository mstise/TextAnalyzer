#!/usr/bin/python
import random
import os
import itertools
#import Clustering.python_lil as sp
import matplotlib.pylab as plb
import scipy.sparse as sp
import numpy as np
random.seed(10)
np.random.seed(10)
from Metromap_generation.Doc_representation_gen import get_doc_representation
from scipy.sparse import csr_matrix, lil_matrix, rand
import shelve
import math
from Metromap_generation.MatrixUtils import init_matrix, save_sparse_csr, load_sparse_csr, save_snap_format
from scipy.stats import bernoulli
from Metromap_generation.Resolution import resolutionize
from Metromap_generation.CosinePreProc import do_pre_processing
import paths
from Metromap_generation.TimelineUtils import factorize
import Metromap_generation.snap.Snap_wrapper as Swrapper

####################################################################################################################################
                                    #            SAVING            #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #

load_adj = False        #False: Creates new adjacency matrix from docs (skal være False hvis paper_epsilon = True)                  #
load_tf_idf = True      #False: Creates new mapping between target docs to tf-idf                                                  #
load_W = False          #False: Cluster words by gradient descent                                                                  #
                                                                                                                                   #
####################################################################################################################################
                                    #       Cluster-Options        #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #
                                                                                                                                   #
cluster_size = 3 #How many clusters?                                                                                               #
group_size = 3 #how many timelines?                                                                                                #
resetter = 0.001  #Resets to this value, if update is below it.                                                                    #
#resetter can take the following values:                                                                                           #
#resetter = 0.001 works best for now (paper_epsilon will have to be false in this case)                                            #
#resetter = 10**(-8) #This seems to be too low, and makes updates too large for convergence                                        #
#resetter = 0 # In this case, the divide by zero is handled by taking highest seen value to date (updates too large here as well)  #
paper_epsilon = False #If false the epsilon is used directly as threshold for clustering, with resetter-value                      #
paper_noisify = False #Introduce noise in graph according to paper. This slows down the approach considerably (for litte dataset atleast)
resolution='month'
incl_ents=True #includ d_entities in tf-idf scheme
snapclam = False




########################################################################################################################


def run():
    partitioned_docs = resolutionize('example_documents/Aalborg_pirates', resolution=resolution)#new_examples Example_documents
    pdocs_incl, pdocs_excl = do_pre_processing(partitioned_docs)
    if load_adj:
        efile = open('dbs/epsilons', 'r')
    else:
        efile = open('dbs/epsilons', 'w') #this line also reset the file
    term2clusters = shelve.open("dbs/term2clusters")
    clusters2term = shelve.open("dbs/clusters2term")
    clustercount = 0
    for i in range(0, len(pdocs_incl)):
        if len(pdocs_incl[i]) == 0:
            print('iteration ' + str(i) + ' is skipped')
            continue
        epsilon = None
        if load_adj:
            V = load_sparse_csr('dbs/V' + str(i) + '.npz').tolil()
            term2idx = shelve.open('dbs/term2idx' + str(i))
            idx2term = shelve.open('dbs/idx2term' + str(i))
        else:
            term2idx = shelve.open("dbs/term2idx" + str(i))
            idx2term = shelve.open("dbs/idx2term" + str(i))
            V, term2idx, idx2term, epsilon = create_dicts(pdocs_incl[i], term2idx, idx2term)
            save_snap_format(V, idx2term)
            Swrapper.snap(len(pdocs_incl[i]))
            save_sparse_csr('dbs/V' + str(i), V.tocsr())
            efile.write(str(epsilon) + '\n')
        if load_W:
            W = load_sparse_csr('dbs/W' + str(i) + '.npz').tolil()
        else:
            if snapclam:
                W = Swrapper.get_data(term2idx, V=V)
            else:
                W = init_matrix((list(V.shape)[0], cluster_size), resetter)
                #W = create_clusters(V, len(pdocs_incl[i]))
                W, _, obj = factorize(V, cluster_size, resetter, W=W)
                save_sparse_csr('dbs/W' + str(i), W.tocsr())
        plot(W, idx2term)
        fill_clusters(epsilon, W, idx2term, term2clusters, clusters2term, clustercount)
        clustercount += cluster_size
        term2idx.close()
        idx2term.close()
        if i == 1:
            print(pdocs_incl[i])
            break

    efile.write(str(clustercount) + '\n')  # last line contain num clustered docs
    efile.close()

    from TopicSummarization.Topic_summarization import ts
    topic_summarization = ts(clusters2term, pdocs_incl)

    term2clusters.close()
    clusters2term.close()

#This also evaluate cluster size
def create_clusters(V, num_docs):
    possible_sizes = list(range(1, num_docs + 2))
    if len(possible_sizes) == 2:
        W, _ = spectrum_nmf(V, 0, 0, possible_sizes)
        return W
    lower_idx = 0
    upper_idx = len(possible_sizes) - 1
    middle_idx = math.floor((len(possible_sizes) - 1) / 2)
    while (upper_idx - lower_idx) > 1: #Continue until only 2 cluster_sizes left and then choose lowest
        W_lower, curr_obj_lower = spectrum_nmf(V, lower_idx, middle_idx, possible_sizes)
        W_upper, curr_obj_upper = spectrum_nmf(V, middle_idx + 1, upper_idx, possible_sizes)
        if curr_obj_lower < curr_obj_upper:
            upper_idx = middle_idx
            middle_idx = math.floor(len(possible_sizes[lower_idx : middle_idx]) / 2)
            W = W_lower
        else:
            lower_idx = middle_idx + 1
            middle_idx = lower_idx + math.floor(len(possible_sizes[middle_idx + 1: upper_idx]) / 2)
            W = W_upper
    return W

def spectrum_nmf(V, lower_idx, upper_idx, possible_sizes):
    tmp_sizes = list(possible_sizes[lower_idx : upper_idx + 1])
    idx = math.floor((len(tmp_sizes) - 1) / 2)
    cluster_size = tmp_sizes[idx]
    W = init_matrix((list(V.shape)[0], cluster_size), resetter)
    W, _, obj = factorize(V, cluster_size, resetter, W=W)
    return W, obj

def fill_clusters(epsilon, W, idx2term, term2clusters, clusters2term, clustercount):
    w_arr = W.toarray()
    for i in range(0, W.shape[0]):
        term = idx2term[str(i)]
        clusters = []
        for j in range(0, W.shape[1]):
            if w_arr[i,j] > limit(epsilon):
                clusters.append(clustercount + j)
            if str(clustercount + j) not in clusters2term:
                clusters2term[str(clustercount + j)] = [(term, w_arr[i,j])]
            else:
                tmp = clusters2term[str(clustercount + j)]
                tmp.append((term, w_arr[i,j]))
                clusters2term[str(clustercount + j)] = tmp
        term2clusters[term] = clusters

def limit(epsilon):
    if paper_epsilon:
        return math.sqrt(-math.log(1 - epsilon))
    else:
        return resetter

def create_dicts(filenames, term2idx, idx2term):
    print("Creating dicts")

    #doc2terms = get_top50_tfidf(document_path='/home/duper/Documents/NewsClustering/TextAnalyzer/Clustering/Example_documents') #skal have full path apparantly
    if load_tf_idf:
        doc2terms = shelve.open("dbs/doc2terms")
    else:
        doc2terms = get_doc_representation(
            document_path='Processed_news', incl_ents=incl_ents) #Processed_news Example_documents
    print('1')
    term2docidx = idx_terms(filenames, doc2terms, idx2term, term2idx) #idx2term and term2idx also gets filled
    print('2')
    V = create_adj(filenames, term2docidx, term2idx)
    print('3')

    if paper_noisify:
        V, epsilon = add_random_edges(V)
    if not paper_epsilon:
        epsilon = resetter
    return V.tolil(), term2idx, idx2term, epsilon #V in CSR format has faster arithmetic and matrix vector operations


def create_adj(filenames, term2docidx, term2idx):
    num_unique_terms = len(term2docidx.keys())
    V = sp.lil_matrix((num_unique_terms, num_unique_terms))  # This is the adjacency matrix to factorize
    tempterm2docidx = {k: v for k, v in term2docidx.items() if len(v) > 1}
    unique_terms = tempterm2docidx.keys()  # Use only terms which is referenced in at least 2 documents without any loss in result! (speeds the method up)
    debug_counter = 0
    for (term1, term2) in itertools.combinations(unique_terms,
                                                 2):  # term1 ='dog', term2='dog' does not happen on purpose!
        shared_docs = set(term2docidx[term1]).intersection(term2docidx[term2])
        if len(shared_docs) < float(len(filenames)) * 0.05 or len(
                shared_docs) < 2:  # Hvis vægt er mindre end max mulige vægt, er co-occurence for lav til at vi laver en edge imellem knuderne
            continue
        V[term2idx[term1], term2idx[term2]] = len(shared_docs)
        V[term2idx[term2], term2idx[term1]] = len(shared_docs)
        debug_counter += 1
        print('shared: ' + term1 + ', ' + term2 + ' in ' + str(len(shared_docs)) + ' docs')
    return V


def idx_terms(filenames, doc2terms, idx2term, term2idx):
    term2docidx = {}
    doc2docidx = {}
    term_idx = 0
    doc_idx = 0
    for filename in filenames:
        if doc_idx % 1000 == 0:
            print(doc_idx)
        doc2docidx[filename] = term_idx
        for term in doc2terms[filename]:
            if term[0] == 'a' and str(term[1]).isdigit():
                continue
            term = term_preprocess(term)
            if term == '':
                continue
            if term not in term2docidx:
                term2docidx[term] = [doc_idx]
            if term2docidx[term][-1] != doc_idx:
                tmp = term2docidx[term]
                tmp.append(doc_idx)
                term2docidx[term] = tmp

            if term not in term2idx:
                term2idx[term] = term_idx
                idx2term[str(term_idx)] = term
                term_idx += 1
        doc_idx += 1
    return term2docidx


def add_random_edges(V):
    #add to V random epsilon value which is 2|E|/|V|(|V|−1)
    num_edges = 0
    for i in range(0, V.shape[0]):
        num_edges += len(V.rows[i])
    epsilon = (2 * num_edges) / (V.shape[0] * (V.shape[0] - 1))
    rvs = bernoulli(1).rvs
    one_matrix = sp.random(V.shape[0], V.shape[0], density=epsilon, format='lil', data_rvs=rvs)
    V = V + one_matrix
    return V, epsilon


def term_preprocess(term):
    # lowers and remove stop words, digits, symbols, too short words
    term = term.strip().replace(',', '').replace('.', '').replace('(', '').replace(')', '').replace('?', '').replace(
        '!', '').replace(':', '').replace(';', '').replace('+', '').replace('-', '').replace('*', '')
    term = term.lower()
    if term in additional_stop_words or str.isdigit(term):
        term = ''
    return term

def plot(W, idx2term):
    print("Plot basisvectors")
    for basisvector_idx in range(W.shape[1]):
        top10 = np.argsort(np.asarray(W[:, basisvector_idx].todense()).flatten())[-10:]
        val = W[top10, basisvector_idx].todense()
        plb.figure(basisvector_idx)
        plb.barh(np.arange(10) + .5, val, color="blue", align="center", height=0.4)
        plb.yticks(np.arange(10) + .5, [idx2term[str(idx)] for idx in top10])
        plb.xlabel("Weight")
        plb.ylabel("Term")
        plb.title("Top10 terms in basisvector " + str(basisvector_idx))
        plb.savefig("Visual_output/documents_basisW%d.png" % (basisvector_idx), bbox_inches="tight")

additional_stop_words = [
    ".", " ", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
    "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)",
    "bliver", "ligger", "siger", "mange", "får", "siden"]

if __name__ == "__main__":
    run()