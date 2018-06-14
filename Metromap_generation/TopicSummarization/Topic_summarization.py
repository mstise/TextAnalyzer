import re
import shelve

from sklearn.metrics.pairwise import cosine_similarity
from dateutil import relativedelta
from Metromap_generation.TimelineUtils import get_rec_disamb_pairs

def split_sentence_into_list(sentence):
    result = re.sub("[^\w]", " ", sentence).split()
    for word in result:
        result[result.index(word)] = word.lower()
    return result

def figure_out_index_for_sentence(sentence, index_list):
    words = split_sentence_into_list(sentence)
    for word in words:
        if word not in index_list:
            index_list.append(word)
    return index_list

def create_vector_for_topic(topic, vectorizer_list):
    result_vector = []
    for value in vectorizer_list:
        result_vector.append(0)
    for word in split_sentence_into_list(topic):
        index = vectorizer_list.index(word)
        result_vector[index] += 1
    return result_vector

def are_topics_similar(topic1, topic2, threshold=0.8):
    vectorizer_list = figure_out_index_for_sentence(topic1, [])
    vectorizer_list = figure_out_index_for_sentence(topic2, vectorizer_list)
    vector_for_topic1 = create_vector_for_topic(topic1, vectorizer_list)
    vector_for_topic2 = create_vector_for_topic(topic2, vectorizer_list)
    similarity = cosine_similarity([vector_for_topic1, vector_for_topic2])
    similarity = similarity[0,1]
    if similarity > threshold:
        return True
    else:
        return False

