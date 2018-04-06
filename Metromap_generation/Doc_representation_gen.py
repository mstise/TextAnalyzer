#!/usr/bin/env python
import codecs
import os
import re
from scipy.sparse import csr_matrix, lil_matrix, rand
import shelve
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

DISAMBIGUATED_PATH = 'Disambiguated'

def get_doc_representation(document_path, incl_ents=False):
    if incl_ents:
        doc2ents = get_doc2ents()
        doc2terms = get_top50_tfidf(document_path, doc2ents=doc2ents)
        populate_ents(doc2terms, doc2ents)
    else:
        doc2terms = get_top50_tfidf(document_path)
    return doc2terms

def get_doc2ents():
    doc2ents = {}
    for filename in os.listdir(DISAMBIGUATED_PATH):
        d_ents = get_disambiguations(filename, DISAMBIGUATED_PATH)
        dent_set = set() #We do not want multiple of the same disambiguations per doc
        for d_ent in d_ents:
            if str(d_ent[:4]) != 'None':
                dent_set.add('*' + d_ent)
            else:
                dent_set.add(str(d_ent[5:]))
        doc2ents[filename] = list(dent_set)

    return doc2ents

def populate_ents(doc2terms, doc2ents):
    for filename in doc2ents:
        tmp = list(doc2terms[filename])
        tmp.extend(doc2ents[filename])
        doc2terms[filename] = tmp

def get_top50_tfidf(document_path, doc2ents={}):
    vectorizer = TfidfVectorizer(input='filename', stop_words=create_stop_words(350, doc2ents=doc2ents), token_pattern=r"(?u)\b[a-zA-ZøØæÆåÅ]\w+\b")#, max_features=50)
    full_filenames = [os.path.join(document_path, each) for each in os.listdir(document_path)]
    tfidf_result = vectorizer.fit_transform(list(full_filenames))
    feature_terms = vectorizer.get_feature_names()
    doc2terms = shelve.open("dbs/doc2terms")
    doc2features = shelve.open("dbs/doc2features")
    for i in range(0, len(full_filenames)):
        if i % 100 == 0:
            print(i)
        scores = zip(feature_terms,
                     tfidf_result[i,:].toarray()[0])
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:50]
        filename = full_filenames[i].split('/')[-1]
        sorted_terms = list(zip(*(sorted_scores[:50])))[0] #this only took the words :b
        doc2terms[filename] = sorted_terms
        doc2features[filename] = lil_matrix(tfidf_result[i,:].toarray()[0])
    return doc2terms

def create_stop_words(limit = 150, doc2ents = {}):
    stop_words = []
    counter = 0
    with open('5000_common_terms') as f:
        for line in f:
            if counter == limit:
                break
            splits = line.split()
            stop_words.append(splits[0])
            counter += 1
    if doc2ents.keys(): #if not empty
        dent_set = set()
        for filename in doc2ents.keys():
            for d_ent in doc2ents[filename]:
                for dent_word in str(d_ent[2:]).split():
                    if dent_word[0] == '(':  # so we dont include last part of: Thomas (footballplayer)
                        break
                    dent_set.add(dent_word)
        stop_words.extend(list(dent_set))

    return stop_words

def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    if len(indices) < 2:
        print('following line is corrupted: ' + line)
        return ''
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line

def get_disambiguations(filename, path):
    entities = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        if new_line == '': continue
        if new_line == 'None':
            new_line = new_line + ' ' + line.split(',')[0]
        entities.append(new_line)
    return entities