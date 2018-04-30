import re
from sklearn.metrics.pairwise import cosine_similarity
from nltk import bigrams


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

def ts(text, lemmatized_text, hypernyms_text, query, amount_of_summarizations=5):
    scores = {}
    topic_candidates = re.split('(?<=[.!?]) +', text)
    lemmatized_topic_candidates = re.split('(?<=[.!?]) +', lemmatized_text)
    topic_candidate_number = 0
    for topic_candidate in topic_candidates:
        score = 0
        # Split the topic candidate into individual words and check whether any match the query words, score accordingly
        words = split_sentence_into_list(topic_candidate)
        lemmatized_topic_candidate = lemmatized_topic_candidates[topic_candidate_number]
        lemmatized_words = split_sentence_into_list(lemmatized_topic_candidate)
        hypernym_list = hypernyms_text.split('\n')
        hypernyms = {}
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
        for term in query:
            score_for_term = 1# query[term] # 1
            if term[0:2] == '*w' or term[0:2] == '*r':
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
            elif term[0:2] == '*f':
                for word in lemmatized_words:
                    if word in hypernyms and term[2:] in hypernyms[word]:
                        score += score_for_term
                        break
            else:
                for word in lemmatized_words:
                    if term.lower() == word.lower():
                        score += score_for_term
        scores[topic_candidate] = score
        topic_candidate_number += 1
    result = (sorted(scores, key=scores.get, reverse=True))
    # Make sure not to get out of bounds when returning
    if len(result) < amount_of_summarizations:
        amount_of_summarizations = len(result)
    # Check if any of the top topics are similar, and that we have enough to afford losing one, if so, delete the lower scoring one of them.
    for candidate1_index in range(len(result) - 1, 0, -1):
        if len(result) <= amount_of_summarizations:
            break
        for candidate2_index in range(len(result) - 1, 0, -1):
            if candidate1_index >= candidate2_index or candidate1_index >= amount_of_summarizations or len(result) <= amount_of_summarizations:
                break
            if are_topics_similar(result[candidate1_index], result[candidate2_index]):
                del result[candidate2_index]
    return result[0:amount_of_summarizations]

def topic_summarization(cluster2term, cluster2resolution, documents):
    result = {}
    for cluster in cluster2term:
        query = {}
        tuples = cluster2term[str(cluster)]
        text = ''
        lemmatized_text = ''
        hyponyms_text = ''
        for entry in tuples:
            query[entry[0]] = entry[1]
        for document in documents[int(cluster2resolution[str(cluster)])]:
            doc = open('example_documents/Aalborg_pirates/' + document, "r")
            text += doc.read() + ". "
            doc = open('Lemmatized/' + document, "r")
            lemmatized_text += doc.read() + ". "
            doc = open('Ranked/' + document, "r")
            hyponyms_text += doc.read()
        text = text.replace('..', '.')
        lemmatized_text = lemmatized_text.replace('..', '.')
        cluster_result = ts(text, lemmatized_text, hyponyms_text, query)
        include = True
        for a_result in result:
            if do_the_lists_contain_the_same(result[a_result], cluster_result):
                include = False
        if include:
            result[cluster] = cluster_result
    return result

#test = ts('Dette er en tests streng. Den handler om Aalborg Pirates! Og har åbenbart også noget, med, frederikshavn White Hawks at gøre?. Dette er stadig en tests streng',
#                    {'Aalborg': 9, '*wWhite hawks': 2, 'test': 0.5, 'en': 0.1})
#testing = 1

def do_the_lists_contain_the_same(list1, list2):
    result = True
    for entry in list1:
        if entry not in list2:
            result = False
            break
    return result