def ts(text, lemmatized_text, hypernyms_text, query, headline, cluster_number, ent2idf, dis2rec):
    scores = {}
    text = text.replace(".", ". ")
    text = text.replace(".", ". ").replace("!", "! ").replace("?", "? ").replace("/", "/ ")
    while " ." in text or " !" in text or " ?" in text or " /" in text:
        text = text.replace(" .", ".").replace(" !", "!").replace(" ?", "?").replace(" /", "/")
    lemmatized_text = lemmatized_text.replace(".", ". ").replace("!", "! ").replace("?", "? ").replace("/", "/ ")
    while " ." in lemmatized_text or " !" in lemmatized_text or " ?" in lemmatized_text or " /" in lemmatized_text:
        lemmatized_text = lemmatized_text.replace(" .", ".").replace(" !", "!").replace(" ?", "?").replace(" /", "/")
    lemmatized_topic_candidates = re.split('(?<=[.!?]) +', lemmatized_text)
    for lem_entry in range(len(lemmatized_topic_candidates) - 1, 0, -1):
        #lemmatized_topic_candidates[lem_entry] = lemmatized_topic_candidates[lem_entry].replace(" .", ".").replace(" /", "/")
        #lemmatized_topic_candidates[lem_entry] = lemmatized_topic_candidates[lem_entry].replace(" /", "/")
        if len(lemmatized_topic_candidates[lem_entry]) == 1 or len(lemmatized_topic_candidates[lem_entry]) == 0 or ' ' not in lemmatized_topic_candidates[lem_entry] or '\n' in lemmatized_topic_candidates[lem_entry] or (len(lemmatized_topic_candidates[lem_entry].split()) == 2 and not lemmatized_topic_candidates[lem_entry].replace('|', '').split()[0].isalpha()):
            del lemmatized_topic_candidates[lem_entry]
    #topic_candidates = [text]
    topic_candidates = re.split('(?<=[.!?]) +', text)
    for entry in range(len(topic_candidates) - 1, 0, -1):
        if len(topic_candidates[entry]) == 1 or len(topic_candidates[entry]) == 0 or ' ' not in topic_candidates[entry] or '\n' in topic_candidates[entry] or (len(topic_candidates[entry].split()) == 2 and not topic_candidates[entry].split()[0].isalpha()):
            del topic_candidates[entry]

    topic_candidate_number = 0
    for topic_candidate in topic_candidates:
        score = 0
        if topic_candidate == '' or topic_candidate == ' ' or topic_candidate == '.' or topic_candidate == '?' or topic_candidate == '!':
            continue
        # Split the topic candidate into individual words and check whether any match the query words, score accordingly
        words = split_sentence_into_list(topic_candidate)
        try:
            lemmatized_topic_candidate = lemmatized_topic_candidates[topic_candidate_number]
        except:
            print('um')
            exit()
        lemmatized_words = split_sentence_into_list(lemmatized_topic_candidate)
        hypernym_list = hypernyms_text.split('\n')
        hypernyms = {}
        used_words = []
        for hypernym_set in hypernym_list:
            if hypernym_set == '':
                continue
            hypernym = hypernym_set.split('[')[1][0:-1]
            hypernym_split = hypernym.split(',')
            hyponym = hypernym_set.split('[')[0][0:-1]
            for hyper in hypernym_split:
                if hyper not in hypernyms:
                    hypernyms[hyper] = [hyponym]
                else:
                    hypernyms[hyper].append(hyponym)
        if next(iter(query.values())) == -1:
            topicNumber = 1
            topic1 = ''
            topic2 = ''
            topic3 = ''
            for word in headline[str(cluster_number)]:
                if topicNumber == 1 and len(word[0]) > 0 and word[0] != '.':
                    topic1 += word[0] + ' '
                elif topicNumber == 2 and len(word[0]) > 0 and word[0] != '.':
                    topic2 += word[0] + ' '
                elif topicNumber == 3 and len(word[0]) > 0 and word[0] != '.':
                    topic3 += word[0] + ' '
                if len(word[0]) > 0 and word[0][-1] == '.' and word[0] != '.':
                    if topicNumber == 1 and len(topic1) > 0:
                        topicNumber += 1
                    elif topicNumber == 2 and len(topic2) > 0:
                        topicNumber += 1
                    elif topicNumber == 3 and len(topic3) > 0:
                        topicNumber += 1
            #topic = topic[0:-1] + '.'
            scores[topic1] = 3
            scores[topic2] = 2
            scores[topic3] = 1
        else:
            for term in query:
                score_for_term = query[term] # 1
                if term[0:2] == '*w' or term[0:2] == '*r':
                    try:
                        score_for_term = score_for_term * ent2idf[term]
                    except:
                        print('not in ent2idf: ' + term)
                    if score_for_term * 20 > 3:
                        score_for_term = 3
                    else:
                        score_for_term *= 20
                if term[0:2] == '*w':
                    try:
                        recognized = dis2rec[term]
                    except:
                        tmp = ''
                        for word in term.split()[:-1]:
                            tmp += word + ' '
                        tmp += '(' + term.split()[-1] + ')'
                        if tmp in dis2rec:
                            recognized = dis2rec[tmp]#
                            print(term + 'handled')
                        tmp = ''#
                        for word in term.split()[:-2]:
                            tmp += word + ' '
                        if len(term.split()) > 2:
                            tmp += '(' + term.split()[-2] + ' ' + term.split()[-1] + ')'
                        if tmp in dis2rec:
                            recognized = dis2rec[tmp]#
                            print(term + ' handled')
                        else:#l
                            print(term + ' failed')#
                            print('with ' + tmp)
                            continue
                    for term in recognized:
                        term = term[2:]
                        words_in_term = len(term.split())
                        current_word_set = 0
                        while current_word_set < len(words) - words_in_term:
                            words_term = ''
                            for word in words[current_word_set:current_word_set + words_in_term]:
                                words_term += word + " "
                            words_term = words_term[:-1]
                            if term.lower() == words_term.lower():
                                score += score_for_term
                            current_word_set += 1
                elif term[0:2] == '*r':
                    term = term[2:]
                    if len(term.split('*r')) > 1:
                        test = term.split('*r')
                        testing = 1
                    terms = term.split('*r')
                    do_break = False
                    for term in terms:
                        words_in_term = len(term.split())
                        current_word_set = 0
                        while current_word_set < len(words) - words_in_term:
                            words_term = ''
                            for word in words[current_word_set:current_word_set + words_in_term]:
                                words_term += word + " "
                            words_term = words_term[:-1]
                            if term.lower() == words_term.lower():
                                score += score_for_term
                                do_break = True
                                break
                            current_word_set += 1
                        if do_break:
                            break
                elif term[0:2] == '*f':
                    for word in lemmatized_words:
                        for hypernym in hypernyms:
                            if word in hypernyms[hypernym] and term[2:] == hypernym:
                                score += score_for_term
                                used_words.append(word)
                                break
                elif score_for_term > 0:
                    for word in lemmatized_words:
                        if term.lower() == word.lower() and word not in used_words:
                            score += score_for_term
                            used_words.append(word)
                elif score_for_term < 0:
                    for word in words:
                        if term.lower() == word.lower():
                            score += score_for_term
        if score != 0:
            scores[topic_candidate] = score
        topic_candidate_number += 1
    # Check if any of the top topics are similar, and that we have enough to afford losing one, if so, delete the lower scoring one of them.
    candidates_to_delete = []
    candidates_already_checked = []
    if cluster_number == '28':
        TESTING = True
    for candidate1 in scores:
        candidates_already_checked.append(candidate1)
        chars_in_candidate1 = re.sub(r'[^A-Za-z]+', '', candidate1)
        for candidate2 in scores:
            if candidate2 in candidates_already_checked:
                continue
            chars_in_candidate2 = re.sub(r'[^A-Za-z]+', '', candidate2)
            if chars_in_candidate1 == chars_in_candidate2 and candidate2 not in candidates_to_delete:
                candidates_to_delete.append(candidate2)
            if are_topics_similar(candidate1, candidate2) and candidate2 not in candidates_to_delete:
                candidates_to_delete.append(candidate2)
    for candidate in candidates_to_delete:
        del scores[candidate]
    # Make sure any 1-document cluster only returns one summarization (headline)
    query_text = ''
    for text in query:
        query_text += ' ' + text
    candidates_to_delete = []
    for candidate in scores:
        if scores[candidate] < 0:
            for word in candidate.split(' '):
                for char in '.,:;!?"\'':
                    word = word.replace(char, '')
                if word.lower() not in query_text and '*w' + word.lower() not in query_text and '*r' + word.lower() not in query_text:
                    candidates_to_delete.append(candidate)
                    break
            if candidate not in candidates_to_delete:
                for word in query:
                    if word not in candidate.lower() and (word[0] == '*' and word[2:] not in candidate.lower()):
                        candidates_to_delete.append(candidate)
                        break
    for candidate in candidates_to_delete:
        del scores[candidate]
    # Make sure not to get out of bounds when returning
    #summarizations = (sorted(scores, key=scores.get, reverse=True))
    #if len(summarizations) < amount_of_summarizations:
    #    amount_of_summarizations = len(summarizations)
    #for candidate1_index in range(len(summarizations) - 1, 0, -1):
    #    if len(summarizations) <= amount_of_summarizations:
    #        break
    #    for candidate2_index in range(len(summarizations) - 1, 0, -1):
    #        if candidate1_index >= candidate2_index or candidate1_index >= amount_of_summarizations or len(summarizations) <= amount_of_summarizations:
    #            break
    #        if are_topics_similar(summarizations[candidate1_index], summarizations[candidate2_index]):
    #            del summarizations[candidate2_index]
    return scores# summarizations[0:amount_of_summarizations]

