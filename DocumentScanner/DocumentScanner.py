import os
import xml.etree.ElementTree
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *

def readXML(node):
    global body
    global header
    tag = node.tag[38:]
    if (tag == "p"):
        if (isinstance(node.text, str)):
            if body[-1] != ' ':
                body += ' '
            body += node.text
    if (tag == "hl1"):
        header = node.text
    for child in node:
        readXML(child)

body = ""
header = ""

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
ix = create_in("/home/erisos/WhooshTest", schema)
writer = ix.writer()

for subdir, dirs, files in os.walk('/home/erisos/Articles/mnt/newsarchive_share'):
    if (subdir[-10:] == "/TabletXML"):
        for filename in os.listdir(subdir):
            if (filename[-4:] == ".xml"):
                readXML(xml.etree.ElementTree.parse(subdir + '/' + filename).getroot())
                writer.add_document(title=header, path=filename,
                                    content=body)
                body = ""
                header = ""

writer.commit()