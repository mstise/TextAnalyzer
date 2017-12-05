#From folder of recognized entities and folder of annotated entities, get an accuracy score.

import os
import re
import paths

def clean_line(line):
    indices = [m.start() for m in re.finditer('\'', line)]
    grouped_indices =list(zip(indices[0::2], indices[1::2]))
    cleaned_line = line[grouped_indices[0][0]+1 : grouped_indices[0][1]]
    for i, k in grouped_indices[1:len(grouped_indices)]:
        cleaned_line += ' ' + line[i+1 : k]
    return cleaned_line

def get_disambiguations(filename, path):
    mentions = []
    for line in open(path + "/" + filename):
        new_line = clean_line(line)
        mentions.append(new_line)
    return mentions


def ned_evaluator(disambiguated_path="/home/duper/Desktop/Predicted_Disambiguations", annotated_path="/home/duper/Desktop/entiti"):
    correct = 0
    for filename in os.listdir(annotated_path):
        mentions = get_disambiguations(filename, disambiguated_path)
        for line in open(annotated_path + "/" + filename):
            ground_truths = re.findall(r'\|[^\]]*\]\*\]', line)
            for ground_truth in ground_truths:
                groundtruth_string = str(ground_truth[1:-3])
                if groundtruth_string in mentions:
                    mentions.remove(groundtruth_string)
                    correct += 1
    precision_slash_accuracy = (correct / (correct + len(mentions)))

    return precision_slash_accuracy

#precision_slash_accuracy = ner_evaluator()
