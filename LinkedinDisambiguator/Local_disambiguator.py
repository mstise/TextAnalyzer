from LinkedinDisambiguator.Google_scraper import google_scraper
from NamedEntityRecognizer.EvaluateEntityRecognizer import get_mentions
import re
import paths
from random import uniform
from time import sleep

MAX_LIMIT_GOOGLE = 32 #words that google defines as a limit in its query
NUM_ENTITY_CANDIDATES = 3

def policy(results, mention_to_disamb):
    higheset_matches = -1
    for link in results:
        link = link[0]
        name = ""
        if link.find("/company/"):
            name = re.split(' |-', link[32:])
        if link.find("/in/"):
            name = re.split(' |-', link[27:])
        match_words = set(re.split(' |-', mention_to_disamb.lower()))
        matches = len(match_words.intersection(name))
        if matches > higheset_matches:
            higheset_matches = matches
            result = link
    return result



def local_disambiguator(doc_name, entity_path=paths.get_all_external_entities_path(), annotated_path=paths.get_external_annotated()):
    #with open(doc_name) as f:
    mentions = get_mentions(doc_name, entity_path)
    for i in range(0, len(mentions)):
        sleep(uniform(1, 3))
        mention_to_disamb = mentions[i]
        related_mentions = []
        word_counter = len(mention_to_disamb.split()) + 2 #+2 to include the 2 site: queries
        backward_flag = True
        backward_i = i - 1
        forward_i = i + 1
        while True:
            related_mention = ""
            if backward_flag and backward_i > -1:
                related_mention = mentions[backward_i]
                backward_i -= 1
            if not backward_flag and forward_i < len(mentions):
                related_mention = mentions[forward_i]
                forward_i += 1
            word_counter += len(related_mention.split())
            if word_counter > MAX_LIMIT_GOOGLE:
                break
            elif (backward_i == 0 and forward_i > len(mentions) or (backward_i < 0 and forward_i == len(mentions))):
                if related_mention != '':
                    related_mentions.append(related_mention)
                break
            else:
                if related_mention != '':
                    related_mentions.append(related_mention)
                backward_flag = not backward_flag
        query_results = google_scraper(mention_to_disamb, related_mentions)
        results = []#[next(query_results), next(query_results), next(query_results)]
        try:
            results.append([next(query_results)])
            results.append([next(query_results)])
            results.append([next(query_results)])
        except StopIteration:
            result = policy(results, mention_to_disamb)
            continue
        result = policy(results, mention_to_disamb)


#print(policy(["https://dk.linkedin.com/in/poul-ole-jensen-2418405", "https://dk.linkedin.com/in/poul-jensen-7a304699"], "Poul-Ole Jensen"))
import os
for doc_name in os.listdir(paths.get_external_annotated()):
    local_disambiguator(doc_name)


