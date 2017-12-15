import sys
from itertools import product
from NamedEntityDisambiguator.Category_names import category_words
from NamedEntityDisambiguator.Link_anchor_text import find_link_anchor_texts
import NamedEntityDisambiguator.Utilities as util
import time
import math
import os
import shelve
import psutil
import threading

NUM_WIKI_ARTICLES = 474017

class myThread (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, category_kps, entities, entity_candidates, keyphrases_dic, link_anchors_of_ent,
                                    reference_keyphrases, title_of_ent_linking_to_ent, words_of_document):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.category_kps = category_kps
        self.entities = entities
        self.entity_candidates = entity_candidates
        self.keyphrases_dic = keyphrases_dic
        self.link_anchors_of_ent = link_anchors_of_ent
        self.reference_keyphrases = reference_keyphrases
        self.title_of_ent_linking_to_ent = title_of_ent_linking_to_ent
        self.words_of_document = words_of_document
        self.simscore = {}
    def run(self):
        for entity in self.entities:
            self.simscore[entity] = get_simscore(self.category_kps, entity, self.entity_candidates, self.keyphrases_dic, self.link_anchors_of_ent,
                                    self.reference_keyphrases, self.title_of_ent_linking_to_ent,
                                    self.words_of_document)

def split_list(lst, parts=1):
    length = len(lst)
    return [lst[i * length // parts: (i + 1) * length // parts]
            for i in range(parts)]

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

def uniqueify_grouped_kps(grouped_kps):
    already_found = {}
    new_kpwords = []
    new_grouped_kps = []
    for kp_words in grouped_kps:
        for word in kp_words:
            if already_found.get(word, False):
                continue
            else:
                new_kpwords.append(word)
                already_found[word] = True
        new_grouped_kps.append(new_kpwords)
    return new_grouped_kps

def mk_unique_foreign_entity_to_keyphrases(entities, reference_keyphrases, category_kps, link_anchors_of_entity, title_of_ent_linking_to_ent):
    entity_to_keyphrases = {}
    for entity in entities:
        tmp_set = set()
        #tmp_set = tmp_set.union(reference_keyphrases.get(entity, []))
        #tmp_set = tmp_set.union(category_kps.get(entity, []))
        tmp_set = tmp_set.union(link_anchors_of_entity.get(entity, []))
        #tmp_set = tmp_set.union(title_of_ent_linking_to_ent.get(entity, []))

        grouped_kps = [util.split_and_delete_special_characters(kp) for kp in list(tmp_set)]

        entity_to_keyphrases[entity] = grouped_kps#uniqueify_grouped_kps(grouped_kps)
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
        for kp_words in mixed_keyphrases[entity]:
            w_count += 1 if word in kp_words else 0
            if w_count > 0:
                entity_count += 1
                #print("entity count: " + str(entity_count))
                break

    return entity_count / NUM_WIKI_ARTICLES

def npmi(word, entities, mixed_grouped_keyphrases, keyphrases_dic, npmi_speedup_dict): #foreign_entities is a dictionary containing only 1 entry
    #print("new word: " + word)
    result = npmi_speedup_dict.get(word, -1)
    if result != -1 or word.isdigit():
        return 0
    joint_prob = joint_probability(word, mixed_grouped_keyphrases)
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
def keyphrase_similarity(wiki_tree_root, entities, entity_candidates_lst, words_of_document, reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent):
    #mem_observor = psutil.Process(os.getpid())
    #print("starting-similarity at mem: " + str(mem_observor.memory_full_info().vms / 1024 / 1024 / 1024))
    start = time.time()
    category_kps = category_words(entities)
    end = time.time()
    print("categories time: " + str(end - start))
    simscore_dic = {}
    #print("word of document: " + str(words_of_document))
    start = time.time()
    for entity_candidates in entity_candidates_lst:
        keyphrases_dic = mk_entity_to_keyphrases(entity_candidates, reference_keyphrases, category_kps, link_anchors_of_ent,
                                                 title_of_ent_linking_to_ent)
        split_candidates = split_list(entity_candidates, parts=8)
        threads = []
        counter = 1
        for entities in split_candidates:
            threads.append(myThread(counter, category_kps, entities, entity_candidates, keyphrases_dic, link_anchors_of_ent,
                                    reference_keyphrases, title_of_ent_linking_to_ent,
                                    words_of_document))
            counter += 1

        # Start new Threads
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for thread in threads:
            for entity in thread.simscore.keys():
                simscore_dic[entity] = thread.simscore[entity]

    end = time.time()
    print("keyphrase_similarity" + str(end - start))
    return simscore_dic


def get_simscore(category_kps, entity, entity_candidates, keyphrases_dic, link_anchors_of_ent, reference_keyphrases,
                 title_of_ent_linking_to_ent, words_of_document):
    npmi_speedup_dict_num = {}
    npmi_speedup_dict_den = {}
    # print("beginning entitiy: " + entity)
    simscore = 0.0
    # if simscore_dic.get(entity, -1) != -1:
    #    print("no go: " + str(entity))
    #    continue
    # find here the keyphrases of IN_e (in the article)
    foreign_grouped_keyphrases = {}
    # gc.collect()
    foreign_grouped_keyphrases = mk_unique_foreign_entity_to_keyphrases(title_of_ent_linking_to_ent[entity],
                                                                        reference_keyphrases, category_kps,
                                                                        link_anchors_of_ent,
                                                                        title_of_ent_linking_to_ent)
    grouped_kps = [util.split_and_delete_special_characters(kp) for kp in keyphrases_dic[entity]]
    foreign_grouped_keyphrases[entity] = uniqueify_grouped_kps(grouped_kps)
    # print("mem after foreign: " + str(mem_observor.memory_full_info().vms / 1024 / 1024 / 1024))
    # if len(keyphrases_dic[entity]) != 0:
    #    print("keyphrases: " + str(keyphrases_dic[entity]))
    # print(str(entity) + " has kp total of: " + str(len(keyphrases_dic[entity])))
    for kp in keyphrases_dic[entity]:
        # if str(entity) == "sjælland (skib, 1860)":
        #    print(kp)
        indices = []
        kp_words = util.split_and_delete_special_characters(kp)
        if len(kp_words) > 10:
            kp_words = list(kp_words[:10])
        kp_words = [word for word in kp_words if word not in npmi_speedup_dict_den.keys()]

        maximum_words_in_doc = list(set(kp_words).intersection(words_of_document))
        if len(maximum_words_in_doc) == 0:
            continue
        for word in maximum_words_in_doc:
            word_idxs = [i for i, x in enumerate(words_of_document) if
                         x == word]  # Get indicies of all occurences of a kp-word
            if len(word_idxs) > 0:  # if empty, the word is not considered in the cover
                indices.append(word_idxs)
        cover, cover_span = min_distance_indices(indices)  # finds cover
        # print("indicies in cover: " + str(cover))
        if cover_span == 0:
            continue
        z = len(maximum_words_in_doc) / cover_span
        denominator = sum(
            [npmi(word, entity_candidates, foreign_grouped_keyphrases, keyphrases_dic, npmi_speedup_dict_den) for word
             in kp_words])
        if denominator == 0.0:
            # print("denom is zero")
            continue
        numerator = sum([npmi(words_of_document[index], entity_candidates, foreign_grouped_keyphrases, keyphrases_dic,
                              npmi_speedup_dict_num) for index in cover])
        score = z * (numerator / denominator) ** 2
        simscore += score
    npmi_speedup_dict_num = {}
    npmi_speedup_dict_den = {}
    # print("simscore is : " + str(simscore))
    return simscore


'''import threading
print(threading.active_count())
from lxml import etree
import paths
tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()
print(str(keyphrase_similarity(root, ["paris", "paris (supertramp)", "paris (lemvig kommune)", "anders fogh rasmussen"], [["paris", "paris (supertramp)", "paris (lemvig kommune)"], ["anders fogh rasmussen"]], ["paris", "er", "en", "by", "som", "blev", "bombet", "af", "tyskland", "under", "krigen", "mod", "danmark"], shelve.open("NamedEntityDisambiguator/dbs/references_dic"), shelve.open("NamedEntityDisambiguator/dbs/link_dic"))))
#"paris", "er", "det", "progressive", "rockband", "supertramps", "første", "livealbum", "udgivet", "i", "1980"̈́
'''