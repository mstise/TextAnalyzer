import sys
print(sys.path)

import re
from NamedEntityDisambiguator import Utilities

def find_link(search_term, text):
    if text == None:
        return []
    search_term = search_term
    text = text
    with_split = re.findall(r'\[\[' + search_term + '\|[^\]]*\]\]', text)
    without_split = re.findall(r'\[\[' + search_term + '\]\]', text)
    return with_split + without_split

def links_to_me(names, wiki_tree_root):
    Utilities.make_parentheses_for_regex_list(names)
    title = ''
    linking_list = []
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                if len(result) > 0:
                                    new_name = Utilities.unmake_parentheses_for_regex(name)
                                    linking_list.append([new_name, title])

    linking_return_list = {}
    for name in names:
        new_name = Utilities.unmake_parentheses_for_regex(name)
        matches = [match for match in linking_list if match[0] == new_name]
        links = []
        for match in matches:
            links.append(match[1])
        linking_return_list[new_name] = links

    return linking_return_list

#from lxml import etree
#import paths
#tree = etree.parse(paths.get_wikipedia_article_path())
#root = tree.getroot()
#print(links_to_me(["Anders Fogh Rasmussen"], root))