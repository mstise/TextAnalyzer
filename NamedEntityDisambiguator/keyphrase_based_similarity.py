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
import copy
from sortedcontainers import SortedList, SortedDict

NUM_WIKI_ARTICLES = 474017

class myThread (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, entities, entity_candidates, keyphrases_dic, link_anchors_of_ent, title_of_ent_linking_to_ent, words_of_document):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.entities = entities
        self.entity_candidates = entity_candidates
        self.keyphrases_dic = keyphrases_dic
        self.link_anchors_of_ent = link_anchors_of_ent
        self.title_of_ent_linking_to_ent = title_of_ent_linking_to_ent
        self.words_of_document = words_of_document
        self.simscore = {}
    def run(self):
        for entity in self.entities:
            self.simscore[entity] = get_simscore(entity, self.entity_candidates, self.keyphrases_dic, self.link_anchors_of_ent,
                                    self.title_of_ent_linking_to_ent, copy.deepcopy(self.words_of_document))

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
        new_dist = sorted_combinations[i][-1] - sorted_combinations[i][0] + 1
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

def mk_unique_foreign_entity_to_keyphrases(entities, link_anchors_of_entity):
    entity_to_keyphrases = {}
    for entity in entities:
        tmp_set = set()
        #tmp_set = tmp_set.union(reference_keyphrases.get(entity, []))
        #tmp_set = tmp_set.union(category_kps.get(entity, []))
        tmp_set = tmp_set.union(link_anchors_of_entity.get(entity, []))
        #tmp_set = tmp_set.union(title_of_ent_linking_to_ent.get(entity, []))

        grouped_kps = [util.split_and_delete_special_characters(kp) for kp in list(tmp_set)]

        entity_to_keyphrases[entity] = SortedList(list(grouped_kps))#uniqueify_grouped_kps(grouped_kps)
    return entity_to_keyphrases

def word_probability(word, entities, entity_keyphrases):
    num_kps = 0
    encountered_kps = 0
    for entity in entities:
        num_kps += len(entity_keyphrases)
        for kp in entity_keyphrases:
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
    print(str(word) + " has entity_count: " + str(entity_count))
    return entity_count / len(mixed_keyphrases.keys())

def npmi(word, entities, mixed_grouped_keyphrases, entity_keyphrases, npmi_speedup_dict, entity, num_ent_in_kps_dic): #foreign_entities is a dictionary containing only 1 entry
    #print("new word: " + word)
    result = npmi_speedup_dict.get(word, -1)
    if result != -1 or word.isdigit():
        return 0
    joint_prob = num_ent_in_kps_dic[word] / len(mixed_grouped_keyphrases.keys())#joint_probability(word, mixed_grouped_keyphrases)
    print(str(entity) + " join prob is: " + str(joint_prob))
    ent_prob = 1 / NUM_WIKI_ARTICLES#len(entities)
    word_prob = word_probability(word, entities, entity_keyphrases)
    print(str(entity) + " word prob is: " + str(word_prob))
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
def keyphrase_similarity(wiki_tree_root, entities, candidates_dic, words_of_document, reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent):
    print("words_of_doc: " + str(words_of_document))
    #mem_observor = psutil.Process(os.getpid())
    #print("starting-similarity at mem: " + str(mem_observor.memory_full_info().vms / 1024 / 1024 / 1024))
    start = time.time()
    category_kps = category_words(entities)
    end = time.time()
    print("categories time: " + str(end - start))
    simscore_dic = {}
    #print("word of document: " + str(words_of_document))
    start = time.time()
    for entity_candidates in candidates_dic.values():
        keyphrases_dic = mk_entity_to_keyphrases(entity_candidates, reference_keyphrases, category_kps, link_anchors_of_ent,
                                                 title_of_ent_linking_to_ent)
        split_candidates = split_list(entity_candidates, parts=8)
        threads = []
        counter = 1
        #print("these are the split candidates: " + str(split_candidates))
        for entities in split_candidates:
            threads.append(myThread(counter, entities, entity_candidates, keyphrases_dic, link_anchors_of_ent,
                                    title_of_ent_linking_to_ent, words_of_document))
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

