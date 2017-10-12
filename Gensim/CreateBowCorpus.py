from gensim import corpora
import os
import xml.etree.ElementTree
from six import iteritems
import paths

dictionary = corpora.Dictionary()
dictionary.load("newsDict")
#tokenize
class MyCorpus(object):
    def __iter__(self):
        for filename in os.listdir(paths.get_external_disk_path()):
            for string in open(filename):
                # there is one string per document, tokens separated by whitespace
                yield dictionary.doc2bow(string.lower().split())

