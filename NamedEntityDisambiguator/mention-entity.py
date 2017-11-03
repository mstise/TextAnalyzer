from lxml import etree
import paths
import sys
from NamedEntityDisambiguator import Prior
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator import LinksToEntity
from itertools import product
from NamedEntityDisambiguator.Prior import popularityPrior

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
    words_of_document = [word for line in open("/home/duper/Desktop/Fogh_eks", 'r') for word in line.split()]

    keyphrases = []
    reference_keyphrases = References.References(wiki_tree_root)
    keyphrases.extend(reference_keyphrases[entity])
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

        print("5")  # priors = Prior.popularityPrior(names, root)

tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()

priors = popularityPrior(["HP"], root)
entities = []
for prior in priors:
    for entity in prior[1]:
        entities.append(entity[0])

print("du er dum")

#links_to_entity = LinksToEntity.links_to_me(entities, root)



test = 5