from lxml import etree
import paths
from NamedEntityDisambiguator.Prior import popularityPrior
from NamedEntityDisambiguator.Entity_entity_coherence import entity_entity_coherence
from NamedEntityDisambiguator.keyphrase_based_similarity import keyphrase_similarity
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator.Mention_entity_finder import get_mention_entity_possibilities
import networkx as nx

def construct_ME_graph(document = "/home/duper/Desktop/Fogh_eks", alpha=0.4, beta=0.4, gamma=0.1):

    recognized_mentions = retrieve_ner_single_document("/home/duper/Desktop/entiti/Fogh_eks") #TODO: Husk at ændre denne så den passer med entitii

    tree = etree.parse(paths.get_wikipedia_article_path()) #TODO: Flyt disse 2 linjer ud i Main!
    root = tree.getroot()

    priors = popularityPrior(recognized_mentions, root)
    entities = [item[0] for item in priors] #get_mention_entity_possibilities(open("/home/duper/Desktop/entiti/Fogh_eks", 'r'), root)
    entity_node_dict = {}
    G = nx.Graph()

    # alle mentions til den samme entity candidate har samme sim_score (derfor der kun er entity-keys i dic)
    simscore_dic = keyphrase_similarity(root, entities, [word for line in open(document, 'r') for word in line.split()])

    for prior in priors:
        mention_nr = G.number_of_nodes()
        G.add_node(mention_nr, key=prior[0], entity=False)
        for entity_with_prior in prior[1]:
            entity = entity_with_prior[0] #TODO: entity her er lowercased mens simscores ikke er
            entity_nr = G.number_of_nodes()
            G.add_node(entity_nr, key=entity, entity=True)
            G.add_edge(entity_nr, mention_nr, weight=alpha * entity_with_prior[1] + beta * simscore_dic[entity])
            #entities.append(entity)
            entity_node_dict[entity] = entity_nr

    #kp_sim_score = keyphrase_similarity(root, )


    ent_ent_coh_triples = entity_entity_coherence(entities, root)
    node_nr_triples = [(entity_node_dict[entity1], entity_node_dict[entity2], gamma * coherence) for entity1, entity2, coherence in ent_ent_coh_triples]
    G.add_weighted_edges_from(node_nr_triples)

    #nx.write_gml(G, "/home/duper/Desktop")
    #nx.read_gml("/home/duper/Desktop")

    return G
import time
start = time.time()

G = construct_ME_graph()

end = time.time()
print(end - start)
print("hello!")