def find_num_ent_in_kps(entity_keyphrases, mixed_keyphrases):
    num_ent_in_kps_dic = SortedDict()
    #num_ent_in_kps_dic = {}
    num_kp_in_kps_dic = {}
    for kp in entity_keyphrases:
        kp_words = util.split_and_delete_special_characters(kp)
        if len(kp_words) > 10:
            kp_words = list(kp_words[:10])
        for word in kp_words:
            num_ent_in_kps_dic[word] = 0
            num_kp_in_kps_dic[word] = 0
    for entity in mixed_keyphrases.keys():
        for ent_kp_words in mixed_keyphrases[entity]:
            for word in num_kp_in_kps_dic.keys():
                if word in ent_kp_words:
                    num_kp_in_kps_dic[word] += 1
        for word in num_ent_in_kps_dic.keys():
            if num_kp_in_kps_dic[word] > 0:
                num_ent_in_kps_dic[word] += 1
                num_kp_in_kps_dic[word] = 0

    return num_ent_in_kps_dic




def get_simscore(entity, entity_candidates, keyphrases_dic, link_anchors_of_ent,
                 title_of_ent_linking_to_ent, words_of_document):
    npmi_speedup_dict_num = {}
    npmi_speedup_dict_den = {}
    entity_keyphrases = keyphrases_dic[entity]
    #print("beginning entitiy: " + entity)
    simscore = 0.0
    # if simscore_dic.get(entity, -1) != -1:
    #    print("no go: " + str(entity))
    #    continue
    # find here the keyphrases of IN_e (in the article)
    foreign_grouped_keyphrases = {}
    # gc.collect()
    foreign_grouped_keyphrases = mk_unique_foreign_entity_to_keyphrases(title_of_ent_linking_to_ent[entity], link_anchors_of_ent)
    grouped_kps = [util.split_and_delete_special_characters(kp) for kp in entity_keyphrases]
    foreign_grouped_keyphrases[entity] = SortedList(grouped_kps)# uniqueify_grouped_kps(grouped_kps)
    # print("mem after foreign: " + str(mem_observor.memory_full_info().vms / 1024 / 1024 / 1024))
    # if len(keyphrases_dic[entity]) != 0:
    #    print("keyphrases: " + str(keyphrases_dic[entity]))
    print(str(entity) + " has " + str(len(entity_keyphrases)) + "keyphrases")
    start = time.time()
    num_ent_in_kps_dic = find_num_ent_in_kps(entity_keyphrases, foreign_grouped_keyphrases)
    end = time.time()
    #print("num_ent_in_kps_dic for " + str(entity) + " at time: " + str(end - start))

    for kp in entity_keyphrases:
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
        print("These are indices: " + str(indices) + " of words: " + str(maximum_words_in_doc))
        cover, cover_span = min_distance_indices(indices)  # finds cover
        # print("indicies in cover: " + str(cover))
        if len(maximum_words_in_doc) > 0:
            print(str(entity) + " has max_words in doc: " + str(maximum_words_in_doc) + " and span_len: " + str(cover_span))
        if cover_span == 0:
            continue
        z = len(maximum_words_in_doc) / cover_span
        denominator = sum(
            [npmi(word, entity_candidates, foreign_grouped_keyphrases, entity_keyphrases, npmi_speedup_dict_den, entity, num_ent_in_kps_dic) for word
             in kp_words])
        print(str(entity) + ": denom = " + str(denominator))
        if denominator == 0.0:
            #print(str(entity) + ": denom is zero")
            continue
        numerator = sum([npmi(words_of_document[index], entity_candidates, foreign_grouped_keyphrases, entity_keyphrases,
                              npmi_speedup_dict_num, entity, num_ent_in_kps_dic) for index in cover])
        print(str(entity) + ": numerator = " + str(numerator))
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

#l = SortedList(["åbenrå", "æv", "banan", "abe", "t-bone", "isbjørn"])
#print(str(l))

#print(str("t-bone" in l))