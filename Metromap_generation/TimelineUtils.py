from Metromap_generation.nmf import Nmf
import re

def factorize(V, rank, resetter, W=None, H=None, update="log_update", objective="log_obj"):
    #Do this: V = V.tocsr(), before nmf, if update is eucledian or divergence... makes it faster
    nmf_inst = Nmf(V, rank, max_iter=35, W=W, H=H, update=update,
                    objective=objective, resetter=resetter)
    basis, coef, obj = nmf_inst.factorize()
    return basis, coef, obj

def get_rec_disamb_pairs(filename, path):
    entities = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        if new_line == '': continue
        if new_line[:2] == 'w.' or new_line == 'None':
            entities.append((line.split(',')[0], new_line))
    return entities

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