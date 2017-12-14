import re
from NamedEntityDisambiguator import Utilities
import shelve
import os

def find_references(text):
    if text == None:
        return []
    text = text.lower()
    text = Utilities.make_parentheses_for_regex_text(text)
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
        reference = Utilities.unmake_parentheses_for_regex(reference)
        final_references.append(reference)
    return final_references

def References(wiki_tree_root):
    result = shelve.open("NamedEntityDisambiguator/dbs/references_dic")
    #result = {}
    for root_child in wiki_tree_root:
        if Utilities.cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if Utilities.cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if Utilities.cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if Utilities.cut_brackets(text.tag) == 'text':
                            references = find_references(text.text)
                            if references:
                                result[title.lower()] = references
    result.close()
    f = open("NamedEntityDisambiguator/dbs/references_dic.txt", "w")
    f.write(str(os.path.getmtime("NamedEntityDisambiguator/References.py")))
    f.close()
    return result

'''from lxml import etree
import paths
tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()
print(References(root))'''