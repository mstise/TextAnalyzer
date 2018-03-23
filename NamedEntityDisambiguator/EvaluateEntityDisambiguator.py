#From folder of recognized entities and folder of annotated entities, get an accuracy score.

import os
import re
import paths
from NamedEntityRecognizer.EvaluateEntityRecognizer import correctly_recognized_lists

def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line

def get_disambiguations(filename, path):
    entities = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        entities.append(new_line)
    return entities


def ned_evaluator(disambiguated_path=paths.get_external_disambiguated_outputs(), annotated_path=paths.get_external_annotated(), remove=[]):
    correct = 0
    incorrect = 0
    for filename in os.listdir(annotated_path):
        recognized_mentions = correctly_recognized_lists(filename, entity_path=paths.get_all_external_entities_path(), remove=remove)
        new_rec_men = []
        for men in recognized_mentions:
            if men[1][-1:] == '/':
                new_men = [men[0], men[1][:-1]]
                new_rec_men.append(new_men)
            else:
                new_rec_men.append(men)
        recognized_mentions = new_rec_men
        ent_men_disambiguated = []
        for line in open(disambiguated_path + "/" + filename):
            gt_mention = re.findall(r'.*, \[u', line)
            gt_entity = re.findall(r'\[u\'.*\'\]', line)
            if gt_mention == []:
                gt_mention = re.findall(r'.*, \[', line)
                if gt_mention != []:
                    mention = gt_mention[0] + 'u'
                    gt_mention.remove(gt_mention[0])
                    gt_mention.append(mention)
            if gt_entity == []:
                gt_entity = re.findall(r'\[u\'.*\]\'', line)
                if gt_entity != []:
                    entity = gt_entity[0][:-2] + "\']"
                    gt_entity.remove(gt_entity[0])
                    gt_entity.append(entity)
                else:
                    gt_entity = re.findall(r'\[.*\]', line)
                    if gt_entity != []:
                        entity = '[u\'' + gt_entity[0][1:-1] + '\']'
                        gt_entity.remove(gt_entity[0])
                        gt_entity.append(entity)
            do_continue = False
            for rem in remove:
                if '[u\'' + rem in gt_entity[0]:
                    do_continue = True
            if do_continue:
                continue
            if gt_entity[0][-5:] == '/da\']':
                gt_entity[0] = gt_entity[0][:-5] + '\']'
            ent_men_disambiguated.append([gt_mention[0][:-4].lower(), gt_entity[0][3:-2].lower()])

        for mention in recognized_mentions:
            if not any(mention[0] in disambiguated[0] for disambiguated in ent_men_disambiguated):
                continue
            if mention in ent_men_disambiguated:
                ent_men_disambiguated.remove(mention)
                correct += 1
            else:
                incorrect += 1

    return correct / (correct+incorrect)

# accuracy_for_everything = ned_evaluator()
# accuracy_without_linkedin = ned_evaluator(remove=['l.'])
# accuracy_without_none_and_linkedin = ned_evaluator(remove=['None', 'l.'])
# print('Accuracy for wikipedia disambiguator: ' + str(accuracy_for_everything))
# print('Accuracy for wikipedia disambiguator not including LinkedIn entities: ' + str(accuracy_without_linkedin))
# print('Accuracy for wikipedia disambiguator not including LinkedIn or None entities: ' + str(accuracy_without_none_and_linkedin))
#path = paths.get_external_disambiguated_outputs() + '2'
# accuracy_for_everything = ned_evaluator(disambiguated_path=path)
# accuracy_without_linkedin = ned_evaluator(remove=['w.'], disambiguated_path=path)
#accuracy_without_none_and_linkedin = ned_evaluator(remove=['None', 'w.'], disambiguated_path=path)
# print('Accuracy for linkedin disambiguator: ' + str(accuracy_for_everything))
# print('Accuracy for linkedin disambiguator not including Wikipedia entities: ' + str(accuracy_without_linkedin))
#print('Accuracy for linkedin disambiguator not including Wikipedia or None entities: ' + str(accuracy_without_none_and_linkedin))