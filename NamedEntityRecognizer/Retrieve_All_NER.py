#From folder of recognized entities, retrieve ALL recognized mentions into a set: s

import os
import re

def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line


def ner_retriever(path="/home/duper/Desktop/tmp"):
    s = set()
    for filename in os.listdir(path):
        for line in open(path + "/" + filename):
            new_line = clean_line(line)
            s.add(new_line)
    return s

s = ner_retriever()