def topic_summarization(cluster2term, clusters2headlines, cluster2resolution, documents, dis2rec, sentences_per_cluster=3):
    cluster2summaries = {}
    already_seen_words = {}
    ent2idf = df_creator(documents)
    for cluster in cluster2term.keys():
        tuples = cluster2term[str(cluster)]
        query = {}
        for entry in tuples:
            query[entry[0]] = entry[1]
        for word in query:
            already_seen_words.setdefault(word, 0)
            already_seen_words[word] += 1
    counter = 0
    for cluster in cluster2term:
        if counter % 10 == 0:
            print(str(counter) + ' of ' + str(len(cluster2term.keys())))
        document2summary_candidates = {}
        query = {}
        tuples = cluster2term[str(cluster)]
        for entry in tuples:
            if entry[1] == -1:
                query[entry[0]] = entry[1]
            else:
                if already_seen_words[entry[0]] > 5:
                    query[entry[0]] = 1 #0.5
                else:
                    query[entry[0]] = 1
            #query[entry[0]] = entry[1]
        for document in documents[int(cluster2resolution[str(cluster)])]:
            #if get_date_from_docname(document)
            doc = open('example_documents/Socialdemokratiet/' + document, "r")#v
            text = doc.read() + ". "
            text = text.replace('..', '.')
            doc = open('Lemmatized/' + document, "r")
            lemmatized_text = doc.read() + ". "
            lemmatized_text = lemmatized_text.replace('..', '.')
            doc = open('Ranked/' + document, "r")
            hyponyms_text = doc.read()
            text = replace_abbreviation_dots(text)
            lemmatized_text = replace_abbreviation_dots(lemmatized_text)
            summary_candidates = ts(text, lemmatized_text, hyponyms_text, query, clusters2headlines, cluster, ent2idf, dis2rec)
            for candidate in summary_candidates.keys():
                document2summary_candidates[candidate] = [summary_candidates[candidate], document]
        if summary_candidates == []:
            continue
        winner_summaries = []
        for candidate in document2summary_candidates:
            #if len(winner_summaries) < 5:
            if len([equal for equal in winner_summaries if re.sub(r'[^A-Za-z]+', '', candidate.replace('\t','')) == re.sub(r'[^A-Za-z]+', '', equal[1].replace('\t',''))]) < 1:
                winner_summaries.append([document2summary_candidates[candidate][0], candidate, document2summary_candidates[candidate][1]])
                winner_summaries.sort(key=lambda x: x[0], reverse=True)
            #elif winner_summaries[4][0] < document2summary_candidates[candidate][0]:
            #    del winner_summaries[4]
            #    winner_summaries.append([document2summary_candidates[candidate][0], candidate, document2summary_candidates[candidate][1]])
            #    winner_summaries.sort(key=lambda x: x[0], reverse=True)
        cluster2summaries.setdefault(cluster, [])
        for summary in winner_summaries:
            cluster2summaries[cluster].append(summary)

        # Scale scores based on the time of the document
        timescore = {}
        for summary in cluster2summaries[cluster]:
            time = get_date_from_docname(summary[2])
            timescore.setdefault(time, 0)
            timescore[time] += summary[0]

        if len(timescore) > 0:
            winner_time = max(timescore.keys(), key=(lambda k: timescore[k]))
            for summary in cluster2summaries[cluster]:
                cluster_time = get_date_from_docname(summary[2])
                time_difference = relativedelta.relativedelta(winner_time, cluster_time)
                days = time_difference.days
                time_factor = 1
                while days != 0:
                    time_factor = time_factor - time_factor * 0.05
                    if days > 0:
                        days -= 1
                    else:
                        days += 1
                summary[0] *= time_factor
            cluster2summaries[cluster].sort(key=lambda x: x[0], reverse=True)
            test = 1

    #REMEMBER THAT find_primary_entity SHOULD NOT BE FURTHER INDENTED THAN IT IS, SOME MOVING MIGHT BE REQUIRED
    #find_primary_entity(cluster2summaries, query, ent2idf)
        cluster2summaries[cluster] = cluster2summaries[cluster][:sentences_per_cluster]
        clusters2summaries_for_cluster = []
        cluster_total_score = 0
        for summary in cluster2summaries[cluster]:
            if summary[0] >= 1:
                clusters2summaries_for_cluster.append(summary)
                cluster_total_score += summary[0]
        if cluster_total_score < 15 and list(query.values())[0] != -1:
            clusters2summaries_for_cluster = []
        cluster2summaries[cluster] = clusters2summaries_for_cluster

