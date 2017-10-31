import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def find_references(text):
    text = make_parentheses_for_regex(text)
    if text == None:
        return []
    references = re.findall(r'<ref>[^<]*</ref>', text)
    for reference in re.findall(r'<ref>[^<]*<sup>[^<]*</sup>[^<]*</ref>', text):
        references.append(reference)
    final_references = []
    titles = []
    for reference in references:
        if "title=" in reference:
            if len(re.findall(r'title=.*</ref>', text)) == 0:
                continue
            title = re.findall(r'title=.*</ref>', text)[0]
            title = title.split('|')[0]
            title = title[6:]
            if title not in titles:
                titles.append(title)
                reference = re.findall(r'title=.*</ref>', text)[0]
                if len(reference.split('|')) > 1:
                    reference = reference.split('|')[1]
                    final_references.append(reference)
            continue
        reference = re.sub(r'<ref>', '', reference)
        reference = re.sub(r'</ref>', '', reference)
        reference = re.sub(r'\[', '', reference)
        reference = re.sub(r'\]', '', reference)
        reference = re.sub(r'\{.*\}', '', reference)
        reference = re.sub(r'https:[^ ]* ', '', reference)
        reference = re.sub(r'http:[^ ]* ', '', reference)
        reference = unmake_parentheses_for_regex(reference)
        final_references.append(reference)
    return final_references

def make_parentheses_for_regex(name):
    new_name = name.replace('(', '\(')
    new_name = new_name.replace(')', '\)')
    return new_name

def unmake_parentheses_for_regex(name):
    new_name = name.replace('\(', '(')
    new_name = new_name.replace('\)', ')')
    return new_name

def References(wiki_tree_root):
    #make_parentheses_for_regex(names)
    result = []
    for root_child in wiki_tree_root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            if title == 'Danmark':
                                test = 1
                            result.append([title, find_references(text.text)])
    return result