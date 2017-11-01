import NamedEntityRecognizer.Retrieve_All_NER as NER
from lxml import etree
import paths
import re
import itertools
import math

NUM_WIKI_ARTICLES = 474017

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

def entity_entity_coherence(entities):
    make_parentheses_for_regex(entities)
    tree = etree.parse("/home/duper/Desktop/Wikidump/dawiki-20171001-pages-articles.xml")
    root = tree.getroot()
    reference_dict = {}
    entity_entity_coherences = []
    for entity in entities:
        reference_dict[entity] = set()
    for root_child in root:
        if cut_brackets(root_child.tag) == 'page':
            for page_child in root_child:
                if cut_brackets(page_child.tag) == 'revision':
                    for text in page_child:
                        if cut_brackets(text.tag) == 'text':
                            for entity in entities:
                                result = find_link(entity, text.text)
                                if len(result) != 0:
                                    for child in root_child:
                                        if cut_brackets(child.tag) == 'title':
                                            reference_dict[entity].add(child.text)

    for two_combination in itertools.combinations(entities, 2):
        entity_links1 = reference_dict[two_combination[0]]
        entity_links2 = reference_dict[two_combination[1]]
        shared_links = entity_links1 & entity_links2 #& er intersection operator
        if len(shared_links) == 0:
            continue
        nominator = math.log(max(len(entity_links1), len(entity_links2))) - math.log(len(shared_links)) #Logs here are with root: e
        denominator = math.log(NUM_WIKI_ARTICLES) - math.log(min(len(entity_links1), len(entity_links2))) #Logs here are with root: e
        if denominator == 0:
            continue
        mw_coh = 1 - (nominator / denominator)
        if mw_coh > 0:
            entity_entity_coherences.append((two_combination[0], two_combination[1], mw_coh))

    return entity_entity_coherences

print(entity_entity_coherence(list(NER.ner_retriever())))