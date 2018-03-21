import time
from datetime import datetime
from NamedEntityDisambiguator.Construct_mention_entity import construct_ME_graph
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator.LinksToEntity import links_to_me
from NamedEntityDisambiguator.Graph_disambiguation_algorithm import graph_disambiguation_algorithm
from NamedEntityDisambiguator.EvaluateEntityDisambiguator import ned_evaluator
from NamedEntityDisambiguator.Entity_entity_coherence import create_entity_entity_dict
from NamedEntityDisambiguator.Utilities import convert_danish_letters_list
from NamedEntityDisambiguator.Link_anchor_text import find_link_anchor_texts
from lxml import etree
import paths
import os
import copy
import threading
import shelve
import multiprocessing as mp

class myThread1 (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, root):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.root = root
    def run(self):
        f = open("NamedEntityDisambiguator/dbs/references_dic.txt", "r")
        if f.readline() != str(os.path.getmtime("NamedEntityDisambiguator/References.py")):
            References.References(self.root)
        self.result = "NamedEntityDisambiguator/dbs/references_dic"
class myThread2 (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, root):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.root = root
    def run(self):
        f = open("NamedEntityDisambiguator/dbs/link_dic.txt", "r")
        if f.readline() != str(os.path.getmtime("NamedEntityDisambiguator/LinksToEntity.py")):
            links_to_me(self.root)
        self.result = "NamedEntityDisambiguator/dbs/link_dic"
class myThread3 (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, root):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.root = root
    def run(self):
        f = open("NamedEntityDisambiguator/dbs/ent_coh_dic.txt", "r")
        if f.readline() != str(os.path.getmtime("NamedEntityDisambiguator/Entity_entity_coherence.py")):
            create_entity_entity_dict(self.root)
        self.result = "NamedEntityDisambiguator/dbs/ent_coh_dic"

class myThread4 (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, root):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.root = root
    def run(self):
        f = open("NamedEntityDisambiguator/dbs/link_anchor_dic.txt", "r")
        if f.readline() != str(os.path.getmtime("NamedEntityDisambiguator/LinksToEntity.py")):
            find_link_anchor_texts(self.root)
        self.result = "NamedEntityDisambiguator/dbs/link_anchor_dic"

def keyphrase_sim_speedup(wiki_tree_root):
    start = time.time()
    threads = []
    threads.append(myThread1(1, wiki_tree_root))
    threads.append(myThread2(2, wiki_tree_root))
    threads.append(myThread3(3, wiki_tree_root))
    threads.append(myThread4(4, wiki_tree_root))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    reference_keyphrases = threads[0].result
    title_of_ent_linking_to_ent = threads[1].result
    ent_ent_coh_dict = threads[2].result
    link_anchors_of_ent = threads[3].result

    end = time.time()
    print("references, incoming & ent_ent_coh_dict" + str(end - start))
    return reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict, link_anchors_of_ent

def main():
    mp.set_start_method('fork')
    print("Usable CPUs: " + str(len(os.sched_getaffinity(0))))
    start = time.time()

    tree = etree.parse(paths.get_wikipedia_article_path())
    root = tree.getroot()

    reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict, link_anchors_of_ent = keyphrase_sim_speedup(root)

    prior_dict = shelve.open("NamedEntityDisambiguator/dbs/prior_dic")
    reference_keyphrases = shelve.open(reference_keyphrases)
    title_of_ent_linking_to_ent = shelve.open(title_of_ent_linking_to_ent)
    link_anchors_of_ent = shelve.open(link_anchors_of_ent)
    ent_ent_coh_dict = shelve.open(ent_ent_coh_dict)

    num_files = len(os.listdir(paths.get_all_external_entities_path()))
    counter = 0
    for filename in os.listdir(paths.get_all_external_entities_path()):
        if counter < 585:
            counter += 1
            continue
        print("Beginning file " + str(counter) + " out of " + str(num_files))
        print('Document started at: ' + str(datetime.now()))
        recognized_mentions = retrieve_ner_single_document(paths.all_external_entities + "/" + filename)
        recognized_mentions = convert_danish_letters_list(recognized_mentions)

        G = construct_ME_graph(paths.get_external_procesed_news() + "/" + filename, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent, ent_ent_coh_dict, prior_dict)
        print("Graph constructed at: " + str(datetime.now()))
        men_ent_list = graph_disambiguation_algorithm(copy.deepcopy(G))
        print("Graph algorithm completed at:" + str(datetime.now()))

        print("These are the disambiguations: ")
        with open(paths.get_external_disambiguated_outputs() + '/' + filename, 'w') as f:
            for men_ent in men_ent_list:
                mention = men_ent[0]
                if men_ent[1] == None:
                    matching_entity = "None"
                else:
                    matching_entity = "w." + str(men_ent[1])

                f.write(mention + ", [u\'" + matching_entity + "\']\n")
                print(mention + ", [u\'" + matching_entity + "\']")
        counter += 1

    accuracy = ned_evaluator(paths.get_external_disambiguated_outputs(), paths.get_external_annotated())
    print("NED accuracy is: " + str(accuracy))



    end = time.time()
    print(end - start)

main()