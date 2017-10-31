from lxml import etree
import paths
import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def find_link(search_term, text):
    if text == None:
        return []
    search_term = search_term.lower()
    text = text.lower()
    with_split = re.findall(r'\[\[[^\]]*\|' + search_term + '\]\]', text)
    without_split = re.findall(r'\[\[' + search_term + '\]\]', text)
    return with_split + without_split

def make_parentheses_for_regex(names):
    for name in names:
        new_name = name.replace('(', '\(')
        new_name = new_name.replace(')', '\)')
        names.remove(name)
        names.append(new_name)

def unmake_parentheses_for_regex(name):
    new_name = name.replace('\(', '(')
    new_name = new_name.replace('\)', ')')
    return new_name

def get_link_names(name):
    if '|' in name:
        link_text = re.sub(r'\]\]', '', re.sub(r'[^\|]*\|', '', name))
        link_name = re.sub(r'\[\[', '', re.sub(r'\|[^\|]*', '', name))
    else:
        link_text = re.sub(r'\[\[', '', re.sub(r'\]\]', '', name))
        link_name = link_text
    unmake_parentheses_for_regex(link_text)
    unmake_parentheses_for_regex(link_name)
    return [link_text, link_name]

def popularityPrior(names, wiki_tree_root):
    make_parentheses_for_regex(names)
    reference_list = []
    for root_child in wiki_tree_root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                for link in result:
                                    reference_list.append(get_link_names(link))

    prior_return_list = []
    for name in names:
        new_name = unmake_parentheses_for_regex(name)
        matches = [match for match in reference_list if match[0] == new_name.lower()]
        list_length = len(matches)
        sub_list = []
        while len(matches) != 0:
            first_match = [match for match in matches if match == matches[0]]
            sub_list_length = len(first_match)
            matches = [x for x in matches if x not in first_match]
            sub_list.append([first_match[0][1], sub_list_length/list_length])
        prior_return_list.append([first_match[0][0], sub_list])

    return prior_return_list