from lxml import etree
import paths
from NamedEntityDisambiguator.Prior import popularityPrior
from NamedEntityDisambiguator.keyphrase_based_similarity import keyphrase_similarity
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator.Mention_entity_finder import get_mention_entity_possibilities
from NamedEntityDisambiguator.Entity_entity_coherence import entity_entity_coherence
import NamedEntityDisambiguator.Utilities as util
import networkx as nx

def construct_ME_graph(document, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict, alpha=0.45, beta=0.45, gamma=0.1):

    priors = popularityPrior(recognized_mentions, root)
    print("these are priors: " + str(priors))
    priors_wo_mentions = [prior[1] for prior in priors]
    entities = []
    counter = 0
    second_round_list = []
    second_round_priors_id = []
    for entities_AND_priors in priors_wo_mentions:
        if len(entities_AND_priors) != 0:
            entities.extend([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])
            counter += 1
        else:
            if priors[counter][0][-1] == 's':
                second_round_list.append(str(priors[counter][0][0:-1]))
                second_round_priors_id.append(counter)
                counter += 1

    if len(second_round_list) != 0:
        new_priors = popularityPrior(second_round_list, root)
        for i in range(0, len(new_priors)):
            priors[second_round_priors_id[i]] = new_priors[i]
        new_priors_wo_mentions = [prior[1] for prior in new_priors]
        for entities_AND_priors in new_priors_wo_mentions:
            if len(entities_AND_priors) != 0:
                entities.extend([entities_AND_priors[0] for entities_AND_priors in entities_AND_priors])
    entity_node_dict = {}
    G = nx.Graph()

    print("these are entities: " + str(entities))
    # alle mentions til den samme entity candidate har samme sim_score (derfor der kun er entity-keys i dic)
    simscore_dic = keyphrase_similarity(root, entities, [word for line in open(document, 'r') for word in util.split_and_delete_special_characters(line)], reference_keyphrases, title_of_ent_linking_to_ent)

    print("these are simscore keys: " + str(simscore_dic.keys()))


    for prior in priors:
        mention_nr = G.number_of_nodes()
        G.add_node(mention_nr, key=prior[0], entity=False, taboo=False)
        for entity_with_prior in prior[1]:
            entity = entity_with_prior[0]
            if entity in entity_node_dict.keys():
                entity_nr = entity_node_dict[entity]
                G.add_edge(entity_nr, mention_nr, weight=alpha * entity_with_prior[1] + beta * simscore_dic[entity])
                continue
            entity_nr = G.number_of_nodes()
            G.add_node(entity_nr, key=entity, entity=True, taboo=False)
            G.add_edge(entity_nr, mention_nr, weight=alpha * entity_with_prior[1] + beta * simscore_dic[entity])
            #entities.append(entity)
            entity_node_dict[entity] = entity_nr


    #kp_sim_score = keyphrase_similarity(root, )
    print("Beginning on ent_ent_coh")
    ent_ent_coh_triples = entity_entity_coherence(entities, ent_ent_coh_dict)
    node_nr_triples = [(entity_node_dict[entity1], entity_node_dict[entity2], gamma * coherence) for entity1, entity2, coherence in ent_ent_coh_triples]
    G.add_weighted_edges_from(node_nr_triples)

    print("this is graph before: ")
    for node in G.nodes():
        print(str(G.node[node]["key"]))

    #nx.write_gml(G, "/home/duper/Desktop")
    #nx.read_gml("/home/duper/Desktop")
    return G
'''import time
start = time.time()

G = construct_ME_graph()

end = time.time()
print(end - start)
print("hello!")'''