#        clusters_to_remove = []
#        for summary in cluster2summaries[cluster]:
#            if summary == []:
#                for summary2 in cluster2summaries[cluster]:

#                test = 1
        counter += 1
    return cluster2summaries


def replace_abbreviation_dots(text):
    if "tidl." in text or "f.eks." in text or "fx." in text:
        test = 1
    text = text.replace("tidl.", "tidl\u2024").replace("f.eks.", "f\u2024eks\u2024").replace("fx.", "fx\u2024")
    return text


#test = ts('Dette er en tests streng. Den handler om Aalborg Pirates! Og har åbenbart også noget, med, frederikshavn White Hawks at gøre?. Dette er stadig en tests streng',
#                    {'Aalborg': 9, '*wWhite hawks': 2, 'test': 0.5, 'en': 0.1})
#testing = 1

from datetime import date
def get_date_from_docname(docname):
    timepoint = docname.split('_')[-2]
    timepoint = date(int(timepoint[0:4]), int(timepoint[4:6]), int(timepoint[6:8]))
    return timepoint

def find_primary_entity(cluster2summaries, query, ent2idf):
    # Check for the primary entity in the cluster
    for cluster in cluster2summaries:
        scores = cluster2summaries[cluster]
        entity_score = {}
        for score_and_sentence in scores:
            sentence_score = score_and_sentence[0]
            if sentence_score < 3:
                continue
            sentence = score_and_sentence[1]
            for term in query:
                if term[:2] == "*r" or term[:2] == "*w":
                    entity_names = term[2:].split("*r")
                    for entity_name in entity_names:
                        if entity_name.lower() in sentence.lower():
                            entity_score.setdefault(term, 0)
                            entity_score[term] += sentence_score * ent2idf[term]
                            break
        if len(entity_score) == 0:
            cluster2summaries[cluster] = cluster2summaries[cluster][:5]
            continue
        winner_ent = sorted(list(entity_score.items()), key=lambda x: x[1], reverse=True)[0][0]
        summaries_to_include = []
        for summary_triple in cluster2summaries[cluster]:
            summary_triple.append(winner_ent)
            entities = winner_ent[2:].split("*r")
            for entity in entities:
                if entity.lower() in summary_triple[1].lower():
                    summaries_to_include.append(summary_triple)
                    break
        cluster2summaries[cluster] = summaries_to_include

