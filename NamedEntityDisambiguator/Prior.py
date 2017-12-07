import re
from NamedEntityDisambiguator import Utilities

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
    Utilities.make_parentheses_for_regex_list(names)
    reference_list = []
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                for link in result:
                                    link_names = get_link_names(link)
                                    if len(link_names[1]) > 9 and link_names[1][:9] != 'kategori:':
                                        reference_list.append(get_link_names(link))

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
            prior_return_list.append([first_match[0][0], sub_list])
        else:
            prior_return_list.append([name, []])

    return prior_return_list