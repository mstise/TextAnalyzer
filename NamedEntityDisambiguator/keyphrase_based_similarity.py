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
from collections import defaultdict
from multiprocessing import Process, Queue
from sortedcontainers import SortedList, SortedDict

NUM_WIKI_ARTICLES = 474017

def threaded_func(q, set_of_candidates, reference_keyphrases, category_kps, link_anchors_of_ent, title_of_ent_linking_to_ent, words_of_document):
    simscore = {}
    for entity_candidates in set_of_candidates:
        print("Make entity to keyphrases start: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + str(entity_candidates))
        grouped_keyphrases_dic = mk_entity_to_keyphrases(entity_candidates, reference_keyphrases, category_kps,
                                                         link_anchors_of_ent, title_of_ent_linking_to_ent)
        for entity in entity_candidates:
            simscore[entity] = get_simscore(entity, entity_candidates, grouped_keyphrases_dic, link_anchors_of_ent,
                                            title_of_ent_linking_to_ent, words_of_document)
        print("End simscore creation: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + str(entity_candidates))
    q.put(simscore)


def split_list(lst, parts=1):
    length = len(lst)
    return [lst[i * length // parts: (i + 1) * length // parts]
            for i in range(parts)]

#This function finds the indicies of the minimum cover using maximum amount of words from kp
def min_distance_indices(indices):
    # makes the following combinations: (ex) [[1,2,3],[4,5,6],[7,8,9,10]] -> [[1,4,7],[1,4,8],...,[3,6,10]]
    combinations = list(product(*indices)) #*indicies unpacks the list to positional arguments in the function
    print('INDICES: ' + str(indices))
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
        grouped_kps = [util.split_and_delete_special_characters(kp) for kp in list(tmp_set)]
        entity_to_keyphrases[entity] = SortedList(list(grouped_kps))#list(tmp_set)
    return entity_to_keyphrases

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

def npmi(word, entities, mixed_grouped_keyphrases, grouped_keyphrases_dic, npmi_speedup_dict, entity, num_ent_in_kps_dic, num_kp_in_candidate_kps_dic, num_kps_in_candidates): #foreign_entities is a dictionary containing only 1 entry
    #print("new word: " + word)
    result = npmi_speedup_dict.get(word, -1)
    if result != -1 or word.isdigit():
        return 0
    print('KEY: ' + word)
    joint_prob = num_ent_in_kps_dic[word] / len(mixed_grouped_keyphrases.keys())#joint_probability(word, mixed_grouped_keyphrases)
    #print(str(entity) + " join prob is: " + str(joint_prob))
    ent_prob = 1 / len(entities) #NUM_WIKI_ARTICLES
    word_prob = num_kp_in_candidate_kps_dic[word] / num_kps_in_candidates#= word_probability(word, entities, grouped_keyphrases_dic, num_kp_in_candidate_kps_dic)
    #print(str(entity) + " word prob is: " + str(word_prob))
    denominator = ent_prob * word_prob
    if denominator <= 0.0 or joint_prob <= 0.0: #security check if division by zero occurs
        npmi_speedup_dict[word] = 0
        return 0
    else:
        pmi = math.log10(joint_prob / denominator)
        #print("joint_prob: " + str(joint_prob) + ", math.log10(joint_prob): " + str(math.log10(joint_prob)) + ", boolean = " + str(math.log10(joint_prob) == 0))
        if math.log10(joint_prob) == 0:
            return pmi
        result = pmi/-math.log10(joint_prob) if pmi/-math.log10(joint_prob) > 0 else 0
        npmi_speedup_dict[word] = result
        return result


#Makes keyphrase-based similarity between alle mentions and entity candidates in ONE document (entities = All candidates from the given document)
def keyphrase_similarity(entities, candidates_dic, words_of_document, reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent, category_kps):
    # print("words_of_doc: " + str(words_of_document))
    # mem_observor = psutil.Process(os.getpid())
    # print("starting-similarity at mem: " + str(mem_observor.memory_full_info().vms / 1024 / 1024 / 1024))
    simscore_dic = {}
    # print("word of document: " + str(words_of_document))
    start = time.time()
    print("Start of kpbs: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
    split_set_of_candidates = split_list(list(candidates_dic.values()), parts=8)
    threads = []
    q = Queue()
    print("Start of process creation: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    for set_of_entity_candidates in split_set_of_candidates:
        threads.append(Process(target=threaded_func, args=(q, set_of_entity_candidates, reference_keyphrases, category_kps, link_anchors_of_ent, title_of_ent_linking_to_ent, words_of_document)))

    print("End of process creation: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # Start new Threads
    for thread in threads:
        thread.start()
    print("End of process starting: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    for thread in threads:
        thread.join()
    print("End of kpbs threads: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    while not q.empty():
        thread_item = q.get()
        for key in thread_item.keys():
            simscore_dic[key] = thread_item[key]
    end = time.time()
    print("keyphrase_similarity" + str(end - start))
    return simscore_dic

def init_word_dics(grouped_entity_kps):
    num_ent_in_kps_dic = SortedDict()
    num_kp_in_kps_dic = SortedDict()
    word_dict3 = SortedDict()
    for kp_words in grouped_entity_kps:
        if len(kp_words) > 10:
            kp_words = list(kp_words[:10])
        for word in kp_words:
            num_ent_in_kps_dic[word] = 0
            num_kp_in_kps_dic[word] = 0
            word_dict3[word] = 0
    return (num_kp_in_kps_dic, num_ent_in_kps_dic, word_dict3)

def find_num_ent_in_kps(num_kp_in_kps_dic, num_ent_in_kps_dic, mixed_keyphrases):
    for entity in mixed_keyphrases.keys():
        for ent_kp_words in mixed_keyphrases[entity]:
            for word in num_kp_in_kps_dic.keys():
                if word in ent_kp_words:
                    num_kp_in_kps_dic[word] += 1
        for word in num_ent_in_kps_dic.keys():
            if num_kp_in_kps_dic[word] > 0:
                num_ent_in_kps_dic[word] += 1
                num_kp_in_kps_dic[word] = 0
    num_kp_in_kps_dic = {}
    return num_ent_in_kps_dic

def find_num_kp_in_candidate_kps(grouped_keyphrases_dic, num_kp_in_candidate_kps_dic, entity_candidates):
    num_kps_in_candidates = 0
    for entity in entity_candidates:
        num_kps_in_candidates += len(grouped_keyphrases_dic[entity])
        for kp_words in grouped_keyphrases_dic[entity]:
            for word in num_kp_in_candidate_kps_dic.keys():
                if word in kp_words:
                    num_kp_in_candidate_kps_dic[word] += 1


    return (num_kp_in_candidate_kps_dic, num_kps_in_candidates)


def get_simscore(entity, entity_candidates, grouped_keyphrases_dic, link_anchors_of_ent,
                 title_of_ent_linking_to_ent, words_of_document):
    if 'paradise' in entity:
        print('ENTITY1: ' + entity)
    npmi_speedup_dict_num = {}
    npmi_speedup_dict_den = {}
    grouped_entity_kps = grouped_keyphrases_dic[entity]
    simscore = 0.0
    # find here the keyphrases of IN_e (in the article)
    foreign_grouped_keyphrases = mk_unique_foreign_entity_to_keyphrases(title_of_ent_linking_to_ent[entity], link_anchors_of_ent)
    foreign_grouped_keyphrases[entity] = SortedList(grouped_entity_kps)# uniqueify_grouped_kps(grouped_kps)

    word_dictionary1, word_dictionary2, word_dict3 = init_word_dics(grouped_entity_kps)
    num_ent_in_kps_dic = find_num_ent_in_kps(word_dictionary1, word_dictionary2, foreign_grouped_keyphrases)

    num_kp_in_candidate_kps_dic, num_kps_in_candidates = find_num_kp_in_candidate_kps(grouped_keyphrases_dic, word_dict3, entity_candidates)

    if 'paradise' in entity:
        print('ENTITY2: ' + entity)

    for kp_words in grouped_entity_kps:
        if 'paradise' in entity:
            print('KP_WORDS_TEST1: *' + entity + '*' + str(kp_words))
        indices = []
        if len(kp_words) > 10:
            kp_words = list(kp_words[:10])
        if 'paradise' in entity:
            for i in range(len(kp_words) - 1, 0, -1):
                word = kp_words[i]
                #print('CHECK FOR REMOVE: ' + word)
                if word == '' or word == 'er' or word == 'med' or word == 'det' or word == 'til' or word == 'en':
                    kp_words.remove(word)
        kp_words = [word for word in kp_words if word not in npmi_speedup_dict_den.keys()]

        maximum_words_in_doc = list(set(kp_words).intersection(words_of_document))
        if len(maximum_words_in_doc) == 0:
            continue
        if 'paradise' in entity:
            print('KP_WORDS_TEST2: *' + entity + '*' + str(kp_words))
        for word in maximum_words_in_doc:
            word_idxs = [i for i, x in enumerate(words_of_document) if
                         x == word]  # Get indicies of all occurences of a kp-word
            if len(word_idxs) > 0:  # if empty, the word is not considered in the cover
                indices.append(word_idxs)

        cover, cover_span = min_distance_indices(indices)  # finds cover
        if 'paradise' in entity:
            print('COVER: ' + str(cover_span) + ' - ' + str(cover))
        if cover_span == 0:
            continue
        if 'paradise' in entity:
            print('KP_WORDS_TEST3: *' + entity + '*' + str(kp_words))
        z = len(maximum_words_in_doc) / cover_span
        denominator = sum(
            [npmi(word, entity_candidates, foreign_grouped_keyphrases, grouped_keyphrases_dic, npmi_speedup_dict_den, entity, num_ent_in_kps_dic, num_kp_in_candidate_kps_dic, num_kps_in_candidates) for word
             in kp_words])
        if denominator == 0.0:
            continue
        if 'paradise' in entity:
            print('KP_WORDS_TEST4: *' + entity + '*' + str(kp_words))
        numerator = sum([npmi(words_of_document[index], entity_candidates, foreign_grouped_keyphrases, grouped_keyphrases_dic,
                              npmi_speedup_dict_num, entity, num_ent_in_kps_dic, num_kp_in_candidate_kps_dic, num_kps_in_candidates) for index in cover])
        score = z * (numerator / denominator) ** 2
        simscore += score
        if 'paradise' in entity:
            print('KP_WORDS_TEST5: *' + entity + '*' + str(kp_words))
    if 'paradise' in entity:
        print('ENTITY3: ' + entity)
    return simscore

#import threading
#print(threading.active_count())
#from lxml import etree
import paths
#tree = etree.parse(paths.get_wikipedia_article_path())
#root = tree.getroot()
#print(str(keyphrase_similarity(["paris", "paris (supertramp)", "paris (lemvig kommune)", "anders fogh rasmussen"], {"paris": ["paris", "paris (supertramp)", "paris (lemvig kommune)"], "anders fogh rasmussen": ["anders fogh rasmussen"]}, ["paris", "er", "en", "by", "som", "blev", "bombet", "af", "tyskland", "under", "krigen", "mod", "danmark"], shelve.open("NamedEntityDisambiguator/dbs/references_dic"), shelve.open("NamedEntityDisambiguator/dbs/link_dic"), shelve.open("NamedEntityDisambiguator/dbs/link_anchor_dic"))))
#"paris", "er", "det", "progressive", "rockband", "supertramps", "første", "livealbum", "udgivet", "i", "1980"̈́


#l = SortedList(["åbenrå", "æv", "banan", "abe", "t-bone", "isbjørn"])
#print(str(l))

#print(str("t-bone" in l))