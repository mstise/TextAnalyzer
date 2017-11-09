from lxml import etree
import paths
import sys
from NamedEntityDisambiguator.keyphrase_based_similarity import keyphrase_similarity
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator import LinksToEntity
from itertools import product
from NamedEntityDisambiguator.Prior import popularityPrior
from NamedEntityDisambiguator.Entity_entity_coherence import entity_entity_coherence
from NamedEntityRecognizer.Retrieve_All_NER import ner_lst_retriever
import networkx as nx
import matplotlib.pyplot as plt

recognized_mentions = ner_lst_retriever(path="/home/duper/Desktop/entiti")

tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()

priors = popularityPrior(recognized_mentions, root)
entities = []
entity_node_dict = {}
G = nx.Graph()
for prior in priors:
    mention_nr = G.number_of_nodes()
    G.add_node(mention_nr, key=prior[0], entity=False)
    for entity_with_prior in prior[1]:
        entity_nr = G.number_of_nodes()
        G.add_node(entity_nr, key=entity_with_prior[0], entity=True)
        G.add_edge(entity_nr, mention_nr, weight=entity_with_prior[1])
        entities.append(entity_with_prior[0])
        entity_node_dict[entity_with_prior[0]] = entity_nr

#kp_sim_score = keyphrase_similarity(root, )


#links_to_entity = LinksToEntity.links_to_me(entities, root)
#for n in G.nodes_iter():
#    print(str(n) + ", " + str(G.node[n]["entity"]) + ", " + str(G.node[n]["key"]))

ent_ent_coh_triples = entity_entity_coherence(entities, root)
node_nr_triples = [(entity_node_dict[entity1], entity_node_dict[entity2], coherence) for entity1, entity2, coherence in ent_ent_coh_triples]
G.add_weighted_edges_from(node_nr_triples)

nx.write_gml(G, "/home/duper/Desktop")
#nx.read_gml("/home/duper/Desktop")
test = 5