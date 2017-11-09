import re
from NamedEntityDisambiguator import Utilities

def lat(text):
    if text == None:
        return []
    with_split = re.findall(r'\[\[[^\]]*\|[^\]]*\]\]', text)
    without_split = re.findall(r'\[\[[^\]]\]\]', text)
    return with_split + without_split

def find_link_anchor_texts(names, wiki_tree_root):
    title = ''
    anchor_texts = []
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if title in names:
                    if Utilities.cut_brackets(page_child.tag) == 'revision':
                        for text in page_child:
                            if Utilities.cut_brackets(text.tag) == 'text':
                                result = lat(text.text)
                                if len(result) > 0:
                                    anchor_texts.append([title, result])
    for entity_with_lat in anchor_texts:
        new_anchor_texts = []
        new_entity_with_lat = [entity_with_lat[0], []]
        for text in entity_with_lat[1]:
            if '|' in text:
                text = re.findall(r'\[\[[^\|]*\|', text)[0]
                text = text[2:-1]
            else:
                text = text[2:-2]
            new_entity_with_lat[1].append(text)
            new_anchor_texts.append(new_entity_with_lat)

    return anchor_texts

from lxml import etree
import paths
tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()
find_link_anchor_texts(root, 'ritt bjerregaard')