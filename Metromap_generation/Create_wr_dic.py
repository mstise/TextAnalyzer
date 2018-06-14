from Metromap_generation.TimelineUtils import get_rec_disamb_pairs
import random
import itertools
import scipy.sparse as sp
import numpy as np
random.seed(10)
np.random.seed(10)
import shelve
import os

DISAMBIGUATED_PATH = 'Disambiguated'

dis2rec = shelve.open('dbs/dis2rec')

for filename in os.listdir('example_documents/Socialdemokratiet'):
    d_ents = get_rec_disamb_pairs(filename, DISAMBIGUATED_PATH)
    for d_ent in d_ents:
        dis = '*w' + d_ent[1][2:].lower().replace('.','')
        rec = '*r' + d_ent[0].lower().replace('.','')
        if dis == '*wnone':
            continue
        dis2rec.setdefault(dis, [])
        tmp = dis2rec[dis]
        if rec not in tmp:
            tmp.append(rec)
            dis2rec[dis] = tmp