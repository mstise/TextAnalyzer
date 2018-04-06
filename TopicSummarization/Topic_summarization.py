import re


def similarity_comparer(topic1, topic2, threshold=0):
    print('Not yet implemented')

def topic_summarization(text, query):
    scores = {}
    topic_candidates = re.split('(?<=[.!?:]) +',text)
    for test in topic_candidates:
        score = 0
        words = re.sub("[^\w]", " ", test).split()
        for term in query:
            for word in words:
                if term.lower() == word.lower():
                    score += query[term]
        scores[test] = score
    something = sorted(scores, key=scores.get, reverse=True)
    testing = 1

topic_summarization('Dette er en tests streng. Den handler om Aalborg Pirates! Og har åbenbart også noget, med, frederikshavn White Hawks at gøre?',
                    {'Aalborg': 9, 'White hawks': 2, 'test': 0.5, 'en': 0.1})