#From folder of recognized entities and folder of annotated entities, get an accuracy score.

import os
import re
import paths
import numpy as np
from NamedEntityDisambiguator import Utilities

def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line

def get_mentions(filename, path):
    mentions = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        new_line = Utilities.convert_danish_letters(new_line)
        mentions.append(new_line)
    return mentions


def get_undisambiguated_mentions(filename, path):
    ud_mentions = []
    for line in open(path + "/" + filename):
        if u'None' in line:
            new_line = re.findall(r'.*, \[', line)[0][:-3]
            new_line = Utilities.convert_danish_letters(new_line)
            ud_mentions.append(new_line)
    return ud_mentions

def correctly_recognized_lists(filename, entity_path=paths.get_all_external_entities_path(), annotated_path=paths.get_external_annotated(), remove=['None']):
    mentions = get_mentions(filename, entity_path)
    danish_mentions = []
    for mention in mentions:
        danish_mentions.append(Utilities.convert_danish_letters(mention))
    mentions = [x.lower() for x in danish_mentions]
    result = []
    for line in open(annotated_path + "/" + filename):
        gt_entities = re.findall(r'\|[^\]]*\]\*\]', line)
        ground_truths = re.findall(r'\[\*\[[^\|]*\|', line)
        counter = 0
        for ent in gt_entities:
            for bad_string in remove:
                if '|' + bad_string in ent:
                    del ground_truths[counter]
                    counter -= 1
                    break
            counter += 1
        counter = 0
        for bad_string in remove:
            gt_entities = list(filter(lambda string: '|' + bad_string not in string, gt_entities))
        counter = 0
        for ground_truth in ground_truths:
            groundtruth_string = str(ground_truth[3:-1])
            if groundtruth_string.lower() in mentions:
                mentions.remove(groundtruth_string.lower())
                result.append([groundtruth_string.lower(), gt_entities[counter][1:-3].lower()])
            else:
                test = 1
            counter += 1
    return result


def correctly_recognized(entity_path=paths.get_all_external_entities_path(), annotated_path=paths.get_external_annotated(), remove=[]):
    correct = 0
    for filename in os.listdir(annotated_path):
        mentions = get_mentions(filename, entity_path)
        danish_mentions = []
        for mention in mentions:
            danish_mentions.append(Utilities.convert_danish_letters(mention))
        mentions = [x.lower() for x in danish_mentions]
        for line in open(annotated_path + "/" + filename):
            gt_entities = re.findall(r'\|[^\]]*\]\*\]', line)
            ground_truths = re.findall(r'\[\*\[[^\|]*\|', line)
            counter = 0
            for ent in gt_entities:
                for bad_string in remove:
                    if '|' + bad_string in ent:
                        del ground_truths[counter]
                        counter -= 1
                        break
                counter += 1
            for ground_truth in ground_truths:
                groundtruth_string = str(ground_truth[3:-1])
                if groundtruth_string.lower() in mentions:
                    mentions.remove(groundtruth_string.lower())
                    correct += 1
    return correct

def ner_evaluator(entity_path=paths.get_all_external_entities_path(), annotated_path=paths.get_external_annotated()):
    correct = 0
    imperfect_correct = 0
    ground_truth_not_found = 0
    imperfect_ground_truth_not_found = 0
    excess_mentions = 0
    imperfect_excess_mentions = 0
    gt_none = 0
    entities = []
    entities_in_document = []
    for filename in os.listdir(annotated_path):
        if filename[:1] == '.':
            continue
        mentions = get_mentions(filename, entity_path)
        danish_mentions = []
        for mention in mentions:
            danish_mentions.append(Utilities.convert_danish_letters(mention))
        mentions = [x.lower() for x in danish_mentions]
        for line in open(annotated_path + "/" + filename):
            mentions_with_none = re.findall(r'\[\*\[[^\|]*\|None\]\*\]', line)
            gt_none += len([men[3:-8] for men in mentions_with_none])
            ground_truths = re.findall(r'\[\*\[[^\|]*\|', line)
            for men in re.findall(r'\|[^\]]*\]\*\]', line):
                if '|None]*]' not in men:
                    entities.append(men)
            entities_in_document.append(len(re.findall(r'\|[^\]]*\]\*\]', line)))
            for ground_truth in ground_truths:
                groundtruth_string = str(ground_truth[3:-1])
                if groundtruth_string.lower() in mentions:
                    mentions.remove(groundtruth_string.lower())
                    correct += 1
                    imperfect_correct += len(groundtruth_string.lower().split(' '))
                else:
                    ground_truth_not_found += 1
                    imperfect_ground_truth_not_found += len(groundtruth_string.lower().split(' '))
            excess_mentions += len(mentions)
            imperfect_mentions = mentions
            for ground_truth in ground_truths:
                groundtruth_string = str(ground_truth[3:-1])
                for men in imperfect_mentions:
                    if groundtruth_string.lower() in men:
                        if men in mentions:
                            mentions.remove(men)
                        new_men = men.replace(groundtruth_string, "")
                        if any(letter.isalpha() for letter in new_men):
                            imperfect_mentions.append(new_men)
                        imperfect_correct += 1
                        imperfect_ground_truth_not_found -= 1
                        break
            for men in mentions:
                imperfect_excess_mentions += len(men.split(' '))
    num_ground_truth = correct + ground_truth_not_found
    imperfect_num_ground_truth = imperfect_correct + imperfect_ground_truth_not_found
    recall = (correct / num_ground_truth)
    precision = (correct / (correct + excess_mentions))
    imperfect_recall = (imperfect_correct / imperfect_num_ground_truth)
    imperfect_precision = (imperfect_correct / (imperfect_correct + imperfect_excess_mentions))
    num_mentions = len(entities) + gt_none
    avg_mentions = num_ground_truth / len(os.listdir(annotated_path))
    distinct_entities = []
    [distinct_entities.append(ent) for ent in entities if not distinct_entities.count(ent)]
    distinct_entities = len(distinct_entities)
    avg_distinct_entities = distinct_entities / len(os.listdir(annotated_path))
    standard_deviation = np.std(entities_in_document)
    wikipedia_entities = []
    [wikipedia_entities.append(ent) for ent in entities if ent[1] == 'w']
    linkedin_entities = []
    [linkedin_entities.append(ent) for ent in entities if ent[1] == 'l']
    test = []
    [test.append(ent) for ent in entities if ent[1] != 'l' and ent[1] != 'w']

    return precision, recall, imperfect_precision, imperfect_recall, num_mentions, gt_none, avg_mentions, distinct_entities, avg_distinct_entities, standard_deviation
    #recall = 73%: 73% of the ones annotated gets recognized, precision = 44%: Of the ones recognized, 44% should be recognized

# p, r, ip, ir, m, mn, avgm, dent, avgdent, std = ner_evaluator()
# print('Precision: ' + str(p))
# print('Recall: ' + str(r))
# print('Imperfect Precision: ' + str(ip))
# print('Imperfect Recall: ' + str(ir))
#p, r, ip, ir, m, mn, avgm, dent, avgdent, std = ner_evaluator('/media/erisos/My Passport/Entities2')
# print('Precision: ' + str(p))
# print('Recall: ' + str(r))
# print('Imperfect Precision: ' + str(ip))
# print('Imperfect Recall: ' + str(ir))
# print('Mentions: ' + str(m))
# print('Mentions with no entity: ' + str(mn))
# print('Average mentions per document: ' + str(avgm))
# print('Distinct entities found: ' + str(dent))
# print('Average distinct entities per document: ' + str(avgdent))
# print('Standard deviation for entities in articles: ' + str(std))