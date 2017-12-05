import time
from NamedEntityDisambiguator.Construct_mention_entity import construct_ME_graph
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator.LinksToEntity import links_to_me
from NamedEntityDisambiguator.Graph_disambiguation_algorithm import graph_disambiguation_algorithm
from NamedEntityDisambiguator.EvaluateEntityDisambiguator import ned_evaluator
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
        recognized_mentions = retrieve_ner_single_document("/home/duper/Desktop/Predicted_Disambiguations/" + filename)

        tree = etree.parse(paths.get_wikipedia_article_path())
        root = tree.getroot()

        reference_keyphrases, title_of_ent_linking_to_ent = keyphrase_sim_speedup(root)

        G = construct_ME_graph("/home/duper/Desktop/Predicted_Disambiguations/" + filename, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent)
        mennr_entnr_list = graph_disambiguation_algorithm(G)
        for mennr_entnr in mennr_entnr_list:
            mention = G.node[mennr_entnr[0]]["key"]
            matching_entity = G.node[mennr_entnr[1]]["key"]

            ned_evaluator(disambiguated_path="/home/duper/Desktop/Predicted_Disambiguations", annotated_path="/home/duper/Desktop/entiti")



    end = time.time()
    print(end - start)

main()