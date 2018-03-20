from lxml import etree
import paths
from NamedEntityDisambiguator.Prior import popularityPrior
from NamedEntityDisambiguator.keyphrase_based_similarity import keyphrase_similarity
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator.Mention_entity_finder import get_mention_entity_possibilities
from NamedEntityDisambiguator.Entity_entity_coherence import entity_entity_coherence
import NamedEntityDisambiguator.Utilities as util
import networkx as nx
import shelve
import time

def column(matrix, i):
    return [row[i] for row in matrix]


def remove_large_priors(priors, entities, candidate_dic):
    removed = []
    for prior in priors:
        if prior[1][-1][1] > 0.9:
            del candidate_dic[prior[0]]
            for ent in prior[1]:
                entities.remove(ent[0])
            removed.append(prior)
    return removed

def populate_sim_score(removed_priors, sim_score):
    for prior in removed_priors:
        for tuple in prior[1]:
            sim_score[tuple[0]] = 0
        sim_score[prior[1][-1][0]] = 1


def construct_ME_graph(document, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent, ent_ent_coh_dict, prior_dict, alpha=0.45, beta=0.45, gamma=0.1):
    start = time.time()
    priors = popularityPrior(recognized_mentions, prior_dict)
    #print("prior-before: " + str(priors))
    priors_wo_mentions = [prior[1] for prior in priors]
    entities = []
    #entity_candidates_lst = []
    counter = 0
    second_round_list = []
    second_round_priors_id = []
    for entities_AND_priors in priors_wo_mentions:
        #print("counter: " + str(counter))
        #print("with priors: " + str(entities_AND_priors))
        if len(entities_AND_priors) != 0:
            entities.extend([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])
            #entity_candidates_lst.append([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])
            counter += 1
        else:
            if priors[counter][0][-1] == 's':
                second_round_list.append(str(priors[counter][0][0:-1]))
                second_round_priors_id.append(counter)
                #print("second_round_list is now:" + str(second_round_list))
                #print("2nd_round_lst: " + str(second_round_list))
            counter += 1

    if len(second_round_list) != 0:
        new_priors = popularityPrior(second_round_list, prior_dict)
        #print("new_priors: " + str(new_priors))
        for i in range(0, len(new_priors)):
            #print("new_priors[i]: " + str(new_priors[i]) + " and second_round_priors_id[i]: " + str(second_round_priors_id[i]) + "priors[second_round_priors_id[i]]: " + str(priors[second_round_priors_id[i]]))
            new_priors[i][0] = priors[second_round_priors_id[i]][0]
            priors[second_round_priors_id[i]] = new_priors[i]
        new_priors_wo_mentions = [prior[1] for prior in new_priors]
        for entities_AND_priors in new_priors_wo_mentions:
            if len(entities_AND_priors) != 0:
                entities.extend([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])
                #entity_candidates_lst.append([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])

    candidates_dic = {key: value for key, value in zip(column(priors, 0), column(priors, 1))}
    for entity in candidates_dic.keys():
        candidates_dic[entity] = [doble[0] for doble in candidates_dic[entity]]
    end = time.time()
    print("prior time: " + str(end - start) + "********************************************************priors start")
    for prior in priors:
        print("ENTITY: " + str(prior[0]) + " has " + str(len(prior[1])) + ": " + str(prior[1]))
    print("priors end*********************************************************************************priors end")

    entity_node_dict = {}
    G = nx.Graph()

    #print("these are entities: " + str(entities))

    entities_for_sim_score = []
    for ent in entities:
        entities_for_sim_score.append(ent)
    removed_priors = remove_large_priors(priors, entities_for_sim_score, candidates_dic)

    #reference_keyphrases = shelve.open(reference_keyphrases)
    #title_of_ent_linking_to_ent = shelve.open(title_of_ent_linking_to_ent)
    #link_anchors_of_ent = shelve.open(link_anchors_of_ent)
    # alle mentions til den samme entity candidate har samme sim_score (derfor der kun er entity-keys i dic)
    simscore_dic = keyphrase_similarity(root, entities_for_sim_score, candidates_dic, [word for line in open(document, 'r') for word in util.split_and_delete_special_characters(line)], reference_keyphrases, title_of_ent_linking_to_ent, link_anchors_of_ent)

    populate_sim_score(removed_priors, simscore_dic)

    #reference_keyphrases.close()
    #title_of_ent_linking_to_ent.close()
    #link_anchors_of_ent.close()

    #print("sim before normalisation: " + str(simscore_dic))
    #normalise simscore to sum to 1 between candidates
    mention_entities_sim = {}
    for prior in priors:
        mention_entities_sim[prior[0]] = {}
        overall_score = 0
        for entities_comma_props in prior[1]:
            overall_score += simscore_dic[entities_comma_props[0]]
        for entities_comma_props in prior[1]:
            if overall_score == 0:
                mention_entities_sim[prior[0]][entities_comma_props[0]] = 1
                continue
            mention_entities_sim[prior[0]][entities_comma_props[0]] = simscore_dic[entities_comma_props[0]] / overall_score

    print("similarity_scores: " + str(mention_entities_sim))

    for prior in priors:
        mention_nr = G.number_of_nodes()
        G.add_node(mention_nr, key=prior[0], entity=False, taboo=False)
        for entity_with_prior in prior[1]:
            entity = entity_with_prior[0]
            if entity in entity_node_dict.keys():
                entity_nr = entity_node_dict[entity]
                G.add_edge(entity_nr, mention_nr, weight=alpha * entity_with_prior[1] + beta * mention_entities_sim[prior[0]][entity])
                continue
            entity_nr = G.number_of_nodes()
            G.add_node(entity_nr, key=entity, entity=True, taboo=False)
            G.add_edge(entity_nr, mention_nr, weight=alpha * entity_with_prior[1] + beta * mention_entities_sim[prior[0]][entity])
            #entities.append(entity)
            entity_node_dict[entity] = entity_nr


    #kp_sim_score = keyphrase_similarity(root, )
    print("Beginning on ent_ent_coh")
    #ent_ent_coh_dict = shelve.open(ent_ent_coh_dict)
    ent_ent_coh_triples = entity_entity_coherence(entities, ent_ent_coh_dict)
    #ent_ent_coh_dict.close()
    node_nr_triples = [(entity_node_dict[entity1], entity_node_dict[entity2], gamma * coherence) for entity1, entity2, coherence in ent_ent_coh_triples]
    G.add_weighted_edges_from(node_nr_triples)

    # print("this is graph before: ")
    # for node in G.nodes():
    #     print(str(G.node[node]["key"]))

    #nx.write_gml(G, "/home/duper/Desktop")
    #nx.read_gml("/home/duper/Desktop")
    return G
#import time
#start = time.time()

#G = construct_ME_graph()

#end = time.time()
#print(end - start)
#print("hello!")'''

#priors = [['København', [['København', 0.8], ["dør", 0.333], ["ø", 0.00009]]], ['Fyn', [['Fyn', 0.8], ["dr", 0.333], ["Karen", 0.00009]]]]

#prior_dic = {key: value for key, value in zip(column(priors, 0), column(priors, 1))}

#for entity in prior_dic.keys():
#    prior_dic[entity] = [doble[0] for doble in prior_dic[entity]]

#print(str(prior_dic.values()))