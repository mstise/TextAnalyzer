from gensim import corpora
import os
import xml.etree.ElementTree
from six import iteritems
import paths

def what(thisis):
    return thisis

# collect statistics about all tokens
whatsthis = list(what(line.lower().split() for line in open('mycorpus.txt')))
dictionary = corpora.Dictionary(line.lower().split() for line in open('mycorpus.txt'))
dictionary.add_documents(line.lower().split() for line in open('mycorpus2.txt'))
# remove stop words and words that appear only once
#stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
#            if stopword in dictionary.token2id]
#dictionary.filter_tokens(stop_ids + once_ids)  # remove stop words and words that appear only once
#dictionary.compactify()  # remove gaps in id sequence after words that were removed
#print(dictionary)


body = ""
header = ""
bodies = []
dictionary = corpora.Dictionary()

for filename in os.listdir(paths.get_external_disk_path()):
    dictionary.add_documents(line.lower().split() for line in open(filename))
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
dictionary.filter_tokens(once_ids)  # remove stop words and words that appear only once
dictionary.compactify()  # remove gaps in id sequence after words that were removed
#tokenize
class MyCorpus(object):
    def __iter__(self):
        for line in open('mycorpus.txt'):
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())

texts = [[word for word in document.lower().split()] for document in bodies ]

print(texts)

