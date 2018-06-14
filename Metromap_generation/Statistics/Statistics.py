#statistics:
#OVERALL
#How many recognitions
#How many disambiguations
#Avg size of document in words
#Avg rec entity per document
#Avg disambed entity per document
#
#PER CASE:
#How many recognitions
#How many disambiguations
#How many unique recognitions
#How many unique disambiguations
#Avg size of document in words
#Avg rec entity per document
#Avg disambed entity per document
#Avg unique rec entity per document
#Avg unique disambed entity per document

from Metromap_generation.TimelineUtils import get_rec_disamb_pairs
import random
import numpy as np
random.seed(10)
np.random.seed(10)
import os

DISAMBIGUATED_PATH = 'Disambiguated'
PROCESSED_PATH = 'Processed_news'
EXAMPLE_PATH = 'example_documents'

def search_string_statistics(case):
    # How many recognitions
    # How many disambiguations
    # Avg size of document in words
    # Avg rec entity per document
    # Avg disambed entity per document
    # How many unique recognitions
    # How many unique disambiguations
    # Avg unique rec entity per document
    # Avg unique disambed entity per document
    num_rec = 0
    num_dis = 0
    docsizes = []
    num_docrecs = []
    num_docdisambs = []
    all_rec = []
    all_disamb = []
    num_unique_docrecs = []
    num_unique_docdisambs = []
    counter = 0
    for filename in os.listdir('example_documents/' + case):
        d_ents = get_rec_disamb_pairs(filename, DISAMBIGUATED_PATH)
        rec_lst = []
        dis_lst = []
        for d_ent in d_ents:
            dis = '*w' + d_ent[1][2:].lower().replace('.', '')
            rec = '*r' + d_ent[0].lower().replace('.', '')
            rec_lst.append(rec)
            if dis != '*wne':
                dis_lst.append(dis)
        docsizes.append(len(str(open(PROCESSED_PATH + '/' + filename).read()).split(' ')))
        num_docrecs.append(len(rec_lst))
        num_docdisambs.append(len(dis_lst))
        num_rec += len(rec_lst)
        num_dis += len(dis_lst)
        all_rec.extend(rec_lst)
        all_disamb.extend(dis_lst)
        num_unique_docrecs.append(len(set(rec_lst)))
        num_unique_docdisambs.append(len(set(dis_lst)))


        counter += 1
    docavg = np.mean(docsizes)
    recavg = np.mean(num_docrecs)
    disavg = np.mean(num_docdisambs)
    urecavg = np.mean(num_unique_docrecs)
    udisavg = np.mean(num_unique_docdisambs)
    print(case.upper())
    print('How many recognitions: ' + str(num_rec))
    print('How many disambiguations: ' + str(num_dis))
    print('Avg size of document in words: ' + str(docavg))
    print('Avg rec entity per document: ' + str(recavg))
    print('Avg disambed entity per document: ' + str(disavg))
    print('How many unique recognitions: ' + str(len(set(all_rec))))
    print('How many unique disambiguations: ' + str(len(set(all_disamb))))
    #Cut the ones below because they give nearly the same result :b
    #print('Avg unique rec entity per document: ' + str(urecavg))
    #print('Avg unique disambed entity per document: ' + str(udisavg))


def Overall_statistics():
    num_rec = 0
    num_dis = 0
    docsizes = []
    num_docrecs = []
    num_docdisambs = []
    counter = 0
    for filename in os.listdir('Disambiguated'):
        if counter % 100 == 0:
            print(str(counter))
        d_ents = get_rec_disamb_pairs(filename, DISAMBIGUATED_PATH)
        dis_count = 0
        rec_count = 0
        for d_ent in d_ents:
            dis = '*w' + d_ent[1][2:].lower().replace('.', '')
            rec_count += 1
            if dis != '*wne':
                dis_count += 1
        docsizes.append(len(str(open(PROCESSED_PATH + '/' + filename).read()).split(' ')))
        num_docrecs.append(rec_count)
        num_docdisambs.append(dis_count)
        num_rec += rec_count
        num_dis += dis_count

        counter += 1
    docavg = np.mean(docsizes)
    recavg = np.mean(num_docrecs)
    disavg = np.mean(num_docdisambs)
    print('How many recognitions: ' + str(num_rec))
    print('How many disambiguations: ' + str(num_dis))
    print('Avg size of document in words: ' + str(docavg))
    print('Avg rec entity per document: ' + str(recavg))
    print('Avg disambed entity per document: ' + str(disavg))

search_string_statistics('Aalborg_Portland')
search_string_statistics('Birgit_Hansen')
search_string_statistics('Industri')
search_string_statistics('Per_Michael_Johansen')
search_string_statistics('Thomas_Kastrup')
search_string_statistics('Karneval')
search_string_statistics('Aab')
search_string_statistics('Frederikshavn')
search_string_statistics('Socialdemokratiet')
#Overall_statistics()