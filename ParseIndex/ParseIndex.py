import os
import xml.etree.ElementTree
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *

ix = open_dir("/home/erisos/WhooshTest")

from whoosh.qparser import QueryParser
with ix.searcher() as searcher:
    query = QueryParser("content", ix.schema).parse("er")
    results = searcher.search(query)
    for result in results:
        print(result)