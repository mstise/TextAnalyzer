import sys
from itertools import product
from NamedEntityDisambiguator.Category_names import category_words
from NamedEntityDisambiguator.Link_anchor_text import find_link_anchor_texts
import NamedEntityDisambiguator.Utilities as util
import time
import math

NUM_WIKI_ARTICLES = 474017

#This function finds the indicies of the minimum cover using maximum amount of words from kp
def min_distance_indices(indices):
    # makes the following combinations: (ex) [[1,2,3],[4,5,6],[7,8,9,10]] -> [[1,4,7],[1,4,8],...,[3,6,10]]
    combinations = list(product(*indices)) #*indicies unpacks the list to positional arguments in the function

    sorted_combinations = [sorted(x) for x in combinations]
    min_dist = sys.maxsize
    for i in range(0, len(sorted_combinations)):
        new_dist = sorted_combinations[i][-1] - sorted_combinations[i][0]
        if new_dist < min_dist:
            min_dist = new_dist
            min_dist_index = i
    return combinations[min_dist_index], min_dist #returns cover (in indices) and length of the cover

def mk_entity_to_keyphrases(entities, reference_keyphrases, category_kps, link_anchors_of_entity, title_of_ent_linking_to_ent):
    entity_to_keyphrases = {}
    for entity in entities:
        tmp_set = set()
        tmp_set = tmp_set.union(reference_keyphrases.get(entity, []))
        tmp_set = tmp_set.union(category_kps.get(entity, []))
        tmp_set = tmp_set.union(link_anchors_of_entity.get(entity, []))
        tmp_set = tmp_set.union(title_of_ent_linking_to_ent.get(entity, []))
        entity_to_keyphrases[entity] = list(tmp_set)
    return entity_to_keyphrases

def word_probability(word, entities, keyphrases_dic):
    num_kps = 0
    encountered_kps = 0
    for entity in entities:
        keyphrases = keyphrases_dic[entity]
        num_kps += len(keyphrases)
        for kp in keyphrases:
            kp_words = util.split_and_delete_special_characters(kp)
            encountered_kps += 1 if word in kp_words else 0
    return encountered_kps / num_kps

def joint_probability(word, mixed_keyphrases): #foreign_entities is a dictionary containing only 1 entry
    entity_count = 0
    #print("nums mixed entitie: " + str(len(mixed_keyphrases.keys())))
    for entity in mixed_keyphrases.keys():
        w_count = 0
        for kp in mixed_keyphrases[entity]:
            kp_words = util.split_and_delete_special_characters(kp)
            w_count += 1 if word in kp_words else 0
            if w_count > 0:
                entity_count += 1
                #print("entity count: " + str(entity_count))
                break

    return entity_count / NUM_WIKI_ARTICLES

def npmi(word, entities, mixed_keyphrases, keyphrases_dic, npmi_speedup_dict): #foreign_entities is a dictionary containing only 1 entry
    #print("new word: " + word)
    result = npmi_speedup_dict.get(word, -1)
    if result != -1 or word.isdigit():
        return 0
    joint_prob = joint_probability(word, mixed_keyphrases)
    ent_prob = 1 / NUM_WIKI_ARTICLES#len(entities)
    word_prob = word_probability(word, entities, keyphrases_dic)
    denominator = ent_prob * word_prob
    if denominator <= 0.0 or joint_prob <= 0.0: #security check if division by zero occurs
        npmi_speedup_dict[word] = 0
        return 0
    else:
        pmi = math.log10(joint_prob / denominator)
        result = pmi/-math.log10(joint_prob) if pmi/-math.log10(joint_prob) > 0 else 0
        npmi_speedup_dict[word] = result
        return result


