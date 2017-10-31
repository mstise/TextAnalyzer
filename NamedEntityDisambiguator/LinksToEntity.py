import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def find_link(search_term, text):
    if text == None:
        return []
    search_term = search_term.lower()
    text = text.lower()
    with_split = re.findall(r'\[\[' + search_term + '\|[^\]]*\]\]', text)
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

def links_to_me(names, wiki_tree_root):
    make_parentheses_for_regex(names)
    title = ''
    linking_list = []
    for root_child in wiki_tree_root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                if len(result) > 0:
                                    new_name = unmake_parentheses_for_regex(name)
                                    linking_list.append([new_name, title])

    linking_return_list = []
    for name in names:
        new_name = unmake_parentheses_for_regex(name)
        matches = [match for match in linking_list if match[0] == new_name.lower()]
        links = []
        for match in matches:
            links.append(match[1])
        linking_return_list.append([new_name, links])

    return linking_return_list