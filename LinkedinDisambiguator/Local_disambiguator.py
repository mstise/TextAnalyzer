from LinkedinDisambiguator.Google_scraper import google_scraper
import re
import paths
import os
from NamedEntityDisambiguator import Utilities

MAX_LIMIT_GOOGLE = 32 #words that google defines as a limit in its query
NUM_ENTITY_CANDIDATES = 3


def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line

def get_mentions_from_disambs(doc_name, path):
    m_e_list = []
    for line in open(path + "/" + doc_name):
        m_e = re.split(r', \[', line)
        mention = m_e[0]
        entity = m_e[1][2:-3]
        m_e_list.append([mention, entity])
    return m_e_list

def get_mentions_from_ents(filename, path):
    mentions = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        new_line = Utilities.convert_danish_letters(new_line)
        mentions.append(new_line)
    return mentions

def policy(results, mention_to_disamb):
    result = None
    higheset_matches = -1
    for link in results:
        name = ""
        if link.find("/company/"):
            #name = re.split(' |-', link[32:])
            name = str(link[32:])
        if link.find("/in/"):
            #name = re.split(' |-', link[27:])
            name = str(link[27:])
        match_words = list(re.split(' |-', mention_to_disamb.lower()))
        matches = 0
        end_matches = False
        for match_word in match_words:
            if match_word in name:
                matches += 1
                end_matches = True
            else:
                end_matches = False

        #This deals with the trailing s from polyglots recognizer
        if not end_matches and match_word[-1] == 's':
            #res = str(match_word[:-1])
            if str(match_word[:-1]) in name:
                matches += 1
        #matches = len(match_words.intersection(name))
        if matches > higheset_matches:
            higheset_matches = matches
            result = link
    #Here the None is set only if there is no similarity and the first characters does not match (so acronyms isnt set to None)
    if higheset_matches == 0 and result[0] != mention_to_disamb.lower()[0]:
        return 'None'
    else:
        return result

def translate_to_danish(text):
    text = text.replace('%C3%A6', 'æ')
    text = text.replace('%C3%86', 'Æ')
    text = text.replace('%C3%B8', 'ø')
    text = text.replace('%C3%98', 'Ø')
    text = text.replace('%C3%A5', 'å')
    text = text.replace('%C3%85', 'Å')
    text = text.replace('%C3%B4', 'ô')
    text = text.replace('%C3%94', 'Ô')
    text = text.replace('%C3%BC', 'ü')
    text = text.replace('%C3%9C', 'Ü')
    text = text.replace('%C3%B6', 'ö')
    text = text.replace('%C3%96', 'Ö')
    return text

def run_local_disambiguator():
    counter = 1
    for doc_name in os.listdir(paths.get_external_disambiguated_outputs()):
        if os.path.isfile(paths.get_external_disambiguated_outputs() + '2/' + doc_name):
            continue
        # if '00_05_1-_sektion_fre_s005_01_erhverv__0408_201708040000_1007986827' in doc_name:
        mention_entities = local_disambiguator(doc_name)
        with open(paths.get_external_disambiguated_outputs() + '2/' + doc_name, 'w') as f:
        #with open('/home/erisos/Desktop/Disambiguated/Disambiguated2/' + doc_name, 'w') as f:
            for line in mention_entities:
                f.write(line + '\n')
                print(line)
        print('    Completed document ' + str(counter))
        counter += 1

def local_disambiguator(doc_name, path=paths.get_all_external_entities_path()):# entity_path=paths.get_all_external_entities_path(), disambiguated_path=paths.get_external_disambiguated_outputs()):
    #with open(doc_name) as f:
    returned_results = []
    old_mention_entity_list = get_mentions_from_disambs(doc_name, paths.get_external_disambiguated_outputs())
    order_mention_entity_list = get_mentions_from_ents(doc_name, path)#entity_path)
    mention_entity_list = []
    #After disambiguation the order of entities have been sorted. They need to be unsorted! (which is done in this loop)
    for item in order_mention_entity_list:
        for tuple in old_mention_entity_list:
            if tuple[0].lower() == item.lower():
                mention_entity_list.append(tuple)
                break
    for i in range(0, len(mention_entity_list)):
        if mention_entity_list[i][1] != 'None':
            returned_results.append(mention_entity_list[i][0] + ', [u\'' + mention_entity_list[i][1] + '\']')
            continue
        # sleep(uniform(10, 20))
        mention_to_disamb = mention_entity_list[i][0]
        related_mentions = []
        word_counter = len(mention_to_disamb.split()) + 2 #+2 to include the 2 site: queries
        entity_counter = 0
        backward_flag = True
        backward_i = i - 1
        forward_i = i + 1
        while True:
            related_mention = ""
            if backward_flag and backward_i > -1:
                related_mention = mention_entity_list[backward_i][0]
                backward_i -= 1
            if not backward_flag and forward_i < len(mention_entity_list):
                related_mention = mention_entity_list[forward_i][0]
                forward_i += 1
            if related_mention in related_mentions:
                backward_flag = not backward_flag
                continue
            word_counter += len(related_mention.split())
            if related_mention != '':
                entity_counter += 1
            if word_counter > MAX_LIMIT_GOOGLE or entity_counter > 10:
                break
            elif (backward_i == 0 and forward_i > len(mention_entity_list) or (backward_i < 0 and forward_i == len(mention_entity_list))):
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
            #print(results)
        except StopIteration:
            "No matches were found"
        finally:
            if len(results) > 0:
                translated_results = []
                for result in results:
                    result = translate_to_danish(result[0])
                    translated_results.append(result)
                result = policy(translated_results, mention_to_disamb)
                if result == 'None':
                    returned_results.append(mention_entity_list[i][0] + ', [u\'None\']')
                else:
                    returned_results.append(mention_entity_list[i][0] + ', [u\'l.' + result[24:] + '\']')
            else:
                returned_results.append(mention_entity_list[i][0] + ', [u\'None\']')
        # except StopIteration:
        #     result = policy(results, mention_to_disamb)
        #     result = translate_to_danish(result)
        #     returned_results.append(mention_entity_list[i][0] + ', [l.' + result[24:] + ']')
        #     continue

    # with open(paths.get_external_disambiguated_outputs() + '2/' + doc_name, 'w') as f:
    #     for men_ent in returned_results:
    #         mention = men_ent[0]
    #         if men_ent[1] == None:
    #             matching_entity = "None"
    #         else:
    #             matching_entity = "w." + str(men_ent[1])
    #
    #         f.write(mention + ", [u\'" + matching_entity + "\']\n")
    #         print(mention + ", [u\'" + matching_entity + "\']")
    return returned_results

# local_disambiguator("00_04_1-_sektion_lør_s004_01_kultur___0909_201709090000_1008261881.txt")
#print(policy(["https://dk.linkedin.com/in/poul-ole-jensen-2418405", "https://dk.linkedin.com/in/poul-jensen-7a304699"], "Poul-Ole Jensen"))
#import os
#for doc_name in os.listdir(paths.get_external_annotated()):
#    local_disambiguator(doc_name)
run_local_disambiguator()
#print(policy(["https://www.linkedin.com/in/lisa", "https://www.linkedin.com/in/lisasandagerramlow", "https://www.linkedin.com/in/lars-sandager-ramlow"], 'Lisa Sandager Ramlows'))