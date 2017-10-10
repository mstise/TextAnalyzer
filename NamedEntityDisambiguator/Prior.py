from lxml import etree
import paths
import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def find_link(search_term, text):
    if text == None:
        return []
    with_split = re.findall(r'\[\[[^\]]*\|' + search_term + '\]\]', text)
    without_split = re.findall(r'\[\[' + search_term + '\]\]', text)
    return with_split + without_split

def popularityPrior(names):
    tree = etree.parse(paths.get_wikipedia_article_path())
    root = tree.getroot()
    title = ''
    for root_child in root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'title':
                    title = page_child.text
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            for name in names:
                                result = find_link(name, text.text)
                                for group in result:
                                    print(title + " " + group)

popularityPrior(['Aalborghus', 'ældre bronzealder'])