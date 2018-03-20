from lxml import etree
import paths
import re
import shelve
from NamedEntityDisambiguator import Utilities
import os

def find_link(text):
    if text == None:
        return []
    text = text.lower()
    results = re.findall(r'\[\[[^\]]*\]\]', text)
    return results

def get_link_names(name):
    if '|' in name:
        link_text = re.sub(r'\]\]', '', re.sub(r'[^\|]*\|', '', name))
        link_name = re.sub(r'\[\[', '', re.sub(r'\|[^\|]*', '', name))
    else:
        link_text = re.sub(r'\[\[', '', re.sub(r'\]\]', '', name))
        link_name = link_text
    Utilities.unmake_parentheses_for_regex(link_text)
    Utilities.unmake_parentheses_for_regex(link_name)
    return [link_text, link_name]

tree = etree.parse(paths.get_wikipedia_article_path())
wiki_tree_root = tree.getroot()

link_dictionary = shelve.open("NamedEntityDisambiguator/dbs/prior_dic", writeback=True)
for root_child in wiki_tree_root:
    if Utilities.cut_brackets(root_child.tag) == 'page':
        for page_child in root_child:
            if Utilities.cut_brackets(page_child.tag) == 'revision':
                for text in page_child:
                    if Utilities.cut_brackets(text.tag) == 'text':
                        result = find_link(text.text)
                        for link in result:
                            link_names = get_link_names(link)
                            link_names[0] = link_names[0].lower()
                            link_names[1] = link_names[1].lower()
                            if (len(link_names[1]) < 9 or link_names[1][:9] != 'kategori:') and \
                                    (len(link_names[1]) < 4 or link_names[1][:4] != 'fil:') and \
                                    (len(link_names[1]) < 5 or link_names[1][:5] != 'file:') and \
                                    (len(link_names[1]) < 8 or link_names[1][:8] != 'billede:') and \
                                    (len(link_names[1]) < 1 or link_names[1][0] != ':'):
                                link_dictionary.setdefault(link_names[0], [])
                                tmp = link_dictionary[link_names[0]]
                                tmp.append(link_names[1])
                                link_dictionary[link_names[0]] = tmp
                                print(link_names[0])
link_dictionary.close()