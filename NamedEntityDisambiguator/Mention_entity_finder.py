import re
import os
from NamedEntityDisambiguator import Utilities
from NamedEntityRecognizer import Retrieve_All_NER

def find_link(search_term, text):
    if text is None:
        return []
    search_term = search_term.lower()
    text = text.lower()
    with_split = re.findall(r'\[\[[^\]]*\|' + search_term + '\]\]', text)
    without_split = re.findall(r'\[\[' + search_term + '\]\]', text)
    return with_split + without_split


def get_link_name(name):
    if '|' in name:
        link_text = re.sub(r'\]\]', '', re.sub(r'[^\|]*\|', '', name))
        link_name = re.sub(r'\[\[', '', re.sub(r'\|[^\|]*', '', name))
    else:
        link_text = re.sub(r'\[\[', '', re.sub(r'\]\]', '', name))
        link_name = link_text
    Utilities.unmake_parentheses_for_regex(link_text)
    Utilities.unmake_parentheses_for_regex(link_name)
    return [link_text, link_name]


def get_mention_entity_possibilities(document, wiki_tree_root):
    names = []
    reference_list = []
    for name in document.readlines():
        names.append(Retrieve_All_NER.clean_line(name))
    Utilities.make_parentheses_for_regex_list(names)
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                for link in result:
                                    gln = get_link_name(link)
                                    link_name = [os.path.basename(document.name), gln[0], gln[1]]
                                    if link_name not in reference_list:
                                        reference_list.append(link_name)

    return reference_list
