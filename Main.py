import time
from NamedEntityDisambiguator import Construct_mention_entity
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator.LinksToEntity import links_to_me
from NamedEntityDisambiguator.Graph_disambiguation_algorithm import graph_disambiguation_algorithm
from lxml import etree
import paths
import os

def keyphrase_sim_speedup(wiki_tree_root):
    start = time.time()
    reference_keyphrases = References.References(wiki_tree_root)
    end = time.time()
    print("references" + str(end - start))
    start = time.time()
    title_of_ent_linking_to_ent = links_to_me(wiki_tree_root)
    end = time.time()
    print("incoming_ent_titles" + str(end - start))

    return reference_keyphrases, title_of_ent_linking_to_ent

def main():
    start = time.time()

    for filename in os.listdir("/home/duper/Desktop/entiti/"):
        recognized_mentions = retrieve_ner_single_document("/home/erisos/Desktop/entitii/" + filename)

        tree = etree.parse(paths.get_wikipedia_article_path())
        root = tree.getroot()

        reference_keyphrases, title_of_ent_linking_to_ent = keyphrase_sim_speedup(root)

        G = Construct_mention_entity(filename, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent)
        mennr_entnr_list = graph_disambiguation_algorithm(G)
        for mennr_entnr in mennr_entnr_list:
            mention = G.node[mennr_entnr[0]]["key"]
            matching_entity = G.node[mennr_entnr[1]]["key"]



    end = time.time()
    print(end - start)

main()