def do_the_lists_contain_the_same(list1, list2):
    result = True
    for entry in list1:
        if entry not in list2:
            result = False
            break
    return result

def df_creator(document_clusters):
    documents = []
    for doc_cluster in document_clusters:
        for doc in doc_cluster:
            documents.append(doc)
    clusters2term = shelve.open('dbs/clusters2term')
    ent2doc = shelve.open('dbs/ent2doctuple')
    docidx2name = shelve.open('dbs/docidx2name')
    entities = set()
    for cluster in clusters2term:
        for term in clusters2term[cluster]:
            if term[0][:2] == '*w' or term[0][:2] == '*r':
                entities.add(term[0])
    ent2idf = {}
    for entity in entities:
        recognized = entity[2:].split("*r")
        for rec in recognized:
            if "*w" + rec in ent2doc:
                doctuples = ent2doc["*w" + rec]
            elif "*r" + rec in ent2doc:
                doctuples = ent2doc["*r" + rec] #
            try:
                for doctuple in doctuples:
                    if docidx2name[str(doctuple[0])] in documents:
                        ent2idf.setdefault(entity, 0)
                        ent2idf[entity] += doctuple[1]
            except:
                print(entity + ' does not exist in ent2doc')
    for entity in ent2idf:
        ent2idf[entity] = 1 / ent2idf[entity]
    return ent2idf

def test_topic_summarization():
    clusters2term = shelve.open("dbs/clusters2term")
    clusters2headlines = shelve.open("dbs/zclusters2headlines")
    cluster2resolution = shelve.open("dbs/cluster2resolution")
    dis2rec = shelve.open("dbs/dis2rec")
    dirpath = 'example_documents/Aalborg_Kommune'
    resolution = 'month'
    from Metromap_generation.Resolution import resolutionize
    partitioned_docs, _ = resolutionize(dirpath, resolution=resolution)
    topic_summarization(clusters2term, clusters2headlines, cluster2resolution, partitioned_docs, dis2rec)

#test_topic_summarization()