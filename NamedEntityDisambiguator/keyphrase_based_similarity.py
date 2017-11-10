import sys
from NamedEntityDisambiguator import References
from itertools import product
from NamedEntityDisambiguator.Category_names import category_words
from NamedEntityDisambiguator.Link_anchor_text import find_link_anchor_texts
from NamedEntityDisambiguator.LinksToEntity import links_to_me

#This function finds the indicies of the minimum cover using maximum amount of words from kp
def min_distance_indices(indices):
    # makes the following combinations: (ex) [[1,2,3],[4,5,6],[7,8,9,10]] -> [[1,4,7],[1,4,8],...,[3,6,10]]
    combinations = list(product(*indices)) #*indicies unpacks the list to positional arguments in the function

    sorted_combinations = [sorted(x) for x in combinations]
    min_dist = sys.maxsize
    for i in range(0, len(sorted_combinations)-1):
        new_dist = sorted_combinations[i][-1] - sorted_combinations[i][0]
        if new_dist < min_dist:
            min_dist = new_dist
            min_dist_index = i
    return combinations[min_dist_index], min_dist #returns cover (in indices) and length of the cover

def mk_entity_to_keyphrases(entities, wiki_tree_root):
    reference_keyphrases = References.References(wiki_tree_root)
    category_kps = category_words(entities)
    link_anchors_of_entity = find_link_anchor_texts(entities, wiki_tree_root)
    title_of_ent_linking_to_ent = links_to_me(entities, wiki_tree_root)

    entity_to_keyphrases = {}
    for entity in entities:
        entity_to_keyphrases[entity] = []
        entity_to_keyphrases[entity].extend(reference_keyphrases[entity])
        entity_to_keyphrases[entity].extend(category_kps[entity])
        entity_to_keyphrases[entity].extend(link_anchors_of_entity[entity])
        entity_to_keyphrases[entity].extend(title_of_ent_linking_to_ent[entity])

    return entity_to_keyphrases


def mutual_information(e, w, keyphrases, num_entities, wiki_tree_root):
    foreign_entities = links_to_me([e], wiki_tree_root)  # foreign_entities is a dictionary containing only 1 entry
    foreign_keyphrases = mk_entity_to_keyphrases(foreign_entities[e], wiki_tree_root)
    mixed_keyphrases = set().union(keyphrases, foreign_keyphrases)
    w_count = 0
    for kp in mixed_keyphrases:
        w_count += kp.count(w)
    return w_count / num_entities


#Makes keyphrase-based similarity between alle mentions and entity candidates in ONE document (entities = All candidates from the given document)
def keyphrase_similarity(wiki_tree_root, entities = ["Ritt Bjerregaard", "Anders Fogh Rasmussen"], words_of_document = [word for line in open("/home/duper/Desktop/Fogh_eks", 'r') for word in line.split()]):
    keyphrases_dic = mk_entity_to_keyphrases(entities, wiki_tree_root)
    simscore_dic = {}
    for entity in entities:

        simscore = 0

        for kp in keyphrases_dic[entity]:
            indices = []
            kp_words = kp.split()
            maximum_words_in_doc = list(set().intersection(kp_words, words_of_document))
            if len(maximum_words_in_doc) == 0:
                continue
            for word in maximum_words_in_doc:
                word_idxs = [i for i, x in enumerate(words_of_document) if x == word] #Get indicies of all occurences of a kp-word
                if len(word_idxs) > 0: #if empty, the word is not considered in the cover
                    indices.append(word_idxs)
            cover, cover_span = min_distance_indices(indices) #finds cover
            if cover_span == 0:
                continue
            z = len(maximum_words_in_doc) / cover_span
            nominator = sum([mutual_information(entity, words_of_document[index], keyphrases_dic[entity], len(entities), wiki_tree_root) for index in cover])
            denominator = sum([mutual_information(entity, word, keyphrases_dic[entity], len(entities), wiki_tree_root) for word in kp_words])
            score = z * (nominator / denominator)**2
            simscore += score
        simscore_dic[entity] = simscore

    return simscore_dic

#from lxml import etree
#import paths
#tree = etree.parse(paths.get_wikipedia_article_path())
#root = tree.getroot()
#print(keyphrase_similarity(root))