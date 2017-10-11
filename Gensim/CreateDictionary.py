from gensim import corpora
import os
from six import iteritems
import paths

# remove stop words and words that appear only once
#stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
#            if stopword in dictionary.token2id]
#dictionary.filter_tokens(stop_ids + once_ids)  # remove stop words and words that appear only once
#dictionary.compactify()  # remove gaps in id sequence after words that were removed
#print(dictionary)

dictionary = corpora.Dictionary()

for filename in os.listdir(paths.get_external_disk_path()):
    dictionary.add_documents(line.lower().split() for line in open(paths.get_external_disk_path() + "/" + filename))
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
dictionary.filter_tokens(once_ids)  # remove stop words and words that appear only once
dictionary.compactify()  # remove gaps in id sequence after words that were removed
dictionary.save("newsDict")

class MyCorpus(object):
    def __iter__(self):
        for filename in os.listdir(paths.get_external_disk_path()):
            for string in open(paths.get_external_disk_path() + "/" + filename):
                # there is one string per document, tokens separated by whitespace
                yield dictionary.doc2bow(string.lower().split())

corpus = MyCorpus()
counter = 0
for document in corpus:
    if counter == 10:
        break
    print(document)
    counter += 1