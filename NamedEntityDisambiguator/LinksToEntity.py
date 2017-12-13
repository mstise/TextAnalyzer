import re
from NamedEntityDisambiguator import Utilities
import shelve
import os

def find_links(text):
    if text == None:
        return []
    text = text.lower()
    links = re.findall(r'\[\[[^\]]*\]\]', text)
    return links

def links_to_me(wiki_tree_root):
    title = ''
    link_dictionary = shelve.open("NamedEntityDisambiguator/dbs/link_dic", writeback=True)
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'title':
                    title = (page_child.text).lower()
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            result = find_links(text.text)
                            if len(result) > 0:
                                for link in result:
                                    if 'fil:' in link:
                                        continue
                                    link = Utilities.unmake_parentheses_for_regex(link)
                                    if '|' in link:
                                        link_entity = link[2:].partition('|')[0]
                                    else:
                                        link_entity = link[2:-2]
                                    link_dictionary.setdefault(link_entity, [])
                                    link_dictionary[link_entity].append(title)

    # linking_return_list = {}
    # for name in names:
    #     new_name = Utilities.unmake_parentheses_for_regex(name)
    #     matches = [match for match in linking_list if match[0] == new_name]
    #     links = []
    #     for match in matches:
    #         links.append(match[1])
    #     linking_return_list[new_name.lower()] = links

    link_dictionary.close()
    f = open("NamedEntityDisambiguator/dbs/link_dic.txt", "w")
    f.write(str(os.path.getmtime("NamedEntityDisambiguator/LinksToEntity.py")))
    f.close()
    return "NamedEntityDisambiguator/dbs/link_dic"

'''from lxml import etree
import paths
tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()
print(links_to_me(["anders fogh rasmussen"], root))'''