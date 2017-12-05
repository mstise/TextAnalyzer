import time
from NamedEntityDisambiguator.Construct_mention_entity import construct_ME_graph
from NamedEntityRecognizer.Retrieve_All_NER import retrieve_ner_single_document
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator.LinksToEntity import links_to_me
from NamedEntityDisambiguator.Graph_disambiguation_algorithm import graph_disambiguation_algorithm
from NamedEntityDisambiguator.EvaluateEntityDisambiguator import ned_evaluator
from NamedEntityDisambiguator.Entity_entity_coherence import create_entity_entity_dict
from lxml import etree
import paths
import os
import copy

def keyphrase_sim_speedup(wiki_tree_root):
    start = time.time()
    reference_keyphrases = References.References(wiki_tree_root)
    end = time.time()
    print("references" + str(end - start))
    start = time.time()
    title_of_ent_linking_to_ent = links_to_me(wiki_tree_root)
    end = time.time()
    print("incoming_ent_titles" + str(end - start))
    start = time.time()
    ent_ent_coh_dict = create_entity_entity_dict(wiki_tree_root)
    end = time.time()
    print("ent_ent_coh_dict" + str(end - start))
    return reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict

def main():
    start = time.time()

    num_files = len(os.listdir(paths.get_external_annotated()))
    counter = 0
    for filename in os.listdir(paths.get_external_annotated()):
        print("Beginning file " + str(counter) + " out of " + str(num_files))
        recognized_mentions = retrieve_ner_single_document(paths.all_external_entities + "/" + filename)

        tree = etree.parse(paths.get_wikipedia_article_path())
        root = tree.getroot()

        reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict = keyphrase_sim_speedup(root)

        G = construct_ME_graph(paths.get_external_procesed_news() + "/" + filename, recognized_mentions, root, reference_keyphrases, title_of_ent_linking_to_ent, ent_ent_coh_dict)
        mennr_entnr_list = graph_disambiguation_algorithm(copy.deepcopy(G))

        with open(paths.get_external_disambiguated_outputs() + '/' + filename, 'w') as f:
            for mennr_entnr in mennr_entnr_list:
                mention = G.node[mennr_entnr[0]]["key"]
                if mennr_entnr[1] == None:
                    matching_entity = "None"
                else:
                    matching_entity = "w." + str(G.node[mennr_entnr[1]]["key"])

                f.write(mention + ", [u\'" + matching_entity + "\']\n")
        counter += 1

    accuracy = ned_evaluator(paths.get_external_disambiguated_outputs(), paths.get_external_annotated())
    print("NED accuracy is: " + str(accuracy))



    end = time.time()
    print(end - start)

main()