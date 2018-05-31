#!/usr/bin/env python
import codecs
import os
import re
from scipy.sparse import csr_matrix, lil_matrix, rand
import shelve
from Metromap_generation.TimelineUtils import get_rec_disamb_pairs
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

DISAMBIGUATED_PATH = 'Disambiguated'
incl_ents = True

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
        d_ents = get_rec_disamb_pairs(filename, DISAMBIGUATED_PATH)
        dent_set = set() #We do not want multiple of the same disambiguations per doc
        for d_ent in d_ents:
            if str(d_ent[1]) != 'None':
                dent_set.add('*w.' + d_ent[0])
            else:
                dent_set.add('*r.' + str(d_ent[0]))
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
        sorted_terms = []
        counter = 0
        for score in sorted_scores:
            if score[1] == 0.0 or counter == 50:
                break
            sorted_terms.append(score[0])
            counter += 1
        filename = full_filenames[i].split('/')[-1]
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
                for dent_word in str(d_ent[3:]).split():
                    if dent_word[-2:] == 'en':
                        dent_set.add(str(dent_word[:-1]).lower())
                        dent_set.add(str(dent_word[:-2]).lower())
                    if dent_word[-1:] == 's':
                        dent_set.add(str(dent_word[:-1]).lower())
                    if dent_word[-2:] == 'er':
                        dent_set.add(str(dent_word[:-1]).lower())
                        dent_set.add(str(dent_word[:-2]).lower())
                    if dent_word[-1:] == 'e':
                        dent_set.add(str(dent_word[:-1]).lower())

                    dent_set.add(dent_word.lower())
        stop_words.extend(list(dent_set))

    return stop_words

doc2terms = get_doc_representation(document_path='Lemmatized', incl_ents=incl_ents) #Processed_news