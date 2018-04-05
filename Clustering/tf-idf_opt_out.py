import shelve
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_matrix_for_similarity(partition, dict):
    matrix = []
    for docidx in range(len(partition)):
        matrix.append(dict[partition[docidx]].toarray()[0])
    temp = np.array(matrix)

    return sparse.csr_matrix(temp)

# Input: List of lists containing document names and optionally a threshold for the cosine similarity scores
# Output 1: List of lists containing the document names of the documents found to be similar to at least one other document within its timeslice
# Output 2: List of lists containing the document names of the documents found to be similar to no other documents within its timeslice
def do_pre_processing(partitioned_docs, threshold=0.15):
    partitioned_docs_included = []
    partitioned_docs_excluded = []
    dict = shelve.open("/home/michael/PreProcessing/doc2features/doc2features")

    # Remove noid documents before starting the similarity comparison
    for partition in partitioned_docs:
        for document in partition:
            if '_noid' in document:
                partition.remove(document)

    # Compare documents using cosine similarity
    for partition in partitioned_docs:
        incl = []
        excl = []

        if len(partition) == 1:
            partitioned_docs_included.append([])
            partitioned_docs_excluded.append(partition)
            continue

        matr = create_matrix_for_similarity(partition, dict)
        similarity = cosine_similarity(matr)
        for row in range(len(similarity)):
            if partition[row] in incl:
                continue
            for column in range(len(similarity[row])):
                if row == column:
                    continue
                if similarity[row, column] > threshold:
                    if partition[row] not in incl:
                        incl.append(partition[row])
                    if partition[column] not in incl:
                        incl.append(partition[column])
                    break
        for doc in partition:
            if doc not in incl:
                excl.append(doc)
        partitioned_docs_included.append(incl)
        partitioned_docs_excluded.append(excl)

    return partitioned_docs_included, partitioned_docs_excluded