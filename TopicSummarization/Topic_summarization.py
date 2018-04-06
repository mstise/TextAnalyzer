import re
from sklearn.metrics.pairwise import cosine_similarity


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

def topic_summarization(text, query, amount_of_summarizations=1):
    scores = {}
    topic_candidates = re.split('(?<=[.!?:]) +',text)
    for topic_candidate in topic_candidates:
        score = 0
        # Split the topic candidate into individual words and check whether any match the query words, score accordingly
        words = split_sentence_into_list(topic_candidate)
        for term in query:
            for word in words:
                if term.lower() == word:
                    score += query[term]
        scores[topic_candidate] = score
    result = (sorted(scores, key=scores.get, reverse=True))
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

test = topic_summarization('Dette er en tests streng. Den handler om Aalborg Pirates! Og har åbenbart også noget, med, frederikshavn White Hawks at gøre?. Dette er stadig en tests streng',
                    {'Aalborg': 9, 'White hawks': 2, 'test': 0.5, 'en': 0.1})
testing = 1