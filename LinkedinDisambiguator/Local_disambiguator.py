from LinkedinDisambiguator.Google_scraper import google_scraper
from NamedEntityRecognizer.EvaluateEntityRecognizer import get_mentions
import paths
import re

MAX_LIMIT_GOOGLE = 36 #words that google defines as a limit in its query
NUM_ENTITY_CANDIDATES = 3

def policy(results, mention_to_disamb):
    higheset_matches = 0
    for link in results:
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



def local_disambiguator(doc_name, entity_path):
    with open(doc_name) as f:
        mentions = get_mentions(doc_name, entity_path)
        for i in range(0, len(mentions)):
            mention_to_disamb = mentions[i]
            related_mentions = []
            word_counter = len(mention_to_disamb.split()) + 2 #+2 to include the 2 site: queries
            backward_flag = True
            backward_i = i - 1
            forward_i = i + 1
            while True:
                related_mention = ""
                if backward_flag and backward_i > 0:
                    related_mention = mentions[backward_i]
                    backward_i -= 1
                if not backward_flag and forward_i < len(mentions):
                    related_mention = mentions[forward_i]
                    forward_i += 1
                word_counter += len(related_mention.split())
                if word_counter > MAX_LIMIT_GOOGLE or (backward_i < 0 and forward_i > len(mentions)):
                    break
                else:
                    related_mentions.append(related_mention)
                    backward_flag = not backward_flag
            query_results = google_scraper(mention_to_disamb, related_mentions)
            results = [next(query_results), next(query_results), next(query_results)]
            result = policy(results, mention_to_disamb)


print(policy(["https://dk.linkedin.com/in/poul-ole-jensen-2418405", "https://dk.linkedin.com/in/poul-jensen-7a304699"], "Poul-Ole Jensen"))

#local_disambiguator(doc_name, paths.get_external_disk_path())


