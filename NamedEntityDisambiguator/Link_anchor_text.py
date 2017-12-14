import re
from NamedEntityDisambiguator import Utilities
import shelve
import os

def lat(text):
    if text == None:
        return []
    text = text.lower()
    with_split = re.findall(r'\[\[[^\]]*\|[^\]]*\]\]', text)
    without_split = re.findall(r'\[\[[^\]]\]\]', text)
    return with_split + without_split

def find_link_anchor_texts(wiki_tree_root):
    title = ''
    anchor_texts = []
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'title':
                    title = page_child.text.lower()
                #if title in names:
                    if Utilities.cut_brackets(page_child.tag) == 'revision':
                        for text in page_child:
                            if Utilities.cut_brackets(text.tag) == 'text':
                                result = lat(text.text)
                                if len(result) > 0:
                                    anchor_texts.append([title, result])

    new_anchor_texts = shelve.open("NamedEntityDisambiguator/dbs/link_anchor_dic")
    #new_anchor_texts = {}
    for entity_with_lat in anchor_texts:
        new_entity_with_lat = [entity_with_lat[0], []]
        for text in entity_with_lat[1]:
            if 'fil:' in text:
                continue
            if '|' in text:
                text = re.findall(r'\|[^\]]*\]\]', text)[0]
                text = text[1:-2]
            else:
                text = text[2:-2]
            new_entity_with_lat[1].append(text)
        new_anchor_texts[new_entity_with_lat[0].lower()] = new_entity_with_lat[1]

    new_anchor_texts.close()
    f = open("NamedEntityDisambiguator/dbs/link_anchor_dic.txt", "w")
    f.write(str(os.path.getmtime("NamedEntityDisambiguator/Link_anchor_text.py")))
    f.close()

#from lxml import etree
#import paths
#tree = etree.parse(paths.get_wikipedia_article_path())
#root = tree.getroot()
#print(find_link_anchor_texts(["anders fogh rasmussen"], root))