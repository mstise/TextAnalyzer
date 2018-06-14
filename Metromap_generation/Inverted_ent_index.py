#!/usr/bin/python
import random
import numpy as np
random.seed(10)
np.random.seed(10)
import shelve
import os
from Metromap_generation.TimelineUtils import get_rec_disamb_pairs

def append(dic, key, val):
    tmp = dic[key]
    tmp.append(val)
    dic[key] = tmp

docidx2name = shelve.open('dbs/docidx2name')
ent2doctuple = shelve.open('dbs/ent2doctuple')
#print(sorted(list(docidx2name.keys()), key=lambda k: int(k)))
idxcounter = 0

total_docs = len(os.listdir('Disambiguated'))
for filename in os.listdir('Disambiguated'):
    if idxcounter % 500 == 0:
        print(str(idxcounter) + ' out of ' + str(total_docs))
    rec_disamb_pairs = get_rec_disamb_pairs(filename, 'Disambiguated')
    counter_dic = {}
    for rec_disamb_pair in rec_disamb_pairs:
        rec = '*r' + rec_disamb_pair[0].lower().replace('.', '')
        disamb = '*w' + str(rec_disamb_pair[1][2:]).lower().replace('.', '')
        counter_dic.setdefault(rec, 0)
        counter_dic[rec] += 1
        if disamb != '*wne': #if none
            counter_dic.setdefault(disamb, 0)
            counter_dic[disamb] += 1
    for wr_key in counter_dic:
        ent2doctuple.setdefault(wr_key, [])
        append(ent2doctuple, wr_key, (idxcounter, counter_dic[wr_key]))
    docidx2name[str(idxcounter)] = filename
    idxcounter += 1
