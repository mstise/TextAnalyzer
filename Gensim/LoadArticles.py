from gensim import corpora
import os
import xml.etree.ElementTree

def readXML(node):
    global body
    global header
    tag = node.tag[38:]
    if (tag == "p"):
        if (isinstance(node.text, str)):
            body += node.text
    if (tag == "hl1"):
        header = node.text
    for child in node:
        readXML(child)

body = ""
header = ""
counter = 0
bodies = []

for subdir, dirs, files in os.walk('/home/erisos/Articles/mnt/newsarchive_share'):
    if (subdir[-10:] == "/TabletXML"):
        counter += 1
        if counter == 10:
            break
        for filename in os.listdir(subdir):
            if (filename[-4:] == ".xml"):
                readXML(xml.etree.ElementTree.parse(subdir + '/' + filename).getroot())
                bodies.append(body)
                body = ""
                header = ""

#tokenize
class MyCorpus(object):
    def __iter__(self):
        for line in open('mycorpus.txt'):
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())

texts = [[word for word in document.lower().split()] for document in bodies ]

print(texts)