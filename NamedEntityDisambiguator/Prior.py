import re
from NamedEntityDisambiguator import Utilities

# def find_link(text):
#     if text == None:
#         return []
#     return re.findall(r'\[\[[^\]]*\]\]', text)

def find_link(search_term, text):
    if text == None:
        return []
    search_term = search_term.lower()
    text = text.lower()
    with_split = re.findall(r'\[\[[^\]]*\|' + search_term + '\]\]', text)
    without_split = re.findall(r'\[\[' + search_term + '\]\]', text)
    return with_split + without_split

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

#names: ALLE recognized entities. Prior return list: [["Hp", [["Hewlett-Packard, 52,5], [HP, 40.0], [Harry Potter, 7.5]]], "Voldemort", [...]]
def popularityPrior(names, wiki_tree_root):
    u_names = set(names)
    u_names = Utilities.make_parentheses_for_regex_list(u_names)
    reference_list = []
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            # links = find_link(text.text)
                            # for link in links:
                            #     link_names = get_link_names(link)
                            #     for link_name in link_names:
                            #         for name in u_names:
                            #             if link_name[0] == name:
                            #                 if (len(link_names[1]) < 9 or link_names[1][:9] != 'kategori:') and \
                            #                         (len(link_names[1]) < 4 or link_names[1][:4] != 'fil:') and \
                            #                         (len(link_names[1]) < 8 or link_names[1][:8] != 'billede:'):
                            #                     reference_list.append(link_names)

                            for name in u_names:
                                result = find_link(name, text.text)
                                for link in result:
                                    link_names = get_link_names(link)
                                    if (len(link_names[1]) < 9 or link_names[1][:9] != 'kategori:') and\
                                       (len(link_names[1]) < 4 or link_names[1][:4] != 'fil:') and\
                                       (len(link_names[1]) < 8 or link_names[1][:8] != 'billede:') and\
                                       (len(link_names[1]) < 1 or link_names[1][0] != ':'):
                                        reference_list.append(link_names)

    prior_return_list = []
    for name in names:
        new_name = Utilities.unmake_parentheses_for_regex(name)
        matches = [match for match in reference_list if match[0] == new_name.lower()]
        list_length = len(matches)
        sub_list = []
        if len(matches) != 0:
            while len(matches) != 0:
                first_match = [match for match in matches if match == matches[0]]
                sub_list_length = len(first_match)
                matches = [x for x in matches if x not in first_match]
                sub_list.append([first_match[0][1], sub_list_length/list_length])
            prior_return_list.append([first_match[0][0], sorted(sub_list, key=lambda x: x[1])[-20:]])
        else:
            prior_return_list.append([name, []])

    return prior_return_list

# from lxml import etree
# import paths
# tree = etree.parse(paths.get_wikipedia_article_path())
# root = tree.getroot()
# popularityPrior(['København'], root)