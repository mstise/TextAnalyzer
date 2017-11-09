import sys
from NamedEntityDisambiguator import References
from itertools import product
from NamedEntityDisambiguator.Category_names import category_words
from NamedEntityDisambiguator.Link_anchor_text import find_link_anchor_texts
from NamedEntityDisambiguator.LinksToEntity import links_to_me

#This function finds the indicies of the minimum cover using maximum amount of words from kp
def min_distance_indices(indices):
    combinations = list(product(*indices))
    sorted_combinations = [sorted(x) for x in combinations]
    min_dist = sys.maxsize
    for i in range(0, len(sorted_combinations)-1):
        new_dist = sorted_combinations[i][-1] - sorted_combinations[i][0]
        if new_dist < min_dist:
            min_dist = new_dist
            min_dist_index = i
    return combinations[min_dist_index], min_dist #returns cover (in indices) and length of the cover

def mutual_information(e, w, keyphrases, num_entities):
    for kp in keyphrases:
        w_count = kp.count(w)
        return w_count / num_entities

def keyphrase_similarity(wiki_tree_root, entity = "Anders Fogh Rasmussen", num_entities = 1):
    words_of_document = [word for line in open("/home/duper/Desktop/Fogh_eks", 'r') for word in line.split()] #TODO: This should be dealt with :D

    keyphrases = []

    reference_keyphrases = References.References(wiki_tree_root)
    keyphrases.extend(reference_keyphrases[entity])

    category_kps = category_words([entity]) #TODO: Muligvis også lav alle disse til en dictionary, sådan at keyphrase_similarity kan tage alle entities?
    keyphrases.extend(category_kps[entity])

    link_anchors_of_entity = find_link_anchor_texts([entity], wiki_tree_root) #TODO: Make real link anchor text
    keyphrases.extend(link_anchors_of_entity[1])

    title_of_ent_linking_to_ent = links_to_me([entity], wiki_tree_root)
    keyphrases.extend(title_of_ent_linking_to_ent[1])

    simscore = 0

    for kp in keyphrases:
        indices = []
        kp_words = kp.split()
        maximum_words_in_doc = list(set().union(kp_words, words_of_document))
        for word in maximum_words_in_doc:
            indices.append([i for i, x in enumerate(words_of_document) if x == word]) #Get indicies of all occurences of word
        cover, cover_span = min_distance_indices(indices) #finds cover
        z = len(maximum_words_in_doc) / cover_span
        nominator = sum([mutual_information(entity, words_of_document[index], keyphrases, num_entities) for index in cover])
        denominator = sum([mutual_information(entity, word, keyphrases, num_entities) for word in kp_words])
        score = z * (nominator / denominator)**2
        simscore += score

    return simscore