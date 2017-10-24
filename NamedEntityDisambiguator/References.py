from lxml import etree
import paths
import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def find_references(text):
    if text == None:
        return []
    references = re.findall(r'<ref>[^<]*</ref>', text)
    final_references = []
    for reference in references:
        reference = re.sub(r'<ref>', '', reference)
        reference = re.sub(r'</ref>', '', reference)
        reference = re.sub(r'\[', '', reference)
        reference = re.sub(r'\]', '', reference)
        reference = re.sub(r'\{.*\}', '', reference)
        reference = re.sub(r'https:[^ ]* ', '', reference)
        reference = re.sub(r'http:[^ ]* ', '', reference)
        if "https:" in reference:
            test = 1
        final_references.append(reference)
    return final_references

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

def References(names):
    make_parentheses_for_regex(names)
    tree = etree.parse(paths.get_wikipedia_article_path())
    root = tree.getroot()
    for root_child in root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_references(text.text)

References(['kashmir (band)'])