#Makes keyphrase-based similarity between alle mentions and entity candidates in ONE document (entities = All candidates from the given document)
def keyphrase_similarity(wiki_tree_root, entities, entity_candidates_lst, words_of_document, reference_keyphrases, title_of_ent_linking_to_ent):
    npmi_speedup_dict_num = {}
    npmi_speedup_dict_den = {}
    start = time.time()
    category_kps = category_words(entities)
    end = time.time()
    print("categories" + str(end - start))
    start = time.time()
    link_anchors_of_entity = find_link_anchor_texts(entities, wiki_tree_root)
    end = time.time()
    print("link_anchor" + str(end - start))
    keyphrases_dic = mk_entity_to_keyphrases(entities, reference_keyphrases, category_kps, link_anchors_of_entity, title_of_ent_linking_to_ent)
    simscore_dic = {}
    #print("word of document: " + str(words_of_document))
    start = time.time()
    for entity_candidates in entity_candidates_lst:
        for entity in entity_candidates:
            #print("beginning entitiy: " + entity)
            simscore = 0
            if simscore_dic.get(entity, -1) != -1:
                continue
            # find here the keyphrases of IN_e (in the article)
            #print("entity is: " + entity)
            foreign_keyphrases = mk_entity_to_keyphrases(title_of_ent_linking_to_ent[entity], reference_keyphrases, category_kps, link_anchors_of_entity, title_of_ent_linking_to_ent)
            foreign_keyphrases[entity] = keyphrases_dic[entity]

            #if len(keyphrases_dic[entity]) != 0:
            #    print("keyphrases: " + str(keyphrases_dic[entity]))

            #print(str(entity) + "has kp total of: " + str(len(keyphrases_dic[entity])))
            for kp in keyphrases_dic[entity]:
                indices = []
                kp_words = util.split_and_delete_special_characters(kp)
                kp_words = [word for word in kp_words if word not in npmi_speedup_dict_den.keys()]
                maximum_words_in_doc = list(set(kp_words).intersection(words_of_document))
                if len(maximum_words_in_doc) == 0:
                    continue
                for word in maximum_words_in_doc:
                    word_idxs = [i for i, x in enumerate(words_of_document) if x == word] #Get indicies of all occurences of a kp-word
                    if len(word_idxs) > 0: #if empty, the word is not considered in the cover
                        indices.append(word_idxs)
                cover, cover_span = min_distance_indices(indices) #finds cover
                #print("indicies in cover: " + str(cover))
                if cover_span == 0:
                    continue
                z = len(maximum_words_in_doc) / cover_span
                denominator = sum([npmi(word, entity_candidates, foreign_keyphrases, keyphrases_dic, npmi_speedup_dict_den) for word in kp_words])
                if denominator == 0.0:
                    #print("denom is zero")
                    continue
                numerator = sum([npmi(words_of_document[index], entity_candidates, foreign_keyphrases, keyphrases_dic, npmi_speedup_dict_num) for index in cover])
                score = z * (numerator / denominator)**2
                simscore += score
            npmi_speedup_dict_num = {}
            npmi_speedup_dict_den = {}
            #print("simscore is : " + str(simscore))
            simscore_dic[entity] = simscore
    end = time.time()
    print("keyphrase_similarity" + str(end - start))
    return simscore_dic

'''import threading
print(threading.active_count())
from lxml import etree
import paths
tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()
start = time.time()
from NamedEntityDisambiguator.References import References
from NamedEntityDisambiguator.LinksToEntity import links_to_me
reference_keyphrases = References(root)
end = time.time()
print("references" + str(end - start))
start = time.time()
title_of_ent_linking_to_ent = links_to_me(root)
end = time.time()
print("incoming_ent_titles" + str(end - start))
print(str(keyphrase_similarity(root, ["paris", "paris (supertramp)", "paris (lemvig kommune)", "anders fogh rasmussen"], [["paris", "paris (supertramp)", "paris (lemvig kommune)"], ["anders fogh rasmussen"]], ["paris", "er", "en", "by", "som", "blev", "bombet", "af", "tyskland", "under", "krigen", "mod", "danmark"], reference_keyphrases, title_of_ent_linking_to_ent)))
#"paris", "er", "det", "progressive", "rockband", "supertramps", "første", "livealbum", "udgivet", "i", "1980"̈́
'''